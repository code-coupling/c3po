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

from C3PO.CollaborativeDataManager import CollaborativeDataManager
from C3POMPI.MPIRemoteProcess import MPIRemoteProcess


class MPICollaborativeDataManager(CollaborativeDataManager):
    """! MPICollaborativeDataManager is the MPI collaborative version of C3PO.CollaborativeDataManager.CollaborativeDataManager (for collaborative MPI paradigm). 

    It allows to handle a set of C3PO.DataManager.DataManager (some of then being remote) as a single one. Thanks to this class, data can be distributed on different MPI processes but still used in the same way. 

    Exchanges are still to be done with the individual C3PO.DataManager.DataManager.

    When at least one MPIRemoteProcess is present, MPICollaborativeDataManager uses collective MPI communications: the object must be built and used in the same way for all the involved processes. They must all share the same communicator, and all the processes of that communicator must be involved.

    Can replace, without impact, a C3PO.CollaborativeDataManager.CollaborativeDataManager of a single processor calculation, if the MPI environment is available.
    """

    def __init__(self, dataManagers):
        """! Build a MPICollaborativeDataManager object.

        Has the same form than CollaborativeDataManager.__init__() but can also contain MPIRemoteProcess objects.

        When at least one MPIRemoteProcess is present, MPICollaborativeDataManager uses collective MPI communications: the object must be built and used in the same way for all the involved processes. They must all share the same communicator, and all the processes of that communicator must be involved.

        @param dataManagers a list of C3PO.DataManager.DataManager.
        """
        self.MPIComm_ = -1
        self.isMPI_ = False
        ranks = []
        localData = []
        for data in dataManagers:
            if isinstance(data, MPIRemoteProcess):
                if not self.isMPI_:
                    if data.MPIComm_ == MPI.COMM_NULL:
                        raise Exception("MPICollaborativeDataManager.__init__ All distant process must be part of the communicator (MPI.COMM_NULL found).")
                    self.isMPI_ = True
                    self.MPIComm_ = data.MPIComm_
                    ranks.append(data.MPIComm_.Get_rank())
                else:
                    if self.MPIComm_ != data.MPIComm_:
                        raise Exception("MPICollaborativeDataManager.__init__ All distant process must used the same MPI communicator")
                rank = data.rank_
                if rank not in ranks:
                    ranks.append(rank)
            else:
                localData.append(data)
        if len(ranks) != 0:
            if len(ranks) != self.MPIComm_.Get_size():
                raise Exception("MPICollaborativeDataManager.__init__ All process of the MPI communicator are not involve in the MPICollaborativeDataManager")
        CollaborativeDataManager.__init__(self, localData)

    def cloneEmpty(self):
        """! Return a clone of self without copying the data. 

        @return An empty clone of self.
        """
        notMPIoutput = CollaborativeDataManager.cloneEmpty(self)
        output = MPICollaborativeDataManager(notMPIoutput.dataManagers_)
        output.MPIComm_ = self.MPIComm_
        output.isMPI_ = self.isMPI_
        return output

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields. 
        """
        norm = CollaborativeDataManager.normMax(self)
        if self.isMPI_:
            norm = self.MPIComm_.allreduce(norm, op=MPI.MAX)
        return norm

    def norm2(self):
        """! Return the norm 2.

        @return sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.  
        """
        norm = CollaborativeDataManager.norm2(self)
        if self.isMPI_:
            norm = self.MPIComm_.allreduce(norm * norm, op=MPI.SUM)
            norm = math.sqrt(norm)
        return norm

    def dot(self, other):
        """! Return the scalar product of self with other.

        @param other a MPICollaborativeDataManager consistent with self.

        @return the scalar product of self with other.

        @throw Exception if self and other are not consistent.
        """
        result = CollaborativeDataManager.dot(self, other)
        if self.isMPI_:
            result = self.MPIComm_.allreduce(result, op=MPI.SUM)
        return result
