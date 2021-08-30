# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPIMasterPhysicsDriver. """
from __future__ import print_function, division
from mpi4py import MPI

from c3po.PhysicsDriver import PhysicsDriver
from c3po.mpi.MPICollectiveProcess import MPICollectiveProcess
from c3po.mpi.MPITag import MPITag


class MPIMasterPhysicsDriver(PhysicsDriver):
    """! MPIMasterPhysicsDriver is used by a master process to control a (set of) remote c3po.PhysicsDriver.PhysicsDriver as a local one.

    It can, in addition, be in charge of a local one (can be usefull for codes using an internal collaborative MPI parallelization).

    Inherits from c3po.PhysicsDriver.PhysicsDriver. All the methods of c3po.PhysicsDriver.PhysicsDriver are implemented and consist
    in commanding the worker to execute them. Methods inherited from c3po.DataAccessor.DataAccessor are NOT implemented (apart from
    the setInput(Double/Int/String)Value methods, for convenience). Use an c3po.mpi.MPIMasterExchanger.MPIMasterExchanger to exchange
    data with the worker.
    """

    def __init__(self, workerProcess, localPhysicsDriver=None):
        """! Build a MPIMasterPhysicsDriver object.

        @param workerProcess a c3po.mpi.MPIRemoteProcess.MPIRemoteProcess or a c3po.mpi.MPICollectiveProcess.MPICollectiveProcess
        identifying the worker process(es). Each worker process can be in charge of only one c3po.PhysicsDriver.PhysicsDriver.
        In case of a c3po.mpi.MPICollectiveProcess.MPICollectiveProcess, the MPIComm must include all the workers + the master,
        and only them.
        @param localPhysicsDriver a c3po.PhysicsDriver.PhysicsDriver the MPIMasterPhysicsDriver object will run in the same
        time than the workers. It enables the master to contribute to a collaborative calculations.
        """
        PhysicsDriver.__init__(self)
        self.mpiComm = workerProcess.mpiComm
        self._masterRank = self.mpiComm.Get_rank()
        self._workerRank = None
        self._isCollective = False
        if isinstance(workerProcess, MPICollectiveProcess):
            self._isCollective = True
        else:
            self._workerRank = workerProcess.rank
        self._localPhysicsDriver = localPhysicsDriver
        self._dataManagersToFree = []

    def sendData(self, tag, data=None):
        """! INTERNAL """
        if self._isCollective:
            toSend = (tag,) if data is None else (tag,data)
            self.mpiComm.bcast(toSend, root=self._masterRank)
        else:
            if data is None:
                data = 0
            self.mpiComm.send(data, dest=self._workerRank, tag=tag)

    def recvData(self, data, collectiveOperator=MPI.MIN):
        """! INTERNAL """
        if self._isCollective:
            return self.mpiComm.reduce(data, op=collectiveOperator, root=self._masterRank)
        else:
            return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def setDataManagerToFree(self, idDataManager):
        """! INTERNAL """
        self._dataManagersToFree.append(idDataManager)

    def getICOCOVersion(self):
        return '2.0'

    def init(self):
        """! See PhysicsDriver.init(). """
        self.sendData(MPITag.init)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.init()

    def getInitStatus(self):
        """! See PhysicsDriver.getInitStatus(). """
        self.sendData(MPITag.getInitStatus)
        data = True
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.getInitStatus()
        return self.recvData(data)

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        self.init()
        return self.getInitStatus()

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        self.sendData(MPITag.terminate)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.terminate()

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        self.sendData(MPITag.presentTime)
        data = 1.E30
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.presentTime()
        return self.recvData(data)

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep(). """
        self.sendData(MPITag.computeTimeStep)
        dt = 1.E30
        stop = True
        if self._localPhysicsDriver is not None:
            (dt, stop) = self._localPhysicsDriver.computeTimeStep()
        dt = self.recvData(dt)
        stop = self.recvData(stop)
        return (dt, stop)

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self.sendData(MPITag.initTimeStep, dt)
        data = True
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.initTimeStep(dt)
        return self.recvData(data)

    def solve(self):
        """! See PhysicsDriver.solve(). """
        if len(self._dataManagersToFree) > 0:
            self.sendData(MPITag.deleteDataManager, self._dataManagersToFree)
            self._dataManagersToFree = []
        self.sendData(MPITag.solve)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.solve()

    def getSolveStatus(self):
        """! See PhysicsDriver.getSolveStatus(). """
        self.sendData(MPITag.getSolveStatus)
        data = True
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.getSolveStatus()
        return self.recvData(data)

    def solveTimeStep(self):
        """! See PhysicsDriver.solveTimeStep(). """
        self.solve()
        return self.getSolveStatus()

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        self.sendData(MPITag.validateTimeStep)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.validateTimeStep()

    def setStationaryMode(self, stationaryMode):
        """! See PhysicsDriver.setStationaryMode(). """
        self.sendData(MPITag.setStationaryMode, stationaryMode)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.setStationaryMode(stationaryMode)

    def getStationaryMode(self):
        """! See PhysicsDriver.getStationaryMode(). """
        self.sendData(MPITag.getStationaryMode)
        data = None
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.getStationaryMode()
        resuMin = self.recvData(True, collectiveOperator=MPI.MIN)
        resuMax = self.recvData(False, collectiveOperator=MPI.MAX)
        if resuMin != resuMax or (data is not None and data != resuMin):
            raise Exception("MPIMasterPhysicsDriver.getStationaryMode Not a unique stationary mode.")
        return resuMin

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        self.sendData(MPITag.abortTimeStep)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.abortTimeStep()

    def isStationary(self):
        """! See PhysicsDriver.isStationary(). """
        self.sendData(MPITag.isStationary)
        data = True
        if self._localPhysicsDriver is not None:
            data = self._localPhysicsDriver.isStationary()
        return self.recvData(data)

    def resetTime(self, time_):
        """! See PhysicsDriver.resetTime(). """
        self.sendData(MPITag.resetTime, time_)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.resetTime(time_)

    def iterate(self):
        """! See PhysicsDriver.iterate(). """
        if len(self._dataManagersToFree) > 0:
            self.sendData(MPITag.deleteDataManager, self._dataManagersToFree)
            self._dataManagersToFree = []
        self.sendData(MPITag.iterate)
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.iterate()

    def getIterateStatus(self):
        """! See PhysicsDriver.getIterateStatus(). """
        self.sendData(MPITag.getIterateStatus)
        (succeed, converged) = (True, True)
        if self._localPhysicsDriver is not None:
            (succeed, converged) = self._localPhysicsDriver.getIterateStatus()
        succeed = self.recvData(succeed)
        converged = self.recvData(converged)
        return (succeed, converged)

    def iterateTimeStep(self):
        """! See PhysicsDriver.iterateTimeStep(). """
        self.iterate()
        return self.getIterateStatus()

    def save(self, label, method):
        """! See PhysicsDriver.save(). """
        self.sendData(MPITag.save, (label, method))
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.save(label, method)

    def restore(self, label, method):
        """! See PhysicsDriver.restore(). """
        self.sendData(MPITag.restore, (label, method))
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.restore(label, method)

    def forget(self, label, method):
        """! See PhysicsDriver.forget(). """
        self.sendData(MPITag.forget, (label, method))
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.forget(label, method)

    def setInputDoubleValue(self, name, value):
        """! See PhysicsDriver.setValue(). """
        self.sendData(MPITag.setInputDoubleValue, (name, value))
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.setInputDoubleValue(name, value)

    def setInputIntValue(self, name, value):
        """! See PhysicsDriver.setValue(). """
        self.sendData(MPITag.setInputIntValue, (name, value))
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.setInputIntValue(name, value)

    def setInputStringValue(self, name, value):
        """! See PhysicsDriver.setValue(). """
        self.sendData(MPITag.setInputStringValue, (name, value))
        if self._localPhysicsDriver is not None:
            self._localPhysicsDriver.setInputStringValue(name, value)
