# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPIRemoteProcess. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver
from c3po.DataManager import DataManager


class MPIRemoteProcess(PhysicsDriver, DataManager):
    """! MPIRemoteProcess identifies a remote process.

    Inherits from c3po.PhysicsDriver.PhysicsDriver and c3po.DataManager.DataManager but passes most of the methods: it does nothing.
    """

    def __init__(self, mpiComm, rank):
        """! Build a MPIRemoteProcess object.

        @param mpiComm MPI communicator.
        @param rank Rank of the remote process on mpiComm.
        """
        PhysicsDriver.__init__(self)
        self.mpiComm = mpiComm
        self.rank = rank
        self._time = 0.
        self._dt = 1.e30
        self._stationaryMode = False

    def setMPIComm(self, mpicomm):
        """! pass """
        pass

    def initialize(self):
        """! return True """
        return True

    def terminate(self):
        """! pass """
        pass

    def presentTime(self):
        """! return the time. """
        return self._time

    def computeTimeStep(self):
        """! return (1.e30, True) """
        return (1.e30, False)

    def initTimeStep(self, dt):
        """! self._dt = dt and return True """
        self._dt = dt
        return True

    def solveTimeStep(self):
        """! return True """
        return True

    def validateTimeStep(self):
        """! self._time += self._dt """
        if self._dt > 0.:
            self._time += self._dt
            self._dt = 0.

    def setStationaryMode(self, stationaryMode):
        """! self._stationaryMode = stationaryMode """
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        """! return self._stationaryMode """
        return self._stationaryMode

    def abortTimeStep(self):
        """! self._dt = 0. """
        self._dt = 0.

    def isStationary(self):
        """! return True """
        return True

    def resetTime(self, time_):
        """! reset time. """
        self._time = time_

    def iterateTimeStep(self):
        """! return (True, True) """
        return (True, True)

    def save(self, label, method):
        pass

    def restore(self, label, method):
        pass

    def forget(self, label, method):
        pass

    def setInputMEDDoubleField(self, name, field):
        """! pass """
        pass

    def setInputMEDIntField(self, name, field):
        """! pass """
        pass

    def setInputMEDStringField(self, name, field):
        """! pass """
        pass

    def setInputDoubleValue(self, name, value):
        """! pass """
        pass

    def setInputIntValue(self, name, value):
        """! pass """
        pass

    def setInputStringValue(self, name, value):
        """! pass """
        pass

    def cloneEmpty(self):
        """! return a clone. """
        new = MPIRemoteProcess(self.mpiComm, self.rank)
        return new
