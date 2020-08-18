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
import time
import sys
import os

from MEDLoader import MEDLoader


def get_setInputMEDField_input(name, field):
    """ For internal use only. """
    return (name, field)


def get_initTimeStep_input(dt):
    """ For internal use only. """
    return dt


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
        self.static_MEDinfo = {}
        self.static_Objectcounter = {}

    def __new__(metacls, name, bases, dct):
        pythonFile = None
        saveMED = True
        stdout = None
        stderr = None
        lWriter = None
        if "static_pythonFile" not in dct:
            for baseclass in bases:
                if hasattr(baseclass, "static_pythonFile"):
                    pythonFile = baseclass.static_pythonFile
                    saveMED = baseclass.static_saveMED
                    stdout = baseclass.static_stdout
                    stderr = baseclass.static_stderr
                    lWriter = baseclass.static_lWriter
        else:
            pythonFile = dct["static_pythonFile"]
            saveMED = dct["static_saveMED"]
            stdout = dct["static_stdout"]
            stderr = dct["static_stderr"]
            lWriter = dct["static_lWriter"]

        def _wrapper(method):
            def _trace(self, *args, **kwargs):
                if pythonFile is not None:
                    objectNameBase = "my" + name
                    if objectNameBase not in self.static_Objectcounter:
                        self.static_Objectcounter[objectNameBase] = 0
                    objectName = "my" + name + str(self.static_Objectcounter[objectNameBase])
                    string_args = getArgsString(*args, **kwargs)
                    if method.__name__ == "__init__":
                        self.static_Objectcounter[objectNameBase] += 1
                        objectName = "my" + name + str(self.static_Objectcounter[objectNameBase])
                        pythonFile.write(objectName + " = " + name + string_args + "\n")
                    elif method.__name__ == "setInputMEDField":
                        (name_field, field) = get_setInputMEDField_input(*args, **kwargs)
                        if saveMED:
                            if name_field not in self.static_MEDinfo:
                                self.static_MEDinfo[name_field] = []
                            nameMEDFile = name_field + str(len(self.static_MEDinfo[name_field])) + ".med"
                            timeMED, iteration, order = field.getTime()
                            self.static_MEDinfo[name_field].append((field.getTypeOfField(), nameMEDFile, field.getMesh().getName(), 0, field.getName(), iteration, order))
                            MEDLoader.WriteField(nameMEDFile, field, True)
                            pythonFile.write("field_" + objectName + " = MEDLoader.ReadField" + str(self.static_MEDinfo[name_field][-1]) + "\n")
                        pythonFile.write(objectName + "." + method.__name__ + "('" + name_field + "', field_" + objectName + ")" + "\n")
                    else:
                        pythonFile.write(objectName + "." + method.__name__ + string_args + "\n")
                    pythonFile.flush()

                if lWriter is not None:
                    if method.__name__ in ["initialize"]:
                        lWriter.writeBefore(self, method.__name__, time.time())

                prev_idstdout = 0
                prev_idstderr = 0
                if stdout is not None:
                    prev_idstdout = os.dup(sys.stdout.fileno())
                    os.dup2(stdout.fileno(), sys.stdout.fileno())
                if stderr is not None:
                    prev_idstderr = os.dup(sys.stderr.fileno())
                    os.dup2(stderr.fileno(), sys.stderr.fileno())

                start = time.time()

                result = method(self, *args, **kwargs)

                end = time.time()

                if stdout is not None:
                    os.dup2(prev_idstdout, sys.stdout.fileno())
                    os.close(prev_idstdout)
                if stderr is not None:
                    os.dup2(prev_idstderr, sys.stderr.fileno())
                    os.close(prev_idstderr)

                if lWriter is not None:
                    if method.__name__ in ["initialize", "computeTimeStep", "initTimeStep", "solveTimeStep", "iterateTimeStep", "validateTimeStep", "abortTimeStep", "terminate", "exchange"]:
                        input_var = 0.
                        if method.__name__ == "initTimeStep":
                            input_var = get_initTimeStep_input(*args, **kwargs)
                        lWriter.writeAfter(self, input_var, result, method.__name__, end, end - start)

                return result

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


def tracer(pythonFile=None, saveMED=True, stdoutFile=None, stderrFile=None, listingWriter=None):
    """ tracer is a class wrapper allowing to trace the calls of the methods of the base class. 

    It has different functions:

        1. It can write all calls of the methods of the base class in a text file in python format in order to allow to replay what happened from the code point of view outside of the coupling.
        2. It can redirect code standard and error outputs in text files.
        3. It can contribute (with listingWriter) to the writing of a global coupling listing file with calculation time measurement.

    .. warning:: The listing redirection seems to need a prior writing in the standard output (print(whatever)).
    .. warning:: tracer can be applied to any class, but it is design for standard C3PO objects: physicsDriver, dataManager and exchanger. It may be hazardous to use on "similar but not identical" classes (typically with the same methods but different inputs and/or outputs).
    .. warning:: tracer only modify the base class, not its parents. As a consequence, inherited methods are invisible to tracer. Redefine them in the final class if needed.

    :param pythonFile: a file object which has to be already open in written mode (file = open("file.txt", "w")). The python script is written there. It has to be closed (file.close()) by caller.
    :param saveMED: This is related to the python file writing.
        - if set to True (default value), every time setInputMEDField is called, the input MED field is stored in an independant .med file, and MEDLoader reading call is written in the output file. 
        - if set to False, the MED field is not stored and the MEDLoader call is not written. Only the setInputMEDField call is written. The replay is not possible.
    :param stdoutFile: a file object which has to be already open in written mode (file = open("file.txt", "w")). The standard output is redirected there. It has to be closed (file.close()) by caller.
    :param stderrFile: a file object which has to be already open in written mode (file = open("file.txt", "w")). The error output is redirected there. It has to be closed (file.close()) by caller.
    :param listingWriter: a listingWriter object which will manage the writing of the coupling listing file. Refer to the documentation of listingWriter.
    
    The parameters of tracer are added to the class ("static" attributes) with the names static_pythonFile and static_saveMED, static_stdout, static_stderr and static_lWriter.
    Two additional static attributes are added for internal use: static_MEDinfo and static_Objectcounter.

    tracer can be used either as a python decorator (where the class is defined) in order to modify the class definition everywhere:
        @C3PO.tracer(...)
        class myclass(...): 
            ...

    or it can be used in order to redefined only locally the class like that:
        myclass = C3PO.tracer(...)(myclass)

    tracer cannot distinguish different instance of the same class. The name of the instance created in the python file changes each time the __init__ method is called. This means that when a new instance is created, tracer assumes that the previous ones are not used any more. If this is not the case, put the ouput of each instance in its own output file :

        myclass1 = C3PO.tracer(pythonFile=file1, ...)(myclass)
        myclass2 = C3PO.tracer(pythonFile=file2, ...)(myclass)
        instance1 = myclass1()
        instance2 = myclass2()

    """

    def classWrapper(baseclass):
        if pythonFile is not None:
            pythonFile.write("# -*- coding: utf-8 -*-" + "\n")
            pythonFile.write("from __future__ import print_function, division" + "\n")
            pythonFile.write("from MEDLoader import MEDLoader" + "\n")
            pythonFile.write("from " + baseclass.__module__ + " import " + baseclass.__name__ + "\n" + "\n")
        baseclass.static_pythonFile = pythonFile
        baseclass.static_saveMED = saveMED
        baseclass.static_stdout = stdoutFile
        baseclass.static_stderr = stderrFile
        baseclass.static_lWriter = listingWriter
        newclass = tracerMeta(baseclass.__name__, baseclass.__bases__, baseclass.__dict__)
        newclass.__doc__ = baseclass.__doc__
        return newclass
    return classWrapper
