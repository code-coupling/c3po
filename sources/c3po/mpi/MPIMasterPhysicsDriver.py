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

from c3po.PhysicsDriver import PhysicsDriver
from c3po.mpi.MPITag import MPITag


class MPIMasterPhysicsDriver(PhysicsDriver):
    """! MPIMasterPhysicsDriver is used by the master process to control a remote c3po.PhysicsDriver.PhysicsDriver.

    Inherits from c3po.PhysicsDriver.PhysicsDriver. All the methods of the mother class are implemented and consist in commanding the
    worker to execute them.
    """

    def __init__(self, workerProcess):
        """! Build a MPIMasterPhysicsDriver object.

        @param workerProcess a c3po.mpi.MPIRemoteProcess.MPIRemoteProcess identifying the worker process. The worker can be in charge of
        only one c3po.PhysicsDriver.PhysicsDriver.
        """
        PhysicsDriver.__init__(self)
        self.mpiComm = workerProcess.mpiComm
        self._workerRank = workerProcess.rank
        self._dataManagersToFree = []

    def setDataManagerToFree(self, idDataManager):
        """! INTERNAL """
        self._dataManagersToFree.append(idDataManager)

    def getCommunicator(self):
        """! INTERNAL """
        return self.mpiComm

    def getWorkerRank(self):
        """! INTERNAL """
        return self._workerRank

    def init(self):
        """! See PhysicsDriver.init(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.init)

    def getInitStatus(self):
        """! See PhysicsDriver.getInitStatus(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.getInitStatus)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        self.init()
        return self.getInitStatus()

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.terminate)

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.presentTime)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.computeTimeStep)
        dt = self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)
        stop = self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)
        return (dt, stop)

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self.mpiComm.send(dt, dest=self._workerRank, tag=MPITag.initTimeStep)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def solve(self):
        """! See PhysicsDriver.solve(). """
        if len(self._dataManagersToFree) > 0:
            self.mpiComm.send(self._dataManagersToFree, dest=self._workerRank, tag=MPITag.deleteDataManager)
            self._dataManagersToFree = []
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.solve)

    def getSolveStatus(self):
        """! See PhysicsDriver.getSolveStatus(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.getSolveStatus)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def solveTimeStep(self):
        """! See PhysicsDriver.solveTimeStep(). """
        self.solve()
        return self.getSolveStatus()

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.validateTimeStep)

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.abortTimeStep)

    def isStationary(self):
        """! See PhysicsDriver.isStationary(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.isStationary)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def iterate(self):
        """! See PhysicsDriver.iterate(). """
        if len(self._dataManagersToFree) > 0:
            self.mpiComm.send(self._dataManagersToFree, dest=self._workerRank, tag=MPITag.deleteDataManager)
            self._dataManagersToFree = []
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.iterate)

    def getIterateStatus(self):
        """! See PhysicsDriver.getIterateStatus(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.getIterateStatus)
        succeed = self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)
        converged = self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)
        return (succeed, converged)

    def iterateTimeStep(self):
        """! See PhysicsDriver.iterateTimeStep(). """
        self.iterate()
        return self.getIterateStatus()

    def save(self, label, method):
        """! See PhysicsDriver.save(). """
        self.mpiComm.send((label, method), dest=self._workerRank, tag=MPITag.save)

    def restore(self, label, method):
        """! See PhysicsDriver.restore(). """
        self.mpiComm.send((label, method), dest=self._workerRank, tag=MPITag.restore)

    def forget(self, label, method):
        """! See PhysicsDriver.forget(). """
        self.mpiComm.send((label, method), dest=self._workerRank, tag=MPITag.forget)

    def getInputFieldsNames(self):
        """! See PhysicsDriver.getInputFieldsNames(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.getInputFieldsNames)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def getInputMEDFieldTemplate(self, name):
        """! See PhysicsDriver.getInputMEDFieldTemplate(). """
        self.mpiComm.send(name, dest=self._workerRank, tag=MPITag.getInputMEDFieldTemplate)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def setInputMEDField(self, name, field):
        """! See PhysicsDriver.setInputMEDField(). """
        self.mpiComm.send((name, field), dest=self._workerRank, tag=MPITag.setInputMEDField)

    def getOutputFieldsNames(self):
        """! See PhysicsDriver.getOutputFieldsNames(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.getOutputFieldsNames)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def getOutputMEDField(self, name):
        """! See PhysicsDriver.getOutputMEDField(). """
        self.mpiComm.send(name, dest=self._workerRank, tag=MPITag.getOutputMEDField)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def getInputValuesNames(self):
        """! See PhysicsDriver.getInputValuesNames(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.getInputValuesNames)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def setValue(self, name, value):
        """! See PhysicsDriver.setValue(). """
        self.mpiComm.send((name, value), dest=self._workerRank, tag=MPITag.setValue)

    def getOutputValuesNames(self):
        """! See PhysicsDriver.getOutputValuesNames(). """
        self.mpiComm.send(0, dest=self._workerRank, tag=MPITag.getOutputValuesNames)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)

    def getValue(self, name):
        """! See PhysicsDriver.getValue(). """
        self.mpiComm.send(name, dest=self._workerRank, tag=MPITag.getValue)
        return self.mpiComm.recv(source=self._workerRank, tag=MPITag.answer)
