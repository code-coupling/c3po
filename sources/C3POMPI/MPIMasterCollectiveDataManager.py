# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the MPIMasterCollectiveDataManager class. """
from __future__ import print_function, division
import math
from mpi4py import MPI

from .MPITag import MPITag


class MPIMasterCollectiveDataManager(object):
    """ This class is used by the master to control a set of remote dataManagers. It can, in addition, be in charge of a local one. This class is well suited to steer a code using an internal collaborative MPI parallelization.

    MPIMasterCollectiveDataManager implements the data manipulation methods of dataManager by instructing the workers to execute them.
    """

    def __init__(self, MPIMasterCollectivephysicsD, IdDataWorker, localDataManager=None):
        """ Builds a MPIMasterCollectiveDataManager object.

        :param MPIMasterCollectivephysicsD: The MPIMasterCollectivePhysicsDriver object driving the physicsDrivers executed by the workers responsible of the remote dataManagers.
        :param IdDataWorker: Number identifying the dataManager in the workers (see MPIWorker).
        :param localDataManager: a dataManager the MPIMasterCollectiveDataManager object will use together with the remote ones handle by the workers. It enables the master to contribute to a collective computation.
        """
        self.physicsDriver_ = MPIMasterCollectivephysicsD
        self.MPIComm_ = MPIMasterCollectivephysicsD.getCommunicator()
        self.masterRank_ = MPIMasterCollectivephysicsD.masterRank_
        self.IdDataWorker_ = IdDataWorker
        self.localDataManager_ = localDataManager

    def __del__(self):
        self.physicsDriver_.setDataManagerToFree(self.IdDataWorker_)

    def checkCompatibility(self, other):
        """ For internal use only. """
        if not isinstance(other, MPIMasterCollectiveDataManager) or self.physicsDriver_ != other.physicsDriver_ or (self.localDataManager_ is not None) and (other.localDataManager_ is None):
            raise Exception("MPIMasterCollectiveDataManager.checkCompatibility : self and other are not compatible.")

    def clone(self):
        return (self * 1.)

    def cloneEmpty(self):
        self.MPIComm_.bcast((MPITag.cloneEmptyData, self.IdDataWorker_), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_.cloneEmpty()
        newIdDataWorker = self.MPIComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def copy(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.copyData, [self.IdDataWorker_, other.IdDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_.copy(other.localDataManager_)

    def normMax(self):
        self.MPIComm_.bcast((MPITag.normMax, self.IdDataWorker_), root=self.masterRank_)
        resu = 0.
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.normMax()
        return self.MPIComm_.reduce(resu, op=MPI.MAX, root=self.masterRank_)

    def norm2(self):
        self.MPIComm_.bcast((MPITag.norm2, self.IdDataWorker_), root=self.masterRank_)
        resu = 0.
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.norm2()
            resu = resu * resu
        resu = self.MPIComm_.reduce(resu, op=MPI.SUM, root=self.masterRank_)
        return math.sqrt(resu)

    def __add__(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.addData, [self.IdDataWorker_, other.IdDataWorker_]), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ + other.localDataManager_
        newIdDataWorker = self.MPIComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __iadd__(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.iaddData, [self.IdDataWorker_, other.IdDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ += other.localDataManager_
        return self

    def __sub__(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.subData, [self.IdDataWorker_, other.IdDataWorker_]), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ - other.localDataManager_
        newIdDataWorker = self.MPIComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __isub__(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.isubData, [self.IdDataWorker_, other.IdDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ -= other.localDataManager_
        return self

    def __mul__(self, scalar):
        self.MPIComm_.bcast((MPITag.mulData, (self.IdDataWorker_, scalar)), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ * scalar
        newIdDataWorker = self.MPIComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __imul__(self, scalar):
        self.MPIComm_.bcast((MPITag.imulData, (self.IdDataWorker_, scalar)), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ *= scalar
        return self

    def imuladd(self, scalar, other):
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.imuladdData, (self.IdDataWorker_, scalar, other.IdDataWorker_)), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_.imuladd(scalar, other.localDataManager_)
        return self

    def dot(self, other):
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.dotData, [self.IdDataWorker_, other.IdDataWorker_]), root=self.masterRank_)
        resu = 0
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.dot(other.localDataManager_)
        return self.MPIComm_.reduce(resu, op=MPI.SUM, root=self.masterRank_)
