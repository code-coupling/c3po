# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the meta-class CheckScopeMeta and class wrapper checkScope. """

from types import FunctionType

import icoco
import icoco.utils

def _scopeInit(self):
    """! INTERNAL """
    if not hasattr(self, 'problemName'):
        self.problemName = f"{self.__class__.__module__}.{self.__class__.__name__}"
    self.iCoCoEnsureScope = True
    self._iCoCoInitialized = False
    self._iCoCoTimeStepDefined = False

def _decoratorInitialized(method):
    """! INTERNAL """
    # pylint: disable=protected-access
    def checkInitialized(self, *args, **kwargs):
        if self.iCoCoEnsureScope and not self._iCoCoInitialized:
            raise icoco.WrongContext(prob=self.problemName,
                               method=method.__name__,
                               precondition="called before initialize() or after terminate().")
        result = method(self, *args, **kwargs)
        if method.__name__ == 'terminate':
            self._iCoCoInitialized = False
        return result

    def checkNotInitialized(self, *args, **kwargs):
        if self.iCoCoEnsureScope and self._iCoCoInitialized:
            raise icoco.WrongContext(prob=self.problemName,
                               method=method.__name__,
                               precondition="called between initialize() and terminate().")
        result = method(self, *args, **kwargs)
        if method.__name__ == 'initialize':
            self._iCoCoInitialized = True
        return result
    if method.__name__ in icoco.utils.ICoCoMethodContext.ONLY_BEFORE_INITIALIZE:
        newMethod = checkNotInitialized
    elif method.__name__ in icoco.utils.ICoCoMethodContext.ONLY_AFTER_INITIALIZE:
        newMethod = checkInitialized
    else:
        return method
    newMethod.__name__ = method.__name__
    newMethod.__doc__ = method.__doc__
    newMethod.__dict__.update(method.__dict__)
    return newMethod

def _decoratorTimeStepContext(method):
    """! INTERNAL """
    # pylint: disable=protected-access
    def checkInsideTimeStep(self, *args, **kwargs):
        if self.iCoCoEnsureScope and not self._iCoCoTimeStepDefined:
            raise icoco.WrongContext(prob=self.problemName,
                               method=method.__name__,
                               precondition="called outside the TIME_STEP_DEFINED context.")
        result = method(self, *args, **kwargs)
        if method.__name__ in ['abortTimeStep', 'validateTimeStep']:
            self._iCoCoTimeStepDefined = False
        return result

    def checkOutsideTimeStep(self, *args, **kwargs):
        if self.iCoCoEnsureScope and self._iCoCoTimeStepDefined:
            raise icoco.WrongContext(prob=self.problemName,
                               method=method.__name__,
                               precondition="called inside the TIME_STEP_DEFINED context.")
        result = method(self, *args, **kwargs)
        if method.__name__ == 'initTimeStep':
            self._iCoCoTimeStepDefined = True
        return result

    if method.__name__ in icoco.utils.ICoCoMethodContext.ONLY_INSIDE_TIME_STEP_DEFINED:
        newMethod = checkInsideTimeStep
    elif method.__name__ in icoco.utils.ICoCoMethodContext.ONLY_OUTSIDE_TIME_STEP_DEFINED:
        newMethod = checkOutsideTimeStep
    else:
        return method
    newMethod.__name__ = method.__name__
    newMethod.__doc__ = method.__doc__
    newMethod.__dict__.update(method.__dict__)
    return newMethod

def _decoratorInit(method):
    """! INTERNAL """
    # pylint: disable=protected-access
    def completedInit(self, *args, **kwargs):
        method(self, *args, **kwargs)
        _scopeInit(self)
    completedInit.__name__ = method.__name__
    completedInit.__doc__ = method.__doc__
    completedInit.__dict__.update(method.__dict__)
    return completedInit

class CheckScopeMeta(type):
    """! Metaclass related to the use of checkScope. """

    def __new__(cls, name, bases, dct):

        toCheck = set()
        for name in icoco.utils.ICoCoMethodContext.ONLY_INSIDE_TIME_STEP_DEFINED + icoco.utils.ICoCoMethodContext.ONLY_OUTSIDE_TIME_STEP_DEFINED + icoco.utils.ICoCoMethodContext.ONLY_BEFORE_INITIALIZE + icoco.utils.ICoCoMethodContext.ONLY_AFTER_INITIALIZE:
            if name not in toCheck:
                toCheck.add(name)

        newDct = {}
        for nameattr, item in dct.items():
            if isinstance(item, FunctionType):
                if item.__name__ == '__init__':
                    newDct[nameattr] = _decoratorInit(item)
                else:
                    if item.__name__ in toCheck:
                        newDct[nameattr] = _decoratorTimeStepContext(item)
                        newDct[nameattr] = _decoratorInitialized(newDct[nameattr])
            if nameattr not in newDct:
                newDct[nameattr] = item

        if '__init__' not in newDct:
            def newInit(self):
                for base in bases:
                    super(base, self).__init__()
                _scopeInit(self)
            newInit.__name__ = "__init__"
            newDct['__init__'] = newInit

        for nameattr in toCheck:
            if nameattr not in newDct:
                for base in bases:
                    if hasattr(base, nameattr):
                        item = getattr(base, nameattr)
                        newDct[nameattr] = _decoratorTimeStepContext(item)
                        newDct[nameattr] = _decoratorInitialized(newDct[nameattr])
                        break

        return type.__new__(cls, name, bases, newDct)

def checkScope(baseclass):
    """! Add a verification of the calling context of ICoCo methods.

    checkScope is to be applied on a class (not an object) and return a new class that inherits from the provided one.

    checkScope has the following effects:
      - It raises icoco.WrongContext errors when an ICoCo method is called in a wrong context (see ICoCo documentation).
      - It adds an object attribute 'problemName' used in the message of these icoco.WrongContext errors. Default: f"{self.__class__.__module__}.{self.__class__.__name__}"
      - It also adds the object attribute 'iCoCoEnsureScope' that can be used to activate / desactivate these checks. Default: iCoCoEnsureScope=True which means activated.

    Two additional object attributes are added for internal use: _iCoCoInitialized and _iCoCoTimeStepDefined.

    @param baseclass the class to modify.

    @return A new class, with modified methods.

    checkScope can be used either as a python decorator (where the class is defined) in order to modify the class definition everywhere:

    ```
    @c3po.raises.checkScope
    class MyClass(...):
        ...
    ```

    or it can be used in order to redefined only locally the class like that:

    ```
    MyNewClass = c3po.raises.checkScope(MyClass)
    ```

    @note checkScope looks for ICoCo methods definitions in base classes in order to overload them.
    @note checkScope relies on a metaclass (c3po.raises.checkScope.CheckScopeMeta). That means that daughter classes will also be modified by checkScope.

    @warning It is recommended not to overload a class:
            use "MyNewClass = c3po.raises.checkScope(MyClass)" and not "MyClass = c3po.raises.checkScope(MyClass)".
            Overloading a class may lead to TypeError, in particular in case of inheritance, if the mother class is not accessible any more.
    """
    newclass = CheckScopeMeta(baseclass.__name__, (baseclass,), baseclass.__dict__)
    newclass.__doc__ = baseclass.__doc__
    return newclass
