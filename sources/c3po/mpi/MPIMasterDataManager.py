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
        self.physicsDriver_ = mpiMasterphysicsD
        self.mpiComm_ = mpiMasterphysicsD.getCommunicator()
        self.workerRank_ = mpiMasterphysicsD.getWorkerRank()
        self.idDataWorker_ = idDataWorker

    def __del__(self):
        """! Destructor. """
        self.physicsDriver_.setDataManagerToFree(self.idDataWorker_)

    def checkCompatibility(self, other):
        """! INTERNAL """
        if self.workerRank_ != other.workerRank_ or self.mpiComm_ != other.mpiComm_:
            raise Exception("MPIMasterDataManager.checkCompatibility : self and other are not compatible : they are on different workers or use different communicators.")

    def clone(self):
        """! See c3po.DataManager.DataManager.clone(). """
        return (self * 1.)

    def cloneEmpty(self):
        """! See c3po.DataManager.DataManager.cloneEmpty(). """
        self.mpiComm_.send(self.idDataWorker_, dest=self.workerRank_, tag=MPITag.cloneEmptyData)
        newIdDataWorker = self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        new_data = MPIMasterDataManager(self.physicsDriver_, newIdDataWorker)
        return new_data

    def copy(self, other):
        """! See c3po.DataManager.DataManager.copy(). """
        self.checkCompatibility(other)
        self.mpiComm_.send([self.idDataWorker_, other.idDataWorker_], dest=self.workerRank_, tag=MPITag.copyData)

    def normMax(self):
        """! See c3po.DataManager.DataManager.normMax(). """
        self.mpiComm_.send(self.idDataWorker_, dest=self.workerRank_, tag=MPITag.normMax)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def norm2(self):
        """! See c3po.DataManager.DataManager.norm2(). """
        self.mpiComm_.send(self.idDataWorker_, dest=self.workerRank_, tag=MPITag.norm2)
        return math.sqrt(self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer))

    def __add__(self, other):
        """! See c3po.DataManager.DataManager.__add__(). """
        self.checkCompatibility(other)
        self.mpiComm_.send([self.idDataWorker_, other.idDataWorker_], dest=self.workerRank_, tag=MPITag.addData)
        newIdDataWorker = self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        new_data = MPIMasterDataManager(self.physicsDriver_, newIdDataWorker)
        return new_data

    def __iadd__(self, other):
        """! See c3po.DataManager.DataManager.__iadd__(). """
        self.checkCompatibility(other)
        self.mpiComm_.send([self.idDataWorker_, other.idDataWorker_], dest=self.workerRank_, tag=MPITag.iaddData)
        return self

    def __sub__(self, other):
        """! See c3po.DataManager.DataManager.__sub__(). """
        self.checkCompatibility(other)
        self.mpiComm_.send([self.idDataWorker_, other.idDataWorker_], dest=self.workerRank_, tag=MPITag.subData)
        newIdDataWorker = self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        new_data = MPIMasterDataManager(self.physicsDriver_, newIdDataWorker)
        return new_data

    def __isub__(self, other):
        """! See c3po.DataManager.DataManager.__isub__(). """
        self.checkCompatibility(other)
        self.mpiComm_.send([self.idDataWorker_, other.idDataWorker_], dest=self.workerRank_, tag=MPITag.isubData)
        return self

    def __mul__(self, scalar):
        """! See c3po.DataManager.DataManager.__mul__(). """
        self.mpiComm_.send((self.idDataWorker_, scalar), dest=self.workerRank_, tag=MPITag.mulData)
        newIdDataWorker = self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        new_data = MPIMasterDataManager(self.physicsDriver_, newIdDataWorker)
        return new_data

    def __imul__(self, scalar):
        """! See c3po.DataManager.DataManager.__imul__(). """
        self.mpiComm_.send((self.idDataWorker_, scalar), dest=self.workerRank_, tag=MPITag.imulData)
        return self

    def imuladd(self, scalar, other):
        """! See c3po.DataManager.DataManager.imuladd(). """
        self.checkCompatibility(other)
        self.mpiComm_.send((self.idDataWorker_, scalar, other.idDataWorker_), dest=self.workerRank_, tag=MPITag.imuladdData)
        return self

    def dot(self, other):
        """! See c3po.DataManager.DataManager.dot(). """
        self.checkCompatibility(other)
        self.mpiComm_.send([self.idDataWorker_, other.idDataWorker_], dest=self.workerRank_, tag=MPITag.dotData)
        return self.mpiComm_.recv(source=self.workerRank_, tag=MPITag.answer)
