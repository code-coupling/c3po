# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the classes MPIFieldRecipient, MPIFileFieldRecipient and MPIValueRecipient.
These classes recieve data from a remote process.
"""
from __future__ import print_function, division
from mpi4py import MPI
import numpy

import c3po.medcouplingCompat as mc
from c3po.mpi.MPITag import MPITag


class MPIFieldRecipient(object):
    """! INTERNAL """

    def __init__(self, sender, storing, isCollective, isTemplate):
        self._sender = sender
        self._storing = storing
        self._isCollective = isCollective
        self._isTemplate = isTemplate
        self._field = 0

    def exchange(self):
        """! INTERNAL """
        mpiComm = self._sender.mpiComm
        senderRank = self._sender.rank
        if not isinstance(self._field, mc.MEDCouplingFieldDouble):
            if self._isCollective:
                self._field = mpiComm.bcast(self._field, root=senderRank)
            else:
                self._field = mpiComm.recv(source=senderRank, tag=MPITag.data)
        elif not self._isTemplate:
            arraySize = self._field.getArray().getNbOfElems()
            numpyArray = numpy.empty(arraySize)
            if self._isCollective:
                mpiComm.Bcast([numpyArray, MPI.DOUBLE], root=senderRank)
            else:
                mpiComm.Recv([numpyArray, MPI.DOUBLE], source=senderRank, tag=MPITag.data)
            dataArray = mc.DataArrayDouble(numpyArray)
            self._field.setArray(dataArray)
        self._storing.store(self._field)


class MPIFileFieldRecipient(object):
    """! INTERNAL """

    def __init__(self, sender, storing, isCollective, isTemplate):
        self._sender = sender
        self._storing = storing
        self._isCollective = isCollective
        self._isTemplate = isTemplate
        self._field = 0

    def exchange(self):
        """! INTERNAL """
        mpiComm = self._sender.mpiComm
        senderRank = self._sender.rank
        if self._field == 0 or not self._isTemplate:
            medInfo = ()
            if self._isCollective:
                mpiComm.Barrier()
                medInfo = mpiComm.bcast(medInfo, root=senderRank)
            else:
                mpiComm.send(0, dest=senderRank, tag=MPITag.data)
                medInfo = mpiComm.recv(source=senderRank, tag=MPITag.data)
            self._field = mc.ReadField(*(medInfo[0]))
            self._field.setNature(medInfo[1])
            self._field.setTime(*(medInfo[2]))
        self._storing.store(self._field)


class MPIValueRecipient(object):
    """! INTERNAL """

    def __init__(self, sender, storing, isCollective):
        self._sender = sender
        self._storing = storing
        self._isCollective = isCollective

    def exchange(self):
        """! INTERNAL """
        mpiComm = self._sender.mpiComm
        senderRank = self._sender.rank
        if self._isCollective:
            value = 0
            self._storing.store(mpiComm.bcast(value, root=senderRank))
        else:
            self._storing.store(mpiComm.recv(source=senderRank, tag=MPITag.data))
