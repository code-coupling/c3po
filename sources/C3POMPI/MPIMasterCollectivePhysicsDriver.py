# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPIMasterCollectivePhysicsDriver. """
from __future__ import print_function, division
from mpi4py import MPI

from C3PO.PhysicsDriver import PhysicsDriver
from C3POMPI.MPITag import MPITag


class MPIMasterCollectivePhysicsDriver(PhysicsDriver):
    """! MPIMasterCollectivePhysicsDriver is used by the master process to control a set of remote C3PO.PhysicsDriver.PhysicsDriver as a single one. 

    It can, in addition, be in charge of a local one. This class is well suited to steer a code using an internal collaborative MPI parallelization.

    Inherits from C3PO.PhysicsDriver.PhysicsDriver. All the methods of the mother class are implemented and consist in commanding the workers to execute them.
    """

    def __init__(self, collectiveWorkerProcess, masterRank=0, localPhysicsDriver=None):
        """! Build a MPIMasterCollectivePhysicsDriver object.

        @param collectiveWorkerProcess a MPICollectiveProcess identifying the worker processes. The MPIComm must include all the workers + the master, and only them. Each worker can be in charge of only one C3PO.PhysicsDriver.PhysicsDriver.
        @param masterRank the rank of the master process in the MPIComm used by collectiveWorkerProcess.
        @param localPhysicsDriver a C3PO.PhysicsDriver.PhysicsDriver the MPIMasterCollectivePhysicsDriver object will run in the same time than the workers. It enables the master to contribute to a collective computation.
        """
        PhysicsDriver.__init__(self)
        self.MPIComm_ = collectiveWorkerProcess.MPIComm_
        self.masterRank_ = masterRank
        self.localPhysicsDriver_ = localPhysicsDriver
        self.dataManagersToFree_ = []

    def setDataManagerToFree(self, IdDataManager):
        """! INTERNAL. """
        self.dataManagersToFree_.append(IdDataManager)

    def getCommunicator(self):
        """! INTERNAL. """
        return self.MPIComm_

    def init(self):
        """! See PhysicsDriver.init(). """
        self.MPIComm_.bcast((MPITag.init,), root=self.masterRank_)
        if self.localPhysicsDriver_ is not None:
            self.localPhysicsDriver_.init()

    def getInitStatus(self):
        """! See PhysicsDriver.getInitStatus(). """
        self.MPIComm_.bcast((MPITag.getInitStatus,), root=self.masterRank_)
        data = True
        if self.localPhysicsDriver_ is not None:
            data = self.localPhysicsDriver_.getInitStatus()
        return self.MPIComm_.reduce(data, op=MPI.MIN, root=self.masterRank_)

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        self.init()
        return self.getInitStatus()

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        self.MPIComm_.bcast((MPITag.terminate,), root=self.masterRank_)
        data = True
        if self.localPhysicsDriver_ is not None:
            data = self.localPhysicsDriver_.terminate()
        return self.MPIComm_.reduce(data, op=MPI.MIN, root=self.masterRank_)

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        self.MPIComm_.bcast((MPITag.presentTime,), root=self.masterRank_)
        data = 1.E30
        if self.localPhysicsDriver_ is not None:
            data = self.localPhysicsDriver_.presentTime()
            return data
        return self.MPIComm_.reduce(data, op=MPI.MIN, root=self.masterRank_)

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep(). """
        self.MPIComm_.bcast((MPITag.computeTimeStep,), root=self.masterRank_)
        dt = 1.E30
        stop = True
        if self.localPhysicsDriver_ is not None:
            (dt, stop) = self.localPhysicsDriver_.computeTimeStep()
        dt = self.MPIComm_.reduce(dt, op=MPI.MIN, root=self.masterRank_)
        stop = self.MPIComm_.reduce(stop, op=MPI.MIN, root=self.masterRank_)
        return (dt, stop)

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self.MPIComm_.bcast((MPITag.initTimeStep, dt), root=self.masterRank_)
        data = True
        if self.localPhysicsDriver_ is not None:
            data = self.localPhysicsDriver_.initTimeStep(dt)
        return self.MPIComm_.reduce(data, op=MPI.MIN, root=self.masterRank_)

    def solve(self):
        """! See PhysicsDriver.solve(). """
        if len(self.dataManagersToFree_) > 0:
            self.MPIComm_.bcast((MPITag.deleteDataManager, self.dataManagersToFree_), root=self.masterRank_)
            self.dataManagersToFree_ = []
        self.MPIComm_.bcast((MPITag.solve,), root=self.masterRank_)
        if self.localPhysicsDriver_ is not None:
            self.localPhysicsDriver_.solve()

    def getSolveStatus(self):
        """! See PhysicsDriver.getSolveStatus(). """
        self.MPIComm_.bcast((MPITag.getSolveStatus,), root=self.masterRank_)
        data = True
        if self.localPhysicsDriver_ is not None:
            data = self.localPhysicsDriver_.getSolveStatus()
        return self.MPIComm_.reduce(data, op=MPI.MIN, root=self.masterRank_)

    def solveTimeStep(self):
        """! See PhysicsDriver.solveTimeStep(). """
        self.solve()
        return self.getSolveStatus()

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        self.MPIComm_.bcast((MPITag.validateTimeStep,), root=self.masterRank_)
        if self.localPhysicsDriver_ is not None:
            self.localPhysicsDriver_.validateTimeStep()

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        self.MPIComm_.bcast((MPITag.abortTimeStep,), root=self.masterRank_)
        if self.localPhysicsDriver_ is not None:
            self.localPhysicsDriver_.abortTimeStep()

    def isStationary(self):
        """! See PhysicsDriver.isStationary(). """
        self.MPIComm_.bcast((MPITag.isStationary,), root=self.masterRank_)
        data = True
        if self.localPhysicsDriver_ is not None:
            data = self.localPhysicsDriver_.isStationary()
        return self.MPIComm_.reduce(data, op=MPI.MIN, root=self.masterRank_)

    def iterate(self):
        """! See PhysicsDriver.iterate(). """
        if len(self.dataManagersToFree_) > 0:
            self.MPIComm_.bcast((MPITag.deleteDataManager, self.dataManagersToFree_), root=self.masterRank_)
            self.dataManagersToFree_ = []
        self.MPIComm_.bcast((MPITag.iterate,), root=self.masterRank_)
        if self.localPhysicsDriver_ is not None:
            self.localPhysicsDriver_.iterate()

    def getIterateStatus(self):
        """! See PhysicsDriver.getIterateStatus(). """
        self.MPIComm_.bcast((MPITag.getIterateStatus,), root=self.masterRank_)
        (succeed, converged) = (True, True)
        if self.localPhysicsDriver_ is not None:
            (succeed, converged) = self.localPhysicsDriver_.getIterateStatus()
        succeed = self.MPIComm_.reduce(succeed, op=MPI.MIN, root=self.masterRank_)
        converged = self.MPIComm_.reduce(converged, op=MPI.MIN, root=self.masterRank_)
        return (succeed, converged)

    def iterateTimeStep(self):
        """! See PhysicsDriver.iterateTimeStep(). """
        self.iterate()
        return self.getIterateStatus()

    def save(self, label, method):
        """! See PhysicsDriver.save(). """
        self.MPIComm_.bcast((MPITag.save, (label, method)), root=self.masterRank_)
        if self.localPhysicsDriver_ is not None:
            self.localPhysicsDriver_.save(label, method)

    def restore(self, label, method):
        """! See PhysicsDriver.restore(). """
        self.MPIComm_.bcast((MPITag.restore, (label, method)), root=self.masterRank_)
        if self.localPhysicsDriver_ is not None:
            self.localPhysicsDriver_.restore(label, method)

    def forget(self, label, method):
        """! See PhysicsDriver.forget(). """
        self.MPIComm_.bcast((MPITag.forget, (label, method)), root=self.masterRank_)
        if self.localPhysicsDriver_ is not None:
            self.localPhysicsDriver_.forget(label, method)
