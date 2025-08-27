# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class :class:`.FixedPointCoupler`. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver
from c3po.Coupler import Coupler
from c3po.CollaborativeDataManager import CollaborativeDataManager
from c3po.services.Printer import Printer


class FixedPointCoupler(Coupler):
    """ :class:`.FixedPointCoupler` inherits from :class:`.Coupler` and proposes a damped fixed
    point algorithm.

    The class proposes an algorithm for the resolution of :math:`F(X) = X`. Thus
    :class:`.FixedPointCoupler` is a :class:`.Coupler` working with :

    - A single :class:`.PhysicsDriver` (possibly a :class:`.Coupler`) defining the calculations to
      be made each time :math:`F` is called.
    - A list of :class:`.DataManager` allowing to manipulate the data in the coupling
      (the :math:`X`).
    - Two :class:`.Exchanger` allowing to go from the :class:`.PhysicsDriver` to the
      :class:`.DataManager` and vice versa.

    Each :class:`.DataManager` is normalized with its own norm got after the first iteration.
    They are then used as a single :class:`.DataManager` using :class:`.CollaborativeDataManager`.

    At each iteration we do (with :math:`n` the iteration number and alpha the damping factor):

    .. math::

        X^{n+1} = \\alpha . F(X^{n}) + (1 - \\alpha).X^{n}

    The convergence criteria is : :math:`||F(X^{n}) - X^{n}|| / ||F(X^{n})|| < \\rm{tolerance}`.
    The default norm used is the infinite norm. :meth:`setNormChoice() <.Coupler.setNormChoice>`
    allows to choose another one.

    The default value of tolerance is 1.E-6. Call :meth:`setConvergenceParameters` to change it.

    The default maximum number of iterations is 100. Call :meth:`setConvergenceParameters` to
    change it.

    The default damping factor is 1 (no damping). Call :meth:`setDampingFactor` to change it.
    """

    def __init__(self, physics, exchangers, dataManagers):
        """ Build a :class:`.FixedPointCoupler` object.

        Parameters
        ----------
        physics : list[PhysicsDriver]
            List of only one :class:`.PhysicsDriver` (possibly a :class:`.Coupler`).
        exchangers : list[Exchanger]
            List of exactly two :class:`.Exchanger` allowing to go from the :class:`.PhysicsDriver`
            to the :class:`.DataManager` and vice versa.
        dataManagers : list[DataManager]
            List of :class:`.DataManager`.
        """
        Coupler.__init__(self, physics, exchangers, dataManagers)
        self._tolerance = 1.E-6
        self._maxiter = 100
        self._dampingFactor = 1.
        self._iterationPrinter = Printer(2)
        self._leaveIfFailed = False
        self._useIterate = False
        self._iter = 0

        if not isinstance(physics, list) or not isinstance(exchangers, list) or not isinstance(dataManagers, list):
            raise Exception("FixedPointCoupler.__init__ physics, exchangers and dataManagers must be lists!")
        if len(physics) != 1:
            raise Exception("FixedPointCoupler.__init__ There must be only one PhysicsDriver")
        if len(exchangers) != 2:
            raise Exception("FixedPointCoupler.__init__ There must be exactly two Exchanger")

        self._data = CollaborativeDataManager(self._dataManagers)
        self._previousData = None
        self._normData = 0.

    def setConvergenceParameters(self, tolerance, maxiter):
        """ Set the convergence parameters (tolerance and maximum number of iterations).

        Parameters
        ----------
        tolerance
            The convergence threshold in
            :math:`||F(X^{n}) - X^{n}|| / ||F(X^{n})|| < \\rm{tolerance}`.
        maxiter
            The maximal number of iterations.
        """
        self._tolerance = tolerance
        self._maxiter = maxiter

    def setDampingFactor(self, dampingFactor):
        """ Set the damping factor of the method.

        Parameters
        ----------
        dampingFactor
            The damping factor alpha in the formula
            :math:`X^{n+1} = \\alpha . F(X^{n}) + (1 - \\alpha).X^{n}`.
        """
        self._dampingFactor = dampingFactor

    def setPrintLevel(self, level):
        """ Set the print level during iterations (0=None, 1 keeps last iteration, 2 prints every
        iteration).

        Parameters
        ----------
        level : int
            Integer in range [0;2]. Default: 2.
        """
        if not level in [0, 1, 2]:
            raise Exception("FixedPointCoupler.setPrintLevel level should be one of [0, 1, 2]!")
        self._iterationPrinter.setPrintLevel(level)

    def setFailureManagement(self, leaveIfSolvingFailed):
        """ Set if iterations should continue or not in case of solver failure
        (:meth:`solveTimeStep` returns False).

        Parameters
        ----------
        leaveIfSolvingFailed : bool
            Set False to continue the iterations, True to stop. Default: False.
        """
        self._leaveIfFailed = leaveIfSolvingFailed

    def setUseIterate(self, useIterate):
        """ If True is given, the :meth:`iterate() <.PhysicsDriver.iterate>` method on the given
        :class:`.PhysicsDriver` is called instead of the :meth:`solve() <.PhysicsDriver.solve>`
        method.

        Parameters
        ----------
        useIterate : bool
            Set True to use :meth:`iterate() <.PhysicsDriver.iterate>`, False to use :meth:`solve()
            <.PhysicsDriver.solve>`. Default: False.
        """
        self._useIterate = useIterate

    def iterateTimeStep(self):
        """ Make on iteration of a damped fixed-point algorithm.

        See also :meth:`c3po.PhysicsDriver.PhysicsDriver.iterateTimeStep`.
        """
        physics = self._physicsDrivers[0]
        physics2Data = self._exchangers[0]
        data2physics = self._exchangers[1]

        if self._iter > 0:
            if not self._useIterate:
                physics.abortTimeStep()
                physics.initTimeStep(self._dt)
            data2physics.exchange()

        if self._useIterate:
            physics.iterate()
        else:
            physics.solve()
        physics2Data.exchange()

        if self._iter == 0:
            self._normData = self.readNormData()
        self.normalizeData(self._normData)

        if self._iter > 0:
            normNewData = self.getNorm(self._data)
            self._data -= self._previousData
            error = self.getNorm(self._data) / normNewData

            self._data *= self._dampingFactor
            self._data += self._previousData

            self._previousData.copy(self._data)
        else:
            error = self._tolerance + 1.
            self._previousData = self._data.clone()

        self.denormalizeData(self._normData)

        if self._iterationPrinter.getPrintLevel() > 0:
            if self._iter == 0:
                self._iterationPrinter.print("fixed-point iteration {} ".format(self._iter))
            else:
                self._iterationPrinter.print("fixed-point iteration {} error : {:.5e}".format(self._iter, error))

        self._iter += 1

        succeed, converged = physics.getIterateStatus() if self._useIterate else (physics.getSolveStatus(), True)
        converged = converged and error <= self._tolerance

        return succeed, converged

    def solveTimeStep(self):
        """ Solve a time step using the damped fixed-point algorithm.

        See also :meth:`c3po.PhysicsDriver.PhysicsDriver.solveTimeStep`.
        """
        converged = False
        succeed = True

        while (succeed or not self._leaveIfFailed) and (not converged) and self._iter < self._maxiter:
            self.iterate()
            succeed, converged = self.getIterateStatus()

        if self._iterationPrinter.getPrintLevel() == 1:
            self._iterationPrinter.reprint(tmplevel=2)

        return succeed and converged

    def getIterateStatus(self):
        """ See :meth:`.PhysicsDriver.getSolveStatus`. """
        return PhysicsDriver.getIterateStatus(self)

    def getSolveStatus(self):
        """ See :meth:`.PhysicsDriver.getSolveStatus`. """
        return PhysicsDriver.getSolveStatus(self)

    def initTimeStep(self, dt):
        """ See :meth:`c3po.PhysicsDriver.PhysicsDriver.initTimeStep`.  """
        self._iter = 0
        self._previousData = 0
        return Coupler.initTimeStep(self, dt)
