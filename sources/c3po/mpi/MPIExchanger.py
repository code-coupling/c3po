# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the classes MPIExchanger and MPIShortcutToData, MPIShortcutToData is for internal use only. """
from __future__ import print_function, division

from c3po.LocalExchanger import LocalExchanger, ShortcutToField, ShortcutToValue
from c3po.CollaborativeExchanger import CollaborativeExchanger
from c3po.mpi.MPIRemoteProcess import MPIRemoteProcess
from c3po.mpi.MPICollectiveProcess import MPICollectiveProcess
from c3po.mpi.MPISender import MPIFieldSender, MPIFileFieldSender, MPIValueSender
from c3po.mpi.MPIRecipient import MPIFieldRecipient, MPIFileFieldRecipient, MPIValueRecipient


class MPIShortcutToData(object):
    """! INTERNAL """

    def __init__(self, containerToSet):
        """! INTERNAL """
        self._something = 0
        self._containerToSet = containerToSet

    def store(self, something):
        """! INTERNAL """
        self._something = something

    def get(self):
        """! INTERNAL """
        return self._something

    def getFieldTemplate(self):
        """! INTERNAL """
        return self._something

    def set(self, something):
        """! INTERNAL """
        self._containerToSet.set(something)


class MPIExchanger(LocalExchanger):
    """! MPIExchanger is the MPI version of c3po.LocalExchanger.LocalExchanger.

    The class takes in charge data exchanges between MPI processes (in the case where each code exposes its data on a single
    MPI process). It manages the MPI exchanges before managing the local exchanges with the mother class.

    Can replace, without impact, an c3po.LocalExchanger.LocalExchanger for a calculation on a single process, if the MPI environment is available.
    """

    def __init__(self, method, fieldsToGet, fieldsToSet, valuesToGet=[], valuesToSet=[], exchangeWithFiles=False):
        """! Build a MPIExchanger object.

        Has the same form as LocalExchanger.__init__() but can also contain MPIRemoteProcess and MPICollectiveProcess
        (and therefore MPICollectiveDataManager) objects.

        MPIExchanger must be built in the same way for all the processes involved in the exchanges. Likewise, the exchange() method
        must be called at the same time by all processes.

        It is assumed that an object is either held by a single process (and of the form MPIRemoteProcess in others), or collective
        (MPICollectiveProcess).

        When there is an MPICollectiveProcess on the get side, all the processes of the communicator of this object must be
        involved in the exchanges.

        See LocalExchanger.__init__() for the documentation of other parameters than exchangeWithFiles.

        when exchangeWithFiles is set to True, exchanged MEDField are written on files and read by the recipient process(es).
        Only basic data (such as the file path) are exchanged via MPI.
        """
        fieldsToGet = self._expandInputList(fieldsToGet)
        fieldsToSet = self._expandInputList(fieldsToSet)
        valuesToGet = self._expandInputList(valuesToGet)
        valuesToSet = self._expandInputList(valuesToSet)

        dividedInputs = self._divideInputsAccordingToPatterns(method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet)

        self._subExchangers = None
        self._dataNeeded = False
        self._isCollective = False

        if len(dividedInputs) > 1:
            self._subExchangers = []
            for divInput in dividedInputs:
                self._subExchangers.append(MPIExchanger(method, divInput[0], divInput[1], divInput[2], divInput[3], exchangeWithFiles))
            self._subExchangers = CollaborativeExchanger(self._subExchangers)
        else:
            LocalExchanger.__init__(self, method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet)

            destinations = []

            # On regarde si on a une communication collective dans les set, auquel cas toutes les communications deviennent collectives
            for i in range(len(fieldsToSet)):
                toSet = fieldsToSet[i][0]
                if isinstance(toSet, MPICollectiveProcess):
                    destinations.append(toSet)
                    self._dataNeeded = True
                    self._isCollective = True
                    break
            if not self._isCollective:
                for i in range(len(valuesToSet)):
                    toSet = valuesToSet[i][0]
                    if isinstance(toSet, MPICollectiveProcess):
                        destinations.append(toSet)
                        self._dataNeeded = True
                        self._isCollective = True
                        break

            # Si on n'a pas de communications collectives, on cherche les destinataires des envois du rank local
            if not self._isCollective:
                for i in range(len(fieldsToSet)):
                    toSet = fieldsToSet[i][0]
                    if isinstance(toSet, MPIRemoteProcess) and toSet not in destinations:
                        destinations.append(toSet)
                    if not isinstance(toSet, MPIRemoteProcess):
                        self._dataNeeded = True
                for i in range(len(valuesToSet)):
                    toSet = valuesToSet[i][0]
                    if isinstance(toSet, MPIRemoteProcess) and toSet not in destinations:
                        destinations.append(toSet)
                    if not isinstance(toSet, MPIRemoteProcess):
                        self._dataNeeded = True

            # On cree enfin les objets Sender et Recipient
            self._mpiExchanges = []
            for i in range(len(fieldsToGet)):
                toGet = fieldsToGet[i][0]
                if not isinstance(toGet, MPICollectiveProcess):
                    self._fieldsToGet[i] = MPIShortcutToData(self._fieldsToGet[i])
                    if not isinstance(toGet, MPIRemoteProcess):
                        fieldSender = MPIFileFieldSender(destinations, ShortcutToField(*fieldsToGet[i]), self._fieldsToGet[i], False) if exchangeWithFiles else MPIFieldSender(destinations, ShortcutToField(*fieldsToGet[i]), self._fieldsToGet[i], False)
                        self._mpiExchanges.append(fieldSender)
                    elif self._dataNeeded:
                        fieldRecipient = MPIFileFieldRecipient(toGet, self._fieldsToGet[i], self._isCollective, False) if exchangeWithFiles else MPIFieldRecipient(toGet, self._fieldsToGet[i], self._isCollective, False)
                        self._mpiExchanges.append(fieldRecipient)
            for i in range(len(fieldsToSet)):
                toSet = fieldsToSet[i][0]
                if not isinstance(toSet, MPICollectiveProcess):
                    self._fieldsToSet[i] = MPIShortcutToData(self._fieldsToSet[i])
                    if not isinstance(toSet, MPIRemoteProcess):
                        fieldSender = MPIFileFieldSender(destinations, ShortcutToField(*fieldsToSet[i]), self._fieldsToSet[i], True) if exchangeWithFiles else MPIFieldSender(destinations, ShortcutToField(*fieldsToSet[i]), self._fieldsToSet[i], True)
                        self._mpiExchanges.append(fieldSender)
                    elif self._dataNeeded:
                        fieldRecipient = MPIFileFieldRecipient(toSet, self._fieldsToSet[i], self._isCollective, True) if exchangeWithFiles else MPIFieldRecipient(toSet, self._fieldsToSet[i], self._isCollective, True)
                        self._mpiExchanges.append(fieldRecipient)
            for i in range(len(valuesToGet)):
                toGet = valuesToGet[i][0]
                if not isinstance(toGet, MPICollectiveProcess):
                    self._valuesToGet[i] = MPIShortcutToData(self._valuesToGet[i])
                    if not isinstance(toGet, MPIRemoteProcess):
                        self._mpiExchanges.append(MPIValueSender(destinations, ShortcutToValue(*valuesToGet[i]), self._valuesToGet[i]))
                    elif self._dataNeeded:
                        self._mpiExchanges.append(MPIValueRecipient(toGet, self._valuesToGet[i], self._isCollective))

    def exchange(self):
        """! Trigger the exchange of data.

        Must be called at the same time by all processes.
        """
        if self._subExchangers is None:
            for exc in self._mpiExchanges:
                exc.exchange()
            if self._dataNeeded:
                LocalExchanger.exchange(self)
        else:
            self._subExchangers.exchange()
