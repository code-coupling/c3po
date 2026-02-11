# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class :class:`.Coupler`. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class NormChoice(object):
    """ Enum definition of norm choice.

    Values :
        - :attr:`normMax`
        - :attr:`norm2`
    """
    normMax = 0
    norm2 = 1


class Coupler(PhysicsDriver):
    """ :class:`.Coupler` is the base class for the definition of a coupling.

    A coupling is defined using :class:`.PhysicsDriver`, :class:`.DataManager` and :class:`.Exchanger` objects.
    A user needs to define his own class inheriting from :class:`.Coupler` and to define its :meth:`solveTimeStep() <.PhysicsDriver.solveTimeStep>` method.
    It may also be necessary to overload the I/O methods (for fields and/or of scalars) inherited
    from :class:`.PhysicsDriver`.

    .. note:: :class:`.Coupler` inherits from :class:`.PhysicsDriver`, it is therefore possible to couple
        of :class:`.Coupler` objects!
    """

    def __init__(self, physics, exchangers, dataManagers=[]):
        """ Build an :class:`.Coupler` object.

        Parameters
        ----------
        physics : list[PhysicsDriver], dict
            A list (or dictionary) of :class:`.PhysicsDriver` objects to be coupled.
        exchangers : list[Exchanger], dict
            A list (or dictionary) of :class:`.Exchanger` for the coupling.
        dataManagers : list[DataManager], dict
            A list (or dictionary) of :class:`.DataManager` used in the coupling.
        """
        PhysicsDriver.__init__(self)
        self._physicsDrivers = physics
        self._physicsDriversList = physics if not isinstance(physics, dict) else list(physics.values())
        self._exchangers = exchangers
        self._dataManagers = dataManagers
        self._norm = NormChoice.normMax
        self._dt = 1.e30
        self._stationaryMode = False

    def getMEDCouplingMajorVersion(self):
        """ See :meth:`.PhysicsDriver.getMEDCouplingMajorVersion`. """
        version = 0
        for physics in self._physicsDriversList:
            localVersion = version
            try:
                localVersion = physics.getMEDCouplingMajorVersion()
            except NotImplementedError:
                localVersion = version
            if localVersion != version:
                if version == 0:
                    version = localVersion
                else:
                    raise Exception("Coupler.getMEDCouplingMajorVersion Not a unique version.")
        if version == 0:
            raise NotImplementedError
        return version

    def isMEDCoupling64Bits(self):
        """ See :meth:`.PhysicsDriver.isMEDCoupling64Bits`. """
        resu = None
        for physics in self._physicsDriversList:
            localResu = resu
            try:
                localResu = physics.isMEDCoupling64Bits()
            except NotImplementedError:
                pass
            if localResu != resu:
                if resu is None:
                    resu = localResu
                else:
                    raise Exception("Coupler.isMEDCoupling64Bits Not a unique answer.")
        if resu is None:
            raise NotImplementedError
        return resu

    def initialize(self):
        """ See :meth:`.PhysicsDriver.initialize`. """
        for physics in self._physicsDriversList:
            physics.init()
        resu = True
        for physics in self._physicsDriversList:
            resu = physics.getInitStatus() and resu
        return resu

    def terminate(self):
        """ See :meth:`.PhysicsDriver.terminate`. """
        for physics in self._physicsDriversList:
            physics.term()

    def presentTime(self):
        """ See :meth:`.PhysicsDriver.presentTime`. """
        if len(self._physicsDriversList) > 0:
            return self._physicsDriversList[0].presentTime()
        return 0.

    def computeTimeStep(self):
        """ See :meth:`.PhysicsDriver.computeTimeStep`. """
        (dt, stop) = (1.e30, False)
        for physics in self._physicsDriversList:
            (dtPhysics, stopPhysics) = physics.computeTimeStep()
            if dtPhysics < dt:
                dt = dtPhysics
            stop = (stop or stopPhysics)
        return (dt, stop)

    def initTimeStep(self, dt):
        """ See :meth:`.PhysicsDriver.initTimeStep`. """
        self._dt = dt
        resu = True
        for physics in self._physicsDriversList:
            resu = physics.initTimeStep(dt) and resu
        return resu

    def getSolveStatus(self):
        """ See :meth:`.PhysicsDriver.getSolveStatus`. """
        resu = True
        for physics in self._physicsDriversList:
            resu = physics.getSolveStatus() and resu
        return resu

    def validateTimeStep(self):
        """ See :meth:`.PhysicsDriver.validateTimeStep`. """
        for physics in self._physicsDriversList:
            physics.validateTimeStep()

    def setStationaryMode(self, stationaryMode):
        """ See :meth:`.PhysicsDriver.setStationaryMode`. """
        for physics in self._physicsDriversList:
            physics.setStationaryMode(stationaryMode)
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        """ See :meth:`.PhysicsDriver.getStationaryMode`. """
        for physics in self._physicsDriversList:
            if physics.getStationaryMode() != self._stationaryMode:
                raise Exception("Coupler.getStationaryMode Not a unique stationary mode.")
        return self._stationaryMode

    def abortTimeStep(self):
        """ See :meth:`.PhysicsDriver.abortTimeStep`. """
        for physics in self._physicsDriversList:
            physics.abortTimeStep()

    def isStationary(self):
        """ See :meth:`.PhysicsDriver.isStationary`. """
        resu = True
        for physics in self._physicsDriversList:
            resu = physics.isStationary() and resu
        return resu

    def resetTime(self, time_):
        """ See :meth:`.PhysicsDriver.resetTime`. """
        for physics in self._physicsDriversList:
            physics.resetTime(time_)

    def getIterateStatus(self):
        """ See :meth:`.PhysicsDriver.getSolveStatus`. """
        succeed = True
        converged = True
        for physics in self._physicsDriversList:
            (physicsSucceed, physicsConverged) = physics.getIterateStatus()
            succeed = succeed and physicsSucceed
            converged = converged and physicsConverged
        return (succeed, converged)

    def setNormChoice(self, choice):
        """ Choose a norm for future use.

        Parameters
        ----------
        choice : :attr:`.NormChoice.normMax`, :attr:`.NormChoice.norm2`
            To be choosen between :

            - :attr:`.NormChoice.normMax` : infinite norm. This is the default choice.
            - :attr:`.NormChoice.norm2` : norm 2 ( ``sqrt(sum_i(val[i] * val[i]))`` ).
        """
        self._norm = choice

    def getNorm(self, data):
        """ Return the norm choosen by :meth:`setNormChoice` of ``data`` (a :class:`.DataManager`).

        Parameters
        ----------
        data : DataManager
            A :class:`.DataManager` object.

        Returns
        -------
            The asked norm of data.
        """
        if self._norm == NormChoice.normMax:
            return data.normMax()
        if self._norm == NormChoice.norm2:
            return data.norm2()
        raise Exception("Coupler.getNorm The required norm is unknown.")

    def readNormData(self):
        """ Return a list of the norms of the :class:`.DataManager` objects hold by ``self``.

        Returns
        -------
        list
            List of the norm of the :class:`.DataManager` objects.
        """
        normData = []
        for data in self._dataManagers:
            normData.append(self.getNorm(data))
        return normData

    def normalizeData(self, norms):
        """ Divide the :class:`.DataManager` objects by the scalar values provided.

        Parameters
        ----------
        norms : list
            List of scalar values. The :class:`.DataManager` are divided by these scalars.
        """
        for i, norm in enumerate(norms):
            if norm > 0.:
                self._dataManagers[i] *= 1. / norm

    def denormalizeData(self, norms):
        """ Multiply the :class:`.DataManager` objects by the scalar values provided.

        Parameters
        ----------
        norms : list
            List of scalar values. The :class:`.DataManager` are multiplied by these scalars.
        """
        for i, norm in enumerate(norms):
            if norm > 0.:
                self._dataManagers[i] *= norm
