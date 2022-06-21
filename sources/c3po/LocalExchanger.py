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
from c3po.CollaborativeObject import CollaborativeObject


class ShortcutToField(object):
    """! INTERNAL. """

    def __init__(self, container, name, type_=None):
        """! INTERNAL."""
        self._container = container
        self._name = name
        self._type = type_
        self._setMethod = None
        self._getMethod = None
        self._getTemplateMethod = None
        self._updateMethod = None
        self._update = True
        self._fieldToUpdate = None
        self._fieldTemplate = None

    def initialize(self):
        """! INTERNAL."""
        if self._type is None:
            try:
                self._type = self._container.getFieldType(self._name)
            except:
                self._type = 'Double'
        if self._type == 'Double':
            self._setMethod = self._container.setInputMEDDoubleField
            self._getMethod = self._container.getOutputMEDDoubleField
            self._getTemplateMethod = self._container.getInputMEDDoubleFieldTemplate
            self._updateMethod = self._container.updateOutputMEDDoubleField
        elif self._type == 'Int':
            self._setMethod = self._container.setInputMEDIntField
            self._getMethod = self._container.getOutputMEDIntField
            self._getTemplateMethod = self._container.getInputMEDIntFieldTemplate
            self._updateMethod = self._container.updateOutputMEDIntField
        elif self._type == 'String':
            self._setMethod = self._container.setInputMEDStringField
            self._getMethod = self._container.getOutputMEDStringField
            self._getTemplateMethod = self._container.getInputMEDStringFieldTemplate
            self._updateMethod = self._container.updateOutputMEDStringField
        else:
            raise Exception("ShortcutToField.initialize unknown field type.")

    def get(self):
        """! INTERNAL."""
        if self._getMethod is None:
            self.initialize()
        if self._fieldToUpdate is not None and self._update:
            try:
                self._updateMethod(self._name, self._fieldToUpdate)
            except:
                self._update = False
                self._fieldToUpdate = self._getMethod(self._name)
        else:
            self._fieldToUpdate = self._getMethod(self._name)
        return self._fieldToUpdate

    def getFieldTemplate(self):
        """! INTERNAL."""
        if self._getTemplateMethod is None:
            self.initialize()
        if self._fieldTemplate is None:
            self._fieldTemplate = self._getTemplateMethod(self._name)
        return self._fieldTemplate

    def set(self, field):
        """! INTERNAL."""
        if self._setMethod is None:
            self.initialize()
        self._setMethod(self._name, field)


class ShortcutToValue(object):
    """! INTERNAL. """

    def __init__(self, container, name, type_=None):
        """! INTERNAL."""
        self._container = container
        self._name = name
        self._type = type_
        self._setMethod = None
        self._getMethod = None

    def initialize(self):
        """! INTERNAL."""
        if self._type is None:
            try:
                self._type = self._container.getValueType(self._name)
            except:
                self._type = 'Double'
        if self._type == 'Double':
            self._setMethod = self._container.setInputDoubleValue
            self._getMethod = self._container.getOutputDoubleValue
        elif self._type == 'Int':
            self._setMethod = self._container.setInputIntValue
            self._getMethod = self._container.getOutputIntValue
        elif self._type == 'String':
            self._setMethod = self._container.setInputStringValue
            self._getMethod = self._container.getOutputStringValue
        else:
            raise Exception("ShortcutToValue.initialize unknown value type.")

    def get(self):
        """! INTERNAL."""
        if self._getMethod is None:
            self.initialize()
        return self._getMethod(self._name)

    def set(self, value):
        """! INTERNAL."""
        if self._setMethod is None:
            self.initialize()
        self._setMethod(self._name, value)


class LocalExchanger(Exchanger):
    """! LocalExchanger is an Exchanger for local data exchanges between DataAccessor objects (PhysicsDriver or LocalDataManager).

    Once the object has been constructed, a call to exchange() triggers the exchanges of data.
    """

    def __init__(self, method, fieldsToGet, fieldsToSet, valuesToGet=[], valuesToSet=[]):
        """! Build an LocalExchanger object.

        @param method a user-defined function (or class with the special method __call__).

        * method must have three input lists:
            * The MED fields obtained by (get/update)OutputMED(Double/Int/String)Field() from the fieldsToGet objects, in the same order.
            * The MED fields obtained by getInputMED(Double/Int/String)FieldTemplate() from the fieldsToSet objects, in the same order.
            * The scalars obtained by (get/update)Output(Double/Int/String)Value() from the valuesToGet objects, in the same order.

        * It must have two ouput lists:
            * The MED fields to impose by setInputMED(Double/Int/String)Field() to the fieldsToSet objects, in the same order.
            * The scalars to impose by setIntput(Double/Int/String)Value() to the valuesToSet objects, in the same order.

        @param fieldsToGet a list of tuples (object, name, type).
            * object must be either a DataAccessor (PhysicsDriver or a LocalDataManager), or a CollaborativeObject with DataAccessor objects.
            * name is the name of the field to get from object.
            * type is either 'Double', 'Int' or 'String' (see c3po.DataAccessor.DataAccessor.ValueType).
            type can be omitted: in this case, LocalExchanger uses getFieldType() to get the type. If getFieldType() is not
            implemented, 'Double' is tried.
        @param fieldsToSet a list of tuples in the same format as fieldsToGet. name is the name of the field to set in object.
        @param valuesToGet idem fieldsToGet but for scalars.
        @param valuesToSet idem fieldsToSet but for scalars.
        """
        fieldsToGet = self._expandInputList(fieldsToGet)
        fieldsToSet = self._expandInputList(fieldsToSet)
        valuesToGet = self._expandInputList(valuesToGet)
        valuesToSet = self._expandInputList(valuesToSet)

        self._divideInputsAccordingToPatterns(method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet)

        self._fieldsToSet = [ShortcutToField(*tupleData) for tupleData in fieldsToSet]
        self._fieldsToGet = [ShortcutToField(*tupleData) for tupleData in fieldsToGet]
        self._valuesToSet = [ShortcutToValue(*tupleData) for tupleData in valuesToSet]
        self._valuesToGet = [ShortcutToValue(*tupleData) for tupleData in valuesToGet]

        self._method = method

    def exchange(self):
        """! Trigger the exchange of data. """
        fieldsToSet = [ds.getFieldTemplate() for ds in self._fieldsToSet]
        fieldsToGet = [ds.get() for ds in self._fieldsToGet]
        valuesToGet = [ds.get() for ds in self._valuesToGet]
        fieldsToSet, valuesToSet = self._method(fieldsToGet, fieldsToSet, valuesToGet)
        if (len(fieldsToSet) != len(self._fieldsToSet) or len(valuesToSet) != len(self._valuesToSet)):
            raise Exception("LocalExchanger.exchange the method does not have the good number of outputs.")
        for i, field in enumerate(fieldsToSet):
            self._fieldsToSet[i].set(field)
        for i, value in enumerate(valuesToSet):
            self._valuesToSet[i].set(value)

    @staticmethod
    def _expandInputList(inputList):
        """! INTERNAL. """
        newList = []
        for tupleData in inputList:
            if isinstance(tupleData[0], CollaborativeObject):
                tupleType = None if len(tupleData) < 3 else tupleData[2]
                newList += [(elem, tupleData[1], tupleType) for elem in tupleData[0].getElementsRecursively()]
            else:
                newList.append(tupleData)
        return newList

    @staticmethod
    def _divideInputsAccordingToPatterns(method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet):
        """! INTERNAL. """
        elements = [fieldsToGet, fieldsToSet, valuesToGet, valuesToSet]
        index = [0, 0, 0, 0]

        try:
            patterns = method.getPatterns()
        except:
            return [elements]

        divisions = [0]*4
        resu = []

        for pattern in patterns:
            for position in range(4):
                divisions[position] = len(elements[position]) - index[position] // pattern[position] if pattern[position] > 0 else -1
            minDivision = -1
            for position in range(4):
                if divisions[position] >= 0 and (divisions[position] < minDivision or minDivision < 0):
                    minDivision = divisions[position]
            subLists = [[], [], [], []]
            if minDivision <= 0:
                for position in range(4):
                    if pattern[position] < 0:
                        subLists[position] = elements[position][index[position]:]
                        index[position] = len(elements[position])
                if subLists != [[], [], [], []]:
                    resu.append(subLists)
            else:
                for _ in range(minDivision):
                    for position in range(4):
                        if pattern[position] < 0:
                            subLists[position] = elements[position][index[position]:]
                        else:
                            for _ in range(pattern[position]):
                                subLists[position].append(elements[position][index[position]])
                                index[position] += 1
                    resu.append(subLists)
                    subLists = [[], [], [], []]
                for position in range(4):
                    if pattern[position] < 0:
                        index[position] = len(elements[position])

        if index != [len(elem) for elem in elements]:
            msg = "LocalExchanger._divideInputsAccordingToPatterns the method pattern does not fit the number of provided elements."
            msg += " The method pattern is {} but we found {} elements.".format(patterns, [len(elem) for elem in elements])
            raise Exception(msg)

        return resu
