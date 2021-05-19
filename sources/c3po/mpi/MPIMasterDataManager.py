# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPIMasterDataManager. """
from __future__ import print_function, division
import math

from c3po.mpi.MPITag import MPITag


class MPIMasterDataManager(object):
    """! MPIMasterDataManager is used by the master process to control a remote c3po.DataManager.DataManager.

    MPIMasterDataManager implements the data manipulation methods of c3po.DataManager.DataManager by instructing the worker to execute them.
    """

    def __init__(self, mpiMasterphysicsD, idDataWorker):
        """! Build a MPIMasterDataManager object.

        @param mpiMasterphysicsD The MPIMasterPhysicsDriver object driving the c3po.PhysicsDriver.PhysicsDriver executed by the worker
        responsible of the remote c3po.DataManager.DataManager.
        @param idDataWorker Number identifying the c3po.DataManager.DataManager in the worker (see c3po.mpi.MPIWorker.MPIWorker).
        """
        self.physicsDriver = mpiMasterphysicsD
        self.mpiComm = mpiMasterphysicsD.getCommunicator()
        self.workerRank = mpiMasterphysicsD.getWorkerRank()
        self.idDataWorker = idDataWorker

    def __del__(self):
        """! Destructor. """
        self.physicsDriver.setDataManagerToFree(self.idDataWorker)

    def checkCompatibility(self, other):
        """! INTERNAL """
        if self.workerRank != other.workerRank or self.mpiComm != other.mpiComm:
            raise Exception("MPIMasterDataManager.checkCompatibility : self and other are not compatible : they are on different workers or use different communicators.")

    def clone(self):
        """! See c3po.DataManager.DataManager.clone(). """
        return self * 1.

    def cloneEmpty(self):
        """! See c3po.DataManager.DataManager.cloneEmpty(). """
        self.mpiComm.send(self.idDataWorker, dest=self.workerRank, tag=MPITag.cloneEmptyData)
        newIdDataWorker = self.mpiComm.recv(source=self.workerRank, tag=MPITag.answer)
        newData = MPIMasterDataManager(self.physicsDriver, newIdDataWorker)
        return newData

    def copy(self, other):
        """! See c3po.DataManager.DataManager.copy(). """
        self.checkCompatibility(other)
        self.mpiComm.send([self.idDataWorker, other.idDataWorker], dest=self.workerRank, tag=MPITag.copyData)

    def normMax(self):
        """! See c3po.DataManager.DataManager.normMax(). """
        self.mpiComm.send(self.idDataWorker, dest=self.workerRank, tag=MPITag.normMax)
        return self.mpiComm.recv(source=self.workerRank, tag=MPITag.answer)

    def norm2(self):
        """! See c3po.DataManager.DataManager.norm2(). """
        self.mpiComm.send(self.idDataWorker, dest=self.workerRank, tag=MPITag.norm2)
        return math.sqrt(self.mpiComm.recv(source=self.workerRank, tag=MPITag.answer))

    def __add__(self, other):
        """! See c3po.DataManager.DataManager.__add__(). """
        self.checkCompatibility(other)
        self.mpiComm.send([self.idDataWorker, other.idDataWorker], dest=self.workerRank, tag=MPITag.addData)
        newIdDataWorker = self.mpiComm.recv(source=self.workerRank, tag=MPITag.answer)
        newData = MPIMasterDataManager(self.physicsDriver, newIdDataWorker)
        return newData

    def __iadd__(self, other):
        """! See c3po.DataManager.DataManager.__iadd__(). """
        self.checkCompatibility(other)
        self.mpiComm.send([self.idDataWorker, other.idDataWorker], dest=self.workerRank, tag=MPITag.iaddData)
        return self

    def __sub__(self, other):
        """! See c3po.DataManager.DataManager.__sub__(). """
        self.checkCompatibility(other)
        self.mpiComm.send([self.idDataWorker, other.idDataWorker], dest=self.workerRank, tag=MPITag.subData)
        newIdDataWorker = self.mpiComm.recv(source=self.workerRank, tag=MPITag.answer)
        newData = MPIMasterDataManager(self.physicsDriver, newIdDataWorker)
        return newData

    def __isub__(self, other):
        """! See c3po.DataManager.DataManager.__isub__(). """
        self.checkCompatibility(other)
        self.mpiComm.send([self.idDataWorker, other.idDataWorker], dest=self.workerRank, tag=MPITag.isubData)
        return self

    def __mul__(self, scalar):
        """! See c3po.DataManager.DataManager.__mul__(). """
        self.mpiComm.send((self.idDataWorker, scalar), dest=self.workerRank, tag=MPITag.mulData)
        newIdDataWorker = self.mpiComm.recv(source=self.workerRank, tag=MPITag.answer)
        newData = MPIMasterDataManager(self.physicsDriver, newIdDataWorker)
        return newData

    def __imul__(self, scalar):
        """! See c3po.DataManager.DataManager.__imul__(). """
        self.mpiComm.send((self.idDataWorker, scalar), dest=self.workerRank, tag=MPITag.imulData)
        return self

    def imuladd(self, scalar, other):
        """! See c3po.DataManager.DataManager.imuladd(). """
        self.checkCompatibility(other)
        self.mpiComm.send((self.idDataWorker, scalar, other.idDataWorker), dest=self.workerRank, tag=MPITag.imuladdData)
        return self

    def dot(self, other):
        """! See c3po.DataManager.DataManager.dot(). """
        self.checkCompatibility(other)
        self.mpiComm.send([self.idDataWorker, other.idDataWorker], dest=self.workerRank, tag=MPITag.dotData)
        return self.mpiComm.recv(source=self.workerRank, tag=MPITag.answer)
