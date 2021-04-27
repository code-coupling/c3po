# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPICollectiveDataManager. """
from __future__ import print_function, division

from c3po.mpi.MPICollectiveProcess import MPICollectiveProcess
from c3po.DataManager import DataManager


class MPICollectiveDataManager(DataManager, MPICollectiveProcess):
    """! MPICollectiveDataManager is the MPI collaborative version of the c3po.DataManager.DataManager in which all processes have locally all data.

    Can replace, without impact, a c3po.DataManager.DataManager for a calculation on a single process, if the MPI environment is available.
    """

    def __init__(self, mpiComm):
        """! Build a MPICollectiveDataManager object.

        @param mpiComm MPI communicator. It must be shared by all processes involved in the MPICollectiveDataManager (and all 
        processes of this MPI communicator must be involed in the MPICollectiveDataManager).
        """
        DataManager.__init__(self)
        MPICollectiveProcess.__init__(self, mpiComm)

    def cloneEmpty(self):
        """! Return a clone of self without copying the data. 

        @return An empty clone of self.
        """
        output = MPICollectiveDataManager(self.mpiComm_)
        output.MEDFieldTemplates_ = self.MEDFieldTemplates_
        return output
