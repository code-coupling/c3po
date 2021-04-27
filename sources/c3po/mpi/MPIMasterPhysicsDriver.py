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
        self.mpiComm_ = workerProcess.mpiComm_
        self.workerRank_ = workerProcess.rank_
        self.dataManagersToFree_ = []

    def setDataManagerToFree(self, IdDataManager):
        """! INTERNAL """
        self.dataManagersToFree_.append(IdDataManager)

    def getCommunicator(self):
        """! INTERNAL """
        return self.mpiComm_

    def getWorkerRank(self):
        """! INTERNAL """
        return self.workerRank_

    def init(self):
        """! See PhysicsDriver.init(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.init)

    def getInitStatus(self):
        """! See PhysicsDriver.getInitStatus(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.getInitStatus)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        self.init()
        return self.getInitStatus()

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.terminate)

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.presentTime)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.computeTimeStep)
        dt = self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        stop = self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        return (dt, stop)

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self.mpiComm_.send(dt, dest=self.workerRank_, tag=MPITag.initTimeStep)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def solve(self):
        """! See PhysicsDriver.solve(). """
        if len(self.dataManagersToFree_) > 0:
            self.mpiComm_.send(self.dataManagersToFree_, dest=self.workerRank_, tag=MPITag.deleteDataManager)
            self.dataManagersToFree_ = []
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.solve)

    def getSolveStatus(self):
        """! See PhysicsDriver.getSolveStatus(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.getSolveStatus)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def solveTimeStep(self):
        """! See PhysicsDriver.solveTimeStep(). """
        self.solve()
        return self.getSolveStatus()

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.validateTimeStep)

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.abortTimeStep)

    def isStationary(self):
        """! See PhysicsDriver.isStationary(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.isStationary)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def iterate(self):
        """! See PhysicsDriver.iterate(). """
        if len(self.dataManagersToFree_) > 0:
            self.mpiComm_.send(self.dataManagersToFree_, dest=self.workerRank_, tag=MPITag.deleteDataManager)
            self.dataManagersToFree_ = []
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.iterate)

    def getIterateStatus(self):
        """! See PhysicsDriver.getIterateStatus(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.getIterateStatus)
        succeed = self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        converged = self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        return (succeed, converged)

    def iterateTimeStep(self):
        """! See PhysicsDriver.iterateTimeStep(). """
        self.iterate()
        return self.getIterateStatus()

    def save(self, label, method):
        """! See PhysicsDriver.save(). """
        self.mpiComm_.send((label, method), dest=self.workerRank_, tag=MPITag.save)

    def restore(self, label, method):
        """! See PhysicsDriver.restore(). """
        self.mpiComm_.send((label, method), dest=self.workerRank_, tag=MPITag.restore)

    def forget(self, label, method):
        """! See PhysicsDriver.forget(). """
        self.mpiComm_.send((label, method), dest=self.workerRank_, tag=MPITag.forget)

    def getInputFieldsNames(self):
        """! See PhysicsDriver.getInputFieldsNames(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.getInputFieldsNames)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def getInputMEDFieldTemplate(self, name):
        """! See PhysicsDriver.getInputMEDFieldTemplate(). """
        self.mpiComm_.send(name, dest=self.workerRank_, tag=MPITag.getInputMEDFieldTemplate)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def setInputMEDField(self, name, field):
        """! See PhysicsDriver.setInputMEDField(). """
        self.mpiComm_.send((name, field), dest=self.workerRank_, tag=MPITag.setInputMEDField)

    def getOutputFieldsNames(self):
        """! See PhysicsDriver.getOutputFieldsNames(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.getOutputFieldsNames)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def getOutputMEDField(self, name):
        """! See PhysicsDriver.getOutputMEDField(). """
        self.mpiComm_.send(name, dest=self.workerRank_, tag=MPITag.getOutputMEDField)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def getInputValuesNames(self):
        """! See PhysicsDriver.getInputValuesNames(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.getInputValuesNames)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def setValue(self, name, value):
        """! See PhysicsDriver.setValue(). """
        self.mpiComm_.send((name, value), dest=self.workerRank_, tag=MPITag.setValue)

    def getOutputValuesNames(self):
        """! See PhysicsDriver.getOutputValuesNames(). """
        self.mpiComm_.send(0, dest=self.workerRank_, tag=MPITag.getOutputValuesNames)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def getValue(self, name):
        """! See PhysicsDriver.getValue(). """
        self.mpiComm_.send(name, dest=self.workerRank_, tag=MPITag.getValue)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
