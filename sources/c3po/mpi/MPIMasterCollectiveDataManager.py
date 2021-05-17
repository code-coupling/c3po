# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPIMasterCollectiveDataManager. """
from __future__ import print_function, division
import math
from mpi4py import MPI

from c3po.mpi.MPITag import MPITag


class MPIMasterCollectiveDataManager(object):
    """! MPIMasterCollectiveDataManager is used by the master process to control a set of remote c3po.DataManager.DataManager as a single one..

    It can, in addition, be in charge of a local one. This class is well suited to steer a code using an internal collaborative MPI parallelization.

    MPIMasterCollectiveDataManager implements the data manipulation methods of c3po.DataManager.DataManager by instructing the workers to execute them.
    """

    def __init__(self, mpiMasterCollectivephysicsD, idDataWorker, localDataManager=None):
        """! Build a MPIMasterCollectiveDataManager object.

        @param mpiMasterCollectivephysicsD The MPIMasterCollectivePhysicsDriver object driving the c3po.PhysicsDriver.PhysicsDriver
        executed by the workers responsible of the remote c3po.DataManager.DataManager.
        @param idDataWorker Number identifying the c3po.DataManager.DataManager in the workers (see c3po.mpi.MPIWorker.MPIWorker).
        @param localDataManager a c3po.DataManager.DataManager the MPIMasterCollectiveDataManager object will use together with the
        remote ones. It enables the master to contribute to a collective computation.
        """
        self.physicsDriver_ = mpiMasterCollectivephysicsD
        self.mpiComm_ = mpiMasterCollectivephysicsD.getCommunicator()
        self.masterRank_ = mpiMasterCollectivephysicsD.masterRank_
        self.idDataWorker_ = idDataWorker
        self.localDataManager_ = localDataManager

    def __del__(self):
        """! Destructor. """
        self.physicsDriver_.setDataManagerToFree(self.idDataWorker_)

    def checkCompatibility(self, other):
        """! INTERNAL """
        if not isinstance(other, MPIMasterCollectiveDataManager) or self.physicsDriver_ != other.physicsDriver_ or (self.localDataManager_ is not None) and (other.localDataManager_ is None):
            raise Exception("MPIMasterCollectiveDataManager.checkCompatibility : self and other are not compatible.")

    def clone(self):
        """! See c3po.DataManager.DataManager.clone(). """
        return (self * 1.)

    def cloneEmpty(self):
        """! See c3po.DataManager.DataManager.cloneEmpty(). """
        self.mpiComm_.bcast((MPITag.cloneEmptyData, self.idDataWorker_), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_.cloneEmpty()
        newIdDataWorker = self.mpiComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def copy(self, other):
        """! See c3po.DataManager.DataManager.copy(). """
        self.checkCompatibility(other)
        self.mpiComm_.bcast((MPITag.copyData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_.copy(other.localDataManager_)

    def normMax(self):
        """! See c3po.DataManager.DataManager.normMax(). """
        self.mpiComm_.bcast((MPITag.normMax, self.idDataWorker_), root=self.masterRank_)
        resu = 0.
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.normMax()
        return self.mpiComm_.reduce(resu, op=MPI.MAX, root=self.masterRank_)

    def norm2(self):
        """! See c3po.DataManager.DataManager.norm2(). """
        self.mpiComm_.bcast((MPITag.norm2, self.idDataWorker_), root=self.masterRank_)
        resu = 0.
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.norm2()
            resu = resu * resu
        resu = self.mpiComm_.reduce(resu, op=MPI.SUM, root=self.masterRank_)
        return math.sqrt(resu)

    def __add__(self, other):
        """! See c3po.DataManager.DataManager.__add__(). """
        self.checkCompatibility(other)
        self.mpiComm_.bcast((MPITag.addData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ + other.localDataManager_
        newIdDataWorker = self.mpiComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __iadd__(self, other):
        """! See c3po.DataManager.DataManager.__iadd__(). """
        self.checkCompatibility(other)
        self.mpiComm_.bcast((MPITag.iaddData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ += other.localDataManager_
        return self

    def __sub__(self, other):
        """! See c3po.DataManager.DataManager.__sub__(). """
        self.checkCompatibility(other)
        self.mpiComm_.bcast((MPITag.subData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ - other.localDataManager_
        newIdDataWorker = self.mpiComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __isub__(self, other):
        """! See c3po.DataManager.DataManager.__isub__(). """
        self.checkCompatibility(other)
        self.mpiComm_.bcast((MPITag.isubData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ -= other.localDataManager_
        return self

    def __mul__(self, scalar):
        """! See c3po.DataManager.DataManager.__mul__(). """
        self.mpiComm_.bcast((MPITag.mulData, (self.idDataWorker_, scalar)), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ * scalar
        newIdDataWorker = self.mpiComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __imul__(self, scalar):
        """! See c3po.DataManager.DataManager.__imul__(). """
        self.mpiComm_.bcast((MPITag.imulData, (self.idDataWorker_, scalar)), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ *= scalar
        return self

    def imuladd(self, scalar, other):
        """! See c3po.DataManager.DataManager.imuladd(). """
        self.checkCompatibility(other)
        self.mpiComm_.bcast((MPITag.imuladdData, (self.idDataWorker_, scalar, other.idDataWorker_)), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_.imuladd(scalar, other.localDataManager_)
        return self

    def dot(self, other):
        """! See c3po.DataManager.DataManager.dot(). """
        self.checkCompatibility(other)
        self.mpiComm_.bcast((MPITag.dotData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        resu = 0
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.dot(other.localDataManager_)
        return self.mpiComm_.reduce(resu, op=MPI.SUM, root=self.masterRank_)