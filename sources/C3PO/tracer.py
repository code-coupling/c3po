# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class wrapper tracer. """
from __future__ import print_function, division
from types import FunctionType

from MEDLoader import MEDLoader


def get_setInputMEDField_input(name, field):
    """ For internal use only. """
    return (name, field)


def getArgsString(*args, **kwargs):
    """ For internal use only. """
    string_args = "("
    for arg in args:
        str_arg = str(arg)
        if isinstance(arg, str):
            str_arg = "'" + arg + "'"
        string_args += str_arg + ","
    for nameattr, arg in kwargs.iteritems():
        str_arg = str(arg)
        if isinstance(arg, str):
            str_arg = "'" + arg + "'"
        string_args += nameattr + " = " + str_arg + ","
    string_args += ")"
    return string_args


class tracerMeta(type):
    """ Metaclass defined for internal use only. """

    def __init__(self, name, bases, dct):
        type.__init__(self, name, bases, dct)
        self.MEDinfo_ = {}
        self.Objectcounter_ = {}

    def __new__(metacls, name, bases, dct):
        file = 0
        save_MED = True
        if "meta_file" not in dct:
            for baseclass in bases:
                if hasattr(baseclass, "meta_file"):
                    file = baseclass.meta_file
                    save_MED = baseclass.meta_save_MED
        else:
            file = dct["meta_file"]
            save_MED = dct["meta_save_MED"]
        if file == 0:
            raise Exception("tracer : we did not find the file where to write.")

        def _wrapper(method):
            def _trace(self, *args, **kwargs):
                objectNameBase = "my" + name
                if objectNameBase not in self.Objectcounter_:
                    self.Objectcounter_[objectNameBase] = 0
                objectName = "my" + name + str(self.Objectcounter_[objectNameBase])
                string_args = getArgsString(*args, **kwargs)
                if method.__name__ == "__init__":
                    self.Objectcounter_[objectNameBase] += 1
                    objectName = "my" + name + str(self.Objectcounter_[objectNameBase])
                    file.write(objectName + " = " + name + string_args + "\n")
                elif method.__name__ == "setInputMEDField":
                    (name_field, field) = get_setInputMEDField_input(*args, **kwargs)
                    if save_MED:
                        if name_field not in self.MEDinfo_:
                            self.MEDinfo_[name_field] = []
                        nameMEDFile = name_field + str(len(self.MEDinfo_[name_field])) + ".med"
                        time, iteration, order = field.getTime()
                        self.MEDinfo_[name_field].append((field.getTypeOfField(), nameMEDFile, field.getMesh().getName(), 0, field.getName(), iteration, order))
                        MEDLoader.WriteField(nameMEDFile, field, True)
                        file.write("field_" + objectName + " = MEDLoader.ReadField" + str(self.MEDinfo_[name_field][-1]) + "\n")
                    file.write(objectName + "." + method.__name__ + "('" + name_field + "', field_" + objectName + ")" + "\n")
                else:
                    file.write(objectName + "." + method.__name__ + string_args + "\n")
                file.flush()
                return method(self, *args, **kwargs)
            _trace.__name__ = method.__name__
            _trace.__doc__ = method.__doc__
            _trace.__dict__.update(method.__dict__)
            return _trace

        newDct = {}
        for nameattr, method in dct.iteritems():
            if type(method) is FunctionType:
                newDct[nameattr] = _wrapper(method)
            else:
                newDct[nameattr] = method
        return type.__new__(metacls, name, bases, newDct)


def tracer(file, save_MED=True):
    """ tracer is a class wrapper allowing to trace the calls of the methods of the base class. It write them all in a text file in python format in order to allow to replay what happened. 

    It works for every class but it includes a special treatment of the input MED field of the setInputMEDField method (from physicsDriver for instance). Do not use with a class having a setInputMEDField method with different arguments than a physicsDriver!

    :param file: a file object which has to be already open in written mode (file = open("file.txt", "w")). Everything is written there. It has to be closed (file.close()) by caller.
    :param save_MED: 
        - if set to True (default value), every time setInputMEDField is called, the input MED field is stored in an independant .med file, and MEDLoader reading call is written in the output file. 
        - if set to False, the MED field is not stored and the MEDLoader call is not written. Only the setInputMEDField call is written. The replay is not possible.

    Two attributes are added to the class ("static" ones) : meta_file and meta_save_MED storing the values of the two tracer parameters.

    tracer can be used either as a python decorator (where the class is defined) in order to modify the class definition everywhere:
        @C3PO.tracer(file, save_MED)
        class myclass(...): 
            ...

    or it can be used in order to redefined only locally the class like that:
        myclass = C3PO.tracer(file, save_MED)(myclass)

    tracer cannot distinguish different instance of the same class. The name of the instance created in the output file changes each time the __init__ method is called. This means that when a new instance is created, tracer assumes that the previous ones are not used any more. If this is not the case, put the ouput of each instance in its own output file :

        myclass1 = C3PO.tracer(file1, save_MED)(myclass)
        myclass2 = C3PO.tracer(file2, save_MED)(myclass)
        instance1 = myclass1()
        instance2 = myclass2()

    """
    counter = {}

    def classWrapper(baseclass):
        file.write("# -*- coding: utf-8 -*-" + "\n")
        file.write("from __future__ import print_function, division" + "\n")
        file.write("from MEDLoader import MEDLoader" + "\n")
        file.write("from " + baseclass.__module__ + " import " + baseclass.__name__ + "\n" + "\n")
        baseclass.meta_file = file
        baseclass.meta_save_MED = save_MED
        newclass = tracerMeta(baseclass.__name__, baseclass.__bases__, baseclass.__dict__)
        newclass.__doc__ = baseclass.__doc__
        return newclass
    return classWrapper
