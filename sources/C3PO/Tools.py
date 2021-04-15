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

from functools import wraps


class MetaClassWithNomenclature(type):
    """Metaclass used to decorate the target methods (contained in the targetMethods list) of the argument class (defined by cls, clsname, superclasses, attributedict) with the decorator addNomenclature2Method (which add the C3PO names nomenclature) using C3PO2PHYS dictionary as parameter."""

    def __new__(cls, clsname, superclasses, attributedict, C3PO2PHYS, targetMethods):
        newDct = {}
        targetMethodsSet = set(targetMethods)
        allMethodsSet    = set(attributedict.keys())
        if not(targetMethodsSet.issubset(allMethodsSet)):
            raise AssertionError("The following methods do not belong to the class {}:\n{}.".format(clsname,targetMethodsSet-allMethodsSet))
        complementarySet = allMethodsSet - targetMethodsSet
        for attr in complementarySet:
            newDct[attr] = attributedict[attr]
        for attr in targetMethodsSet:
            newDct[attr] = cls.addNomenclature2Method(C3PO2PHYS)(attributedict[attr])
        newDct["C3PO2PHYS"] = C3PO2PHYS
        return type.__new__(cls, clsname, superclasses, newDct)

    def __init__(self, clsname, superclasses, attributedict, *args, **kwargs):
        type.__init__(self, clsname, superclasses, attributedict)

    @staticmethod
    def addNomenclature2Method(C3PO2PHYSD):
        def methodWrapper(icocoMethod):
            @wraps(icocoMethod)
            def icocoMethodWithC3PONomenclature(self, *args, **kwargs):
                if "name" in kwargs.keys():
                    name = kwargs.pop("name")
                else:
                    ii = 0
                    for arg_i in args:
                        if type(arg_i) == str:
                            name = arg_i
                            args = args[:ii] + args[ii+1:]
                            break
                        ii += 1

                if name in C3PO2PHYSD.keys():
                    name = C3PO2PHYSD[name]
                return icocoMethod(self, name, *args, **kwargs)
            return icocoMethodWithC3PONomenclature
        return methodWrapper

def AddNomenclature(C3PO2PHYS, targetMethods):
    """Class decorator to add the C3PO2PHYS as possible nomenclature for the target methods (specified in targetMethods list)"""

    def classWrapper(baseclass):
        newclass = MetaClassWithNomenclature(baseclass.__name__, baseclass.__bases__, baseclass.__dict__, C3PO2PHYS, targetMethods)
        return newclass
    return classWrapper
