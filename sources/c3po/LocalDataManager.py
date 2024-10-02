# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class LocalDataManager. """
from __future__ import print_function, division
import math
import numpy

from c3po.DataManager import DataManager
from c3po.DataAccessor import DataAccessor


class LocalDataManager(DataManager, DataAccessor):
    """! LocalDataManager is the implementation of DataManager for local data. It also implements DataAccessor.

    Data can be double, int, string, fields of double of fields of int.
    Only double and fields of double are affected by the methods herited from DataManager.
    Other data are just (shallow) copied in new objects created by these methods.
    """

    def __init__(self):
        """! Default constructor """
        self.valuesDouble = {}
        self.valuesInt = {}
        self.valuesString = {}
        self.fieldsDouble = {}
        self.fieldsInt = {}
        self.fieldsDoubleTemplates = {}

    def clone(self):
        """! Return a clone of self.

        @return A clone of self. Data are copied.
        """
        return self * 1.

    def cloneEmpty(self):
        """! Return a clone of self without copying the data.

        @return An empty clone of self.
        """
        output = LocalDataManager()
        output.valuesInt = self.valuesInt
        output.valuesString = self.valuesString
        output.fieldsInt = self.fieldsInt
        output.fieldsDoubleTemplates = self.fieldsDoubleTemplates
        return output

    def copy(self, other):
        """! Copy data of other in self.

        @param other a LocalDataManager with the same list of data than self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.valuesDouble:
            self.valuesDouble[name] = other.valuesDouble[name]
        for name in self.fieldsDouble:
            otherArray = other.fieldsDouble[name].getArray()
            self.fieldsDouble[name].getArray().setPartOfValues1(other.fieldsDouble[name].getArray(), 0, otherArray.getNumberOfTuples(), 1, 0, otherArray.getNumberOfComponents(), 1)

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields.
        """
        norm = 0.
        for scalar in self.valuesDouble.values():
            if abs(scalar) > norm:
                norm = abs(scalar)
        for med in self.fieldsDouble.values():
            normMED = med.normMax()
            try:
                normMED = max(normMED)
            except:
                pass
            if normMED > norm:
                norm = normMED
        return norm

    def norm2(self):
        """! Return the norm 2.

        @return sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.
        """
        norm = 0.
        for scalar in self.valuesDouble.values():
            norm += scalar * scalar
        for med in self.fieldsDouble.values():
            localNorm = med.norm2()
            norm += localNorm * localNorm
        return math.sqrt(norm)

    def checkBeforeOperator(self, other):
        """! INTERNAL Make basic checks before the call of an operator: same data names between self and other. """
        if len(self.valuesDouble) != len(other.valuesDouble) or len(self.fieldsDouble) != len(other.fieldsDouble):
            raise Exception("LocalDataManager.checkBeforeOperator : we cannot call an operator between two LocalDataManager with different number of stored data.")
        for name in self.valuesDouble:
            if name not in other.valuesDouble:
                raise Exception("LocalDataManager.checkBeforeOperator : we cannot call an operator between two LocalDataManager with different data.")
        for name in self.fieldsDouble:
            if name not in other.fieldsDouble:
                raise Exception("LocalDataManager.checkBeforeOperator : we cannot call an operator between two LocalDataManager with different data.")

    def __add__(self, other):
        """! Return self + other.

        Use "+" to call it. For example a = b + c.

        @param other a LocalDataManager with the same list of data then self.

        @return a new (consistent with self) LocalDataManager where the data are added.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        newData = self.cloneEmpty()
        for name in self.valuesDouble:
            newData.valuesDouble[name] = self.valuesDouble[name] + other.valuesDouble[name]
        for name in self.fieldsDouble:
            newData.fieldsDouble[name] = 1. * self.fieldsDouble[name]
            newData.fieldsDouble[name].getArray().addEqual(other.fieldsDouble[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return newData

    def __iadd__(self, other):
        """! Add other in self (in place addition).

        Use "+=" to call it. For example a += b.

        @param other a LocalDataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.valuesDouble:
            self.valuesDouble[name] += other.valuesDouble[name]
        for name in self.fieldsDouble:
            self.fieldsDouble[name].getArray().addEqual(other.fieldsDouble[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return self

    def __sub__(self, other):
        """! Return self - other.

        Use "-" to call it. For example a = b - c.

        @param other a LocalDataManager with the same list of data then self.

        @return a new (consistent with self) LocalDataManager where the data are substracted.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        newData = self.cloneEmpty()
        for name in self.valuesDouble:
            newData.valuesDouble[name] = self.valuesDouble[name] - other.valuesDouble[name]
        for name in self.fieldsDouble:
            newData.fieldsDouble[name] = 1. * self.fieldsDouble[name]
            newData.fieldsDouble[name].getArray().substractEqual(other.fieldsDouble[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return newData

    def __isub__(self, other):
        """! Substract other to self (in place subtraction).

        Use "-=" to call it. For example a -= b.

        @param other a LocalDataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.valuesDouble:
            self.valuesDouble[name] -= other.valuesDouble[name]
        for name in self.fieldsDouble:
            self.fieldsDouble[name].getArray().substractEqual(other.fieldsDouble[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return self

    def __mul__(self, scalar):
        """! Return scalar * self.

        Use "*" to call it. For example a = b * c. The scalar first.

        @param scalar a scalar value.

        @return a new (consistent with self) LocalDataManager where the data are multiplied by scalar.
        """
        newData = self.cloneEmpty()
        for name in self.valuesDouble:
            newData.valuesDouble[name] = scalar * self.valuesDouble[name]
        for name in self.fieldsDouble:
            newData.fieldsDouble[name] = scalar * self.fieldsDouble[name]
        return newData

    def __imul__(self, scalar):
        """! Multiply self by scalar (in place multiplication).

        Use "*=" to call it. For example a *= b.

        @param scalar a scalar value.

        @return self.
        """
        for name in self.valuesDouble:
            self.valuesDouble[name] *= scalar
        for name in self.fieldsDouble:
            self.fieldsDouble[name] *= scalar
        return self

    def imuladd(self, scalar, other):
        """! Add in self scalar * other (in place operation).

        In order to do so, other *= scalar and other *= 1./scalar are done.

        For example a.imuladd(b, c).

        @param scalar a scalar value.
        @param other a LocalDataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        if scalar == 0:
            return self
        self.checkBeforeOperator(other)
        other *= scalar
        self += other
        other *= 1. / scalar
        return self

    def dot(self, other):
        """! Return the scalar product of self with other.

        @param other a LocalDataManager with the same list of data then self.

        @return the scalar product of self with other.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        result = 0.
        for name in self.valuesDouble:
            result += self.valuesDouble[name] * other.valuesDouble[name]
        for name in self.fieldsDouble:
            nparr1 = self.fieldsDouble[name].getArray().toNumPyArray()
            nparr2 = other.fieldsDouble[name].getArray().toNumPyArray()
            dim = 1
            if self.fieldsDouble[name].getArray().getNumberOfComponents() > 1:
                dim = 2
            result += numpy.tensordot(nparr1, nparr2, dim)
        return result

    def setInputMEDDoubleField(self, name, field):
        """! Store the MED field field under the name name.

        @param name the name given to the field to store.
        @param field a field to store.
        """
        self.fieldsDouble[name] = field

    def getOutputMEDDoubleField(self, name):
        """! Return the MED field of name name previously stored.

        @param name the name of the field to return.

        @return the MED field of name name previously stored.

        @throw Exception If there is no stored name Double field.
        """
        if name not in self.fieldsDouble:
            raise Exception("LocalDataManager.getOutputMEDDoubleField unknown field " + name)
        return self.fieldsDouble[name]

    def setInputMEDIntField(self, name, field):
        """! Similar to setInputMEDDoubleField() but for MEDIntField. """
        self.fieldsInt[name] = field

    def getOutputMEDIntField(self, name):
        """! Similar to getOutputMEDDoubleField() but for MEDIntField. """
        if name not in self.fieldsInt:
            raise Exception("LocalDataManager.getOutputMEDIntField unknown field " + name)
        return self.fieldsInt[name]

    def getFieldType(self, name):
        """! Return the type of a previously stored field. """
        if name in self.fieldsDouble:
            return DataAccessor.ValueType.Double
        if name in self.fieldsInt:
            return DataAccessor.ValueType.Int
        raise Exception("LocalDataManager.getFieldType unknown field " + name)

    def setInputDoubleValue(self, name, value):
        """! Store the scalar value under the name name.

        @param name the name given to the scalar to store.
        @param value a scalar value to store.
        """
        self.valuesDouble[name] = value

    def getOutputDoubleValue(self, name):
        """! Return the scalar of name name previously stored.

        @param name the name of the value to return.

        @return the value of name name previously stored.

        @throw Exception If there is no stored name Double value.
        """
        if name not in self.valuesDouble:
            raise Exception("LocalDataManager.getOutputDoubleValue unknown value " + name)
        return self.valuesDouble[name]

    def setInputIntValue(self, name, value):
        """! Similar to setInputDoubleValue() but for Int. """
        self.valuesInt[name] = value

    def getOutputIntValue(self, name):
        """! Similar to getOutputDoubleValue() but for Int. """
        if name not in self.valuesInt:
            raise Exception("LocalDataManager.getOutputIntValue unknown value " + name)
        return self.valuesInt[name]

    def setInputStringValue(self, name, value):
        """! Similar to setInputDoubleValue() but for String. """
        self.valuesString[name] = value

    def getOutputStringValue(self, name):
        """! Similar to getOutputDoubleValue() but for String. """
        if name not in self.valuesString:
            raise Exception("LocalDataManager.getOutputStringValue unknown value " + name)
        return self.valuesString[name]

    def getValueType(self, name):
        """! Return the type of a previously stored field. """
        if name in self.valuesDouble:
            return DataAccessor.ValueType.Double
        if name in self.valuesInt:
            return DataAccessor.ValueType.Int
        if name in self.valuesString:
            return DataAccessor.ValueType.String
        raise Exception("LocalDataManager.getValueType unknown scalar " + name)

    def setInputMEDDoubleFieldTemplate(self, name, field):
        """! Store the MED field field as a MEDFieldTemplate under the name name.

        @param name the name given to the field to store.
        @param field a field to store.

        @note These fields are not be part of data, and will therefore not be taken into account in data manipulations (operators, norms etc.).
        """
        self.fieldsDoubleTemplates[name] = field

    def getInputMEDDoubleFieldTemplate(self, name):
        """! Return the MED field previously stored as a MEDDoubleFieldTemplate under the name name. If there is not, returns 0.

        @param name the name of the field to return.

        @return the MED field of name name previously stored, or 0.
        """
        if name not in self.fieldsDoubleTemplates:
            return 0
        return self.fieldsDoubleTemplates[name]
