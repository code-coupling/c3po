# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class MPIRemoteProcess. """
from __future__ import print_function, division

from C3PO.physicsDriver import physicsDriver
from C3PO.dataManager import dataManager


class MPIRemoteProcess(physicsDriver, dataManager):
    """ Identifies a remote process. 

    Inherits from physicsDriver and dataManager but passes most of the methods: it does nothing.
    """

    def __init__(self, MPIComm, rank):
        """ Builds a MPIRemoteProcess object.

        :param MPIComm: MPI communicator.
        :param rank: Rank of the remote process on MPIComm.
        """
        physicsDriver.__init__(self)
        dataManager.__init__(self)
        self.MPIComm_ = MPIComm
        self.rank_ = rank
        self.t_ = 0.
        self.dt_ = 1.e30

    def setMPIComm(self, mpicomm):
        pass

    def initialize(self):
        return True

    def terminate(self):
        return True

    def presentTime(self):
        return self.t_

    def computeTimeStep(self):
        return (self.dt_, True)

    def initTimeStep(self, dt):
        self.dt_ = dt
        return True

    def solveTimeStep(self):
        return True

    def validateTimeStep(self):
        if self.dt_ > 0.:
            self.t_ += self.dt_

    def abortTimeStep(self):
        pass

    def isStationary(self):
        True

    def iterateTimeStep(self):
        return (True, True)

    def setInputMEDField(self, name, field):
        pass

    def setValue(self, name, value):
        pass

    def cloneEmpty(self):
        new = MPIRemoteProcess(self.MPIComm_, self.rank_)
        return new
