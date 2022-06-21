# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class ExchangeMethod. """
from __future__ import print_function, division


class ExchangeMethod(object):
    """! ExchangeMethod is a class interface (to be implemented) which standardizes exchange methods to be used with LocalExchanger.

    See c3po.LocalExchanger.LocalExchanger.__init__().
    """

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! Return the MED fields and scalars to be provided to the target DataAccessor. """
        raise NotImplementedError

    def getPatterns(self):
        """!
        Return a list of patterns.

        A pattern is a tuple of 4 integers. They are related respectively to the number of fields to get,
        fields to set, values to get and values to set with the __call__ method.

        Patterns indicate dependencies of the exchange method and is used to check for proper use of the
        object, and for optimizations.

        For example, for an ExchangeMethod with the patterns: [(1,1,0,0), (0,0,1,1)], a call with 3 fields
        to set, 3 fields to get, 2 values to get (that would provide 2 values to set) could be replace by
        5 calls: 3 with 1 field to get and 1 field to set, plus 2 with 1 value to get (that would provide 1
        value to set). On the other hand, this ExchangeMethod could not be called with 0 field to get, 1
        field to set and 1 value to get.

        The order of the pattern list is used as a priority order.

        A negative value can be used to mean that the number of required elements is not known. All elements
        of this kind are required for this pattern, but they will not be available for the following ones.
        """
        return [(-1, -1, -1, -1)]
