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

    Data are scalars or MEDCoupling fields, identified by their names.
    """

    def __init__(self):
        """! Default constructor """
        self.values = {}
        self.medFields = {}
        self.medFieldTemplates = {}

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
        output.medFieldTemplates = self.medFieldTemplates
        return output

    def copy(self, other):
        """! Copy data of other in self.

        @param other a LocalDataManager with the same list of data than self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.values.keys():
            self.values[name] = other.values[name]
        for name in self.medFields.keys():
            otherArray = other.medFields[name].getArray()
            self.medFields[name].getArray().setPartOfValues1(other.medFields[name].getArray(), 0, otherArray.getNumberOfTuples(), 1, 0, otherArray.getNumberOfComponents(), 1)

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields.
        """
        norm = 0.
        for scalar in self.values.values():
            if abs(scalar) > norm:
                norm = abs(scalar)
        for med in self.medFields.values():
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
        for scalar in self.values.values():
            norm += scalar * scalar
        for med in self.medFields.values():
            localNorm = med.norm2()
            norm += localNorm * localNorm
        return math.sqrt(norm)

    def checkBeforeOperator(self, other):
        """! INTERNAL Make basic checks before the call of an operator: same data names between self and other. """
        if len(self.values.keys()) != len(other.values.keys()) or len(self.medFields.keys()) != len(other.medFields.keys()):
            raise Exception("LocalDataManager.checkBeforeOperator : we cannot call an operator between two LocalDataManager with different number of stored data.")
        for name in self.values.keys():
            if not name in other.values.keys():
                raise Exception("LocalDataManager.checkBeforeOperator : we cannot call an operator between two LocalDataManager with different data.")
        for name in self.medFields.keys():
            if not name in other.medFields.keys():
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
        for name in self.values.keys():
            newData.values[name] = self.values[name] + other.values[name]
        for name in self.medFields.keys():
            newData.medFields[name] = 1. * self.medFields[name]
            newData.medFields[name].getArray().addEqual(other.medFields[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return newData

    def __iadd__(self, other):
        """! Add other in self (in place addition).

        Use "+=" to call it. For example a += b.

        @param other a LocalDataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.values.keys():
            self.values[name] += other.values[name]
        for name in self.medFields.keys():
            self.medFields[name].getArray().addEqual(other.medFields[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
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
        for name in self.values.keys():
            newData.values[name] = self.values[name] - other.values[name]
        for name in self.medFields.keys():
            newData.medFields[name] = 1. * self.medFields[name]
            newData.medFields[name].getArray().substractEqual(other.medFields[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return newData

    def __isub__(self, other):
        """! Substract other to self (in place subtraction).

        Use "-=" to call it. For example a -= b.

        @param other a LocalDataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.values.keys():
            self.values[name] -= other.values[name]
        for name in self.medFields.keys():
            self.medFields[name].getArray().substractEqual(other.medFields[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return self

    def __mul__(self, scalar):
        """! Return scalar * self.

        Use "*" to call it. For example a = b * c. The scalar first.

        @param scalar a scalar value.

        @return a new (consistent with self) LocalDataManager where the data are multiplied by scalar.
        """
        newData = self.cloneEmpty()
        for name in self.values.keys():
            newData.values[name] = scalar * self.values[name]
        for name in self.medFields.keys():
            newData.medFields[name] = scalar * self.medFields[name]
        return newData

    def __imul__(self, scalar):
        """! Multiply self by scalar (in place multiplication).

        Use "*=" to call it. For example a *= b.

        @param scalar a scalar value.

        @return self.
        """
        for name in self.values.keys():
            self.values[name] *= scalar
        for name in self.medFields.keys():
            self.medFields[name] *= scalar
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
        for name in self.values.keys():
            result += self.values[name] * other.values[name]
        for name in self.medFields.keys():
            nparr1 = self.medFields[name].getArray().toNumPyArray()
            nparr2 = other.medFields[name].getArray().toNumPyArray()
            dim = 1
            if self.medFields[name].getArray().getNumberOfComponents() > 1:
                dim = 2
            result += numpy.tensordot(nparr1, nparr2, dim)
        return result

    def setInputMEDField(self, name, field):
        """! Store the MED field field under the name name.

        @param name the name given to the field to store.
        @param field a field to store.
        """
        self.medFields[name] = field

    def getOutputMEDField(self, name):
        """! Return the MED field of name name previously stored.

        @param name the name of the field to return.

        @return the MED field of name name previously stored.

        @throw Exception If there is no stored name field.
        """
        if name not in self.medFields.keys():
            raise Exception("LocalDataManager.getOutputMEDField unknown field " + name)
        return self.medFields[name]

    def setValue(self, name, value):
        """! Store the scalar value under the name name.

        @param name the name given to the scalar to store.
        @param value a scalar value to store.
        """
        self.values[name] = value

    def getValue(self, name):
        """! Return the scalar of name name previously stored.

        @param name the name of the value to return.

        @return the value of name name previously stored.

        @throw Exception If there is no stored name value.
        """
        if name not in self.values.keys():
            raise Exception("LocalDataManager.getValue unknown value " + name)
        return self.values[name]

    def setInputMEDFieldTemplate(self, name, field):
        """! Store the MED field field as a MEDFieldTemplate under the name name.

        @param name the name given to the field to store.
        @param field a field to store.

        @note These fields are not be part of data, and will therefore not be taken into account in data manipulations (operators, norms etc.).
        """
        self.medFieldTemplates[name] = field

    def getInputMEDFieldTemplate(self, name):
        """! Return the MED field previously stored as a MEDFieldTemplate under the name name. If there is not, returns 0.

        @param name the name of the field to return.

        @return the MED field of name name previously stored, or 0.
        """
        if name not in self.medFieldTemplates.keys():
            return 0
        return self.medFieldTemplates[name]
