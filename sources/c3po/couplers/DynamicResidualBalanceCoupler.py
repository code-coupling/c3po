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

from c3po.PhysicsDriver import PhysicsDriver
from c3po.Coupler import Coupler
from c3po.LocalDataManager import LocalDataManager
from c3po.services.Printer import Printer

class DynamicResidualBalanceCoupler(Coupler):
    """! DynamicResidualBalanceCoupler inherits from Coupler and proposes a dynamic residual balance algorithm.
    This is a variant of the adaptive residual balance implemented by c3po.AdaptiveResidualBalanceCoupler.AdaptiveResidualBalanceCoupler.

    This algorithm is designed to couple two solvers using an iterative procedure.
    It controls the accuracy required to each solver in order to limit over-solving and make them converge together.

    See R. Delvaux, "Algorithmes de couplage entre neutronique, thermohydraulique et thermique", PhD Thesis, Institut Polytechnique de Paris, 2022.

    DynamicResidualBalanceCoupler works with :

    - Two PhysicsDriver, one for each solver. They must implement the iterateTimeStep() method, together with the possibilities to get residual and set target accuracy.
    - Four Exchanger: two for exchanges between the PhysicsDriver, and two to get residuals.
    - One LocalDataManager (not just a DataManager) which contains the residuals got with the last two exchangers.

    @note Two Exchanger and a DataManager are used to access the residuals in order to support all possible MPI schemes.

    The default target accuracies are 1e-4 and the default maximum number of iterations is 100. Use setConvergenceParameters() to change these values.

    It may be interesting to use a FixedPointCoupler to add a damping factor and to control the coupling error.

    In this case :

    - The option setUseIterate(True) of FixedPointCoupler must be used.
    - The maximal number of iterations provided to DynamicResidualBalanceCoupler.setConvergenceParameters() is ignored.
    - The exchanger '2to1' is also probably redondant with the FixedPointCoupler exchangers and, in this case, can be set to do nothing.
    """

    def __init__(self, physics, exchangers, dataManagers):
        """! Build a DynamicResidualBalanceCoupler object.

        @param physics list (or dict with keys ['Solver1', 'Solver2']) of two PhysicsDriver. If a list is used, it has to be provided in the same order than the keys here.
            The provided PhysicsDriver must implement the iterateTimeStep() method (together with solveTimeStep()) and accept new accuracy (for the solveTimeStep() method) through setInputDoubleValue('Accuracy', value).
        @param exchangers list (or dict with keys ['1to2', '2to1', 'Residual1', 'Residual2']) of four Exchanger. If a list is used, it has to be provided in the same order than the keys here.
        @param dataManagers list (or dict with keys ['Residuals']) of one LocalDataManager (not just a DataManager).
            The residuals must be stored in this DataManager as double values under the names 'Residual1' and 'Residual2'.
        """
        Coupler.__init__(self, physics, exchangers, dataManagers)

        if not isinstance(physics, (dict, list)):
            raise Exception("DynamicResidualBalanceCoupler.__init__ physics must be either a dictionary or a list.")
        if len(physics) != 2:
            raise Exception("DynamicResidualBalanceCoupler.__init__ There must be exactly two PhysicsDriver, not {}.".format(len(physics)))
        if isinstance(physics, dict):
            for key in physics.keys():
                if key not in ["Solver1", "Solver2"] :
                    raise Exception('DynamicResidualBalanceCoupler.__init__ if physics is provided as a dictionary, the keys must be : ["Solver1", "Solver2"]. We found : {}.'.format(list(physics.keys())))
            self._solver1 = physics["Solver1"]
            self._solver2 = physics["Solver2"]
        else:
            self._solver1 = physics[0]
            self._solver2 = physics[1]

        if not isinstance(exchangers, (dict, list)):
            raise Exception("DynamicResidualBalanceCoupler.__init__ exchangers must be either a dictionary or a list.")
        if len(exchangers) != 4:
            raise Exception("DynamicResidualBalanceCoupler.__init__ There must be exactly four Exchanger, not {}.".format(len(exchangers)))
        if isinstance(exchangers, dict):
            for key in exchangers.keys():
                if key not in ["1to2", "2to1", "Residual1", "Residual2"] :
                    raise Exception('DynamicResidualBalanceCoupler.__init__ if exchangers is provided as a dictionary, the keys must be : ["1to2", "2to1", "Residual1", "Residual2"]. We found : {}.'.format(list(exchangers.keys())))
            self._exchanger1to2 = exchangers["1to2"]
            self._exchanger2to1 = exchangers["2to1"]
            self._exchangerResidual1 = exchangers["Residual1"]
            self._exchangerResidual2 = exchangers["Residual2"]
        else:
            self._exchanger1to2 = exchangers[0]
            self._exchanger2to1 = exchangers[1]
            self._exchangerResidual1 = exchangers[2]
            self._exchangerResidual2 = exchangers[3]

        if not isinstance(dataManagers, (dict, list)):
            raise Exception("DynamicResidualBalanceCoupler.__init__ dataManagers must be either a dictionary or a list.")
        if len(dataManagers) != 1:
            raise Exception("DynamicResidualBalanceCoupler.__init__ There must be exactly one DataManager, not {}.".format(len(dataManagers)))
        if isinstance(dataManagers, dict):
            for key in dataManagers.keys():
                if key not in ["Residuals"] :
                    raise Exception('DynamicResidualBalanceCoupler.__init__ if dataManagers is provided as a dictionary, the keys must be : ["Residuals"]. We found : {}.'.format(list(dataManagers.keys())))
            self._data = dataManagers["Residuals"]
        else:
            self._data = dataManagers[0]
        if not isinstance(self._data, LocalDataManager):
            raise Exception("DynamicResidualBalanceCoupler.__init__ The provided Datamanager must be a LocalDataManager.")

        self._iterationPrinter = Printer(2)
        self._leaveIfFailed = False

        self._epsSolver1Ref = 1e-4
        self._accuracySolver1Old = 0.

        self._epsSolver2Ref = 1e-4
        self._accuracySolver2 = 0.
        self._accuracySolver2Old = 0.
        self._convRateSolver2 = 0.

        self._residualTotal = 0.
        self._residualHalfTotal = 0.

        self._iter = 0
        self._maxiter = 100

    def setConvergenceParameters(self, targetResidualSolver1, targetResidualSolver2, maxiter):
        """! Set the convergence parameters (target residuals for each solver and maximum number of iterations).

        @param targetResidualSolver1 target residual for solver 1. Default value: 1.E-4.
        @param targetResidualSolver2 target residual for solver 2. Default value: 1.E-4.
        @param maxiter the maximal number of iterations. Default value: 100.
        """
        self._epsSolver1Ref = targetResidualSolver1
        self._epsSolver2Ref = targetResidualSolver2
        self._maxiter = maxiter

    def setPrintLevel(self, level):
        """! Set the print level during iterations (0=None, 1 keeps last iteration, 2 prints every iteration).

        @param level integer in range [0;2]. Default: 2.
        """
        if not level in [0, 1, 2]:
            raise Exception("DynamicResidualBalanceCoupler.setPrintLevel level should be one of [0, 1, 2]!")
        self._iterationPrinter.setPrintLevel(level)

    def setFailureManagement(self, leaveIfSolvingFailed):
        """! Set if iterations should continue or not in case of solver failure (solveTimeStep returns False).

        @param leaveIfSolvingFailed set False to continue the iterations, True to stop. Default: False.
        """
        self._leaveIfFailed = leaveIfSolvingFailed

    def solveTimeStep(self):
        """! See c3po.PhysicsDriver.PhysicsDriver.solveTimeStep(). """
        converged = False
        succeed = True

        while (succeed or not self._leaveIfFailed) and (not converged) and self._iter < self._maxiter:
            self.iterate()
            succeed, converged = self.getIterateStatus()

        if self._iterationPrinter.getPrintLevel() == 1:
            self._iterationPrinter.reprint(tmplevel=2)

        return succeed and converged

    def iterateTimeStep(self):
        """! See c3po.PhysicsDriver.PhysicsDriver.iterateTimeStep(). """

        converged = False

        if self._iter == 0 :
            # -- Computation of the initial residual for Solver1
            self._solver1.iterate()
            self._exchangerResidual1.exchange()
            residualSolver1Initial = self._data.getOutputDoubleValue("Residual1")

            # -- Computation of the initial value of the normalized total residual
            self._residualTotal = residualSolver1Initial / self._epsSolver1Ref

            # -- Initial residual for Solver2, obtained from the last calculation made outside of the algorithm.
            self._exchangerResidual2.exchange()

            # -- Convergence criteria for Solver1
            accuracySolver1 = self._data.getOutputDoubleValue('Residual2') / self._epsSolver2Ref * self._epsSolver1Ref
            self._solver1.setInputDoubleValue("Accuracy", accuracySolver1)
            self._accuracySolver1Old = accuracySolver1

            # -- First iteration for Solver1
            self._solver1.solve()

            # -- Get the precision reached by Solver1 after the first iteration
            self._exchangerResidual1.exchange()

            # -- Exchange physical data between Solver1 and Solver2
            self._exchanger1to2.exchange()

            # -- Computation of the initial residual for Solver2
            self._solver2.iterate()
            self._exchangerResidual2.exchange()
            residualSolver2Initial = self._data.getOutputDoubleValue('Residual2')

            # -- Initial value of the total "demi residual"
            self._residualHalfTotal = residualSolver2Initial / self._epsSolver2Ref + self._data.getOutputDoubleValue('Residual1') /self._epsSolver1Ref

            # -- Convergence criteria for Solver2
            self._accuracySolver2 = self._data.getOutputDoubleValue('Residual1') / self._epsSolver1Ref * self._epsSolver2Ref
            self._solver2.setInputDoubleValue("Accuracy", self._accuracySolver2)
            self._accuracySolver2Old = self._accuracySolver2

            if self._iterationPrinter.getPrintLevel() > 0:
                self._iterationPrinter.print("Dynamic Residual Balance iteration {} accuracies: {} ; {}".format(self._iter, accuracySolver1, self._accuracySolver2))

            # -- First iteration for Solver2
            self._solver2.solve()

            # -- End of the first multiphysics iteration

        else :
            # -- Exchange precision reached by Solver2 and compute current partial residual and intermediate coeff
            self._exchangerResidual2.exchange()
            residualPartial = self._data.getOutputDoubleValue('Residual2') / self._epsSolver2Ref
            lastResidual = self._residualTotal

            # -- Computation of the initial residual for Solver1
            self._solver1.iterate()
            self._exchangerResidual1.exchange()
            residualSolver1Initial = self._data.getOutputDoubleValue('Residual1')

            # -- Compute total residual and convergence rate
            self._residualTotal = residualSolver1Initial / self._epsSolver1Ref + residualPartial
            convRateSolver1 = self._residualTotal / lastResidual

            # -- Deal with the new precision computed: we don't want a new precision smaller than the targeted one! And if one solver reachs its targeted precision, the one for the second solver is also set to its targeted value
            if self._accuracySolver1Old > self._epsSolver1Ref and self._accuracySolver2Old > self._epsSolver2Ref:
                # -- Average convergence rate
                conv = (convRateSolver1 + self._convRateSolver2) / 2.

                accuracySolver1 = self._data.getOutputDoubleValue('Residual2') / self._epsSolver2Ref * self._epsSolver1Ref
                accuracySolver1 = min(accuracySolver1, self._accuracySolver1Old)

                if accuracySolver1 <= self._epsSolver1Ref or self._accuracySolver2Old <= self._epsSolver2Ref :
                    converged = True
                    self._accuracySolver2 = self._epsSolver2Ref
                    accuracySolver1 = self._epsSolver1Ref
            else :
                accuracySolver1 = self._epsSolver1Ref
                self._accuracySolver2 = self._epsSolver2Ref
                converged = True

            self._accuracySolver1Old = accuracySolver1
            self._solver1.setInputDoubleValue("Accuracy", accuracySolver1)

            # -- Computation of Solver1 with the new precision computed
            self._solver1.solve()

            # -- Exchange physical data between Solver1 and Solver2
            self._exchanger1to2.exchange()

            # -- Exchange reached precision by Solver1
            self._exchangerResidual1.exchange()

            # -- Deal with the new precision computed: we don't want a new precision smaller than the targeted one! And if one solver reachs its targeted precision, the one for the second solver is also set to its targeted value
            if self._accuracySolver2 > self._epsSolver2Ref and not converged :
                # -- Computation of the initial residual for Solver2
                self._solver2.iterate()
                self._exchangerResidual2.exchange()
                residualSolver2Initial = self._data.getOutputDoubleValue('Residual2')

                # -- Computation of total current total residual
                residualHalfTotalOld = self._residualHalfTotal
                self._residualHalfTotal = residualSolver2Initial / self._epsSolver2Ref + self._data.getOutputDoubleValue('Residual1') / self._epsSolver1Ref

                 # -- Convergence rate for Solver2
                self._convRateSolver2 = self._residualHalfTotal / residualHalfTotalOld
                # -- Average convergence rate
                conv = (convRateSolver1 + self._convRateSolver2) / 2.

                # -- Computation of the new precision for Solver2
                # -- New precision computed : should not be bellow self._epsSolver2Ref
                # -- New precision computed : should not be bigger than self._accuracySolver2Old
                self._accuracySolver2 = conv * self._data.getOutputDoubleValue('Residual1') / self._epsSolver1Ref * self._epsSolver2Ref
                self._accuracySolver2 = min(self._accuracySolver2, self._accuracySolver2Old)
                self._accuracySolver2 = max(self._accuracySolver2, self._epsSolver2Ref)
            else :
                self._accuracySolver2 = self._epsSolver2Ref

            self._accuracySolver2Old = self._accuracySolver2
            self._solver2.setInputDoubleValue("Accuracy", self._accuracySolver2)

            if self._iterationPrinter.getPrintLevel() > 0:
                self._iterationPrinter.print("Dynamic Residual Balance iteration {} accuracies: {} ; {}".format(self._iter, accuracySolver1, self._accuracySolver2))

            # -- Computation of Solver2 with the new precision computed
            self._solver2.solve()

        self._exchanger2to1.exchange()

        succeed = self._solver1.getSolveStatus() and self._solver2.getSolveStatus()
        self._iter += 1

        return succeed, converged

    def getIterateStatus(self):
        """! See c3po.PhysicsDriver.PhysicsDriver.getSolveStatus(). """
        return PhysicsDriver.getIterateStatus(self)

    def getSolveStatus(self):
        """! See c3po.PhysicsDriver.PhysicsDriver.getSolveStatus(). """
        return PhysicsDriver.getSolveStatus(self)

    def initTimeStep(self, dt):
        """! See c3po.PhysicsDriver.PhysicsDriver.initTimeStep().  """
        self._iter = 0
        return Coupler.initTimeStep(self, dt)
