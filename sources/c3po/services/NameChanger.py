# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class wrapper nameChanger. """
from __future__ import print_function, division
from types import FunctionType

from c3po.services.PhysicsDriverWrapper import PhysicsDriverWrapper
from c3po.services.Printer import warning


class NameChanger(PhysicsDriverWrapper):
    """! NameChanger wraps a PhysicsDriver object and changes the names of the values and fields quantities that can be get/set through ICoCo methods.

    This allows to improve the genericity of coupling scripts by using generic variable names without modifying the PhysicsDriver "by hand".
    """

    def __init__(self, physics, nameMappingValue={}, nameMappingField={}, wildcard=None, exclusive=False):
        """! Build a NameChanger object.

        @param physics the PhysicsDriver to wrap.
        @param nameMappingValue a Python dictionary with the mapping from the new names (the generic ones) to the old ones (the names used by the code) for values.
            Names that are not in this mapping dictionary can still be used if exclusive=False.
        @param nameMappingField a Python dictionary with the mapping from the new names (the generic ones) to the old ones (the names used by the code) for fields.
            Names that are not in this mapping dictionary can still be used if exclusive=False.
        @param wildcard a Python string. If both new and old names terminate by this wildcard (a wildcard in the middle of the names is not taken into account),
            nameChanger will substitute only the preceding part. For example : c3po.NameChanger(nameMappingValue={"newName*" : "oldName*"}, wildcard="*") will substitute
            newNameA05 in oldNameA05 and newNameB9 in oldNameB9.
        @param exclusive set True to limit available names to the ones provided in the mapping.

        @note nameMappingValue and nameMappingField are copied.
        """

        PhysicsDriverWrapper.__init__(self, physics)
        self._nameMapping = [{}, {}, {}, {}]
        self._invertNameMapping = [{}, {}, {}, {}]
        self._wildcard = wildcard
        self._exclusive = exclusive
        self._valueO = 0
        self._valueI = 1
        self._fieldO = 2
        self._fieldI = 3
        self._updateNameMapping(nameMappingValue, (0, 1))
        self._updateNameMapping(nameMappingField, (2, 3))

    def _updateNameMapping(self, nameMapping, variableTypes):
        for variableType in variableTypes:
            self._nameMapping[variableType].update(nameMapping)
            for key, val in self._nameMapping[variableType].items():
                if val not in self._invertNameMapping[variableType]:
                    self._invertNameMapping[variableType][val] = [key]
                else:
                    self._invertNameMapping[variableType][val].append(key)

    def updateNameMappingValue(self, nameMappingValue, variableTypes = (0, 1)):
        """! Update (with the update() method of dict) the dictionary nameMappingValue previously provided.

        @param nameMappingValue the Python dictionary used for the update.
        @param variableTypes list which values are 0 (for output) and/or 1 for input.
        """
        self._updateNameMapping(nameMappingValue, variableTypes)

    def updateNameMappingField(self, nameMappingField, variableTypes = (0, 1)):
        """! Update (with the update() method of dict) the dictionary nameMappingField previously provided.

        @param nameMappingField the Python dictionary used for the update.
        @param variableTypes list which values are 0 (for output) and/or 1 for input.
        """
        self._updateNameMapping(nameMappingField, [v + 2 for v in variableTypes])

    def _getNewName(self, name, variableType, inverse):
        """! Return the change name(s).

        @param name (string) previous name.
        @param variableType put 0 (self._valueO) if name is the name of an output value, 1 (self._valueI) if name is the name of an input value, 2 (self._field0) if it is the name of an output field, 3 (self._fieldI) if it is the name of an input field.
        @param inverse True to inverse research (old -> new), False to direct (new -> old).

        @return the list of new names if inverse, and the single old name otherwise.
        """
        dictionary = (self._invertNameMapping if inverse else self._nameMapping)[variableType]

        if name in dictionary:
            return dictionary[name]
        if self._wildcard:
            wildcardLen = len(self._wildcard)
            for key, value in dictionary.items():
                if key.endswith(self._wildcard) and name.startswith(key[:-wildcardLen]):
                    if inverse:
                        result = []
                        for valueName in value:
                            if valueName.endswith(self._wildcard):
                                result.append(name.replace(key[:-wildcardLen], valueName[:-wildcardLen], 1))
                        if len(result) > 0:
                            return result
                    elif value.endswith(self._wildcard):
                        return name.replace(key[:-wildcardLen], value[:-wildcardLen], 1)
        if inverse:
            return []
        elif self._exclusive:
            raise ValueError("name='{}' is not available here. Interface only has {}".format(
                name, list(dictionary.keys())))
        return name

    def _getIONames(self, names, variableType):
        """ INTERNAL """
        newNames = [newName for revNames in [
            self._getNewName(name, variableType=variableType, inverse=True) for name in names]
                    for newName in revNames]    #Transforme une liste de listes en liste.
        if not self._exclusive:
            newNames += [name for name in names if name not in newNames]
        return newNames

    def _getInfo(self, method, isValue, name):
        """ INTERNAL """
        inputEnum = self._valueI if isValue else self._fieldI
        outputEnum = self._valueO if isValue else self._fieldO
        oldName = ""
        try:
            oldName = self._getNewName(name, variableType=inputEnum, inverse=False)
            return method(oldName)
        except Exception as error1:
            try:
                oldName2 = self._getNewName(name, variableType=outputEnum, inverse=False)
                if oldName2 != oldName:
                    return method(oldName2)
                raise ValueError("name='{}' seems not to be available here. We received the following error message from {} method from wrapped PhysicsDriver: \n {}".format(name, method.__name__, error1))
            except Exception as error2:
                raise ValueError("name='{}' seems not to be available here. We received the following error messages from {} method from wrapped PhysicsDriver (we try with {} as an input first, than as an output): \n {} \n and: {}".format(name, method.__name__, name, error1, error2))

    def getInputFieldsNames(self):
        """! See c3po.DataAccessor.DataAccessor.getInputFieldsNames(). """
        return self._getIONames(self._physics.getInputFieldsNames(), self._fieldI)

    def getOutputFieldsNames(self):
        """! See c3po.DataAccessor.DataAccessor.getOutputFieldsNames(). """
        return self._getIONames(self._physics.getOutputFieldsNames(), self._fieldO)

    def getFieldType(self, name):
        """! See c3po.DataAccessor.DataAccessor.getFieldType(). """
        return self._getInfo(self._physics.getFieldType, False, name)

    def getFieldUnit(self, name):
        """! See c3po.DataAccessor.DataAccessor.getFieldUnit(). """
        return self._getInfo(self._physics.getFieldUnit, False, name)

    def getInputMEDDoubleFieldTemplate(self, name):
        """! See c3po.DataAccessor.DataAccessor.getInputMEDDoubleFieldTemplate(). """
        return self._physics.getInputMEDDoubleFieldTemplate(self._getNewName(name, variableType=self._fieldI, inverse=False))

    def setInputMEDDoubleField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.setInputMEDDoubleField(). """
        self._physics.setInputMEDDoubleField(self._getNewName(name, variableType=self._fieldI, inverse=False), field)

    def getOutputMEDDoubleField(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputMEDDoubleField(). """
        return self._physics.getOutputMEDDoubleField(self._getNewName(name, variableType=self._fieldO, inverse=False))

    def updateOutputMEDDoubleField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.updateOutputMEDDoubleField(). """
        return self._physics.updateOutputMEDDoubleField(self._getNewName(name, variableType=self._fieldO, inverse=False), field)

    def getInputMEDIntFieldTemplate(self, name):
        """! See c3po.DataAccessor.DataAccessor.getInputMEDIntFieldTemplate(). """
        return self._physics.getInputMEDIntFieldTemplate(self._getNewName(name, variableType=self._fieldI, inverse=False))

    def setInputMEDIntField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.setInputMEDIntField(). """
        self._physics.setInputMEDIntField(self._getNewName(name, variableType=self._fieldI, inverse=False), field)

    def getOutputMEDIntField(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputMEDIntField(). """
        return self._physics.getOutputMEDIntField(self._getNewName(name, variableType=self._fieldO, inverse=False))

    def updateOutputMEDIntField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.updateOutputMEDIntField(). """
        return self._physics.updateOutputMEDIntField(self._getNewName(name, variableType=self._fieldO, inverse=False), field)

    def getInputValuesNames(self):
        """! See c3po.DataAccessor.DataAccessor.getInputValuesNames(). """
        return self._getIONames(self._physics.getInputValuesNames(), self._valueI)

    def getOutputValuesNames(self):
        """! See c3po.DataAccessor.DataAccessor.getOutputValuesNames(). """
        return self._getIONames(self._physics.getOutputValuesNames(), self._valueO)

    def getValueType(self, name):
        """! See c3po.DataAccessor.DataAccessor.getValueType(). """
        return self._getInfo(self._physics.getValueType, True, name)

    def getValueUnit(self, name):
        """! See c3po.DataAccessor.DataAccessor.getValueUnit(). """
        return self._getInfo(self._physics.getValueUnit, True, name)

    def setInputDoubleValue(self, name, value):
        """! See c3po.DataAccessor.DataAccessor.setInputDoubleValue(). """
        self._physics.setInputDoubleValue(self._getNewName(name, variableType=self._valueI, inverse=False), value)

    def getOutputDoubleValue(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputDoubleValue(). """
        return self._physics.getOutputDoubleValue(self._getNewName(name, variableType=self._valueO, inverse=False))

    def setInputIntValue(self, name, value):
        """! See c3po.DataAccessor.DataAccessor.setInputIntValue(). """
        self._physics.setInputIntValue(self._getNewName(name, variableType=self._valueI, inverse=False), value)

    def getOutputIntValue(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputIntValue(). """
        return self._physics.getOutputIntValue(self._getNewName(name, variableType=self._valueO, inverse=False))

    def setInputStringValue(self, name, value):
        """! See c3po.DataAccessor.DataAccessor.setInputStringValue(). """
        self._physics.setInputStringValue(self._getNewName(name, variableType=self._valueI, inverse=False), value)

    def getOutputStringValue(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputStringValue(). """
        return self._physics.getOutputStringValue(self._getNewName(name, variableType=self._valueO, inverse=False))


class NameChangerMeta(type):
    """! Metaclass related to the use of nameChanger. """

    def __init__(cls, clsname, superclasses, attributedict):
        type.__init__(cls, clsname, superclasses, attributedict)

    def __new__(cls, clsname, superclasses, attributedict):

        def _getChangedName(self, name):
            """! INTERNAL """
            if name in self.static_nameMapping:
                return self.static_nameMapping[name]
            if self.static_wildcard:
                wildcardLen = len(self.static_wildcard)
                for key, value in self.static_nameMapping.items():
                    if key.endswith(self.static_wildcard) and value.endswith(self.static_wildcard) and name.startswith(key[:-wildcardLen]):
                        return name.replace(key[:-wildcardLen], value[:-wildcardLen], 1)
            return None

        def methodWrapper(method):
            def methodWrapped(self, *args, **kwargs):
                name = None
                if "name" in kwargs.keys():
                    name = self._getChangedName(kwargs["name"])  # pylint: disable=protected-access
                    if name:
                        kwargs["name"] = name if name else kwargs["name"]
                else:
                    i = 0
                    for arg in args:
                        if isinstance(arg, str):
                            name = self._getChangedName(arg)  # pylint: disable=protected-access
                            if name:
                                args = args[:i] + (name,) + args[i + 1:]
                        i += 1
                return method(self, *args, **kwargs)

            methodWrapped.__name__ = method.__name__
            methodWrapped.__doc__ = method.__doc__
            methodWrapped.__dict__.update(method.__dict__)
            return methodWrapped

        newDct = {}
        newDct["_getChangedName"] = _getChangedName
        for nameattr, method in attributedict.items():
            if isinstance(method, FunctionType):
                newDct[nameattr] = methodWrapper(method)
            elif nameattr == "static_nameMapping":
                newDct[nameattr] = method.copy()
            else:
                newDct[nameattr] = method

        icocoDataMethods = ["save", "restore", "forget", "getFieldType", "getFieldUnit", "getInputMEDDoubleFieldTemplate", "setInputMEDDoubleField",
                            "getOutputMEDDoubleField", "updateOutputMEDDoubleField", "getInputMEDIntFieldTemplate", "setInputMEDIntField", "getOutputMEDIntField",
                            "updateOutputMEDIntField", "getInputMEDStringFieldTemplate", "setInputMEDStringField", "getOutputMEDStringField",
                            "updateOutputMEDStringField", "getValueType", "getValueUnit", "setInputDoubleValue", "getOutputDoubleValue", "setInputIntValue",
                            "getOutputIntValue", "setInputStringValue", "getOutputStringValue"]
        for method in icocoDataMethods:
            if method not in newDct:
                for base in superclasses:
                    if hasattr(base, method):
                        newDct[method] = methodWrapper(getattr(base, method))
                        break

        return type.__new__(cls, clsname, superclasses, newDct)


def nameChanger(nameMapping, wildcard=None):
    """! nameChanger is a class wrapper that allows to change the names of the variables used by the base class (usually a PhysicsDriver).

    This allows to improve the genericity of coupling scripts by using generic variable names without modifying the PhysicsDriver "by hand".

    When a method of the base class is called there is two possibilities :
    1. The call uses a named argument "name" (for example myObject.setInputDoubleValue(name="myName", value=0.)). In this case, the value passed to the argument "name" is modified (if this is a key of nameMapping).
    2. There is no named argument "name" (for example myObject.setInputDoubleValue("myName", 0.)). In this case, the value of all arguments of type "str" is modified (if the value used is a key of nameMapping).

    In both cases, nothing is done (no error) if the initial value is not in the keys of nameMapping.

    @param nameMapping a Python dictionary with the mapping from the new names (the generic ones) to the old ones (the names used by the code).
    @param wildcard a Python string. If both new and old names terminate by this wildcard (a wildcard in the middle of the names is not taken into account), nameChanger will substitute only the preceding part. For example : c3po.nameChanger({"newName*" : "oldName*"}, "*") will substitute newNameA05 in oldNameA05 and newNameB9 in oldNameB9.

    The parameters of nameChanger are added to the class ("static" attributes) with the names static_nameMapping and static_wildcard.
    A new method is also added for internal use: _getChangedName(self, name).

    nameChanger can be used either as a python decorator (where the class is defined) in order to modify the class definition everywhere. For example:

        @c3po.nameChanger({"newName" : "oldName", "newName2*" : "oldName2*"}, "*")
        class MyClass(...):
            ...

    or it can be used in order to redefined only locally the class like that:

        MyNewClass = c3po.nameChanger({"newName" : "oldName", "newName2*" : "oldName2*"}, "*")(MyClass)

    afterward "newName" can be used in place of "oldName" everywhere with MyNewClass. "oldName" is still working.

    @note nameMapping is copied.

    @warning nameChanger looks for ICoCo methods (the methods to implement in order to define a PhysicsDriver) in base classes and redefine
            them. Other inherited methods are invisible to nameChanger.
    @warning A class that inherits from a class wrapped by nameChanger will be wrapped as well, with the same parameters.
            It may be a workaround for the previous warning.
            The definition of the daughter class ("class Daughter(Mother): ...") must be done after the application of nameChanger on Mother.
            Otherwise it will result in TypeError when the daughter class will try to call mother methods (since its mother class does
            not exist anymore!). As a consequence, if nameChanger is to be applied to C3PO classes, it is recommended to change their name
            "(MyNewClass = c3po.nameChanger(...)(MyClass)").

    @throw Exception if applied to a class already modified by nameChanger, because it could result in an unexpected behavior.
    """

    warning("The class wrapper nameChanger is deprecated and will soon by deleted. "
            + "Please use the class NameChanger (acting on a PhysicsDriver object rather than a class).")

    def classWrapper(baseclass):
        if hasattr(baseclass, "static_nameMapping"):
            raise Exception("nameChanger: the class " + baseclass.__name__ + " has already been modified by nameChanger. This is not allowed.")
        baseclass.static_nameMapping = nameMapping
        baseclass.static_wildcard = wildcard
        newclass = NameChangerMeta(baseclass.__name__, baseclass.__bases__, baseclass.__dict__)
        newclass.__doc__ = baseclass.__doc__
        delattr(baseclass, "static_nameMapping")
        delattr(baseclass, "static_wildcard")
        return newclass
    return classWrapper
