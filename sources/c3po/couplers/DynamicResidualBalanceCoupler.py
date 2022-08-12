# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class DynamicResidualBalanceCoupler. """
from __future__ import print_function, division

from c3po.Coupler import Coupler
from c3po.couplers.FixedPointCoupler import FixedPointCoupler
from c3po.CollaborativeDataManager import CollaborativeDataManager

class DynamicResidualBalanceCoupler(Coupler):

    """! DynamicResidualBalanceCoupler inherits from Coupler and proposes a dynamic residual balance algorithm.

    The class proposes an algorithm for the resolution of F(X) = X. Thus DynamicResidualBalanceCoupler is a Coupler working with :

    - Two PhysicsDrivers defining the calculations to be made each time F is called.
    - Two DataManager allowing to manipulate the data in the coupling (the X) and the precisions reached and to be reached.
    - Seven Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.

    Each DataManager is normalized with its own norm got after the first iteration.
    They are then used as a single DataManager using CollaborativeDataManager.

    - Exch_CurrentResidual1 and Exch_CurrentResidual2 should imply the computation of one iteration/time step in order to have access to the initial residual of each solver

    The control of the convergence, maximal number of iterations and damping factor is done through self.fixedPoint_
    """

    def __init__(self, physics, exchangers, dataManagers):
        Coupler.__init__(self, physics, exchangers, dataManagers)

        if not isinstance(physics, dict) or not isinstance(exchangers, dict) or not isinstance(dataManagers, dict):
            raise Exception("FixedPointCoupler.__init__ physics, exchangers and dataManager must be dictionaries!")
        if len(physics) != 2:
            raise Exception("DynamicResidualBalanceCoupler.__init__ There must be exactly two PhysicsDriver")
        if len(exchangers) != 7:
            raise Exception("DynamicResidualBalanceCoupler.__init__ There must be exactly four Exchanger")
        if len(dataManagers) != 2:
            raise Exception("DynamicResidualBalanceCoupler.__init__ There must be exactly two DataManager")
        for ph in physics.keys():
            if ph not in ["Solver1", "Solver2"] :
                raise Exception('DynamicResidualBalanceCoupler.__init__ PhysicsDriver dictionary keys must be : ["Solver1", "Solver2"]')
        for ek in exchangers.keys():
            if ek not in ["Exch_1to2", "Exch_2toData", "Exch_Datato1", "Exch_CurrentResidual1", "Exch_LastResidual1", "Exch_CurrentResidual2", "Exch_LastResidual2"] :
                raise Exception('DynamicResidualBalanceCoupler.__init__ Exchangers dictionary keys must be : ["Exch_1to2", "Exch_2toData", "Exch_Datato1", "Exch_CurrentResidual1", "Exch_LastResidual1", "Exch_CurrentResidual2", "Exch_LastResidual2"]')
        for dm in dataManagers.keys():
            if dm not in ["DataCoupler", "DataResiduals"] :
                raise Exception('DynamicResidualBalanceCoupler.__init__ DataManager dictionary keys must be : ["DataCoupler", "DataResiduals"]')
        self.isStationaryMode_ = False
        self.initDt_ = False

        self.epsSolver1Ref_ = 1e-6
        self.residualSolver1Initial_ = 0.
        self.accuracySolver1_ = 0.
        self.accuracySolver1Old_ = 0.
        self.accuracySolver1Reached_ = False # Tell if a fully converged computation has been performed or not
        self.convRateSolver1_ = 0.

        self.epsSolver2Ref_ = 1e-4
        self.residualSolver2Initial_ = 0.
        self.accuracySolver2_ = 0.
        self.accuracySolver2Old_ = 0.
        self.accuracySolver2Reached_ = False # Tell if a fully converged computation has been performed or not
        self.convRateSolver2_ = 0.

        self.residualTotal_ = 0.
        self.residualDemiTotal_ = 0.

        self.firstIteration_ = True

        # Creation of a fixed point corresponding to the intial problem F(X) = X
        self.fixedPoint_ = FixedPointCoupler([self], [self._exchangers["Exch_2toData"], self._exchangers["Exch_Datato1"]], [self._dataManagers["DataCoupler"]])

        self.namePrecisionSolver1_ = "ACCURACY"
        self.namePrecisionSolver2_ = "ACCURACY"

        self.precisionReached_ = False


    def setTargetResiduals(self, targetSolver1, targetSolver2):
        """ Set the target residuals for the two coupled solvers. """
        self.epsSolver1Ref_ = targetSolver1
        self.epsSolver2Ref_ = targetSolver2

    def setNamePrecisionParameter(self, nameSolver1, namesolver2):
        """ Set the name for the getOutputDoubleValue(parameter) for the two coupled solvers. """
        self.namePrecisionSolver1_ = nameSolver1
        self.namePrecisionSolver2_ = namesolver2

    def setConvergenceParameters(self, tolerance, maxiter):
        """ Set the convergence parameters (tolerance and maximum number of iterations) of the inner fixed point loop. """
        self.fixedPoint_.setConvergenceParameters(tolerance, maxiter)

    def setDampingFactor(self, dampingFactor):
        """ Set a new damping factor for the inner fixed point loop. """
        self.fixedPoint_.setDampingFactor(dampingFactor)

    def solve(self, fixed_point = False):
        """! Call solveTimeStep() but store its return value instead of returning it.
        The output is accessible with getSolveStatus().

        @warning This method, in association with getSolveStatus(), should always be used inside C3PO instead of
        solveTimeStep(). They fit better with MPI use.
        @warning This method should never be redefined: define solveTimeStep() instead!
        """

        # First implementation proposed: at first, in C3PO, the fixed point should be called : it starts the coupling computation. Inside it, when physics.solve() is called, the Dynamic Residual Balance is called. Thus, a small redefinition of the solve() function is proposed here.
        if fixed_point :
            self.fixedPoint_.solve()
        else :
            self._solveStatus = self.solveTimeStep()

    def getSolveStatus(self):
        return self._solveStatus

    def solveTimeStep(self):

        if self.firstIteration_ :

            # -- Computation of the initial residual for Solver1
            self._exchangers["Exch_CurrentResidual1"].exchange()
            # -- Initial residual for Solver2, obtained from a first iteration during the initialisation
            self._exchangers["Exch_LastResidual2"].exchange()
            self.residualSolver1Initial_ = self._dataManagers["DataResiduals"].getOutputDoubleValue("CurrentResidual1")

            # -- Computation of the initial value of the normalized total residual
            self.residualTotal_ = self.residualSolver1Initial_ / self.epsSolver1Ref_

            # -- Convergence criteria for Solver1
            self.accuracySolver1_ = self._dataManagers["DataResiduals"].getOutputDoubleValue('LastResidual2') / self.epsSolver2Ref_ * self.epsSolver1Ref_
            self._physicsDrivers["Solver1"].setInputDoubleValue(self.namePrecisionSolver1_,self.accuracySolver1_)
            print("accuracySolver1_ : ", self.accuracySolver1_)

            # -- First iteration for Solver1
            self._physicsDrivers["Solver1"].solve()
            # -- Get the precision reached by Solver1 after the first iteration
            self._exchangers["Exch_LastResidual1"].exchange()

            # -- Exchange physical data between Solver1 and Solver2
            self._exchangers["Exch_1to2"].exchange()

            # -- Computation of the initial residual for Solver2
            self._exchangers["Exch_CurrentResidual2"].exchange()
            self.residualSolver2Initial_ = self._dataManagers["DataResiduals"].getOutputDoubleValue('CurrentResidual2')

            # -- Initial value of the total "demi residual"
            self.residualDemiTotal_ = self.residualSolver2Initial_ / self.epsSolver2Ref_ + self._dataManagers["DataResiduals"].getOutputDoubleValue('LastResidual1') /self.epsSolver1Ref_

            # -- Convergence criteria for Solver2
            self.accuracySolver2_ = self._dataManagers["DataResiduals"].getOutputDoubleValue('LastResidual1') / self.epsSolver1Ref_ * self.epsSolver2Ref_
            self._physicsDrivers["Solver2"].setInputDoubleValue(self.namePrecisionSolver2_, self.accuracySolver2_)
            print("accuracySolver2_ : ", self.accuracySolver2_)
            # -- First iteration for Solver2
            self._physicsDrivers["Solver2"].solve()

            # -- End of the first multiphysics iteration
            self.firstIteration_ = False

        else :
            # -- Exchange precision reached by Solver2 and compute current partial residual and intermediate coeff
            self._exchangers["Exch_LastResidual2"].exchange()
            residualPartial = self._dataManagers["DataResiduals"].getOutputDoubleValue('LastResidual2') / self.epsSolver2Ref_
            solver2ResidualScaled = self.residualSolver2Initial_ / self.epsSolver2Ref_ * self.epsSolver1Ref_ / 2.
            lastResidual = self.residualTotal_

            # -- Computation of the initial residual for Solver1
            self._exchangers["Exch_CurrentResidual1"].exchange()
            self.residualSolver1Initial_ = self._dataManagers["DataResiduals"].getOutputDoubleValue('CurrentResidual1')

            # -- Compute total residual and convergence rate
            self.residualTotal_ = self.residualSolver1Initial_ / self.epsSolver1Ref_ + residualPartial
            self.convRateSolver1_ = self.residualTotal_ / lastResidual

            # -- Deal with the new precision computed: we don't want a new precision smaller than the targeted one! And if one solver reachs its targeted precision, the one for the second solver is also set to its targeted value
            self.accuracySolver1Old_ = self._physicsDrivers["Solver1"].getOutputDoubleValue(self.namePrecisionSolver1_)
            if self.accuracySolver1Old_ > self.epsSolver1Ref_ and not self.accuracySolver2Reached_:
                # -- Average convergence rate
                conv = (self.convRateSolver1_ + self.convRateSolver2_) / 2.
                # -- New precision computed : should not be bellow self.epsSolver1Ref_
                self.accuracySolver1_ = max(self._dataManagers["DataResiduals"].getOutputDoubleValue('LastResidual2') / self.epsSolver2Ref_ * self.epsSolver1Ref_, self.epsSolver1Ref_)
                # -- New precision computed : should not be bigger than self.accuracySolver1Old_
                self.accuracySolver1_ = min(self.accuracySolver1_, self.accuracySolver1Old_)

                if self.accuracySolver1_ == self.epsSolver1Ref_ or self.accuracySolver2Reached_ :
                    self._physicsDrivers["Solver2"].setInputDoubleValue(self.namePrecisionSolver2_, self.epsSolver1Ref_)
                    self.accuracySolver1Reached_ = True # On va faire un calcule avec la precision cible
                    self.accuracySolver2_ = self.epsSolver2Ref_
                    self.accuracySolver1_ = self.epsSolver1Ref_
            else :
                self.accuracySolver1_ = self.epsSolver1Ref_
                self.accuracySolver2_ = self.epsSolver2Ref_
                self.accuracySolver1Reached_ = True
            self._physicsDrivers["Solver1"].setInputDoubleValue(self.namePrecisionSolver1_,self.accuracySolver1_)
            print("accuracySolver1_ : ", self.accuracySolver1_)
            # -- Computation of Solver1 with the new precision computed
            self._physicsDrivers["Solver1"].solve()

            # -- Exchange physical data between Solver1 and Solver2
            self._exchangers["Exch_1to2"].exchange()
            # -- Exchange reached precision by Solver1
            self._exchangers["Exch_LastResidual1"].exchange()


            # -- Deal with the new precision computed: we don't want a new precision smaller than the targeted one! And if one solver reachs its targeted precision, the one for the second solver is also set to its targeted value
            self.accuracySolver2Old_ = self._physicsDrivers["Solver2"].getOutputDoubleValue(self.namePrecisionSolver2_)
            if self.accuracySolver2_ > self.epsSolver2Ref_ and not self.accuracySolver1Reached_ :
                # -- Computation of the initial residual for Solver2
                self._exchangers["Exch_CurrentResidual2"].exchange()

                # -- Computation of total current total residual
                self.residualSolver2Initial_ = self._dataManagers["DataResiduals"].getOutputDoubleValue('CurrentResidual2')
                residualDemiTotalOld = self.residualDemiTotal_
                self.residualDemiTotal_ = self.residualSolver2Initial_ / self.epsSolver2Ref_ + self._dataManagers["DataResiduals"].getOutputDoubleValue('LastResidual1') / self.epsSolver1Ref_

                 # -- Convergence rate for Solver2
                self.convRateSolver2_ = self.residualDemiTotal_ / residualDemiTotalOld
                # -- Average convergence rate
                conv = (self.convRateSolver1_ + self.convRateSolver2_) / 2.

                # -- Computation of the new precision for Solver2
                # -- New precision computed : should not be bellow self.epsSolver2Ref_
                # -- New precision computed : should not be bigger than self.accuracySolver2Old_
                self.accuracySolver2_ = conv * self._dataManagers["DataResiduals"].getOutputDoubleValue('LastResidual1') / self.epsSolver1Ref_ * self.epsSolver2Ref_
                self.accuracySolver2_ = min(self.accuracySolver2_, self.accuracySolver2Old_)
                self.accuracySolver2_ = max(self.accuracySolver2_, self.epsSolver2Ref_)

                if self.accuracySolver2_ < self.epsSolver2Ref_ :
                    self.accuracySolver2Reached_ = True # On va faire un calcule avec la precision cible
                    self.accuracySolver2_ = self.epsSolver2Ref_
                    self.accuracySolver1_ = self.epsSolver1Ref_
                    self._physicsDrivers["Solver1"].setInputDoubleValue(self.namePrecisionSolver1_, self.epsSolver1Ref_)
            else :
                self.accuracySolver2_ = self.epsSolver2Ref_
                self.accuracySolver1_ = self.epsSolver1Ref_
                self.accuracySolver2Reached_ = True
            self._physicsDrivers["Solver2"].setInputDoubleValue(self.namePrecisionSolver2_, self.accuracySolver2_)
            print("accuracySolver2_ : ", self.accuracySolver2_)
            # -- Computation of Solver2 with the new precision computed
            self._physicsDrivers["Solver2"].solve()
            print("convRateSolver1_ : ", self.convRateSolver1_)
            print("convRateSolver2_ : ", self.convRateSolver2_)

        succed = self._physicsDrivers["Solver1"].getSolveStatus() and self._physicsDrivers["Solver2"].getSolveStatus()
        self.precisionReached_ = self.accuracySolver2Reached_ and self.accuracySolver1Reached_
        return succed and self.precisionReached_