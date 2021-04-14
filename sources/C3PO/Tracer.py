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
import time
import sys
import os

import C3PO.medcoupling_compat as mc

def get_setInputMEDField_input(name, field):
    """! INTERNAL """
    return (name, field)


def get_initTimeStep_input(dt):
    """! INTERNAL """
    return dt


def getArgsString(*args, **kwargs):
    """! INTERNAL """
    string_args = "("
    for arg in args:
        str_arg = str(arg)
        if isinstance(arg, str):
            str_arg = "'" + arg + "'"
        string_args += str_arg + ","
    for nameattr, arg in kwargs.items():
        str_arg = str(arg)
        if isinstance(arg, str):
            str_arg = "'" + arg + "'"
        string_args += nameattr + " = " + str_arg + ","
    string_args += ")"
    return string_args


def WriteField_MC789(n, f, b):
    """! INTERNAL """
    try:
        writeField = mc.WriteField
    except:
        writeField = ml.WriteField
    writeField(n, f, b)


class TracerMeta(type):
    """! Metaclass related to the use of Tracer. """

    def __init__(self, name, bases, dct):
        type.__init__(self, name, bases, dct)
        self.static_MEDinfo = {}
        self.static_Objectcounter = {}

    def __new__(metacls, name, bases, dct):

        def _wrapper(method):
            def _trace(self, *args, **kwargs):
                if self.static_pythonFile is not None:
                    objectNameBase = "my" + name
                    if objectNameBase not in self.static_Objectcounter:
                        self.static_Objectcounter[objectNameBase] = 0
                    objectName = "my" + name + str(self.static_Objectcounter[objectNameBase])
                    string_args = getArgsString(*args, **kwargs)
                    if method.__name__ == "__init__":
                        self.static_Objectcounter[objectNameBase] += 1
                        objectName = "my" + name + str(self.static_Objectcounter[objectNameBase])
                        self.static_pythonFile.write(objectName + " = " + name + string_args + "\n")
                    elif method.__name__ == "setInputMEDField":
                        (name_field, field) = get_setInputMEDField_input(*args, **kwargs)
                        if self.static_saveMED:
                            if name_field not in self.static_MEDinfo:
                                self.static_MEDinfo[name_field] = []
                            nameMEDFile = name_field + str(len(self.static_MEDinfo[name_field])) + ".med"
                            timeMED, iteration, order = field.getTime()
                            self.static_MEDinfo[name_field].append((field.getTypeOfField(), nameMEDFile, field.getMesh().getName(), 0, field.getName(), iteration, order))
                            WriteField_MC789(nameMEDFile, field, True)
                            self.static_pythonFile.write("field_" + objectName + " = ReadField_MC789" + str(self.static_MEDinfo[name_field][-1]) + "\n")
                        self.static_pythonFile.write(objectName + "." + method.__name__ + "('" + name_field + "', field_" + objectName + ")" + "\n")
                    else:
                        self.static_pythonFile.write(objectName + "." + method.__name__ + string_args + "\n")
                    self.static_pythonFile.flush()

                prev_idstdout = 0
                prev_idstderr = 0
                if self.static_stdout is not None:
                    sys.stdout.flush()
                    prev_idstdout = os.dup(sys.stdout.fileno())
                    os.dup2(self.static_stdout.fileno(), sys.stdout.fileno())
                if self.static_stderr is not None:
                    sys.stderr.flush()
                    prev_idstderr = os.dup(sys.stderr.fileno())
                    os.dup2(self.static_stderr.fileno(), sys.stderr.fileno())

                start = time.time()

                result = method(self, *args, **kwargs)

                end = time.time()

                if self.static_stdout is not None:
                    sys.stdout.flush()
                    os.dup2(prev_idstdout, sys.stdout.fileno())
                    os.close(prev_idstdout)
                if self.static_stderr is not None:
                    sys.stderr.flush()
                    os.dup2(prev_idstderr, sys.stderr.fileno())
                    os.close(prev_idstderr)

                if self.static_lWriter is not None:
                    if method.__name__ in ["initialize", "computeTimeStep", "initTimeStep", "solveTimeStep", "iterateTimeStep", "validateTimeStep", "abortTimeStep", "terminate", "exchange"]:
                        input_var = 0.
                        if method.__name__ == "initTimeStep":
                            input_var = get_initTimeStep_input(*args, **kwargs)
                        self.static_lWriter.writeAfter(self, input_var, result, method.__name__, start, end - start)

                return result

            _trace.__name__ = method.__name__
            _trace.__doc__ = method.__doc__
            _trace.__dict__.update(method.__dict__)
            return _trace

        newDct = {}
        for nameattr, method in dct.items():
            if type(method) is FunctionType:
                newDct[nameattr] = _wrapper(method)
            else:
                newDct[nameattr] = method
        return type.__new__(metacls, name, bases, newDct)


def Tracer(pythonFile=None, saveMED=True, stdoutFile=None, stderrFile=None, listingWriter=None):
    """! Tracer is a class wrapper allowing to trace the calls of the methods of the base class.

    It has different functions:

    1. It can write all calls of the methods of the base class in a text file in python format in order to allow to replay what happened from the code point of view outside of the coupling.
    2. It can redirect code standard and error outputs in text files.
    3. It can contribute (with ListingWriter) to the writing of a global coupling listing file with calculation time measurement.

    @param pythonFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The python script is written there. It has to be closed (file.close()) by caller.
    @param saveMED This is related to the python file writing.
        - if set to True (default value), every time setInputMEDField is called, the input MED field is stored in an independant .med file, and MEDLoader reading call is written in the output file.
        - if set to False, the MED field is not stored and the MEDLoader call is not written. Only the setInputMEDField call is written. The replay is not possible.
    @param stdoutFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The standard output is redirected there. It has to be closed (file.close()) by caller.
    @param stderrFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The error output is redirected there. It has to be closed (file.close()) by caller.
    @param listingWriter a ListingWriter object which will manage the writing of the coupling listing file. Refer to the documentation of ListingWriter.

    The parameters of Tracer are added to the class ("static" attributes) with the names static_pythonFile, static_saveMED, static_stdout, static_stderr and static_lWriter.
    Two additional static attributes are added for internal use: static_MEDinfo and static_Objectcounter.

    Tracer can be used either as a python decorator (where the class is defined) in order to modify the class definition everywhere:

        @C3PO.Tracer(...)
        class MyClass(...):
            ...

    or it can be used in order to redefined only locally the class like that:

        MyNewClass = C3PO.Tracer(...)(MyClass)

    Tracer cannot distinguish different instance of the same class. The name of the instance created in the python file changes each time the __init__ method is called. This means that when a new instance is created, Tracer assumes that the previous ones are not used any more. If this is not the case, put the ouput of each instance in its own output file :

        MyClass1 = C3PO.Tracer(pythonFile=file1, ...)(MyClass)
        MyClass2 = C3PO.Tracer(pythonFile=file2, ...)(MyClass)
        instance1 = MyClass1()
        instance2 = MyClass2()

    @warning Tracer can be applied to any class, but it is design for standard C3PO objects: PhysicsDriver, DataManager and Exchanger. It may be hazardous to use on "similar but not identical" classes (typically with the same methods but different inputs and/or outputs).
    @warning Tracer only modifies the base class, not its parents. As a consequence, inherited methods are invisible to Tracer. Redefine them in the daughter class if needed.
    @warning A class that inherits from a class wrapped by Tracer will be wrapped as well, with the same parameters.
             If the wrapping is applied (without changing the name of the class) after the building of the daughter class, it will result in TypeError when the daughter class will try to call mother methods (since its mother class does not exist anymore!).
             As a consequence, if applied to C3PO classes, it is recommended to change the name of the classes.

    """

    def classWrapper(baseclass):
        if pythonFile is not None:
            pythonFile.write("# -*- coding: utf-8 -*-" + "\n")
            pythonFile.write("from __future__ import print_function, division" + "\n")
            pythonFile.write("import C3PO.medcoupling_compat as mc" + "\n")
            pythonFile.write("from " + baseclass.__module__ + " import " + baseclass.__name__ + "\n" + "\n")

            pythonFile.write("def ReadField_MC789(*args, **kwargs):" + "\n")
            pythonFile.write("  try:" + "\n")
            pythonFile.write("    readField = mc.ReadField" + "\n")
            pythonFile.write("  except:" + "\n")
            pythonFile.write("    readField = ml.ReadField" + "\n")
            pythonFile.write("  readField(*args, **kwargs)" + "\n" + "\n")

        baseclass.static_pythonFile = pythonFile
        baseclass.static_saveMED = saveMED
        baseclass.static_stdout = stdoutFile
        baseclass.static_stderr = stderrFile
        baseclass.static_lWriter = listingWriter
        newclass = TracerMeta(baseclass.__name__, baseclass.__bases__, baseclass.__dict__)
        newclass.__doc__ = baseclass.__doc__
        delattr(baseclass, "static_pythonFile")
        delattr(baseclass, "static_saveMED")
        delattr(baseclass, "static_stdout")
        delattr(baseclass, "static_stderr")
        delattr(baseclass, "static_lWriter")
        return newclass
    return classWrapper