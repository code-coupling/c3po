# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the classes Exchanger and ShortcutToData. ShortcutToData is for internal use only.  """
from __future__ import print_function, division


class ShortcutToData(object):
    """! INTERNAL. It associates a PhysicsDriver or a DataManager with a name to ease further handling. """

    def __init__(self, container, name):
        self.container_ = container
        self.name_ = name

    def getOutputMEDField(self):
        return self.container_.getOutputMEDField(self.name_)

    def getInputMEDFieldTemplate(self):
        return self.container_.getInputMEDFieldTemplate(self.name_)

    def setInputMEDField(self, field):
        self.container_.setInputMEDField(self.name_, field)

    def getValue(self):
        return self.container_.getValue(self.name_)

    def setValue(self, value):
        self.container_.setValue(self.name_, value)


class Exchanger(object):
    """! Exchanger manages data exchanges between PhysicsDriver and / or DataManager.

    Once the object has been constructed, a call to exchange() triggers the exchanges of data. 
    """

    def __init__(self, method, medFieldsToGet, medFieldsToSet, valuesToGet=[], valuesToSet=[]):
        """! Build an Exchanger object.

        @param method a user-defined function (or class with the special method __call__).

        * method must have three input lists:
            * The MED fields obtained by getOutputMEDField() on the medFieldsToGet objects, in the same order.
            * The MED fields obtained by getInputMEDFieldTemplate() on the medFieldsToSet objects, in the same order.
            * The scalars obtained by getValue() on the valuesToGet objects, in the same order.

        * It must have two ouput lists:
            * The MED fields to impose by setInputMEDField() on the medFieldsToSet objects, in the same order.
            * The scalars to impose by setValue() on the valuesToSet objects, in the same order.

        @param medFieldsToGet a list of tuples (object, name). object must be either a PhysicsDriver or a DataManager, and name is the name of the field to get from object.
        @param medFieldsToSet a list of tuples in the same format as medFieldsToGet. name is the name of the field to set in object.
        @param valuesToGet idem medFieldsToGet but for scalars.
        @param valuesToSet idem medFieldsToSet but for scalars.
        """

        self.fieldsToSet_ = [ShortcutToData(field[0], field[1]) for field in medFieldsToSet]
        self.fieldsToGet_ = [ShortcutToData(field[0], field[1]) for field in medFieldsToGet]
        self.valuesToSet_ = [ShortcutToData(field[0], field[1]) for field in valuesToSet]
        self.valuesToGet_ = [ShortcutToData(field[0], field[1]) for field in valuesToGet]
        self.method_ = method

    def exchange(self):
        """! Trigger the exchange of data. """
        fieldsToSet = [ds.getInputMEDFieldTemplate() for ds in self.fieldsToSet_]
        fieldsToGet = [ds.getOutputMEDField() for ds in self.fieldsToGet_]
        valuesToGet = [ds.getValue() for ds in self.valuesToGet_]
        fieldsToSet, valuesToSet = self.method_(fieldsToGet, fieldsToSet, valuesToGet)
        if (len(fieldsToSet) != len(self.fieldsToSet_) or len(valuesToSet) != len(self.valuesToSet_)):
            raise Exception("Exchanger.exchange the method does not have the good number of outputs.")
        for i, f in enumerate(fieldsToSet):
            self.fieldsToSet_[i].setInputMEDField(f)
        for i, v in enumerate(valuesToSet):
            self.valuesToSet_[i].setValue(v)
