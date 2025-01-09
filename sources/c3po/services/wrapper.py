# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# pylint: disable=protected-access

""" Contain the functions buildWrappingClass and wrapper. """
from __future__ import print_function, division
from types import FunctionType


def buildWrappingClass(baseclass, objectAttr):
    """! Return a wrapping class of baseclass.

    The `__init__` method of the returned class writes:

    ```
    def __init__(self, wrappedObject):
        self._wrappedObject = wrappedObject
    ```

    _wrappedObject is the only attribute of instances of the returned class.

    All methods of baseclass (inherited methods are also treated) are wrapped this way:

    ```
    def methodA(self, *args, **kwargs):
        return self._wrappedObject.methodA(*args, **kwargs)
    ```

    Instance attributes of the wrapped class can be provided using objectAttr.
    They are made available in reading and writing using Python property.

    For example:
    ```
    ClassAWrapper = c3po.buildWrappingClass(ClassA, ["toto"])
    objectA = ClassA(...)
    wrapperA = ClassAWrapper(objectA)
    ```
    Now, wrapperA.toto gives access to the same variable than objectA.toto or
    wrapperA._wrappedObject.toto.

    @param baseclass The class we want a wrapper for.
    @param objectAttr List of the names of baseclass instance attributes for which you wish to retain direct access.

    @return A wrapper class for baseclass.
    """

    def wrapperInit(self, wrappedObject):
        self._wrappedObject = wrappedObject
    wrapperInit.__name__ = "__init__"

    newDct = {}
    newDct["__init__"] = wrapperInit

    def _buildWrappingMethod(method):
        def _wrapped(self, *args, **kwargs):
            return method(self._wrappedObject, *args, **kwargs)
        _wrapped.__name__ = method.__name__
        _wrapped.__doc__ = method.__doc__
        _wrapped.__dict__.update(method.__dict__)
        return _wrapped

    wrappedClasses = baseclass.__mro__
    for wrappedClass in wrappedClasses:
        for nameattr, attr in wrappedClass.__dict__.items():
            if nameattr not in newDct and isinstance(attr, FunctionType):
                newDct[nameattr] = _buildWrappingMethod(attr)

    def buildProperty(name):
        return property(fget=lambda self: getattr(self._wrappedObject, name), fset=lambda self, value: setattr(self._wrappedObject, name, value))

    for nameattr in objectAttr:
        if nameattr not in newDct:
            newDct[nameattr] = buildProperty(nameattr)

    return type(baseclass.__name__, (baseclass,), newDct)


def wrapper(toWrap):
    """! Return a wrapping object for toWrap.

    wrapper uses c3po.services.wrapper.buildWrappingClass in order to build a wrapping class for toWrap type,
    and return an instance of this wrapping class (wrapping toWrap).

    @param toWrap Object instance (not class) to be wrapped.

    @return a wrapping object.
    """
    wrappingClass = buildWrappingClass(type(toWrap), toWrap.__dict__.keys())
    return wrappingClass(toWrap)
