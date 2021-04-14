# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPIMasterExchanger. """
from __future__ import print_function, division

from C3POMPI.MPITag import MPITag
from C3POMPI.MPIRemoteProcess import MPIRemoteProcess
from C3POMPI.MPICollectiveProcess import MPICollectiveProcess


class MPIMasterExchanger(object):
    """! MPIMasterExchanger is used by the master to control remote C3PO.Exchanger.Exchanger(s). 

    It can, in addition, be in charge of a local one (that allows the master to participate to the calculation).

    The exchange() method of MPIMasterExchanger commands workers to exchange data.
    """

    def __init__(self, workerProcesses, idExchangerWorker, localExchanger=None):
        """! Build a MPIMasterExchanger object.

        @param workerProcesses The list of MPIRemoteProcess or MPICollectiveProcess identifying the remote processes involved in the 
        exchange. In the case of MPICollectiveProcess, the mpiComm must include all the workers + the master, and only them.
        @param idExchangerWorker Number identifying the controlled C3PO.Exchanger.Exchanger in the involved workers (see C3POMPI.MPIWorker.MPIWorker).
        @param localExchanger a C3PO.Exchanger.Exchanger the MPIMasterExchanger object will run in the same time than the workers. It 
        enables the master to contribute to a collective computation.
        """
        self.workerProcesses_ = workerProcesses
        self.idExchangerWorker_ = idExchangerWorker
        self.localExchanger_ = localExchanger

    def exchange(self):
        """! Trigger the exchange of data. """
        for process in self.workerProcesses_:
            if isinstance(process, MPIRemoteProcess):
                process.MPIComm_.send(self.idExchangerWorker_, dest=process.rank_, tag=MPITag.exchange)
            elif isinstance(process, MPICollectiveProcess):
                process.MPIComm_.bcast((MPITag.exchange, self.idExchangerWorker_), root=process.MPIComm_.Get_rank())
            else:
                raise Exception("MPIMasterExchanger.exchange : we found an unknown worker type.")
        if self.localExchanger_ is not None:
            self.localExchanger_.exchange()
