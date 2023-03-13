# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the classes MPIExchanger and MPIShortcutToData. MPIShortcutToData is for internal use only. """
from __future__ import print_function, division
from mpi4py import MPI as mpi

from c3po.LocalExchanger import LocalExchanger, ShortcutToField, ShortcutToValue
from c3po.CollaborativeExchanger import CollaborativeExchanger
from c3po.mpi.MPIRemote import MPIRemote
from c3po.mpi.MPIRemoteProcess import MPIRemoteProcess
from c3po.mpi.MPIRemoteProcesses import MPIRemoteProcesses
from c3po.mpi.MPICollectiveProcess import MPICollectiveProcess
from c3po.mpi.MPISender import MPIFieldSender, MPIFileFieldSender, MPIValueSender
from c3po.mpi.MPIRecipient import MPIFieldRecipient, MPIFileFieldRecipient, MPIValueRecipient
from c3po.mpi.mpiExchangeMethods.MPIExchangeMethod import MPIExchangeMethod


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

    MPIExchanger can replace, without impact, a c3po.LocalExchanger.LocalExchanger for a calculation on a single process, if
    the MPI environment is available.
    """

    def __init__(self, method, fieldsToGet, fieldsToSet, valuesToGet=[], valuesToSet=[], exchangeWithFiles=False, mpiComm=None):    # pylint: disable=super-init-not-called
        """! Build a MPIExchanger object.

        The constructor has the same form than LocalExchanger.__init__() with two additional optionnal parameters:
        exchangeWithFiles and mpiComm.

        MPIExchanger must be built in the same way for all the processes involved in the exchanges. Likewise, the exchange()
        method must be called at the same time by all processes.

        The first parameter, method, can be either a c3po.mpi.mpiExchangeMethods.MPIExchangeMethod.MPIExchangeMethod or not:

            - In the first case, the exchange method has to deal with data exchanges between MPI processes (in addition to
            local data processing such as unit change). MPIRemoteProcess and MPIRemoteProcesses are accepted, but not
            MPICollectiveProcess.

            - In the second case, these exchanges between MPI processes are done by MPIExchanger. The class manages MPI
            exchanges and then uses the local exchange method with the mother class.

            In this case, it is assumed that an object is either held by a single process (and is replace by a
            MPIRemoteProcess in others), or collectively (MPICollectiveProcess). When there is an MPICollectiveProcess on
            the set side, all the processes of the communicator of this object must be involved in the exchanges.
            MPIRemoteProcesses are not accepted.

        @param exchangeWithFiles (bool) (Only available with an exchange method that is not of type
            c3po.mpi.mpiExchangeMethods.MPIExchangeMethod.MPIExchangeMethod.) When exchangeWithFiles is set to True, exchanged
            MEDField are written on files and read by the recipient process(es). Only basic data (such as the file path) are
            exchanged via MPI.
        @param mpiComm (Only available with an exchange method that is of type
            c3po.mpi.mpiExchangeMethods.MPIExchangeMethod.MPIExchangeMethod.) If not None, it indicated to the exchange method
            to use this communicator for data exchange. Otherwise, all MPIRemoteProcess and MPIRemoteProcesses must use the same
            communicator, which is then used by the exchange method.

        See LocalExchanger.__init__() for the documentation of the other parameters.
        """

        self._subExchangers = None
        self._dataNeeded = True
        self._mpiExchanges = []

        fieldsToGet = self._expandInputList(fieldsToGet)
        fieldsToSet = self._expandInputList(fieldsToSet)
        valuesToGet = self._expandInputList(valuesToGet)
        valuesToSet = self._expandInputList(valuesToSet)

        if isinstance(method, MPIExchangeMethod):
            if exchangeWithFiles:
                raise ValueError("MPIExchanger.__init__: exchangeWithFiles option cannot be activated when using an exchange method of type MPIExchangeMethod.")
            self._initWithMPIExchangeMethod(method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet, mpiComm)
        else:
            if mpiComm is not None:
                raise ValueError("MPIExchanger.__init__: mpiComm cannot be specified when using an exchange method that is not of type MPIExchangeMethod.")
            self._initWithLocalExchangeMethod(method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet, exchangeWithFiles)

    def _initWithLocalExchangeMethod(self, method, fieldsToGet, fieldsToSet, valuesToGet=[], valuesToSet=[], exchangeWithFiles=False):
        """! INTERNAL """
        dividedInputs = self._divideInputsAccordingToPatterns(method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet)

        self._dataNeeded = False
        self._mpiExchanges = []

        if len(dividedInputs) > 1:
            self._subExchangers = []
            for divInput in dividedInputs:
                self._subExchangers.append(MPIExchanger(method, divInput[0], divInput[1], divInput[2], divInput[3], exchangeWithFiles))
            self._subExchangers = CollaborativeExchanger(self._subExchangers)
        else:
            LocalExchanger.__init__(self, method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet)

            destinations = []
            isCollective = False
            invalidDestination = False

            # On regarde si on a une communication collective dans les set, auquel cas toutes les communications deviennent collectives
            for i in range(len(fieldsToSet)):
                toSet = fieldsToSet[i][0]
                if isinstance(toSet, MPICollectiveProcess):
                    destinations.append(toSet)
                    self._dataNeeded = True
                    isCollective = True
                    break
            if not isCollective:
                for i in range(len(valuesToSet)):
                    toSet = valuesToSet[i][0]
                    if isinstance(toSet, MPICollectiveProcess):
                        destinations.append(toSet)
                        self._dataNeeded = True
                        isCollective = True
                        break

            # Si on n'a pas de communications collectives, on cherche les destinataires des envois du rank local
            if not isCollective:
                for i in range(len(fieldsToSet)):
                    toSet = fieldsToSet[i][0]
                    if isinstance(toSet, MPIRemoteProcess) and toSet not in destinations:
                        destinations.append(toSet)
                    elif isinstance(toSet, MPIRemoteProcesses):
                        invalidDestination = True
                    if not isinstance(toSet, MPIRemote):
                        self._dataNeeded = True
                for i in range(len(valuesToSet)):
                    toSet = valuesToSet[i][0]
                    if isinstance(toSet, MPIRemoteProcess) and toSet not in destinations:
                        destinations.append(toSet)
                    elif isinstance(toSet, MPIRemoteProcesses):
                        invalidDestination = True
                    if not isinstance(toSet, MPIRemote):
                        self._dataNeeded = True

            # On cree enfin les objets Sender et Recipient
            for i in range(len(fieldsToGet)):
                toGet = fieldsToGet[i][0]
                if not isinstance(toGet, MPICollectiveProcess):
                    self._fieldsToGet[i] = MPIShortcutToData(self._fieldsToGet[i])
                    if not isinstance(toGet, MPIRemote):
                        if invalidDestination:
                            raise Exception("MPIExchanger.__init__: MPIRemoteProcesses is not allowed with an exchange method that is not of type MPIExchangeMethod.")
                        fieldSender = MPIFileFieldSender(destinations, ShortcutToField(*fieldsToGet[i]), self._fieldsToGet[i], False) if exchangeWithFiles else MPIFieldSender(destinations, ShortcutToField(*fieldsToGet[i]), self._fieldsToGet[i], False)
                        self._mpiExchanges.append(fieldSender)
                    elif self._dataNeeded:
                        if isinstance(toGet, MPIRemoteProcesses):
                            raise Exception("MPIExchanger.__init__: MPIRemoteProcesses is not allowed with an exchange method that is not of type MPIExchangeMethod.")
                        fieldRecipient = MPIFileFieldRecipient(toGet, self._fieldsToGet[i], isCollective, False) if exchangeWithFiles else MPIFieldRecipient(toGet, self._fieldsToGet[i], isCollective, False)
                        self._mpiExchanges.append(fieldRecipient)
            for i in range(len(fieldsToSet)):
                toSet = fieldsToSet[i][0]
                if not isinstance(toSet, MPICollectiveProcess):
                    self._fieldsToSet[i] = MPIShortcutToData(self._fieldsToSet[i])
                    if not isinstance(toSet, MPIRemote):
                        if invalidDestination:
                            raise Exception("MPIExchanger.__init__: MPIRemoteProcesses is not allowed with an exchange method that is not of type MPIExchangeMethod.")
                        fieldSender = MPIFileFieldSender(destinations, ShortcutToField(*fieldsToSet[i]), self._fieldsToSet[i], True) if exchangeWithFiles else MPIFieldSender(destinations, ShortcutToField(*fieldsToSet[i]), self._fieldsToSet[i], True)
                        self._mpiExchanges.append(fieldSender)
                    elif self._dataNeeded:
                        if isinstance(toGet, MPIRemoteProcesses):
                            raise Exception("MPIExchanger.__init__: MPIRemoteProcesses is not allowed with an exchange method that is not of type MPIExchangeMethod.")
                        fieldRecipient = MPIFileFieldRecipient(toSet, self._fieldsToSet[i], isCollective, True) if exchangeWithFiles else MPIFieldRecipient(toSet, self._fieldsToSet[i], isCollective, True)
                        self._mpiExchanges.append(fieldRecipient)
            for i in range(len(valuesToGet)):
                toGet = valuesToGet[i][0]
                if not isinstance(toGet, MPICollectiveProcess):
                    self._valuesToGet[i] = MPIShortcutToData(self._valuesToGet[i])
                    if not isinstance(toGet, MPIRemote):
                        if invalidDestination:
                            raise Exception("MPIExchanger.__init__: MPIRemoteProcesses is not allowed with an exchange method that is not of type MPIExchangeMethod.")
                        self._mpiExchanges.append(MPIValueSender(destinations, ShortcutToValue(*valuesToGet[i]), self._valuesToGet[i]))
                    elif self._dataNeeded:
                        if isinstance(toGet, MPIRemoteProcesses):
                            raise Exception("MPIExchanger.__init__: MPIRemoteProcesses is not allowed with an exchange method that is not of type MPIExchangeMethod.")
                        self._mpiExchanges.append(MPIValueRecipient(toGet, self._valuesToGet[i], isCollective))

    def _initWithMPIExchangeMethod(self, method, fieldsToGet, fieldsToSet, valuesToGet=[], valuesToSet=[], mpiComm=None):
        """! INTERNAL """
        ranksToGet = []
        ranksToSet = []
        exchangerMPIComm = mpiComm

        if mpiComm is None:
            for obj in [data[0] for arg in [fieldsToGet, fieldsToSet, valuesToGet, valuesToSet] for data in arg]:
                if isinstance(obj, MPIRemote):
                    if obj.mpiComm == mpi.COMM_NULL:
                        raise Exception("MPIExchanger.__init__: All distant processes must be part of the communicator (mpi.COMM_NULL found).")
                    if exchangerMPIComm is not None and exchangerMPIComm != obj.mpiComm:
                        raise Exception("MPIExchanger.__init__: All distant processes must used the same MPI communicator.")
                    exchangerMPIComm = obj.mpiComm
        if exchangerMPIComm is None:
            raise Exception("MPIExchanger.__init__: No MPI communicator found.")

        def _readRanks(dataAccessor):
            """! INTERNAL """
            if isinstance(dataAccessor, MPIRemoteProcess):
                return mpi.Group.Translate_ranks(dataAccessor.mpiComm.Get_group(), [dataAccessor.rank], exchangerMPIComm.Get_group())
            if isinstance(dataAccessor, MPIRemoteProcesses):
                group = dataAccessor.mpiComm.Get_group().Incl(dataAccessor.ranks)
            else:
                try:
                    group = dataAccessor.getMPIComm().Get_group()
                except NotImplementedError:
                    return [exchangerMPIComm.Get_rank()]
            intersecGroup = mpi.Group.Intersection(group, exchangerMPIComm.Get_group())
            return mpi.Group.Translate_ranks(intersecGroup, list(range(intersecGroup.Get_size())), exchangerMPIComm.Get_group())

        def _initObjectList(initialList, ranks):
            """! INTERNAL """
            newList = []
            for elem in initialList:
                newRanks = _readRanks(elem[0])
                ranks += list(set(newRanks) - set(ranks))
                if not isinstance(elem[0], MPIRemote):
                    newList.append(elem)
            return newList

        localFieldsToGet = _initObjectList(fieldsToGet, ranksToGet)
        localFieldsToSet = _initObjectList(fieldsToSet, ranksToSet)
        localValuesToGet = _initObjectList(valuesToGet, ranksToGet)
        localValuesToSet = _initObjectList(valuesToSet, ranksToSet)

        LocalExchanger.__init__(self, method, localFieldsToGet, localFieldsToSet, localValuesToGet, localValuesToSet)

        method.setRanks(ranksToGet, ranksToSet, exchangerMPIComm)

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
