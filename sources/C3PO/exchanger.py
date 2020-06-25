# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the classes exchanger and shortcutToData. shortcutToData is for internal use only.  """
from __future__ import print_function, division


class shortcutToData(object):
    # This internal class associate a physicsDriver or a dataManager with a name to ease further handling.

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


class exchanger(object):
    """ Manages data exchanges between physicsDriver and / or dataManager.

    Once the object has been constructed, a call to exchange() triggers the exchanges of data. 
    """

    def __init__(self, method, MEDFieldsToGet, MEDFieldsToSet, ValuesToGet=[], ValuesToSet=[]):
        """ Builds an exchanger object.

        :param method: a user-defined function (or class with the special method __call__). 
            It must have three input lists:
                - The MED fields obtained by getOutputMEDField(name) on the MEDFieldsToGet objects, in the same order.
                - The MED fields obtained by getInputMEDFieldTemplate(name) on the MEDFieldsToSet objects, in the same order.
                - The scalars obtained by getValue(name) on the ValuesToGet objects, in the same order.
            It must have two ouput lists:
                - The MED fields to impose by setInputMEDField(name) on the MEDFieldsToSet objects, in the same order.
                - The scalars to impose by setValue(name) on the ValuesToSet objects, in the same order.
        :param MEDFieldsToGet: a list of tuples (object, name). object here must be either a physicsDriver or a dataManager, and name is a string. This indicates the origin of the fields that method will have to handle.
        :param MEDFieldsToSet: a list of tuples in the same format as MEDFieldsToGet. This indicates the fields to impose by method.
        :param ValuesToGet: idem MEDFieldsToGet but for scalars.
        :param ValuesToSet: idem MEDFieldsToSet but for scalars.
        """

        self.fieldsToSet_ = [shortcutToData(field[0], field[1]) for field in MEDFieldsToSet]
        self.fieldsToGet_ = [shortcutToData(field[0], field[1]) for field in MEDFieldsToGet]
        self.valuesToSet_ = [shortcutToData(field[0], field[1]) for field in ValuesToSet]
        self.valuesToGet_ = [shortcutToData(field[0], field[1]) for field in ValuesToGet]
        self.method_ = method

    def exchange(self):
        """ Triggers the exchange of data. """
        fieldsToSet = [ds.getInputMEDFieldTemplate() for ds in self.fieldsToSet_]
        fieldsToGet = [ds.getOutputMEDField() for ds in self.fieldsToGet_]
        valuesToGet = [ds.getValue() for ds in self.valuesToGet_]
        fieldsToSet, valuesToSet = self.method_(fieldsToGet, fieldsToSet, valuesToGet)
        if (len(fieldsToSet) != len(self.fieldsToSet_) or len(valuesToSet) != len(self.valuesToSet_)):
            raise Exception("exchanger.exchange the method does not have the good number of outputs.")
        for i, f in enumerate(fieldsToSet):
            self.fieldsToSet_[i].setInputMEDField(f)
        for i, v in enumerate(valuesToSet):
            self.valuesToSet_[i].setValue(v)
