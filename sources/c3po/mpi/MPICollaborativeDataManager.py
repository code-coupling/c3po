# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPICollaborativeDataManager. """
from __future__ import print_function, division
import math
from mpi4py import MPI

from c3po.CollaborativeDataManager import CollaborativeDataManager
from c3po.CollaborativeObject import CollaborativeObject
from c3po.mpi.MPIRemote import MPIRemote
from c3po.mpi.MPIDomainDecompositionDataManager import MPIDomainDecompositionDataManager
from c3po.mpi.MPICollectiveDataManager import MPICollectiveDataManager


class MPICollaborativeDataManager(CollaborativeDataManager):
    """! MPICollaborativeDataManager is the MPI collaborative version of c3po.CollaborativeDataManager.CollaborativeDataManager
    (for collaborative MPI paradigm).

    It allows to handle a set of c3po.DataManager.DataManager (some of then being remote) as a single one. Thanks to this class,
    data can be distributed on different MPI processes but still used in the same way.

    When at least one MPIRemote is present, MPICollaborativeDataManager uses collective MPI communications: the object must
    be built and used in the same way for all the involved processes. They must all share the same communicator, and all the processes
    of that communicator must be involved.
    """

    def __init__(self, dataManagers, mpiComm=None):
        """! Build a MPICollaborativeDataManager object.

        Has the same form than CollaborativeDataManager.__init__() but can also contain MPIRemote objects.

        When at least one MPIRemote is present (or if mpiComm is not None), MPICollaborativeDataManager uses collective MPI
        communications: the object must be built and used in the same way for all the involved processes. They must all share the same
        communicator, and all the processes of that communicator must be involved.

        @param dataManagers a list of c3po.DataManager.DataManager.
        @param mpiComm If not None, forces MPICollaborativeDataManager to use collective MPI communications and to use this
        communicator.
        """
        localData = []
        self.mpiComm = mpiComm
        self.isMPI = mpiComm is not None
        indexToIgnore = []

        for data in dataManagers:
            if mpiComm is None and isinstance(data, MPIRemote):
                if not self.isMPI:
                    if data.mpiComm == MPI.COMM_NULL:
                        raise Exception("MPICollaborativeDataManager.__init__ All distant processes must be part of the communicator (MPI.COMM_NULL found).")
                    self.isMPI = True
                    self.mpiComm = data.mpiComm
                else:
                    if self.mpiComm != data.mpiComm:
                        raise Exception("MPICollaborativeDataManager.__init__ All distant processes must used the same MPI communicator")
            if not isinstance(data, MPIRemote):
                if isinstance(data, MPICollaborativeDataManager):
                    localData += data.dataManagers
                elif isinstance(data, MPIDomainDecompositionDataManager):
                    localView = data.getLocalView()
                    localData.append(localView)
                else:
                    if isinstance(data, MPICollectiveDataManager) and data.mpiComm.Get_rank() != 0:
                        indexToIgnore.append(len(localData))
                    localData.append(data)

        CollaborativeDataManager.__init__(self, localData)
        self.ignoreForConstOperators(indexToIgnore)
        CollaborativeObject.__init__(self, dataManagers)    # pylint: disable=non-parent-init-called

    def cloneEmpty(self):
        """! Return a clone of self without copying the data.

        @return An empty clone of self.
        """
        notMPIoutput = CollaborativeDataManager.cloneEmpty(self)
        output = MPICollaborativeDataManager(notMPIoutput.dataManagers)
        output.mpiComm = self.mpiComm
        output.isMPI = self.isMPI
        return output

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields.
        """
        norm = CollaborativeDataManager.normMax(self)
        if self.isMPI:
            norm = self.mpiComm.allreduce(norm, op=MPI.MAX)
        return norm

    def norm2(self):
        """! Return the norm 2.

        @return sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.
        """
        norm = CollaborativeDataManager.norm2(self)
        # print("local :", self, norm)
        if self.isMPI:
            norm = self.mpiComm.allreduce(norm * norm, op=MPI.SUM)
            norm = math.sqrt(norm)
        # print("global :", self, norm)
        return norm

    def dot(self, other):
        """! Return the scalar product of self with other.

        @param other a MPICollaborativeDataManager consistent with self.

        @return the scalar product of self with other.

        @throw Exception if self and other are not consistent.
        """
        result = CollaborativeDataManager.dot(self, other)
        if self.isMPI:
            result = self.mpiComm.allreduce(result, op=MPI.SUM)
        return result
