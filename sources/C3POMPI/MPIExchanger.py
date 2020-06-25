# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the classes MPIExchanger and MPIShortcutToData. MPIShortcutToData is for internal use only. """
from __future__ import print_function, division

from C3PO.exchanger import exchanger, shortcutToData
from MPIRemoteProcess import MPIRemoteProcess
from MPICollectiveProcess import MPICollectiveProcess
from MPISender import MPIFieldSender, MPIValueSender
from MPIRecipient import MPIFieldRecipient, MPIValueRecipient


class MPIShortcutToData(object):
    """ For internal use only. """

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


class MPIExchanger(exchanger):
    """ This is the MPI version of exchanger. The class organizes data exchanges between processes.

    Inherits from exchanger. It manages the MPI exchanges before managing the local exchanges with the mother class.

    Can replace, without impact, an exchanger of a single processor calculation, if the mpi environment is available.
    """

    def __init__(self, method, MEDFieldsToGet, MEDFieldsToSet, ValuesToGet=[], ValuesToSet=[]):
        """ Builds a MPIExchanger object.

        This constructor has the same form as the one of exchanger but can also contain objects of type MPIRemoteProcess and MPICollectiveProcess (and therefore MPICollectiveDataManager).

        The object must be built in the same way for all the processes involved in the exchanges. Likewise, the exchange() method must be called at the same time by all processes.

        It is assumed that an object is either held by a single process (and of the form MPIRemoteProcess in others), or collective (MPICollectiveProcess).

        When there is an MPICollectiveProcess on the get side, all the processes of the communicator of this object must be involved in the exchanges.
        """
        exchanger.__init__(self, method, MEDFieldsToGet, MEDFieldsToSet, ValuesToGet, ValuesToSet)

        self.dataNeeded_ = False
        self.isCollective_ = False
        destinations = []

        # On regarde si on a une communication collective dans les set, auquel cas toutes les communications deviennent collectives
        for i in range(len(MEDFieldsToSet)):
            toSet = MEDFieldsToSet[i][0]
            if isinstance(toSet, MPICollectiveProcess):
                destinations.append(toSet)
                self.dataNeeded_ = True
                self.isCollective_ = True
                break
        if not self.isCollective_:
            for i in range(len(ValuesToSet)):
                toSet = ValuesToSet[i][0]
                if isinstance(toSet, MPICollectiveProcess):
                    destinations.append(toSet)
                    self.dataNeeded_ = True
                    self.isCollective_ = True
                    break

        # Si on n'a pas de communications collectives, on cherche les destinataires des envois du rank local
        if not self.isCollective_:
            for i in range(len(MEDFieldsToSet)):
                toSet = MEDFieldsToSet[i][0]
                if isinstance(toSet, MPIRemoteProcess) and toSet not in destinations:
                    destinations.append(toSet)
                if not isinstance(toSet, MPIRemoteProcess):
                    self.dataNeeded_ = True
            for i in range(len(ValuesToSet)):
                toSet = ValuesToSet[i][0]
                if isinstance(toSet, MPIRemoteProcess) and toSet not in destinations:
                    destinations.append(toSet)
                if not isinstance(toSet, MPIRemoteProcess):
                    self.dataNeeded_ = True

        # On cree enfin les objets Sender et Recipient
        self.MPIexchanges_ = []
        for i in range(len(MEDFieldsToGet)):
            toGet = MEDFieldsToGet[i][0]
            if not isinstance(toGet, MPICollectiveProcess):
                self.fieldsToGet_[i] = MPIShortcutToData(self.fieldsToGet_[i])
                if not isinstance(toGet, MPIRemoteProcess):
                    self.MPIexchanges_.append(MPIFieldSender(destinations, shortcutToData(MEDFieldsToGet[i][0], MEDFieldsToGet[i][1]), self.fieldsToGet_[i], False))
                elif self.dataNeeded_:
                    self.MPIexchanges_.append(MPIFieldRecipient(toGet, self.fieldsToGet_[i], self.isCollective_))
        for i in range(len(MEDFieldsToSet)):
            toSet = MEDFieldsToSet[i][0]
            if not isinstance(toSet, MPICollectiveProcess):
                self.fieldsToSet_[i] = MPIShortcutToData(self.fieldsToSet_[i])
                if not isinstance(toSet, MPIRemoteProcess):
                    self.MPIexchanges_.append(MPIFieldSender(destinations, shortcutToData(MEDFieldsToSet[i][0], MEDFieldsToSet[i][1]), self.fieldsToSet_[i], True))
                elif self.dataNeeded_:
                    self.MPIexchanges_.append(MPIFieldRecipient(toSet, self.fieldsToSet_[i], self.isCollective_))
        for i in range(len(ValuesToGet)):
            toGet = ValuesToGet[i][0]
            if not isinstance(toGet, MPICollectiveProcess):
                self.valuesToGet_[i] = MPIShortcutToData(self.valuesToGet_[i])
                if not isinstance(toGet, MPIRemoteProcess):
                    self.MPIexchanges_.append(MPIValueSender(destinations, shortcutToData(ValuesToGet[i][0], ValuesToGet[i][1]), self.valuesToGet_[i]))
                elif self.dataNeeded_:
                    self.MPIexchanges_.append(MPIValueRecipient(toGet, self.valuesToGet_[i], self.isCollective_))

    def exchange(self):
        """ Triggers the exchange of data. 

        Must be called at the same time by all processes.
        """
        for ex in self.MPIexchanges_:
            ex.exchange()
        if self.dataNeeded_:
            exchanger.exchange(self)
