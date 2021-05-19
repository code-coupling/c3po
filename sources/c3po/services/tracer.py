# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class wrapper tracer. """
from __future__ import print_function, division
from types import FunctionType
import time
import sys
import os

import c3po.medcouplingCompat as mc


def getSetInputMEDFieldInput(name, field):
    """! INTERNAL """
    return (name, field)


def getGetOutputMEDFieldInput(name):
    """! INTERNAL """
    return name


def getInitTimeStepInput(dt):
    """! INTERNAL """
    return dt


def getArgsString(*args, **kwargs):
    """! INTERNAL """
    stringArgs = "("
    for arg in args:
        strArg = str(arg)
        if isinstance(arg, str):
            strArg = "'" + arg + "'"
        stringArgs += strArg + ","
    for nameattr, arg in kwargs.items():
        strArg = str(arg)
        if isinstance(arg, str):
            strArg = "'" + arg + "'"
        stringArgs += nameattr + " = " + strArg + ","
    stringArgs += ")"
    return stringArgs


class TracerMeta(type):
    """! Metaclass related to the use of tracer. """

    def __init__(cls, name, bases, dct):
        type.__init__(cls, name, bases, dct)
        cls.static_Objectcounter = {}

    def __new__(cls, name, bases, dct):

        def _wrapper(method):
            def _trace(self, *args, **kwargs):
                if method.__name__ == "__init__":
                    if name not in self.static_Objectcounter:
                        self.static_Objectcounter[name] = 0
                    self.tracerObjectUniqueId = self.static_Objectcounter[name]
                    self.static_Objectcounter[name] += 1

                if self.static_saveInputMED and method.__name__ == "setInputMEDField":
                    (nameField, field) = getSetInputMEDFieldInput(*args, **kwargs)
                    nameMEDFile = name + "_input_" + nameField + "_"
                    num = 0
                    while os.path.exists(nameMEDFile + str(num) + ".med"):
                        num += 1
                    nameMEDFile = nameMEDFile + str(num) + ".med"
                    _, iteration, order = field.getTime()
                    medInfo = (field.getTypeOfField(), nameMEDFile, field.getMesh().getName(),
                                                            0, field.getName(), iteration, order)
                    mc.WriteField(nameMEDFile, field, True)
                    if self.static_pythonFile is not None:
                        self.static_pythonFile.write("readField = mc.ReadField" + str(medInfo) + "\n")

                if self.static_pythonFile is not None:
                    objectName = "my" + name + str(self.tracerObjectUniqueId)
                    stringArgs = getArgsString(*args, **kwargs)
                    if method.__name__ == "__init__":
                        self.static_pythonFile.write(objectName + " = " + name + stringArgs + "\n")
                    elif method.__name__ == "setInputMEDField":
                        (nameField, _) = getSetInputMEDFieldInput(*args, **kwargs)
                        self.static_pythonFile.write(objectName + "." + method.__name__ + "('" + nameField + "', readField)" + "\n")
                    else:
                        self.static_pythonFile.write(objectName + "." + method.__name__ + stringArgs + "\n")
                    self.static_pythonFile.flush()

                prevIdstdout = 0
                prevIdstderr = 0
                if self.static_stdout is not None:
                    sys.stdout.flush()
                    prevIdstdout = os.dup(sys.stdout.fileno())
                    os.dup2(self.static_stdout.fileno(), sys.stdout.fileno())
                if self.static_stderr is not None:
                    sys.stderr.flush()
                    prevIdstderr = os.dup(sys.stderr.fileno())
                    os.dup2(self.static_stderr.fileno(), sys.stderr.fileno())

                start = time.time()

                result = method(self, *args, **kwargs)

                end = time.time()

                if self.static_stdout is not None:
                    sys.stdout.flush()
                    os.dup2(prevIdstdout, sys.stdout.fileno())
                    os.close(prevIdstdout)
                if self.static_stderr is not None:
                    sys.stderr.flush()
                    os.dup2(prevIdstderr, sys.stderr.fileno())
                    os.close(prevIdstderr)

                if self.static_saveOutputMED and method.__name__ == "getOutputMEDField":
                    nameField = getGetOutputMEDFieldInput(*args, **kwargs)
                    nameMEDFile = name + "_output_" + nameField + "_"
                    num = 0
                    while os.path.exists(nameMEDFile + str(num) + ".med"):
                        num += 1
                    nameMEDFile = nameMEDFile + str(num) + ".med"
                    mc.WriteField(nameMEDFile, result, True)

                if self.static_lWriter is not None:
                    if method.__name__ in ["initialize", "computeTimeStep", "initTimeStep", "solveTimeStep", "iterateTimeStep",
                                           "validateTimeStep", "abortTimeStep", "terminate", "exchange"]:
                        inputVar = 0.
                        if method.__name__ == "initTimeStep":
                            inputVar = getInitTimeStepInput(*args, **kwargs)
                        self.static_lWriter.writeAfter(self, inputVar, result, method.__name__, start, end - start)

                return result

            _trace.__name__ = method.__name__
            _trace.__doc__ = method.__doc__
            _trace.__dict__.update(method.__dict__)
            return _trace

        newDct = {}
        for nameattr, method in dct.items():
            if isinstance(method, FunctionType):
                newDct[nameattr] = _wrapper(method)
            else:
                newDct[nameattr] = method
        return type.__new__(cls, name, bases, newDct)


def tracer(pythonFile=None, saveInputMED=False, saveOutputMED=False, stdoutFile=None, stderrFile=None, listingWriter=None):
    """! tracer is a class wrapper allowing to trace the calls of the methods of the base class.

    It has different functions:

    1. It can write all calls of the methods of the base class in a text file in python format in order to allow to replay what
        happened from the code point of view outside of the coupling.
    2. It can save in .med files input or output MEDFields.
    3. It can redirect code standard and error outputs in text files.
    4. It can contribute (with ListingWriter) to the writing of a global coupling listing file with calculation time measurement.

    @param pythonFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The python script
        is written there. It has to be closed (file.close()) by caller. The script can be run only if saveInputMED is set to True:
        otherwise, input MED fields are not stored.
    @param saveInputMED if set to True, every time setInputMEDField is called, the input MED field is stored in a .med file.
        If pythonFile is activated, a MEDLoader reading instruction is also written in the Python file.
    @param saveOutputMED if set to True, every time getOutputMEDField is called, the output MED field is stored in a .med file.
    @param stdoutFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The standard output
        is redirected there. It has to be closed (file.close()) by caller.
    @param stderrFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The error output is
        redirected there. It has to be closed (file.close()) by caller.
    @param listingWriter a ListingWriter object which will manage the writing of the coupling listing file. Refer to the documentation
        of ListingWriter.

    The parameters of tracer are added to the class ("static" attributes) with the names static_pythonFile, static_saveInputMED,
    static_saveOutputMED, static_stdout, static_stderr and static_lWriter.

    One additional static attributes is added for internal use: static_Objectcounter.

    One addition attribute (not static!) is added for internal use: tracerObjectUniqueId.

    tracer can be used either as a python decorator (where the class is defined) in order to modify the class definition everywhere:

        @c3po.tracer(...)
        class MyClass(...):
            ...

    or it can be used in order to redefined only locally the class like that:

        MyNewClass = c3po.tracer(...)(MyClass)

    @warning tracer can be applied to any class, but it is design for standard C3PO objects: PhysicsDriver, DataManager and Exchanger.
             It may be hazardous to use on "similar but not identical" classes (typically with the same methods but different inputs and/or
             outputs).
    @warning tracer only modifies the base class, not its parents. As a consequence, inherited methods are invisible to tracer.
             Redefine them in the daughter class if needed.
    @warning A class that inherits from a class wrapped by tracer will be wrapped as well, with the same parameters.
             If the wrapping is applied (without changing the name of the class) after the building of the daughter class, it will result
             in TypeError when the daughter class will try to call mother methods (since its mother class does not exist anymore!).
             As a consequence, if applied to C3PO classes, it is recommended to change the name of the classes.
    """

    def classWrapper(baseclass):
        if pythonFile is not None:
            pythonFile.write("# -*- coding: utf-8 -*-" + "\n")
            pythonFile.write("from __future__ import print_function, division" + "\n")
            pythonFile.write("import c3po.medcouplingCompat as mc" + "\n")
            pythonFile.write("from " + baseclass.__module__ + " import " + baseclass.__name__ + "\n" + "\n")

        baseclass.static_pythonFile = pythonFile
        baseclass.static_saveInputMED = saveInputMED
        baseclass.static_saveOutputMED = saveOutputMED
        baseclass.static_stdout = stdoutFile
        baseclass.static_stderr = stderrFile
        baseclass.static_lWriter = listingWriter
        newclass = TracerMeta(baseclass.__name__, baseclass.__bases__, baseclass.__dict__)
        newclass.__doc__ = baseclass.__doc__
        delattr(baseclass, "static_pythonFile")
        delattr(baseclass, "static_saveInputMED")
        delattr(baseclass, "static_saveOutputMED")
        delattr(baseclass, "static_stdout")
        delattr(baseclass, "static_stderr")
        delattr(baseclass, "static_lWriter")
        return newclass
    return classWrapper
