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

from C3PO.PhysicsDriver import PhysicsDriver
from C3PO.DataManager import DataManager


class MPIRemoteProcess(PhysicsDriver, DataManager):
    """! MPIRemoteProcess identifies a remote process. 

    Inherits from C3PO.PhysicsDriver.PhysicsDriver and C3PO.DataManager.DataManager but passes most of the methods: it does nothing.
    """

    def __init__(self, mpiComm, rank):
        """! Build a MPIRemoteProcess object.

        @param mpiComm MPI communicator.
        @param rank Rank of the remote process on mpiComm.
        """
        PhysicsDriver.__init__(self)
        DataManager.__init__(self)
        self.MPIComm_ = mpiComm
        self.rank_ = rank
        self.t_ = 0.
        self.dt_ = 1.e30

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
        return self.t_

    def computeTimeStep(self):
        """! return (1.e30, True) """
        return (1.e30, True)

    def initTimeStep(self, dt):
        """! self.dt_ = dt and return True """
        self.dt_ = dt
        return True

    def solveTimeStep(self):
        """! return True """
        return True

    def validateTimeStep(self):
        """! self.t_ += self.dt_ """
        if self.dt_ > 0.:
            self.t_ += self.dt_
            self.dt_ = 0.

    def abortTimeStep(self):
        """! self.dt_ = 0. """
        self.dt_ = 0.

    def isStationary(self):
        """! return True """
        return True

    def iterateTimeStep(self):
        """! return (True, True) """
        return (True, True)

    def setInputMEDField(self, name, field):
        """! pass """
        pass

    def setValue(self, name, value):
        """! pass """
        pass

    def cloneEmpty(self):
        """! return a clone. """
        new = MPIRemoteProcess(self.MPIComm_, self.rank_)
        return new
