# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class CollaborativeDataManager. """
from __future__ import print_function, division
import math


class CollaborativeDataManager(object):
    """! CollaborativeDataManager allows to handle a set of DataManager as a single one.

    Exchanges are still to be done with the individual DataManager.
    """

    def __init__(self, dataManagers):
        """! Build a CollaborativeDataManager object.

        @param dataManagers a list of DataManager.
        """
        self.dataManagers_ = dataManagers

    def clone(self):
        """! Return a clone of self.

        @return A clone of self. Data are copied.
        """
        return (self * 1.)

    def cloneEmpty(self):
        """! Return a clone of self without copying the data.

        @return An empty clone of self.
        """
        dataClone = [data.cloneEmpty() for data in self.dataManagers_]
        output = CollaborativeDataManager(dataClone)
        return output

    def copy(self, other):
        """! Copy data of other in self.

        @param other a CollaborativeDataManager with the same list of data than self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for i, data in enumerate(self.dataManagers_):
            data.copy(other.dataManagers_[i])

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields.
        """
        norm = 0.
        for data in self.dataManagers_:
            local_norm = data.normMax()
            if local_norm > norm:
                norm = local_norm
        return norm

    def norm2(self):
        """! Return the norm 2.

        @return sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.
        """
        norm = 0.
        for data in self.dataManagers_:
            local_norm = data.norm2()
            norm += local_norm * local_norm
        return math.sqrt(norm)

    def checkBeforeOperator(self, other):
        """! INTERNAL Make basic checks before the call of an operator. """
        if len(self.dataManagers_) != len(other.dataManagers_):
            raise Exception("CollaborativeDataManager.checkBeforeOperator : we cannot call an operator between two CollaborativeDataManager with different number of DataManager.")

    def __add__(self, other):
        """! Return self + other.

        Use "+" to call it. For example a = b + c.

        @param other a CollaborativeDataManager with the same list of data then self.

        @return a new (consistent with self) CollaborativeDataManager where the data are added.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        new_data = self.cloneEmpty()
        for i in range(len(self.dataManagers_)):
            new_data.dataManagers_[i] = self.dataManagers_[i] + other.dataManagers_[i]
        return new_data

    def __iadd__(self, other):
        """! Add other in self (in place addition).

        Use "+=" to call it. For example a += b.

        @param other a CollaborativeDataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for i in range(len(self.dataManagers_)):
            self.dataManagers_[i] += other.dataManagers_[i]
        return self

    def __sub__(self, other):
        """! Return self - other.

        Use "-" to call it. For example a = b - c.

        @param other a CollaborativeDataManager with the same list of data then self.

        @return a new (consistent with self) CollaborativeDataManager where the data are substracted.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        new_data = self.cloneEmpty()
        for i in range(len(self.dataManagers_)):
            new_data.dataManagers_[i] = self.dataManagers_[i] - other.dataManagers_[i]
        return new_data

    def __isub__(self, other):
        """! Substract other to self (in place subtraction).

        Use "-=" to call it. For example a -= b.

        @param other a CollaborativeDataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for i in range(len(self.dataManagers_)):
            self.dataManagers_[i] -= other.dataManagers_[i]
        return self

    def __mul__(self, scalar):
        """! Return scalar * self.

        Use "*" to call it. For example a = b * c. The scalar first.

        @param scalar a scalar value.

        @return a new (consistent with self) CollaborativeDataManager where the data are multiplied by scalar.
        """
        new_data = self.cloneEmpty()
        for i in range(len(self.dataManagers_)):
            new_data.dataManagers_[i] = self.dataManagers_[i] * scalar
        return new_data

    def __imul__(self, scalar):
        """! Multiply self by scalar (in place multiplication).

        Use "*=" to call it. For example a *= b.

        @param scalar a scalar value.

        @return self.
        """
        for i in range(len(self.dataManagers_)):
            self.dataManagers_[i] *= scalar
        return self

    def imuladd(self, scalar, other):
        """! Add in self scalar * other (in place operation).

        In order to do so, other *= scalar and other *= 1./scalar are done.

        For example a.imuladd(b, c).

        @param scalar a scalar value.
        @param other a CollaborativeDataManager with the same list of data then self.

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

        @param other a CollaborativeDataManager with the same list of data then self.

        @return the scalar product of self with other.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        result = 0.
        for i in range(len(self.dataManagers_)):
            result += self.dataManagers_[i].dot(other.dataManagers_[i])
        return result
