# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the MPIMasterExchanger class. """
from __future__ import print_function, division
from mpi4py import MPI

from MPITag import MPITag
from MPIRemoteProcess import MPIRemoteProcess
from MPICollectiveProcess import MPICollectiveProcess


class MPIMasterExchanger(object):
    """ This class is used by the master to control remote exchangers. It can, in addition, be in charge of a local one (allowing the master to participate to the calculation).

    The exchange() method of MPIMasterExchanger commands workers to exchange data.
    """

    def __init__(self, workerProcesses, IdExchangerWorker, localExchanger=None):
        """ Builds a MPIMasterExchanger object.

        :param workerProcesses: The list of MPIRemoteProcess or MPICollectiveProcess identifying the remote processes involved in the exchange. In the case of MPICollectiveProcess, the MPIComm must include all the workers + the master, and only them.
        :param IdExchangerWorker: Common number identifying this exchanger in the involved workers (see MPIWorker).
        :param localExchanger: a exchanger the MPIMasterExchanger object will run in the same time than the workers. It enables the master to contribute to a collective computation.
        """
        self.workerProcesses_ = workerProcesses
        self.IdExchangerWorker_ = IdExchangerWorker
        self.localExchanger_ = localExchanger

    def exchange(self):
        for process in self.workerProcesses_:
            if isinstance(process, MPIRemoteProcess):
                process.MPIComm_.send(self.IdExchangerWorker_, dest=process.rank_, tag=MPITag.exchange)
            elif isinstance(process, MPICollectiveProcess):
                process.MPIComm_.bcast((MPITag.exchange, self.IdExchangerWorker_), root=process.MPIComm_.Get_rank())
            else:
                raise Exception("MPIMasterExchanger.exchange : we found an unknown worker type.")
        if self.localExchanger_ is not None:
            self.localExchanger_.exchange()
