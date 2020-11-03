# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class dataManager. """
from __future__ import print_function, division
import numpy
import math


class dataManager(object):
    """ dataManager stores and manipulates data outside of components (ie physicsDriver implementations). This allows certain coupling techniques or time schemes to be implemented. 

    Data are scalars or MED fields, identified by their names.
    """

    def __init__(self):
        self.values_ = {}
        self.MEDFields_ = {}
        self.MEDFieldTemplates_ = {}

    def clone(self):
        """ Returns a clone of self. """
        return (self * 1.)

    def cloneEmpty(self):
        """ Returns a clone of self without copying the data. """
        output = dataManager()
        output.MEDFieldTemplates_ = self.MEDFieldTemplates_
        return output

    def copy(self, other):
        """ If self and other are two dataManager with the same list of data copy values of other in self. """
        self.checkBeforeOperator(other)
        for name in self.values_.keys():
            self.values_[name] = other.values_[name]
        for name in self.MEDFields_.keys():
            otherArray = other.MEDFields_[name].getArray()
            self.MEDFields_[name].getArray().setPartOfValues1(other.MEDFields_[name].getArray(), 0, otherArray.getNumberOfTuples(), 1, 0, otherArray.getNumberOfComponents(), 1)

    def normMax(self):
        """ Returns the infinite norm, ie the max between the absolute values of the scalars and the infinite norms of the MED fields. """
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
        """ Returns the norm2, ie sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.  """
        norm = 0.
        for scalar in self.values_.values():
            norm += scalar * scalar
        for MED in self.MEDFields_.values():
            localNorm = MED.norm2()
            norm += localNorm * localNorm
        return math.sqrt(norm)

    def checkBeforeOperator(self, other):
        """ Make basic checks before the call of an operator: same data names between self and other. """
        if len(self.values_.keys()) != len(other.values_.keys()) or len(self.MEDFields_.keys()) != len(other.MEDFields_.keys()):
            raise Exception("dataManager.checkBeforeOperator : we cannot call an operator between two dataManager with different number of stored data.")
        for name in self.values_.keys():
            if not(name in other.values_.keys()):
                raise Exception("dataManager.checkBeforeOperator : we cannot call an operator between two dataManager with different data.")
        for name in self.MEDFields_.keys():
            if not(name in other.MEDFields_.keys()):
                raise Exception("dataManager.checkBeforeOperator : we cannot call an operator between two dataManager with different data.")

    def __add__(self, other):
        """ If self and other are two dataManager with the same list of data: returns a new (coherent with self) dataManager where the data are added. """
        self.checkBeforeOperator(other)
        new_data = self.cloneEmpty()
        for name in self.values_.keys():
            new_data.values_[name] = self.values_[name] + other.values_[name]
        for name in self.MEDFields_.keys():
            new_data.MEDFields_[name] = 1. * self.MEDFields_[name]
            new_data.MEDFields_[name].getArray().addEqual(other.MEDFields_[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return new_data

    def __iadd__(self, other):
        """ If self and other are two dataManager with the same list of data: modifies in place self with data added to other (and return self). """
        self.checkBeforeOperator(other)
        for name in self.values_.keys():
            self.values_[name] += other.values_[name]
        for name in self.MEDFields_.keys():
            self.MEDFields_[name].getArray().addEqual(other.MEDFields_[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return self

    def __sub__(self, other):
        """ If self and other are two dataManager with the same list of data: returns a new (coherent with self) dataManager where the data are substracted. """
        self.checkBeforeOperator(other)
        new_data = self.cloneEmpty()
        for name in self.values_.keys():
            new_data.values_[name] = self.values_[name] - other.values_[name]
        for name in self.MEDFields_.keys():
            new_data.MEDFields_[name] = 1. * self.MEDFields_[name]
            new_data.MEDFields_[name].getArray().substractEqual(other.MEDFields_[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return new_data

    def __isub__(self, other):
        """ If self and other are two dataManager with the same list of data: modifies in place self with data substracted to other (and return self). """
        self.checkBeforeOperator(other)
        for name in self.values_.keys():
            self.values_[name] -= other.values_[name]
        for name in self.MEDFields_.keys():
            self.MEDFields_[name].getArray().substractEqual(other.MEDFields_[name].getArray())  # On passe par les dataArray pour eviter la verification d'identite des maillages des operateurs des champs !
        return self

    def __mul__(self, scalar):
        """ Returns a new (coherent with self) dataManager where the data are multiplicated by scalar. """
        new_data = self.cloneEmpty()
        for name in self.values_.keys():
            new_data.values_[name] = scalar * self.values_[name]
        for name in self.MEDFields_.keys():
            new_data.MEDFields_[name] = scalar * self.MEDFields_[name]
        return new_data

    def __imul__(self, scalar):
        """ Modifies and returns self with the data multiplicated by scalar. """
        for name in self.values_.keys():
            self.values_[name] *= scalar
        for name in self.MEDFields_.keys():
            self.MEDFields_[name] *= scalar
        return self

    def imuladd(self, scalar, other):
        """ If self and other are two dataManager with the same list of data: modifies in place self with data added to other * scalar (and return self).

        To do so, other *= scalar and other *= 1./scalar are done.
        """
        if scalar == 0:
            return self
        self.checkBeforeOperator(other)
        other *= scalar
        self += other
        other *= 1. / scalar
        return self

    def dot(self, other):
        """ If self and other are two dataManager with the same list of data: returns the scalar product (sum of the product of every elements) of this and other."""
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
        """ Stores the MED field field under the name name. """
        self.MEDFields_[name] = field

    def getOutputMEDField(self, name):
        """ Returns the MED field of name name previously stored. If there is not throw an exception. """
        if name not in self.MEDFields_.keys():
            raise Exception("dataManager.getOutputMEDField unknown field " + name)
        return self.MEDFields_[name]

    def setValue(self, name, value):
        """ Stores the scalar value under the name name. """
        self.values_[name] = value

    def getValue(self, name):
        """ Returns the scalar of name name previously stored. If there is not throw an exception. """
        if name not in self.values_.keys():
            raise Exception("dataManager.getValue unknown value " + name)
        return self.values_[name]

    def setInputMEDFieldTemplate(self, name, field):
        """ Stores the MED field field as a MEDFieldTemplate under the name name. It will not be part of data, and will therefore not be impacted by data manipulations (operators, norms etc.). """
        self.MEDFieldTemplates_[name] = field

    def getInputMEDFieldTemplate(self, name):
        """ Returns the MED field previously stored as a MEDFieldTemplate under the name name. If there is not, returns 0. """
        if name not in self.MEDFieldTemplates_.keys():
            return 0
        return self.MEDFieldTemplates_[name]
