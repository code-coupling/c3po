# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the MPIMasterDataManager class. """
from __future__ import print_function, division
import math
from mpi4py import MPI

from C3POMPI.MPITag import MPITag


class MPIMasterDataManager(object):
    """ This class is used by the master to control a remote DataManager: the data is not transferred to the master.

    MPIMasterDataManager implements the data manipulation methods of DataManager by instructing the worker to execute them. 
    """

    def __init__(self, MPIMasterphysicsD, IdDataWorker):
        """ Builds a MPIMasterDataManager object.

        :param MPIMasterphysicsD: The MPIMasterPhysicsDriver object driving the PhysicsDriver executed by the worker responsible of the remote DataManager.
        :param IdDataWorker: Number identifying the DataManager in the worker (see MPIWorker).
        """
        self.physicsDriver_ = MPIMasterphysicsD
        self.MPIComm_ = MPIMasterphysicsD.getCommunicator()
        self.workerRank_ = MPIMasterphysicsD.getWorkerRank()
        self.IdDataWorker_ = IdDataWorker

    def __del__(self):
        self.physicsDriver_.setDataManagerToFree(self.IdDataWorker_)

    def checkCompatibility(self, other):
        """ For internal use only. """
        if self.workerRank_ != other.workerRank_ or self.MPIComm_ != other.MPIComm_:
            raise Exception("MPIMasterDataManager.checkCompatibility : self and other are not compatible : they are on different workers or use different communicators.")

    def clone(self):
        return (self * 1.)

    def cloneEmpty(self):
        self.MPIComm_.send(self.IdDataWorker_, dest=self.workerRank_, tag=MPITag.cloneEmptyData)
        newIdDataWorker = self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        new_data = MPIMasterDataManager(self.physicsDriver_, newIdDataWorker)
        return new_data

    def copy(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.send([self.IdDataWorker_, other.IdDataWorker_], dest=self.workerRank_, tag=MPITag.copyData)

    def normMax(self):
        self.MPIComm_.send(self.IdDataWorker_, dest=self.workerRank_, tag=MPITag.normMax)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)

    def norm2(self):
        self.MPIComm_.send(self.IdDataWorker_, dest=self.workerRank_, tag=MPITag.norm2)
        return math.sqrt(self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer))

    def __add__(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.send([self.IdDataWorker_, other.IdDataWorker_], dest=self.workerRank_, tag=MPITag.addData)
        newIdDataWorker = self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        new_data = MPIMasterDataManager(self.physicsDriver_, newIdDataWorker)
        return new_data

    def __iadd__(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.send([self.IdDataWorker_, other.IdDataWorker_], dest=self.workerRank_, tag=MPITag.iaddData)
        return self

    def __sub__(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.send([self.IdDataWorker_, other.IdDataWorker_], dest=self.workerRank_, tag=MPITag.subData)
        newIdDataWorker = self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        new_data = MPIMasterDataManager(self.physicsDriver_, newIdDataWorker)
        return new_data

    def __isub__(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.send([self.IdDataWorker_, other.IdDataWorker_], dest=self.workerRank_, tag=MPITag.isubData)
        return self

    def __mul__(self, scalar):
        self.MPIComm_.send((self.IdDataWorker_, scalar), dest=self.workerRank_, tag=MPITag.mulData)
        newIdDataWorker = self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
        new_data = MPIMasterDataManager(self.physicsDriver_, newIdDataWorker)
        return new_data

    def __imul__(self, scalar):
        self.MPIComm_.send((self.IdDataWorker_, scalar), dest=self.workerRank_, tag=MPITag.imulData)
        return self

    def imuladd(self, scalar, other):
        self.checkCompatibility(other)
        self.MPIComm_.send((self.IdDataWorker_, scalar, other.IdDataWorker_), dest=self.workerRank_, tag=MPITag.imuladdData)
        return self

    def dot(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.send([self.IdDataWorker_, other.IdDataWorker_], dest=self.workerRank_, tag=MPITag.dotData)
        return self.MPIComm_.recv(source=self.workerRank_, tag=MPITag.answer)
