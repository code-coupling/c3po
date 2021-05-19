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
import os

from mpi4py import MPI

import c3po.medcouplingCompat as mc
from c3po.mpi.MPITag import MPITag
from c3po.mpi.MPICollectiveProcess import MPICollectiveProcess


class MPIFieldSender(object):
    """! INTERNAL """

    def __init__(self, destinations, dataAccess, storing, isTemplate):
        self._destinations = destinations
        self._dataAccess = dataAccess
        self._storing = storing
        self._isTemplate = isTemplate
        self._isFirstSend = True

    def exchange(self):
        """! INTERNAL """
        field = 0
        if self._isTemplate:
            field = self._dataAccess.getInputMEDFieldTemplate()
        else:
            field = self._dataAccess.getOutputMEDField()
        for destination in self._destinations:
            mpiComm = destination.mpiComm
            if self._isFirstSend or not hasattr(field, "getArray"):
                if isinstance(destination, MPICollectiveProcess):
                    mpiComm.bcast(field, root=mpiComm.Get_rank())
                else:
                    mpiComm.send(field, dest=destination.rank, tag=MPITag.data)
            elif not self._isTemplate:
                npArray = field.getArray().toNumPyArray()
                if isinstance(destination, MPICollectiveProcess):
                    mpiComm.Bcast([npArray, MPI.DOUBLE], root=mpiComm.Get_rank())
                else:
                    mpiComm.Send([npArray, MPI.DOUBLE], dest=destination.rank, tag=MPITag.data)
        self._isFirstSend = False
        self._storing.store(field)


class MPIFileFieldSender(object):
    """! INTERNAL """

    def __init__(self, destinations, dataAccess, storing, isTemplate):
        self._destinations = destinations
        self._dataAccess = dataAccess
        self._storing = storing
        self._isTemplate = isTemplate
        self._isFirstSend = True

    def exchange(self):
        """! INTERNAL """
        field = 0
        if self._isTemplate:
            field = self._dataAccess.getInputMEDFieldTemplate()
        else:
            field = self._dataAccess.getOutputMEDField()

        if len(self._destinations) > 0 and (self._isFirstSend or not self._isTemplate):
            num = 0
            while os.path.exists("ExchangeField_" + str(num) + ".med"):
                num += 1
            nameFile = "ExchangeField_" + str(num) + ".med"
            mc.WriteField("ExchangeField_" + str(num) + ".med", field, True)

            _, iteration, order = field.getTime()
            medInfo = [(field.getTypeOfField(), os.getcwd() + "/" + nameFile, field.getMesh().getName(), 0, field.getName(), iteration, order), field.getNature()]

            for destination in self._destinations:
                mpiComm = destination.mpiComm
                if isinstance(destination, MPICollectiveProcess):
                    mpiComm.bcast(medInfo, root=mpiComm.Get_rank())
                else:
                    mpiComm.send(medInfo, dest=destination.rank, tag=MPITag.data)
        self._isFirstSend = False
        self._storing.store(field)


class MPIValueSender(object):
    """! INTERNAL """

    def __init__(self, destinations, dataAccess, storing):
        self._destinations = destinations
        self._dataAccess = dataAccess
        self._storing = storing

    def exchange(self):
        """! INTERNAL """
        value = self._dataAccess.getValue()
        for destination in self._destinations:
            mpiComm = destination.mpiComm
            if isinstance(destination, MPICollectiveProcess):
                mpiComm.bcast(value, root=mpiComm.Get_rank())
            else:
                mpiComm.send(value, dest=destination.rank, tag=MPITag.data)
        self._storing.store(value)
