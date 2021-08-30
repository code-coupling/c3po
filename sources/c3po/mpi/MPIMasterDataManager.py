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
from mpi4py import MPI

from c3po.mpi.MPITag import MPITag

from c3po.DataManager import DataManager


class MPIMasterDataManager(DataManager):
    """! MPIMasterDataManager is used by the master process to control a (set of) remote c3po.DataManager.DataManager as a local one.

    It can, in addition, be in charge of a local one (can be usefull to contribute to a collaborative computation).

    MPIMasterDataManager implements the methods of c3po.DataManager.DataManager by instructing the worker to execute them.
    """

    def __init__(self, mpiMasterphysicsD, idDataWorker, localDataManager=None):
        """! Build a MPIMasterDataManager object.

        @param mpiMasterphysicsD The MPIMasterPhysicsDriver object driving the c3po.PhysicsDriver.PhysicsDriver executed by the worker
        responsible of the remote c3po.DataManager.DataManager.
        @param idDataWorker Number identifying the c3po.DataManager.DataManager in the worker (see c3po.mpi.MPIWorker.MPIWorker).
        @param localDataManager a c3po.DataManager.DataManager the MPIMasterDataManager object will use together with the
        remote ones. It enables the master to contribute to a collaborative computation.
        """
        self.physicsDriver = mpiMasterphysicsD
        self.mpiComm = mpiMasterphysicsD.mpiComm
        self.idDataWorker = idDataWorker
        self.localDataManager = localDataManager

    def __del__(self):
        """! Destructor. """
        self.physicsDriver.setDataManagerToFree(self.idDataWorker)

    def checkCompatibility(self, other):
        """! INTERNAL """
        if not isinstance(other, MPIMasterDataManager) or self.physicsDriver != other.physicsDriver or (self.localDataManager is not None) and (other.localDataManager is None):
            raise Exception("MPIMasterDataManager.checkCompatibility : self and other are not compatible.")

    def clone(self):
        """! See c3po.DataManager.DataManager.clone(). """
        return self * 1.

    def cloneEmpty(self):
        """! See c3po.DataManager.DataManager.cloneEmpty(). """
        self.physicsDriver.sendData(MPITag.cloneEmptyData, self.idDataWorker)
        localData = None
        if self.localDataManager is not None:
            localData = self.localDataManager.cloneEmpty()
        newIdDataWorker = self.physicsDriver.recvData(1E30)
        newData = MPIMasterDataManager(self.physicsDriver, newIdDataWorker, localData)
        return newData

    def copy(self, other):
        """! See c3po.DataManager.DataManager.copy(). """
        self.checkCompatibility(other)
        self.physicsDriver.sendData(MPITag.copyData, [self.idDataWorker, other.idDataWorker])
        if self.localDataManager is not None:
            self.localDataManager.copy(other.localDataManager)

    def normMax(self):
        """! See c3po.DataManager.DataManager.normMax(). """
        self.physicsDriver.sendData(MPITag.normMax, self.idDataWorker)
        resu = 0.
        if self.localDataManager is not None:
            resu = self.localDataManager.normMax()
        return self.physicsDriver.recvData(resu, MPI.MAX)

    def norm2(self):
        """! See c3po.DataManager.DataManager.norm2(). """
        self.physicsDriver.sendData(MPITag.norm2, self.idDataWorker)
        resu = 0.
        if self.localDataManager is not None:
            resu = self.localDataManager.norm2()
            resu = resu * resu
        resu = self.physicsDriver.recvData(resu, MPI.SUM)
        return math.sqrt(resu)

    def __add__(self, other):
        """! See c3po.DataManager.DataManager.__add__(). """
        self.checkCompatibility(other)
        self.physicsDriver.sendData(MPITag.addData, [self.idDataWorker, other.idDataWorker])
        localData = None
        if self.localDataManager is not None:
            localData = self.localDataManager + other.localDataManager
        newIdDataWorker = self.physicsDriver.recvData(1E30)
        newData = MPIMasterDataManager(self.physicsDriver, newIdDataWorker, localData)
        return newData

    def __iadd__(self, other):
        """! See c3po.DataManager.DataManager.__iadd__(). """
        self.checkCompatibility(other)
        self.physicsDriver.sendData(MPITag.iaddData, [self.idDataWorker, other.idDataWorker])
        if self.localDataManager is not None:
            self.localDataManager += other.localDataManager
        return self

    def __sub__(self, other):
        """! See c3po.DataManager.DataManager.__sub__(). """
        self.checkCompatibility(other)
        self.physicsDriver.sendData(MPITag.subData, [self.idDataWorker, other.idDataWorker])
        localData = None
        if self.localDataManager is not None:
            localData = self.localDataManager - other.localDataManager
        newIdDataWorker = self.physicsDriver.recvData(1E30)
        newData = MPIMasterDataManager(self.physicsDriver, newIdDataWorker, localData)
        return newData

    def __isub__(self, other):
        """! See c3po.DataManager.DataManager.__isub__(). """
        self.checkCompatibility(other)
        self.physicsDriver.sendData(MPITag.isubData, [self.idDataWorker, other.idDataWorker])
        if self.localDataManager is not None:
            self.localDataManager -= other.localDataManager
        return self

    def __mul__(self, scalar):
        """! See c3po.DataManager.DataManager.__mul__(). """
        self.physicsDriver.sendData(MPITag.mulData, (self.idDataWorker, scalar))
        localData = None
        if self.localDataManager is not None:
            localData = self.localDataManager * scalar
        newIdDataWorker = self.physicsDriver.recvData(1E30)
        newData = MPIMasterDataManager(self.physicsDriver, newIdDataWorker, localData)
        return newData

    def __imul__(self, scalar):
        """! See c3po.DataManager.DataManager.__imul__(). """
        self.physicsDriver.sendData(MPITag.imulData, (self.idDataWorker, scalar))
        if self.localDataManager is not None:
            self.localDataManager *= scalar
        return self

    def imuladd(self, scalar, other):
        """! See c3po.DataManager.DataManager.imuladd(). """
        self.checkCompatibility(other)
        self.physicsDriver.sendData(MPITag.imuladdData, (self.idDataWorker, scalar, other.idDataWorker))
        if self.localDataManager is not None:
            self.localDataManager.imuladd(scalar, other.localDataManager)
        return self

    def dot(self, other):
        """! See c3po.DataManager.DataManager.dot(). """
        self.checkCompatibility(other)
        self.physicsDriver.sendData(MPITag.dotData, [self.idDataWorker, other.idDataWorker])
        resu = 0
        if self.localDataManager is not None:
            resu = self.localDataManager.dot(other.localDataManager)
        return self.physicsDriver.recvData(resu, MPI.SUM)
