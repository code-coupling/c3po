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
import copy


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
    """! nameChanger is a wrapper that allows to change the names of the variables used by the provided class / object (usually a PhysicsDriver).

    This allows to improve the genericity of coupling scripts by using generic variable names without modifying the PhysicsDriver "by hand".

    @note nameChanger can be called either on a class, or an object.
        - If called on a class, nameChanger acts as a class wrapper and return a new class.
        - If called on an object, a new class is dynamically defined by the application of the previous class wrapper to the base
          class of the provided object, and an instance of this new class (in which all the attributes of the provided object are
          copied) is created and returned.

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

    or it can be used in order to redefined only locally the class / object like that:

        MyNewClass = c3po.nameChanger({"newName" : "oldName", "newName2*" : "oldName2*"}, "*")(MyClass)

    or:

        newObject = c3po.nameChanger({"newName" : "oldName", "newName2*" : "oldName2*"}, "*")(myObject)

    afterward "newName" can be used in place of "oldName" everywhere with MyNewClass (or newObject). "oldName" is still working.

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

    def wrapper(wrapped):
        if isinstance(wrapped, type):
            if hasattr(wrapped, "static_nameMapping"):
                raise Exception("nameChanger: the class " + wrapped.__name__ + " has already been modified by nameChanger. This is not allowed.")
            wrapped.static_nameMapping = nameMapping
            wrapped.static_wildcard = wildcard
            newclass = NameChangerMeta(wrapped.__name__, wrapped.__bases__, wrapped.__dict__)
            newclass.__doc__ = wrapped.__doc__
            delattr(wrapped, "static_nameMapping")
            delattr(wrapped, "static_wildcard")
            return newclass
        else:
            def __init__(self, model):
                self.__dict__.update(copy.copy(model.__dict__))
            baseClass = type(wrapped)
            dictBaseClass = {}
            for key in baseClass.__dict__:
                dictBaseClass[key] = baseClass.__dict__[key]
            dictBaseClass["__init__"] = __init__
            baseClassCopy = type(baseClass.__name__, baseClass.__bases__, dictBaseClass)
            baseClassCopy.__doc__ = baseClass.__doc__
            newclass = wrapper(baseClassCopy)
            newobject = newclass(wrapped)
            return newobject
    return wrapper
