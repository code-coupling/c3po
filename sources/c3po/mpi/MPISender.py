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
            field = self._dataAccess.getFieldTemplate()
        else:
            field = self._dataAccess.get()
        for destination in self._destinations:
            mpiComm = destination.mpiComm
            if self._isFirstSend:
                if isinstance(destination, MPICollectiveProcess):
                    mpiComm.bcast(field, root=mpiComm.Get_rank())
                else:
                    mpiComm.send(field, dest=destination.rank, tag=MPITag.data)
            elif not self._isTemplate:
                dataArrayDouble = field.getArray()
                if isinstance(destination, MPICollectiveProcess):
                    mpiComm.bcast(dataArrayDouble, root=mpiComm.Get_rank())
                else:
                    mpiComm.send(dataArrayDouble, dest=destination.rank, tag=MPITag.data)
        self._isFirstSend = False
        self._storing.store(field)

    def clean(self):
        """! INTERNAL """
        self._dataAccess.clean()
        self._isFirstSend = True


class MPIFileFieldSender(object):
    """! INTERNAL """

    def __init__(self, destinations, dataAccess, storing, isTemplate):
        self._destinations = destinations
        self._dataAccess = dataAccess
        self._storing = storing
        self._isTemplate = isTemplate
        self._isFirstSend = True
        self._fileName = None

    def exchange(self):
        """! INTERNAL """
        field = 0
        if self._isTemplate:
            field = self._dataAccess.getFieldTemplate()
        else:
            field = self._dataAccess.get()

        if self._fileName is None:
            num = 0
            rank = MPI.COMM_WORLD.Get_rank()
            fileExist = True
            while fileExist:
                self._fileName = "ExchangeField_rank" + str(rank) + "_" + str(num) + ".med"
                fileExist = os.path.exists(self._fileName)
                num += 1

        if len(self._destinations) > 0 and (self._isFirstSend or not self._isTemplate):
            for destination in self._destinations:
                mpiComm = destination.mpiComm
                if isinstance(destination, MPICollectiveProcess):
                    mpiComm.Barrier()
                else:
                    mpiComm.recv(source=destination.rank, tag=MPITag.data)

            time, iteration, order = field.getTime()
            field.setTime(0, 0, 0)
            if os.path.exists(self._fileName):
                mc.WriteFieldUsingAlreadyWrittenMesh(self._fileName, field)
            else:
                mc.WriteField(self._fileName, field, True)

            medInfo = [(field.getTypeOfField(), os.path.join(os.getcwd(), self._fileName), field.getMesh().getName(), 0, field.getName(), field.getTime()[1], field.getTime()[2]), field.getNature(), (time, iteration, order)]
            field.setTime(time, iteration, order)

            for destination in self._destinations:
                mpiComm = destination.mpiComm
                if isinstance(destination, MPICollectiveProcess):
                    mpiComm.bcast(medInfo, root=mpiComm.Get_rank())
                else:
                    mpiComm.send(medInfo, dest=destination.rank, tag=MPITag.data)

        self._isFirstSend = False
        self._storing.store(field)

    def clean(self):
        """! INTERNAL """
        self._dataAccess.clean()
        self._isFirstSend = True
        self._fileName = None


class MPIValueSender(object):
    """! INTERNAL """

    def __init__(self, destinations, dataAccess, storing):
        self._destinations = destinations
        self._dataAccess = dataAccess
        self._storing = storing

    def exchange(self):
        """! INTERNAL """
        value = self._dataAccess.get()
        for destination in self._destinations:
            mpiComm = destination.mpiComm
            if isinstance(destination, MPICollectiveProcess):
                mpiComm.bcast(value, root=mpiComm.Get_rank())
            else:
                mpiComm.send(value, dest=destination.rank, tag=MPITag.data)
        self._storing.store(value)

