# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the classes LocalExchanger and ShortcutToData. ShortcutToData is for internal use only.  """
from __future__ import print_function, division

from c3po.Exchanger import Exchanger


class ShortcutToData(object):
    """! INTERNAL. It associates a DataAccessor with a name to ease further handling. """

    def __init__(self, container, name):
        """! INTERNAL."""
        self._container = container
        self._name = name

    def getOutputMEDField(self):
        """! INTERNAL."""
        return self._container.getOutputMEDField(self._name)

    def getInputMEDFieldTemplate(self):
        """! INTERNAL."""
        return self._container.getInputMEDFieldTemplate(self._name)

    def setInputMEDField(self, field):
        """! INTERNAL."""
        self._container.setInputMEDField(self._name, field)

    def getValue(self):
        """! INTERNAL."""
        return self._container.getValue(self._name)

    def setValue(self, value):
        """! INTERNAL."""
        self._container.setValue(self._name, value)


class LocalExchanger(Exchanger):
    """! LocalExchanger is an Exchanger for local data exchanges between DataAccessor objects (PhysicsDriver or LocalDataManager).

    Once the object has been constructed, a call to exchange() triggers the exchanges of data.
    """

    def __init__(self, method, medFieldsToGet, medFieldsToSet, valuesToGet=[], valuesToSet=[]):
        """! Build an LocalExchanger object.

        @param method a user-defined function (or class with the special method __call__).

        * method must have three input lists:
            * The MED fields obtained by getOutputMEDField() on the medFieldsToGet objects, in the same order.
            * The MED fields obtained by getInputMEDFieldTemplate() on the medFieldsToSet objects, in the same order.
            * The scalars obtained by getValue() on the valuesToGet objects, in the same order.

        * It must have two ouput lists:
            * The MED fields to impose by setInputMEDField() on the medFieldsToSet objects, in the same order.
            * The scalars to impose by setValue() on the valuesToSet objects, in the same order.

        @param medFieldsToGet a list of tuples (object, name). object must be a DataAccessor (PhysicsDriver or a LocalDataManager),
            and name is the name of the field to get from object.
        @param medFieldsToSet a list of tuples in the same format as medFieldsToGet. name is the name of the field to set in object.
        @param valuesToGet idem medFieldsToGet but for scalars.
        @param valuesToSet idem medFieldsToSet but for scalars.
        """
        self._fieldsToSet = [ShortcutToData(field[0], field[1]) for field in medFieldsToSet]
        self._fieldsToGet = [ShortcutToData(field[0], field[1]) for field in medFieldsToGet]
        self._valuesToSet = [ShortcutToData(field[0], field[1]) for field in valuesToSet]
        self._valuesToGet = [ShortcutToData(field[0], field[1]) for field in valuesToGet]
        self._method = method

    def exchange(self):
        """! Trigger the exchange of data. """
        fieldsToSet = [ds.getInputMEDFieldTemplate() for ds in self._fieldsToSet]
        fieldsToGet = [ds.getOutputMEDField() for ds in self._fieldsToGet]
        valuesToGet = [ds.getValue() for ds in self._valuesToGet]
        fieldsToSet, valuesToSet = self._method(fieldsToGet, fieldsToSet, valuesToGet)
        if (len(fieldsToSet) != len(self._fieldsToSet) or len(valuesToSet) != len(self._valuesToSet)):
            raise Exception("LocalExchanger.exchange the method does not have the good number of outputs.")
        for i, field in enumerate(fieldsToSet):
            self._fieldsToSet[i].setInputMEDField(field)
        for i, value in enumerate(valuesToSet):
            self._valuesToSet[i].setValue(value)
