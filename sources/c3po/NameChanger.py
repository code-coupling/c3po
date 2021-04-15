# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class wrapper Tracer. """
from __future__ import print_function, division
from types import FunctionType


class NameChangerMeta(type):
    """! Metaclass related to the use of NameChanger. """

    def __init__(self, clsname, superclasses, attributedict):
        type.__init__(self, clsname, superclasses, attributedict)

    def __new__(cls, clsname, superclasses, attributedict):

        def methodWrapper(method):
            def methodWrapped(self, *args, **kwargs):
                name = None
                if "name" in kwargs.keys():
                    name = kwargs["name"]
                    if name in self.static_nameMapping.keys():
                        name = self.static_nameMapping[name]
                        kwargs["name"] = name
                else:
                    ii = 0
                    for arg_i in args:
                        if type(arg_i) == str:
                            name = arg_i
                            if name in self.static_nameMapping.keys():
                                name = self.static_nameMapping[name]
                                args = args[:ii] + (name,) + args[ii+1:]
                        ii += 1
                return method(self, *args, **kwargs)

            methodWrapped.__name__ = method.__name__
            methodWrapped.__doc__ = method.__doc__
            methodWrapped.__dict__.update(method.__dict__)
            return methodWrapped

        newDct = {}
        for nameattr, method in attributedict.items():
            if type(method) is FunctionType:
                newDct[nameattr] = methodWrapper(method)
            elif nameattr == "static_nameMapping":
                newDct[nameattr] = method.copy()
            else:
                newDct[nameattr] = method
        return type.__new__(cls, clsname, superclasses, newDct)


def NameChanger(nameMapping):
    """! NameChanger is a class wrapper that allows to change the names of the variables used by the base class (usually a PhysicsDriver).

    This allows to improve the genericity of coupling scripts by using generic variable names without modifying the PhysicsDriver "by hand".

    When a method of the base class is called there is two possibilities :
    1. The call used a named argument "name" (for example myObject.setValue(name="myName", value=0.)). In this case, the value passed to the argument "name" is modified (if the value used is a key of nameMapping).
    2. Their is no named argument "name" (for ecample myObject.setValue("myName", 0.)). In this case, the value of all arguments of type "str" is modified (if the value used is a key of nameMapping).

    In both cases, nothing is done (no error) if the initial value is not in the keys of nameMapping.

    @param nameMapping a Python dictionary with the mapping from the new names (the generic ones) to the old ones (the names used by the code).

    The parameter of NameChanger is added to the class ("static" attributes) with the names static_nameMapping.

    NameChanger can be used either as a python decorator (where the class is defined) in order to modify the class definition everywhere. For example:

        @C3PO.NameChanger({"newName" : "oldName"})
        class MyClass(...):
            ...

    or it can be used in order to redefined only locally the class like that:

        MyNewClass = C3PO.NameChanger({"newName" : "oldName"})(MyClass)

    afterward "newName" can be used in place of "oldName" everywhere with MyNewClass. "oldName" is still working.

    @note nameMapping is copied.

    @warning NameChanger only modifies the base class, not its parents. As a consequence, inherited methods are invisible to NameChanger. Redefine them in the daughter class if needed.
    @warning A class that inherits from a class wrapped by NameChanger will be wrapped as well, with the same parameters.
             If the wrapping is applied (without changing the name of the class) after the building of the daughter class, it will result in TypeError when the daughter class will try to call mother methods (since its mother class does not exist anymore!).
             As a consequence, if applied to C3PO classes, it is recommended to change the name of the classes.
    """

    def classWrapper(baseclass):
        baseclass.static_nameMapping = nameMapping
        newclass = NameChangerMeta(baseclass.__name__, baseclass.__bases__, baseclass.__dict__)
        newclass.__doc__ = baseclass.__doc__
        delattr(baseclass, "static_nameMapping")
        return newclass
    return classWrapper
