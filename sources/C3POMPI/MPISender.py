# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the classes MPIFieldSender, MPIFileFieldSender and MPIValueSender. 
These classes send data to another process.
"""
from __future__ import print_function, division
from mpi4py import MPI
import numpy
import os

from C3POMPI.MPITag import MPITag
from C3POMPI.MPICollectiveProcess import MPICollectiveProcess

import MEDLoader as ml


class MPIFieldSender(object):
    """! INTERNAL """

    def __init__(self, destinations, dataAccess, storing, isTemplate):
        self.destinations_ = destinations
        self.dataAccess_ = dataAccess
        self.storing_ = storing
        self.isTemplate_ = isTemplate
        self.isFirstSend_ = True

    def exchange(self):
        field = 0
        if self.isTemplate_:
            field = self.dataAccess_.getInputMEDFieldTemplate()
        else:
            field = self.dataAccess_.getOutputMEDField()
        for destination in self.destinations_:
            MPIComm = destination.MPIComm_
            if self.isFirstSend_ or not hasattr(field, "getArray"):
                if isinstance(destination, MPICollectiveProcess):
                    MPIComm.bcast(field, root=MPIComm.Get_rank())
                else:
                    MPIComm.send(field, dest=destination.rank_, tag=MPITag.data)
            elif not self.isTemplate_:
                npArray = field.getArray().toNumPyArray()
                if isinstance(destination, MPICollectiveProcess):
                    MPIComm.Bcast([npArray, MPI.DOUBLE], root=MPIComm.Get_rank())
                else:
                    MPIComm.Send([npArray, MPI.DOUBLE], dest=destination.rank_, tag=MPITag.data)
        self.isFirstSend_ = False
        self.storing_.store(field)


class MPIFileFieldSender(object):
    """! INTERNAL """

    def __init__(self, destinations, dataAccess, storing, isTemplate):
        self.destinations_ = destinations
        self.dataAccess_ = dataAccess
        self.storing_ = storing
        self.isTemplate_ = isTemplate
        self.isFirstSend_ = True

    def exchange(self):
        field = 0
        if self.isTemplate_:
            field = self.dataAccess_.getInputMEDFieldTemplate()
        else:
            field = self.dataAccess_.getOutputMEDField()

        if len(self.destinations_) > 0 and (self.isFirstSend_ or not self.isTemplate_):
            num = 0
            while os.path.exists("ExchangeField_" + str(num) + ".med"):
                num += 1
            name_file = "ExchangeField_" + str(num) + ".med"
            try:
                ml.MEDLoader.WriteField("ExchangeField_" + str(num) + ".med", field, True)
            except:
                ml.WriteField("ExchangeField_" + str(num) + ".med", field, True)

            timeMED, iteration, order = field.getTime()
            MEDinfo = [(field.getTypeOfField(), os.getcwd() + "/" + name_file, field.getMesh().getName(), 0, field.getName(), iteration, order), field.getNature()]

            for destination in self.destinations_:
                MPIComm = destination.MPIComm_
                if isinstance(destination, MPICollectiveProcess):
                    MPIComm.bcast(MEDinfo, root=MPIComm.Get_rank())
                else:
                    MPIComm.send(MEDinfo, dest=destination.rank_, tag=MPITag.data)
        self.isFirstSend_ = False
        self.storing_.store(field)


class MPIValueSender(object):
    """! INTERNAL """

    def __init__(self, destinations, dataAccess, storing):
        self.destinations_ = destinations
        self.dataAccess_ = dataAccess
        self.storing_ = storing

    def exchange(self):
        value = self.dataAccess_.getValue()
        for destination in self.destinations_:
            MPIComm = destination.MPIComm_
            if isinstance(destination, MPICollectiveProcess):
                MPIComm.bcast(value, root=MPIComm.Get_rank())
            else:
                MPIComm.send(value, dest=destination.rank_, tag=MPITag.data)
        self.storing_.store(value)
