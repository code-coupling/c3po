# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPIDomainDecompositionDataManager. """
from __future__ import print_function, division
import math
from mpi4py import MPI

from c3po.LocalDataManager import LocalDataManager


class MPIDomainDecompositionDataManager(LocalDataManager):
    """! MPIDomainDecompositionDataManager is the MPI collaborative version of the c3po.DataManager.DataManager in which
    all processes have locally only a part of the data.

    Can replace, without impact, a c3po.LocalDataManager.LocalDataManager for a calculation on a single process, if the MPI
    environment is available.

    MPIDomainDecompositionDataManager behaves a little bit like a MPICollaborativeDataManager built with only one LocalDataManager
    and a mpiComm. However, unlike MPICollaborativeDataManager which will be expanded by MPIExchanger, and therefore seen as a
    simple LocalDataManager in this case, MPIDomainDecompositionDataManager will be directly handled by MPIExchanger.
    This is usually preferable when using a c3po.mpi.mpiExchangeMethods.MPIExchangeMethod.MPIExchangeMethod as exchange method.
    """

    def __init__(self, mpiComm):
        """! Build a MPIDomainDecompositionDataManager object.

        @param mpiComm MPI communicator. It must be shared by all processes involved in the MPIDomainDecompositionDataManager (and all processes
        of this MPI communicator must be involed in the MPIDomainDecompositionDataManager).
        """
        LocalDataManager.__init__(self)
        self.mpiComm = mpiComm

    def getMPIComm(self):
        """! (Optional) Return the MPI communicator used by the code for parallel computations.

        @return (mpi4py.Comm) mpi4py communicator.
        """
        return self.mpiComm

    def cloneEmpty(self):
        """! Return a clone of self without copying the data.

        @return An empty clone of self.
        """
        output = MPIDomainDecompositionDataManager(self.mpiComm)
        output.valuesInt = self.valuesInt
        output.valuesString = self.valuesString
        output.fieldsInt = self.fieldsInt
        output.fieldsDoubleTemplates = self.fieldsDoubleTemplates
        return output

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields.
        """
        norm = LocalDataManager.normMax(self)
        return self.mpiComm.allreduce(norm, op=MPI.MAX)

    def norm2(self):
        """! Return the norm 2.

        @return sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.
        """
        norm = LocalDataManager.norm2(self)
        norm = self.mpiComm.allreduce(norm * norm, op=MPI.SUM)
        return math.sqrt(norm)

    def dot(self, other):
        """! Return the scalar product of self with other.

        @param other a MPICollaborativeDataManager consistent with self.

        @return the scalar product of self with other.

        @throw Exception if self and other are not consistent.
        """
        result = LocalDataManager.dot(self, other)
        return self.mpiComm.allreduce(result, op=MPI.SUM)

    def getLocalView(self):
        """! Return a new LocalDataManager that holds the same data than self

        @return a LocalDataManager that holds the same data than self
        """
        localView = LocalDataManager()
        localView.valuesDouble = self.valuesDouble
        localView.valuesInt = self.valuesInt
        localView.valuesString = self.valuesString
        localView.fieldsDouble = self.fieldsDouble
        localView.fieldsInt = self.fieldsInt
        localView.fieldsDoubleTemplates = self.fieldsDoubleTemplates
        return localView
