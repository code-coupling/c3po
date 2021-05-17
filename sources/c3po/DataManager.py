# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class DataManager. """
from __future__ import print_function, division
import numpy
import math


class DataManager(object):
    """! DataManager stores and manipulates data outside of PhysicsDriver. This is necessary for some coupling techniques or time schemes.

    Data are scalars or MEDCoupling fields, identified by their names.
    """

    def __init__(self):
        """! Default constructor """
        self.values_ = {}
        self.MEDFields_ = {}
        self.MEDFieldTemplates_ = {}

    def clone(self):
        """! Return a clone of self.

        @return A clone of self. Data are copied.
        """
        return (self * 1.)

    def cloneEmpty(self):
        """! Return a clone of self without copying the data.

        @return An empty clone of self.
        """
        output = DataManager()
        output.MEDFieldTemplates_ = self.MEDFieldTemplates_
        return output

    def copy(self, other):
        """! Copy data of other in self.

        @param other a DataManager with the same list of data than self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.values_.keys():
            self.values_[name] = other.values_[name]
        for name in self.MEDFields_.keys():
            otherArray = other.MEDFields_[name].getArray()
            self.MEDFields_[name].getArray().setPartOfValues1(other.MEDFields_[name].getArray(), 0, otherArray.getNumberOfTuples(), 1, 0, otherArray.getNumberOfComponents(), 1)

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields.
        """
        norm = 0.
        for scalar in self.values_.values():
            if abs(scalar) > norm:
                norm = abs(scalar)
        for MED in self.MEDFields_.values():
            normMED = MED.normMax()
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
        for scalar in self.values_.values():
            norm += scalar * scalar
        for MED in self.MEDFields_.values():
            localNorm = MED.norm2()
            norm += localNorm * localNorm
        return math.sqrt(norm)

    def checkBeforeOperator(self, other):
        """! INTERNAL Make basic checks before the call of an operator: same data names between self and other. """
        if len(self.values_.keys()) != len(other.values_.keys()) or len(self.MEDFields_.keys()) != len(other.MEDFields_.keys()):
            raise Exception("DataManager.checkBeforeOperator : we cannot call an operator between two DataManager with different number of stored data.")
        for name in self.values_.keys():
            if not(name in other.values_.keys()):
                raise Exception("DataManager.checkBeforeOperator : we cannot call an operator between two DataManager with different data.")
        for name in self.MEDFields_.keys():
            if not(name in other.MEDFields_.keys()):
                raise Exception("DataManager.checkBeforeOperator : we cannot call an operator between two DataManager with different data.")

    def __add__(self, other):
        """! Return self + other.

        Use "+" to call it. For example a = b + c.

        @param other a DataManager with the same list of data then self.

        @return a new (consistent with self) DataManager where the data are added.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        new_data = self.cloneEmpty()
        for name in self.values_.keys():
            new_data.values_[name] = self.values_[name] + other.values_[name]
        for name in self.MEDFields_.keys():
            new_data.MEDFields_[name] = 1. * self.MEDFields_[name]
            new_data.MEDFields_[name].getArray().addEqual(other.MEDFields_[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return new_data

    def __iadd__(self, other):
        """! Add other in self (in place addition).

        Use "+=" to call it. For example a += b.

        @param other a DataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.values_.keys():
            self.values_[name] += other.values_[name]
        for name in self.MEDFields_.keys():
            self.MEDFields_[name].getArray().addEqual(other.MEDFields_[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return self

    def __sub__(self, other):
        """! Return self - other.

        Use "-" to call it. For example a = b - c.

        @param other a DataManager with the same list of data then self.

        @return a new (consistent with self) DataManager where the data are substracted.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        new_data = self.cloneEmpty()
        for name in self.values_.keys():
            new_data.values_[name] = self.values_[name] - other.values_[name]
        for name in self.MEDFields_.keys():
            new_data.MEDFields_[name] = 1. * self.MEDFields_[name]
            new_data.MEDFields_[name].getArray().substractEqual(other.MEDFields_[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return new_data

    def __isub__(self, other):
        """! Substract other to self (in place subtraction).

        Use "-=" to call it. For example a -= b.

        @param other a DataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for name in self.values_.keys():
            self.values_[name] -= other.values_[name]
        for name in self.MEDFields_.keys():
            self.MEDFields_[name].getArray().substractEqual(other.MEDFields_[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return self

    def __mul__(self, scalar):
        """! Return scalar * self.

        Use "*" to call it. For example a = b * c. The scalar first.

        @param scalar a scalar value.

        @return a new (consistent with self) DataManager where the data are multiplied by scalar.
        """
        new_data = self.cloneEmpty()
        for name in self.values_.keys():
            new_data.values_[name] = scalar * self.values_[name]
        for name in self.MEDFields_.keys():
            new_data.MEDFields_[name] = scalar * self.MEDFields_[name]
        return new_data

    def __imul__(self, scalar):
        """! Multiply self by scalar (in place multiplication).

        Use "*=" to call it. For example a *= b.

        @param scalar a scalar value.

        @return self.
        """
        for name in self.values_.keys():
            self.values_[name] *= scalar
        for name in self.MEDFields_.keys():
            self.MEDFields_[name] *= scalar
        return self

    def imuladd(self, scalar, other):
        """! Add in self scalar * other (in place operation).

        In order to do so, other *= scalar and other *= 1./scalar are done.

        For example a.imuladd(b, c).

        @param scalar a scalar value.
        @param other a DataManager with the same list of data then self.

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

        @param other a DataManager with the same list of data then self.

        @return the scalar product of self with other.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        result = 0.
        for name in self.values_.keys():
            result += self.values_[name] * other.values_[name]
        for name in self.MEDFields_.keys():
            nparr1 = self.MEDFields_[name].getArray().toNumPyArray()
            nparr2 = other.MEDFields_[name].getArray().toNumPyArray()
            Dim = 1
            if self.MEDFields_[name].getArray().getNumberOfComponents() > 1:
                Dim = 2
            result += numpy.tensordot(nparr1, nparr2, Dim)
        return result

    def setInputMEDField(self, name, field):
        """! Store the MED field field under the name name.

        @param name the name given to the field to store.
        @param field a field to store.
        """
        self.MEDFields_[name] = field

    def getOutputMEDField(self, name):
        """! Return the MED field of name name previously stored.

        @param name the name of the field to return.

        @return the MED field of name name previously stored.

        @throw Exception If there is no stored name field.
        """
        if name not in self.MEDFields_.keys():
            raise Exception("DataManager.getOutputMEDField unknown field " + name)
        return self.MEDFields_[name]

    def setValue(self, name, value):
        """! Store the scalar value under the name name.

        @param name the name given to the scalar to store.
        @param value a scalar value to store.
        """
        self.values_[name] = value

    def getValue(self, name):
        """! Return the scalar of name name previously stored.

        @param name the name of the value to return.

        @return the value of name name previously stored.

        @throw Exception If there is no stored name value.
        """
        if name not in self.values_.keys():
            raise Exception("DataManager.getValue unknown value " + name)
        return self.values_[name]

    def setInputMEDFieldTemplate(self, name, field):
        """! Store the MED field field as a MEDFieldTemplate under the name name.

        @param name the name given to the field to store.
        @param field a field to store.

        @note These fields are not be part of data, and will therefore not be taken into account in data manipulations (operators, norms etc.).
        """
        self.MEDFieldTemplates_[name] = field

    def getInputMEDFieldTemplate(self, name):
        """! Return the MED field previously stored as a MEDFieldTemplate under the name name. If there is not, returns 0.

        @param name the name of the field to return.

        @return the MED field of name name previously stored, or 0.
        """
        if name not in self.MEDFieldTemplates_.keys():
            return 0
        return self.MEDFieldTemplates_[name]
