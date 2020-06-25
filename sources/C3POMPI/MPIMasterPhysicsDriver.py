# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the MPIMasterPhysicsDriver class. """
from __future__ import print_function, division
from mpi4py import MPI

from C3PO.physicsDriver import physicsDriver
from MPITag import MPITag


class MPIMasterPhysicsDriver(physicsDriver):
    """ This class is used by the master process to control a remote physicsDriver. 

    Inherits from physicsDriver. All the methods of the mother class are implemented and consist in commanding the worker to execute them.
    """

    def __init__(self, workerProcess):
        """ Builds a MPIMasterPhysicsDriver object.

        :param workerProcess: a MPIRemoteProcess identifying the worker process. The worker can be in charge of only one physicsDriver.
        """
        physicsDriver.__init__(self)
        self.MPIComm_ = workerProcess.MPIComm_
        self.workerRank_ = workerProcess.rank_
        self.dataManagersToFree_ = []

    def setDataManagerToFree(self, IdDataManager):
        self.dataManagersToFree_.append(IdDataManager)

    def getCommunicator(self):
        return self.MPIComm_

    def getWorkerRank(self):
        return self.workerRank_

    def init(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.init)

    def getInitStatus(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.getInitStatus)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def initialize(self):
        self.init()
        return self.getInitStatus()

    def terminate(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.terminate)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def presentTime(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.presentTime)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def computeTimeStep(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.computeTimeStep)
        dt = self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        stop = self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        return (dt, stop)

    def initTimeStep(self, dt):
        self.MPIComm_.send(dt, dest=self.workerRank_, tag=MPITag.initTimeStep)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def solve(self):
        if len(self.dataManagersToFree_) > 0:
            self.MPIComm_.send(self.dataManagersToFree_, dest=self.workerRank_, tag=MPITag.deleteDataManager)
            self.dataManagersToFree_ = []
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.solve)

    def getSolveStatus(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.getSolveStatus)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def solveTimeStep(self):
        self.solve()
        return self.getSolveStatus()

    def validateTimeStep(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.validateTimeStep)

    def abortTimeStep(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.abortTimeStep)

    def isStationary(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.isStationary)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def iterate(self):
        if len(self.dataManagersToFree_) > 0:
            self.MPIComm_.send(self.dataManagersToFree_, dest=self.workerRank_, tag=MPITag.deleteDataManager)
            self.dataManagersToFree_ = []
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.iterate)

    def getIterateStatus(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.getIterateStatus)
        succeed = self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        converged = self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        return (succeed, converged)

    def iterateTimeStep(self):
        self.iterate()
        return self.getIterateStatus()

    def save(self, label, method):
        self.MPIComm_.send((label, method), dest=self.workerRank_, tag=MPITag.save)

    def restore(self, label, method):
        self.MPIComm_.send((label, method), dest=self.workerRank_, tag=MPITag.restore)

    def forget(self, label, method):
        self.MPIComm_.send((label, method), dest=self.workerRank_, tag=MPITag.forget)

    def getInputFieldsNames(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.getInputFieldsNames)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def getInputMEDFieldTemplate(self, name):
        self.MPIComm_.send(name, dest=self.workerRank_, tag=MPITag.getInputMEDFieldTemplate)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def setInputMEDField(self, name, field):
        self.MPIComm_.send((name, field), dest=self.workerRank_, tag=MPITag.setInputMEDField)

    def getOutputFieldsNames(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.getOutputFieldsNames)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def getOutputMEDField(self, name):
        self.MPIComm_.send(name, dest=self.workerRank_, tag=MPITag.getOutputMEDField)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def getInputValuesNames(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.getInputValuesNames)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def setValue(self, name, value):
        self.MPIComm_.send((name, value), dest=self.workerRank_, tag=MPITag.setValue)

    def getOutputValuesNames(self):
        self.MPIComm_.send(0, dest=self.workerRank_, tag=MPITag.getOutputValuesNames)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def getValue(self, name):
        self.MPIComm_.send(name, dest=self.workerRank_, tag=MPITag.getValue)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
