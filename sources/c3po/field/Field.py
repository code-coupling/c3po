# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Contains the classes Exchanger."""
from __future__ import print_function, division

import c3po


class Field(object):
    """! Field is a class interface (to be implemented) which standardizes the data exchanged by the exchangers.

    Before an operation with another field should be calling the function checkBeforeOperator before computing the operation.
    """

    def checkBeforeOperator(self, other: "Field"):
        """! INTERNAL Make basic checks before the call of an operator: same data type, same lengths..."""
        raise NotImplementedError

    def clone(self):
        """! Return a clone of self.

        @return A clone of self. Data are copied.
        """
        return self * 1.

    def cloneEmpty(self):
        """! Return a clone of self without copying the data.

        @return An empty clone of self.
        """
        raise NotImplementedError

    def copy(self, other):
        """! Copy data of other in self.

        @param other a Field with the same list of data than self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        raise NotImplementedError

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields.
        """
        raise NotImplementedError

    def norm2(self):
        """! Return the norm 2.

        @return sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.
        """
        raise NotImplementedError

    def __add__(self, other: "Field"):
        """! Return self + other.

        Use "+" to call it. For example a = b + c.

        @param other a DataManager with the same list of data then self.

        @return a new (consistent with self) DataManager where the data are added.

        @throw Exception if self and other are not consistent.
        """
        raise NotImplementedError

    def __iadd__(self, other: "Field"):
        """! Add other in self (in place addition).

        Use "+=" to call it. For example a += b.

        @param other a DataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        raise NotImplementedError

    def __sub__(self, other: "Field"):
        """! Return self - other.

        Use "-" to call it. For example a = b - c.

        @param other a DataManager with the same list of data then self.

        @return a new (consistent with self) DataManager where the data are substracted.

        @throw Exception if self and other are not consistent.
        """
        raise NotImplementedError

    def __isub__(self, other: "Field"):
        """! Substract other to self (in place subtraction).

        Use "-=" to call it. For example a -= b.

        @param other a DataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        raise NotImplementedError

    def __mul__(self, scalar):
        """! Return scalar * self.

        Use "*" to call it. For example a = b * c. The scalar first.

        @param scalar a scalar value.

        @return a new (consistent with self) DataManager where the data are multiplied by scalar.
        """
        raise NotImplementedError

    def __imul__(self, scalar):
        """! Multiply self by scalar (in place multiplication).

        Use "*=" to call it. For example a *= b.

        @param scalar a scalar value.

        @return self.
        """
        raise NotImplementedError

    def __rmul__(self, scalar):
        """! Return self * scalar (reverse multiplication).

        Use "*" to call it. For example a = c * b.

        @param scalar a scalar value.

        @return a new (consistent with self) DataManager where the data are multiplied by scalar.
        """
        raise NotImplementedError

    def imuladd(self, scalar, other: "Field"):
        """! Add in self scalar * other (in place operation).

        In order to do so, other *= scalar and other *= 1./scalar are done.

        For example a.imuladd(b, c).

        @param scalar a scalar value.
        @param other a DataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        raise NotImplementedError

    def dot(self, other: "Field"):
        """! Return the scalar product of self with other.

        @param other a DataManager with the same list of data then self.

        @return the scalar product of self with other.

        @throw Exception if self and other are not consistent.
        """
        raise NotImplementedError


class ShortcutToObject(object):
    """! INTERNAL.
        Defines a physics driver get and set functions.
    """

    def __init__(self, container: c3po.PhysicsDriver, name, type_=None):
        """! INTERNAL."""
        self._container: c3po.PhysicsDriver = container
        self._name = name
        self._type = type_
        self._setMethod = None
        self._getMethod = None

    def initialize(self):
        """Stores the physics driver functions in _setMethod and _getMethod based on the data type """
        self._setMethod = self._container.setInputObject
        self._getMethod = self._container.getOutputObject

    def get(self):
        """This function provides the exchanger what it means to get(name), based on the initialized value."""
        if self._getMethod is None:
            self.initialize()
        return self._getMethod(self._name)

    def set(self, value):
        """This function provides the exchanger what it means to set(name, value), based on the initialized value."""
        if self._setMethod is None:
            self.initialize()
        self._setMethod(self._name, value)


class ObjectExchanger(c3po.LocalExchanger):
    def __init__(self,
                 method,
                 objectsToGet,
                 objectsToSet,
                 fieldsToGet=[], fieldsToSet=[],
                 valuesToGet=[], valuesToSet=[]):
        # In this exchanger, we only implement DirectMatching which does not edit the object between the get and the set.
        if not isinstance(method, c3po.DirectMatching):
            raise ValueError("method is expected to be c3po.DirectMatching")

        # Calling the c3po.LocalExchanger constructor with empty objects to build internal attributes, notable the _method.
        super().__init__(method, fieldsToGet, fieldsToSet, valuesToGet, valuesToSet)

        # objectsToGet and objectsToSet are provided as lists of tuples [ (PhysicsDriver, variableName) ].
        # Sometimes, the PhysicsDriver can be a CollaborativeObject which dispatches the objects on several drivers.
        # These _expandInputList calls unpack these dispatchings.
        objectsToGet = self._expandInputList(objectsToGet)
        objectsToSet = self._expandInputList(objectsToSet)

        # Building the ShortcutToObject objects that map the get and set functions on the PhysicsDrivers
        self._objectsToSet = [ShortcutToObject(*tupleData) for tupleData in objectsToSet]
        self._objectsToGet = [ShortcutToObject(*tupleData) for tupleData in objectsToGet]

    def exchange(self):
        """Exchange method, gets the value from the source and sets it at the target.
        """
        super().exchange()

        #   For each object to get, getting it from the physics driver
        objectsToGet = [ds.get() for ds in self._objectsToGet]

        objectsToSet = objectsToGet  # Setting the objects to set as equal the ones got as we implement DirectMatching

        #   We ensure we have as many objects to set as we had targets in the constructor.
        #   The object will be set in order
        if (len(objectsToSet) != len(self._objectsToSet)):
            expectedNb = len(self._fieldsToSet)
            foundNb = len(objectsToSet)
            raise Exception("objectExchanger.exchange the method does not have the good number of outputs (we got {} outputs instead of {}).". format(foundNb, expectedNb))

        #   For each object, setting it at the target
        for i, object in enumerate(objectsToSet):
            self._objectsToSet[i].set(object)
