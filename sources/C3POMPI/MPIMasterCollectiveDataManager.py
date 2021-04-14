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

from C3POMPI.MPITag import MPITag


class MPIMasterCollectiveDataManager(object):
    """! MPIMasterCollectiveDataManager is used by the master process to control a set of remote C3PO.DataManager.DataManager as a single one.. 

    It can, in addition, be in charge of a local one. This class is well suited to steer a code using an internal collaborative MPI parallelization.

    MPIMasterCollectiveDataManager implements the data manipulation methods of C3PO.DataManager.DataManager by instructing the workers to execute them.
    """

    def __init__(self, mpiMasterCollectivephysicsD, idDataWorker, localDataManager=None):
        """! Build a MPIMasterCollectiveDataManager object.

        @param mpiMasterCollectivephysicsD The MPIMasterCollectivePhysicsDriver object driving the C3PO.PhysicsDriver.PhysicsDriver 
        executed by the workers responsible of the remote C3PO.DataManager.DataManager.
        @param idDataWorker Number identifying the C3PO.DataManager.DataManager in the workers (see C3POMPI.MPIWorker.MPIWorker).
        @param localDataManager a C3PO.DataManager.DataManager the MPIMasterCollectiveDataManager object will use together with the 
        remote ones. It enables the master to contribute to a collective computation.
        """
        self.physicsDriver_ = mpiMasterCollectivephysicsD
        self.MPIComm_ = mpiMasterCollectivephysicsD.getCommunicator()
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
        """! See C3PO.DataManager.DataManager.clone(). """
        return (self * 1.)

    def cloneEmpty(self):
        """! See C3PO.DataManager.DataManager.cloneEmpty(). """
        self.MPIComm_.bcast((MPITag.cloneEmptyData, self.idDataWorker_), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_.cloneEmpty()
        newIdDataWorker = self.MPIComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def copy(self, other):
        """! See C3PO.DataManager.DataManager.copy(). """
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.copyData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_.copy(other.localDataManager_)

    def normMax(self):
        """! See C3PO.DataManager.DataManager.normMax(). """
        self.MPIComm_.bcast((MPITag.normMax, self.idDataWorker_), root=self.masterRank_)
        resu = 0.
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.normMax()
        return self.MPIComm_.reduce(resu, op=MPI.MAX, root=self.masterRank_)

    def norm2(self):
        """! See C3PO.DataManager.DataManager.norm2(). """
        self.MPIComm_.bcast((MPITag.norm2, self.idDataWorker_), root=self.masterRank_)
        resu = 0.
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.norm2()
            resu = resu * resu
        resu = self.MPIComm_.reduce(resu, op=MPI.SUM, root=self.masterRank_)
        return math.sqrt(resu)

    def __add__(self, other):
        """! See C3PO.DataManager.DataManager.__add__(). """
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.addData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ + other.localDataManager_
        newIdDataWorker = self.MPIComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __iadd__(self, other):
        """! See C3PO.DataManager.DataManager.__iadd__(). """
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.iaddData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ += other.localDataManager_
        return self

    def __sub__(self, other):
        """! See C3PO.DataManager.DataManager.__sub__(). """
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.subData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ - other.localDataManager_
        newIdDataWorker = self.MPIComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __isub__(self, other):
        """! See C3PO.DataManager.DataManager.__isub__(). """
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.isubData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ -= other.localDataManager_
        return self

    def __mul__(self, scalar):
        """! See C3PO.DataManager.DataManager.__mul__(). """
        self.MPIComm_.bcast((MPITag.mulData, (self.idDataWorker_, scalar)), root=self.masterRank_)
        localData = None
        if self.localDataManager_ is not None:
            localData = self.localDataManager_ * scalar
        newIdDataWorker = self.MPIComm_.reduce(1E30, op=MPI.MIN, root=self.masterRank_)
        new_data = MPIMasterCollectiveDataManager(self.physicsDriver_, newIdDataWorker, localData)
        return new_data

    def __imul__(self, scalar):
        """! See C3PO.DataManager.DataManager.__imul__(). """
        self.MPIComm_.bcast((MPITag.imulData, (self.idDataWorker_, scalar)), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_ *= scalar
        return self

    def imuladd(self, scalar, other):
        """! See C3PO.DataManager.DataManager.imuladd(). """
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.imuladdData, (self.idDataWorker_, scalar, other.idDataWorker_)), root=self.masterRank_)
        if self.localDataManager_ is not None:
            self.localDataManager_.imuladd(scalar, other.localDataManager_)
        return self

    def dot(self, other):
        """! See C3PO.DataManager.DataManager.dot(). """
        self.checkCompatibility(other)
        self.MPIComm_.bcast((MPITag.dotData, [self.idDataWorker_, other.idDataWorker_]), root=self.masterRank_)
        resu = 0
        if self.localDataManager_ is not None:
            resu = self.localDataManager_.dot(other.localDataManager_)
        return self.MPIComm_.reduce(resu, op=MPI.SUM, root=self.masterRank_)
