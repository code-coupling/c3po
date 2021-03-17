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

import MEDCoupling
import MEDLoader as ml

from C3POMPI.MPITag import MPITag


class MPIFieldRecipient(object):
    """! INTERNAL """

    def __init__(self, sender, storing, isCollective, isTemplate):
        self.sender_ = sender
        self.storing_ = storing
        self.isCollective_ = isCollective
        self.isTemplate_ = isTemplate
        self.field_ = 0

    def exchange(self):
        MPIComm = self.sender_.MPIComm_
        senderRank = self.sender_.rank_
        if not hasattr(self.field_, "getArray"):
            if self.isCollective_:
                self.field_ = MPIComm.bcast(self.field_, root=senderRank)
            else:
                self.field_ = MPIComm.recv(source=senderRank, tag=MPITag.data)
        elif not self.isTemplate_:
            arraySize = self.field_.getArray().getNbOfElems()
            numpyArray = numpy.empty(arraySize)
            if self.isCollective_:
                MPIComm.Bcast([numpyArray, MPI.DOUBLE], root=senderRank)
            else:
                MPIComm.Recv([numpyArray, MPI.DOUBLE], source=senderRank, tag=MPITag.data)
            dataArray = MEDCoupling.DataArrayDouble(numpyArray)
            self.field_.setArray(dataArray)
        self.storing_.store(self.field_)


class MPIFileFieldRecipient(object):
    """! INTERNAL """

    def __init__(self, sender, storing, isCollective, isTemplate):
        self.sender_ = sender
        self.storing_ = storing
        self.isCollective_ = isCollective
        self.isTemplate_ = isTemplate
        self.field_ = 0

    def exchange(self):
        MPIComm = self.sender_.MPIComm_
        senderRank = self.sender_.rank_
        if not hasattr(self.field_, "getArray") or not self.isTemplate_:
            MEDinfo = ()
            if self.isCollective_:
                MEDinfo = MPIComm.bcast(MEDinfo, root=senderRank)
            else:
                MEDinfo = MPIComm.recv(source=senderRank, tag=MPITag.data)
            try:
                self.field_ = ml.MEDLoader.ReadField(*(MEDinfo[0]))
            except:
                self.field_ = ml.ReadField(*(MEDinfo[0]))
            self.field_.setNature(MEDinfo[1])
        self.storing_.store(self.field_)


class MPIValueRecipient(object):
    """! INTERNAL """

    def __init__(self, sender, storing, isCollective):
        self.sender_ = sender
        self.storing_ = storing
        self.isCollective_ = isCollective

    def exchange(self):
        MPIComm = self.sender_.MPIComm_
        senderRank = self.sender_.rank_
        if self.isCollective_:
            value = 0
            self.storing_.store(MPIComm.bcast(value, root=senderRank))
        else:
            self.storing_.store(MPIComm.recv(source=senderRank, tag=MPITag.data))
