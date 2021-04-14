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

from C3PO.Exchanger import Exchanger, ShortcutToData
from C3POMPI.MPIRemoteProcess import MPIRemoteProcess
from C3POMPI.MPICollectiveProcess import MPICollectiveProcess
from C3POMPI.MPISender import MPIFieldSender, MPIFileFieldSender, MPIValueSender
from C3POMPI.MPIRecipient import MPIFieldRecipient, MPIFileFieldRecipient, MPIValueRecipient


class MPIShortcutToData(object):
    """! INTERNAL """

    def __init__(self, containerToSet):
        self.something_ = 0
        self.containerToSet_ = containerToSet

    def store(self, something):
        self.something_ = something

    def getOutputMEDField(self):
        return self.something_

    def getInputMEDFieldTemplate(self):
        return self.something_

    def setInputMEDField(self, field):
        if hasattr(self.containerToSet_, 'setInputMEDField'):
            self.containerToSet_.setInputMEDField(field)

    def getValue(self):
        return self.something_

    def setValue(self, value):
        if hasattr(self.containerToSet_, 'setValue'):
            self.containerToSet_.setValue(value)


class MPIExchanger(Exchanger):
    """! MPIExchanger is the MPI version of C3PO.Exchanger.Exchanger. 

    The class takes in charge data exchanges between MPI processes (in the case where each code exposes its data on a single 
    MPI process). It manages the MPI exchanges before managing the local exchanges with the mother class.

    Can replace, without impact, an C3PO.Exchanger.Exchanger for a calculation on a single process, if the MPI environment is available.
    """

    def __init__(self, method, medFieldsToGet, medFieldsToSet, valuesToGet=[], valuesToSet=[], exchangeWithFiles=False):
        """! Build a MPIExchanger object.

        Has the same form as the one of Exchanger.__init__() but can also contain objects of type MPIRemoteProcess and 
        MPICollectiveProcess (and therefore MPICollectiveDataManager).

        The object must be built in the same way for all the processes involved in the exchanges. Likewise, the exchange() method 
        must be called at the same time by all processes.

        It is assumed that an object is either held by a single process (and of the form MPIRemoteProcess in others), or collective 
        (MPICollectiveProcess).

        When there is an MPICollectiveProcess on the get side, all the processes of the communicator of this object must be 
        involved in the exchanges.

        @param method a user-defined function (or class with the special method __call__).

        * method must have three input lists:
            * The MED fields obtained by getOutputMEDField() on the medFieldsToGet objects, in the same order.
            * The MED fields obtained by getInputMEDFieldTemplate() on the medFieldsToSet objects, in the same order.
            * The scalars obtained by getValue() on the valuesToGet objects, in the same order.

        * It must have two ouput lists:
            * The MED fields to impose by setInputMEDField() on the medFieldsToSet objects, in the same order.
            * The scalars to impose by setValue() on the valuesToSet objects, in the same order.

        @param medFieldsToGet a list of tuples (object, name). object must be either a C3PO.PhysicsDriver.PhysicsDriver or a 
        C3PO.DataManager.DataManager, and name is the name of the field to get from object.
        @param medFieldsToSet a list of tuples in the same format as medFieldsToGet. name is the name of the field to set in object.
        @param valuesToGet idem medFieldsToGet but for scalars.
        @param valuesToSet idem medFieldsToSet but for scalars.
        @param exchangeWithFiles when set to True, exchanged MEDField are written on files and read by the recipient process(es). 
        Only basic data (such as the file path) are exchanged via MPI.
        """
        Exchanger.__init__(self, method, medFieldsToGet, medFieldsToSet, valuesToGet, valuesToSet)

        self.dataNeeded_ = False
        self.isCollective_ = False
        destinations = []

        # On regarde si on a une communication collective dans les set, auquel cas toutes les communications deviennent collectives
        for i in range(len(medFieldsToSet)):
            toSet = medFieldsToSet[i][0]
            if isinstance(toSet, MPICollectiveProcess):
                destinations.append(toSet)
                self.dataNeeded_ = True
                self.isCollective_ = True
                break
        if not self.isCollective_:
            for i in range(len(valuesToSet)):
                toSet = valuesToSet[i][0]
                if isinstance(toSet, MPICollectiveProcess):
                    destinations.append(toSet)
                    self.dataNeeded_ = True
                    self.isCollective_ = True
                    break

        # Si on n'a pas de communications collectives, on cherche les destinataires des envois du rank local
        if not self.isCollective_:
            for i in range(len(medFieldsToSet)):
                toSet = medFieldsToSet[i][0]
                if isinstance(toSet, MPIRemoteProcess) and toSet not in destinations:
                    destinations.append(toSet)
                if not isinstance(toSet, MPIRemoteProcess):
                    self.dataNeeded_ = True
            for i in range(len(valuesToSet)):
                toSet = valuesToSet[i][0]
                if isinstance(toSet, MPIRemoteProcess) and toSet not in destinations:
                    destinations.append(toSet)
                if not isinstance(toSet, MPIRemoteProcess):
                    self.dataNeeded_ = True

        # On cree enfin les objets Sender et Recipient
        self.MPIexchanges_ = []
        for i in range(len(medFieldsToGet)):
            toGet = medFieldsToGet[i][0]
            if not isinstance(toGet, MPICollectiveProcess):
                self.fieldsToGet_[i] = MPIShortcutToData(self.fieldsToGet_[i])
                if not isinstance(toGet, MPIRemoteProcess):
                    fieldSender = MPIFileFieldSender(destinations, ShortcutToData(medFieldsToGet[i][0], medFieldsToGet[i][1]), self.fieldsToGet_[i], False) if exchangeWithFiles else MPIFieldSender(destinations, ShortcutToData(medFieldsToGet[i][0], medFieldsToGet[i][1]), self.fieldsToGet_[i], False)
                    self.MPIexchanges_.append(fieldSender)
                elif self.dataNeeded_:
                    fieldRecipient = MPIFileFieldRecipient(toGet, self.fieldsToGet_[i], self.isCollective_, False) if exchangeWithFiles else MPIFieldRecipient(toGet, self.fieldsToGet_[i], self.isCollective_, False)
                    self.MPIexchanges_.append(fieldRecipient)
        for i in range(len(medFieldsToSet)):
            toSet = medFieldsToSet[i][0]
            if not isinstance(toSet, MPICollectiveProcess):
                self.fieldsToSet_[i] = MPIShortcutToData(self.fieldsToSet_[i])
                if not isinstance(toSet, MPIRemoteProcess):
                    fieldSender = MPIFileFieldSender(destinations, ShortcutToData(medFieldsToSet[i][0], medFieldsToSet[i][1]), self.fieldsToSet_[i], True) if exchangeWithFiles else MPIFieldSender(destinations, ShortcutToData(medFieldsToSet[i][0], medFieldsToSet[i][1]), self.fieldsToSet_[i], True)
                    self.MPIexchanges_.append(fieldSender)
                elif self.dataNeeded_:
                    fieldRecipient = MPIFileFieldRecipient(toSet, self.fieldsToSet_[i], self.isCollective_, True) if exchangeWithFiles else MPIFieldRecipient(toSet, self.fieldsToSet_[i], self.isCollective_, True)
                    self.MPIexchanges_.append(fieldRecipient)
        for i in range(len(valuesToGet)):
            toGet = valuesToGet[i][0]
            if not isinstance(toGet, MPICollectiveProcess):
                self.valuesToGet_[i] = MPIShortcutToData(self.valuesToGet_[i])
                if not isinstance(toGet, MPIRemoteProcess):
                    self.MPIexchanges_.append(MPIValueSender(destinations, ShortcutToData(valuesToGet[i][0], valuesToGet[i][1]), self.valuesToGet_[i]))
                elif self.dataNeeded_:
                    self.MPIexchanges_.append(MPIValueRecipient(toGet, self.valuesToGet_[i], self.isCollective_))

    def exchange(self):
        """! Trigger the exchange of data. 

        Must be called at the same time by all processes.
        """
        for ex in self.MPIexchanges_:
            ex.exchange()
        if self.dataNeeded_:
            Exchanger.exchange(self)
