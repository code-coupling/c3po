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

from c3po.PhysicsDriver import PhysicsDriver
from c3po.mpi.MPITag import MPITag


class MPIMasterCollectivePhysicsDriver(PhysicsDriver):
    """! MPIMasterCollectivePhysicsDriver is used by the master process to control a set of remote c3po.PhysicsDriver.PhysicsDriver
    as a single one.

    It can, in addition, be in charge of a local one. This class is well suited to steer a code using an internal collaborative MPI
    parallelization.

    Inherits from c3po.PhysicsDriver.PhysicsDriver. All the methods of the mother class are implemented and consist in commanding the
    workers to execute them.
    """

    def __init__(self, collectiveWorkerProcess, masterRank=0, localPhysicsDriver=None):
        """! Build a MPIMasterCollectivePhysicsDriver object.

        @param collectiveWorkerProcess a MPICollectiveProcess identifying the worker processes. The MPIComm must include all the
        workers + the master, and only them. Each worker can be in charge of only one c3po.PhysicsDriver.PhysicsDriver.
        @param masterRank the rank of the master process in the MPIComm used by collectiveWorkerProcess.
        @param localPhysicsDriver a c3po.PhysicsDriver.PhysicsDriver the MPIMasterCollectivePhysicsDriver object will run in the same
        time than the workers. It enables the master to contribute to a collective computation.
        """
        PhysicsDriver.__init__(self)
        self.mpiComm = collectiveWorkerProcess.mpiComm
        self._masterRank = masterRank
        self._localPhysicsDriver = localPhysicsDriver
        self._dataManagersToFree = []

    def setDataManagerToFree(self, idDataManager):
        """! INTERNAL. """
        self._dataManagersToFree.append(idDataManager)

    def init(self):
        """! See PhysicsDriver.init(). """
        self.mpiComm.bcast((MPITag.init,), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.init()

    def getInitStatus(self):
        """! See PhysicsDriver.getInitStatus(). """
        self.mpiComm.bcast((MPITag.getInitStatus,), root=self._masterRank)
        data = True
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.getInitStatus()
        return self.mpiComm.reduce(data, op=MPI.MIN, root=self._masterRank)

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        self.init()
        return self.getInitStatus()

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        self.mpiComm.bcast((MPITag.terminate,), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.terminate()

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        self.mpiComm.bcast((MPITag.presentTime,), root=self._masterRank)
        data = 1.E30
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.presentTime()
            return data
        return self.mpiComm.reduce(data, op=MPI.MIN, root=self._masterRank)

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep(). """
        self.mpiComm.bcast((MPITag.computeTimeStep,), root=self._masterRank)
        dt = 1.E30
        stop = True
        if self._localPhysicsDriver is not None:
            (dt, stop) = self._localPhysicsDriver.computeTimeStep()
        dt = self.mpiComm.reduce(dt, op=MPI.MIN, root=self._masterRank)
        stop = self.mpiComm.reduce(stop, op=MPI.MIN, root=self._masterRank)
        return (dt, stop)

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self.mpiComm.bcast((MPITag.initTimeStep, dt), root=self._masterRank)
        data = True
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.initTimeStep(dt)
        return self.mpiComm.reduce(data, op=MPI.MIN, root=self._masterRank)

    def solve(self):
        """! See PhysicsDriver.solve(). """
        if len(self._dataManagersToFree) > 0:
            self.mpiComm.bcast((MPITag.deleteDataManager, self._dataManagersToFree), root=self._masterRank)
            self._dataManagersToFree = []
        self.mpiComm.bcast((MPITag.solve,), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.solve()

    def getSolveStatus(self):
        """! See PhysicsDriver.getSolveStatus(). """
        self.mpiComm.bcast((MPITag.getSolveStatus,), root=self._masterRank)
        data = True
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.getSolveStatus()
        return self.mpiComm.reduce(data, op=MPI.MIN, root=self._masterRank)

    def solveTimeStep(self):
        """! See PhysicsDriver.solveTimeStep(). """
        self.solve()
        return self.getSolveStatus()

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        self.mpiComm.bcast((MPITag.validateTimeStep,), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.validateTimeStep()

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        self.mpiComm.bcast((MPITag.abortTimeStep,), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.abortTimeStep()

    def isStationary(self):
        """! See PhysicsDriver.isStationary(). """
        self.mpiComm.bcast((MPITag.isStationary,), root=self._masterRank)
        data = True
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.isStationary()
        return self.mpiComm.reduce(data, op=MPI.MIN, root=self._masterRank)

    def iterate(self):
        """! See PhysicsDriver.iterate(). """
        if len(self._dataManagersToFree) > 0:
            self.mpiComm.bcast((MPITag.deleteDataManager, self._dataManagersToFree), root=self._masterRank)
            self._dataManagersToFree = []
        self.mpiComm.bcast((MPITag.iterate,), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.iterate()

    def getIterateStatus(self):
        """! See PhysicsDriver.getIterateStatus(). """
        self.mpiComm.bcast((MPITag.getIterateStatus,), root=self._masterRank)
        (succeed, converged) = (True, True)
        if self._localPhysicsDriver is not None:
            (succeed, converged) = self._localPhysicsDriver.getIterateStatus()
        succeed = self.mpiComm.reduce(succeed, op=MPI.MIN, root=self._masterRank)
        converged = self.mpiComm.reduce(converged, op=MPI.MIN, root=self._masterRank)
        return (succeed, converged)

    def iterateTimeStep(self):
        """! See PhysicsDriver.iterateTimeStep(). """
        self.iterate()
        return self.getIterateStatus()

    def save(self, label, method):
        """! See PhysicsDriver.save(). """
        self.mpiComm.bcast((MPITag.save, (label, method)), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.save(label, method)

    def restore(self, label, method):
        """! See PhysicsDriver.restore(). """
        self.mpiComm.bcast((MPITag.restore, (label, method)), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.restore(label, method)

    def forget(self, label, method):
        """! See PhysicsDriver.forget(). """
        self.mpiComm.bcast((MPITag.forget, (label, method)), root=self._masterRank)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.forget(label, method)
