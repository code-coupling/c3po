# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class CollaborativeDataManager. """
from __future__ import print_function, division
import math


class CollaborativeDataManager(object):
    """ CollaborativeDataManager allows to handle a set of DataManager as a single one. Exchanges are still to be done with the individual DataManagers.

    """

    def __init__(self, dataManagers):
        """ Builds a CollaborativeDataManager object.

        :param dataManagers: a list of DataManager.
        """
        self.dataManagers_ = dataManagers

    def clone(self):
        """ Returns a clone of self. """
        return (self * 1.)

    def cloneEmpty(self):
        """ Returns a clone of self without copying the data. """
        dataClone = [data.cloneEmpty() for data in self.dataManagers_]
        output = CollaborativeDataManager(dataClone)
        return output

    def copy(self, other):
        """ If self and other are two CollaborativeDataManager with the same list of data copy values of other in self. """
        self.checkBeforeOperator(other)
        for i, data in enumerate(self.dataManagers_):
            data.copy(other.dataManagers_[i])

    def normMax(self):
        """ Returns the infinite norm, ie the max between the absolute values of the scalars and the infinite norms of the MED fields. """
        norm = 0.
        for data in self.dataManagers_:
            local_norm = data.normMax()
            if local_norm > norm:
                norm = local_norm
        return norm

    def norm2(self):
        """ Returns the norm2, ie sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.  """
        norm = 0.
        for data in self.dataManagers_:
            local_norm = data.norm2()
            norm += local_norm * local_norm
        return math.sqrt(norm)

    def checkBeforeOperator(self, other):
        """ Make basic checks before the call of an operator: same number of DataManager in self and other. """
        if len(self.dataManagers_) != len(other.dataManagers_):
            raise Exception("CollaborativeDataManager.checkBeforeOperator : we cannot call an operator between two CollaborativeDataManager with different number of DataManager.")

    def __add__(self, other):
        """ If self and other are two CollaborativeDataManager with the same list of data: returns a new (coherent with self) CollaborativeDataManager where the data are added. """
        self.checkBeforeOperator(other)
        new_data = self.cloneEmpty()
        for i in range(len(self.dataManagers_)):
            new_data.dataManagers_[i] = self.dataManagers_[i] + other.dataManagers_[i]
        return new_data

    def __iadd__(self, other):
        """ If self and other are two CollaborativeDataManager with the same list of data: modifies in place self with data added to other (and return self). """
        self.checkBeforeOperator(other)
        for i in range(len(self.dataManagers_)):
            self.dataManagers_[i] += other.dataManagers_[i]
        return self

    def __sub__(self, other):
        """ If self and other are two CollaborativeDataManager with the same list of data: returns a new (coherent with self) CollaborativeDataManager where the data are substracted. """
        self.checkBeforeOperator(other)
        new_data = self.cloneEmpty()
        for i in range(len(self.dataManagers_)):
            new_data.dataManagers_[i] = self.dataManagers_[i] - other.dataManagers_[i]
        return new_data

    def __isub__(self, other):
        """ If self and other are two CollaborativeDataManager with the same list of data: modifies in place self with data substracted to other (and return self). """
        self.checkBeforeOperator(other)
        for i in range(len(self.dataManagers_)):
            self.dataManagers_[i] -= other.dataManagers_[i]
        return self

    def __mul__(self, scalar):
        """ Returns a new (coherent with self) CollaborativeDataManager where the data are multiplicated by scalar. """
        new_data = self.cloneEmpty()
        for i in range(len(self.dataManagers_)):
            new_data.dataManagers_[i] = self.dataManagers_[i] * scalar
        return new_data

    def __imul__(self, scalar):
        """ Modifies and returns self with the data multiplicated by scalar. """
        for i in range(len(self.dataManagers_)):
            self.dataManagers_[i] *= scalar
        return self

    def imuladd(self, scalar, other):
        """ If self and other are two CollaborativeDataManager with the same list of data: modifies in place self with data added to other * scalar (and return self).

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
        """ If self and other are two CollaborativeDataManager with the same list of data: returns the scalar product (sum of the product of every elements) of this and other."""
        self.checkBeforeOperator(other)
        result = 0.
        for i in range(len(self.dataManagers_)):
            result += self.dataManagers_[i].dot(other.dataManagers_[i])
        return result
