# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class SharedRemapping. """
from __future__ import print_function, division
from mpi4py import MPI as mpi

from c3po.mpi.mpiExchangeMethods.MPIExchangeMethod import MPIExchangeMethod


class MPIValueBcast(MPIExchangeMethod):
    """! MPIValueBcast can be used to exchange values between two sets of processes.

    A reduce is first made on the source processes, then the result is broacasted on the target processes.
    """

    def __init__(self, reduceOp=None):
        """! Build an MPIValueBcast object, to be given to an c3po.mpi.MPIExchanger.MPIExchanger.

        @param reduceOp A mpi4py reduce operator. The result of the reduce is sent to the target processes.
            None can be used to skip the reduce step: the value of the first source process is directly sent.
        """
        self._reduceOp = reduceOp
        self._mpiGetComm = None
        self._mpiBroadcastComm = None
        self._isSetterProcess = False
        self._isGetterProcess = False
        self._isBcastProcess = False

    def setRanks(self, ranksToGet, ranksToSet, mpiComm):
        """! See MPIExchangeMethod.setRanks. """
        rank = mpiComm.Get_rank()
        self._isGetterProcess = rank in ranksToGet
        self._isSetterProcess = rank in ranksToSet
        self._mpiGetComm = mpiComm.Split(0 if self._isGetterProcess else mpi.UNDEFINED, rank)
        isBcastRoot = self._isGetterProcess and self._mpiGetComm.Get_rank() == 0
        self._isBcastProcess = isBcastRoot or self._isSetterProcess
        self._mpiBroadcastComm = mpiComm.Split(0 if self._isBcastProcess else mpi.UNDEFINED, key=0 if isBcastRoot else 1)

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! Perform the exchange. """
        if len(fieldsToGet) != 0 or len(fieldsToSet) != 0:
            raise ValueError("MPIValueBcast: we cannot deal with fields.")

        nbValues = 0
        if self._isGetterProcess:
            nbValues = self._mpiGetComm.allreduce(len(valuesToGet), op=mpi.MIN)
        if self._isBcastProcess:
            nbValues = self._mpiBroadcastComm.bcast(nbValues)

        valuesToSet = []
        for i in range(nbValues):
            value = 0.
            if self._isGetterProcess:
                value = valuesToGet[i]
                if self._reduceOp is not None:
                    value = self._mpiGetComm.reduce(value, op=self._reduceOp)
            if self._isBcastProcess:
                value = self._mpiBroadcastComm.bcast(value)
            if self._isSetterProcess:
                valuesToSet.append(value)

        return [], valuesToSet

    def getPatterns(self):
        """! See ExchangeMethod.getPatterns. """
        return [(0, 0, 1, 0), (0, 0, 0, 1)]
