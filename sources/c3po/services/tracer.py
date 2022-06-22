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


def getNameFieldInput(name, field):
    """! INTERNAL """
    return (name, field)


def getNameInput(name):
    """! INTERNAL """
    return name


def getDtInput(dt):
    """! INTERNAL """
    return dt


def getStationaryModeInput(stationaryMode):
    """! INTERNAL """
    return stationaryMode


def getTimeInput(time_):
    """! INTERNAL """
    return time_


def getSaveInput(label, method):
    """! INTERNAL """
    return label, method


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
    if len(stringArgs) > 1:
        stringArgs = stringArgs[:-1]
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
                if hasattr(self, "tracerRecurrenceDepth") and self.tracerRecurrenceDepth > 0:
                    return method(self, *args, **kwargs)

                if method.__name__ == "__init__":
                    if name not in self.static_Objectcounter:
                        self.static_Objectcounter[name] = 0
                    self.tracerObjectName = "my" + name + str(self.static_Objectcounter[name])
                    self.static_Objectcounter[name] += 1
                    self.tracerRecurrenceDepth = 0

                if self.static_saveInputMED and method.__name__.startswith("setInputMED"):
                    (nameField, field) = getNameFieldInput(*args, **kwargs)
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
                    toWritePython = ""
                    if method.__name__ == "__init__":
                        stringArgs = getArgsString(*args, **kwargs)
                        toWritePython = self.tracerObjectName + " = " + name + stringArgs + "\n"
                    elif method.__name__.startswith("setInputMED"):
                        (nameField, _) = getNameFieldInput(*args, **kwargs)
                        toWritePython = self.tracerObjectName + "." + method.__name__ + "('" + nameField + "', readField)" + "\n"
                    elif method.__name__.startswith("getOutputMED"):
                        nameField = getNameInput(*args, **kwargs)
                        toWritePython = nameField + "_" + self.tracerObjectName + " = " + self.tracerObjectName + "." + method.__name__ + "('" + nameField + "')" + "\n"
                    elif method.__name__.startswith("updateOutputMED"):
                        (nameField, _) = getNameFieldInput(*args, **kwargs)
                        toWritePython = self.tracerObjectName + "." + method.__name__ + "('" + nameField + "', " + nameField + "_" + self.tracerObjectName + ")" + "\n"
                    else:
                        stringArgs = getArgsString(*args, **kwargs)
                        toWritePython = self.tracerObjectName + "." + method.__name__ + stringArgs + "\n"

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

                self.tracerRecurrenceDepth += 1

                start = time.time()

                try:
                    result = method(self, *args, **kwargs)
                except:
                    if self.static_pythonFile is not None:
                        toWritePython = "try: " + toWritePython + "except: pass" + "\n"
                    raise
                else:
                    end = time.time()
                finally:
                    if self.static_pythonFile is not None:
                        self.static_pythonFile.write(toWritePython)
                        self.static_pythonFile.flush()
                    self.tracerRecurrenceDepth -= 1

                    if self.static_stdout is not None:
                        sys.stdout.flush()
                        os.dup2(prevIdstdout, sys.stdout.fileno())
                        os.close(prevIdstdout)
                    if self.static_stderr is not None:
                        sys.stderr.flush()
                        os.dup2(prevIdstderr, sys.stderr.fileno())
                        os.close(prevIdstderr)

                if self.static_saveOutputMED and (method.__name__.startswith("getOutputMED") or method.__name__.startswith("updateOutputMED")):
                    nameField = getNameInput(*args, **kwargs)
                    nameMEDFile = name + "_output_" + nameField + "_"
                    num = 0
                    while os.path.exists(nameMEDFile + str(num) + ".med"):
                        num += 1
                    nameMEDFile = nameMEDFile + str(num) + ".med"
                    mc.WriteField(nameMEDFile, result, True)

                if self.static_lWriter is not None:
                    if method.__name__ in ["initialize", "computeTimeStep", "initTimeStep", "solveTimeStep", "iterateTimeStep",
                                           "validateTimeStep", "setStationaryMode", "abortTimeStep", "resetTime", "terminate", "exchange",
                                           "save", "restore"]:
                        inputVar = 0.
                        if method.__name__ == "initTimeStep":
                            inputVar = getDtInput(*args, **kwargs)
                        elif method.__name__ == "setStationaryMode":
                            inputVar = getStationaryModeInput(*args, **kwargs)
                        elif method.__name__ == "resetTime":
                            inputVar = getTimeInput(*args, **kwargs)
                        elif method.__name__ in ["save", "restore"]:
                            inputVar = getArgsString(*getSaveInput(*args, **kwargs))

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

        icocoMethods = ["setDataFile", "setMPIComm", "initialize", "terminate", "presentTime", "computeTimeStep", "initTimeStep", "solveTimeStep", "validateTimeStep", "setStationaryMode",
                        "getStationaryMode", "isStationary", "abortTimeStep", "resetTime", "iterateTimeStep", "save", "restore", "forget", "getInputFieldsNames", "getOutputFieldsNames",
                        "getFieldType", "getMeshUnit", "getFieldUnit", "getInputMEDDoubleFieldTemplate", "setInputMEDDoubleField", "getOutputMEDDoubleField", "updateOutputMEDDoubleField",
                        "getInputMEDIntFieldTemplate", "setInputMEDIntField", "getOutputMEDIntField", "updateOutputMEDIntField", "getInputMEDStringFieldTemplate", "setInputMEDStringField",
                        "getOutputMEDStringField", "updateOutputMEDStringField", "getInputValuesNames", "getOutputValuesNames", "getValueType", "getValueUnit", "setInputDoubleValue",
                        "getOutputDoubleValue", "setInputIntValue", "getOutputIntValue", "setInputStringValue", "getOutputStringValue"]
        for method in icocoMethods:
            if method not in newDct:
                for base in bases:
                    if hasattr(base, method):
                        newDct[method] = _wrapper(getattr(base, method))
                        break

        return type.__new__(cls, name, bases, newDct)


def tracer(pythonFile=None, saveInputMED=False, saveOutputMED=False, stdoutFile=None, stderrFile=None, listingWriter=None):
    """! tracer is a class wrapper allowing to trace the calls of the methods of the base class.

    tracer is to be applied on a class (not an object) and return a new class that inherits from the provided one.

    It has different functions:

    1. It can write all calls of the methods of the base class in a text file in python format in order to allow to replay what
        happened from the code point of view outside of the coupling.
    2. It can save in .med files input or output MEDFields.
    3. It can redirect code standard and error outputs in text files.
    4. It can contribute (with ListingWriter) to the writing of a global coupling listing file with calculation time measurement.

    @param pythonFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The python script
        is written there. It has to be closed (file.close()) by caller. The script can be run only if saveInputMED is set to True:
        otherwise, input MED fields are not stored.
    @param saveInputMED if set to True, every time setInputMED(Double/Int/String)Field is called, the input MED field is stored in
        a .med file. If pythonFile is activated, a MEDLoader reading instruction is also written in the Python file.
    @param saveOutputMED if set to True, every time getOutputMED(Double/Int/String)Field is called, the output MED field is stored
        in a .med file.
    @param stdoutFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The standard output
        is redirected there. It has to be closed (file.close()) by caller.
    @param stderrFile a file object which has to be already open in written mode (file = open("file.txt", "w")). The error output is
        redirected there. It has to be closed (file.close()) by caller.
    @param listingWriter a ListingWriter object which will manage the writing of the coupling listing file. Refer to the documentation
        of ListingWriter.

    The parameters of tracer are added to the class ("static" attributes) with the names static_pythonFile, static_saveInputMED,
    static_saveOutputMED, static_stdout, static_stderr and static_lWriter.

    One additional static attribute is added for internal use: static_Objectcounter.

    Two additional attributes (not static!) are added for internal use: tracerObjectName and tracerRecurrenceDepth.

    tracer can be used either as a python decorator (where the class is defined) in order to modify the class definition everywhere:

        @c3po.tracer(...)
        class MyClass(...):
            ...

    or it can be used in order to redefined only locally the class like that:

        MyNewClass = c3po.tracer(...)(MyClass)

    @note In case a method calls another method of self, tracer modifies only to the first method call.

    @warning tracer can be applied to any class, but it is design for standard C3PO objects: PhysicsDriver, DataManager and Exchanger.
            It may be hazardous to use on "similar but not identical" classes (typically with the same methods but different inputs and/or
            outputs).
    @warning tracer looks for ICoCo methods (the methods to implement in order to define a PhysicsDriver) in base classes and redefine
            them. Other inherited methods are invisible to tracer.
    @warning A class that inherits from a class wrapped by tracer will be wrapped as well, with the same parameters.
            It may be a workaround for the previous warning.
            The definition of the daughter class ("class Daughter(Mother): ...") must be done after the application of tracer on Mother.
            Otherwise it will result in TypeError when the daughter class will try to call mother methods (since its mother class does
            not exist anymore!). As a consequence, if tracer is to be applied to C3PO classes, it is recommended to change their name
            "(MyNewClass = c3po.tracer(...)(MyClass)").

    @throw Exception if applied to a class already modified by tracer, because it could result in an unexpected behavior.
    """

    def classWrapper(baseclass):
        if pythonFile is not None:
            pythonFile.write("# -*- coding: utf-8 -*-" + "\n")
            pythonFile.write("from __future__ import print_function, division" + "\n")
            pythonFile.write("import c3po.medcouplingCompat as mc" + "\n")
            pythonFile.write("from " + baseclass.__module__ + " import " + baseclass.__name__ + "\n" + "\n")

        if hasattr(baseclass, "static_pythonFile"):
            raise Exception("tracer: the class " + baseclass.__name__ + " has already been modified by tracer. It is not allowed.")
        baseclass.static_pythonFile = pythonFile
        baseclass.static_saveInputMED = saveInputMED
        baseclass.static_saveOutputMED = saveOutputMED
        baseclass.static_stdout = stdoutFile
        baseclass.static_stderr = stderrFile
        baseclass.static_lWriter = listingWriter
        newclass = TracerMeta(baseclass.__name__, (baseclass,), baseclass.__dict__)
        newclass.__doc__ = baseclass.__doc__
        delattr(baseclass, "static_pythonFile")
        delattr(baseclass, "static_saveInputMED")
        delattr(baseclass, "static_saveOutputMED")
        delattr(baseclass, "static_stdout")
        delattr(baseclass, "static_stderr")
        delattr(baseclass, "static_lWriter")
        return newclass
    return classWrapper
