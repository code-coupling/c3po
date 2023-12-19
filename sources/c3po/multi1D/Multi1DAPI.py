# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the classes Multi1DAPI and Multi1DWithObjectsAPI. """
from abc import ABC, abstractmethod


class Multi1DAPI(ABC):
    """! Multi1DAPI is an abstract class handling a set of 1D object. """

    @abstractmethod
    def getSize(self):
        """! Return the number of 1D objects handled by self.

        @return the number of 1D objects.
        """

    @abstractmethod
    def getNumberOfCells(self, index):
        """! Return the number of cells of the 1D object with the required index.

        @param index index of the queried 1D object .
        @return the number of cells in the required 1D object.
        """

    @abstractmethod
    def getCellSizes(self, index):
        """! Return the list of the sizes of the cells of the 1D object with the required index.

        @note The length of the returned list should be equal to getNumberOfCells().

        @param index index of the queried 1D object.
        @return List with the sizes of the cells of the required 1D object.
        """

    @abstractmethod
    def getNature(self, fieldName):
        """! Return the nature of the field fieldName, which mush be available for getValues, using MEDCoupling enum.

        @param fieldName name of the field.
        @return Nature of the field.
        """

    @abstractmethod
    def getValues(self, index, fieldName):
        """! Return the values of the field fieldName for the 1D object with the required index.

        @note The length of the returned list should be equal to getNumberOfCells().

        @param index index of the queried 1D object.
        @param fieldName name of the field.
        @return list of values.
        """

    @abstractmethod
    def setValues(self, index, fieldName, values):
        """! Set the values of the field fieldName to the 1D object with the required index.

        @note The length of values should be equal to getNumberOfCells().

        @param index index of the queried 1D object.
        @param fieldName name of the field.
        @param values list of values to set.
        """


class Multi1DWithObjectsAPI(Multi1DAPI):
    """! Multi1DWithObjectsAPI is an abstract class that extends Multi1DAPI with the possibility for each 1D object to hold internal objects.

    These internal objects are named. They can differ from one 1D object to another.
    Values may be written and read from (or on) these internal objects. They may not be all involved in every set or get.
    """

    @abstractmethod
    def getObjectNames(self, index):
        """! @brief Return the list of list of the names of the internal objects hold by the 1D object with the required index at each cell.

        @note The length of the returned list should be equal to getNumberOfCells().

        @param index index of the queried 1D object.
        @return list (for each cell) of list of internal object names.
        """

    @abstractmethod
    def getObjectNamesInField(self, fieldName):
        """! Return the list of the names of the internal objects that are involved in get / set methods for the field fieldName.

        @note The names of all involved internal object should be listed, even if they appear in only one cell of one 1D object.
        @note The ordering of the names must be coherent with getObjectValues() and setObjectValues() behavior.

        @param fieldName name of the field.
        @return list of internal object names involved in the required field.
        """

    @abstractmethod
    def getObjectValues(self, index, fieldName):
        """! Return the list of list of the values for the field fieldName for the 1D object with the required index (for each object and for each cell).

        @note The length of the returned list should be equal to the lenght of the list returned by getObjectNamesInField(fieldName).
        @note For every i, the length of the i-th components of the return list should be equal to getNumberOfCells(index).

        @param index index of the queried 1D object.
        @param fieldName name of the field.
        @return list of list of values.
        """

    @abstractmethod
    def setObjectValues(self, index, fieldName, values):
        """! Set the values for the field fieldName to the 1D object with the required index (for each object and for each cell).

        @note The length of values should be equal to the lenght of the list returned by getObjectNamesInField(fieldName).
        @note For every i, the length of values[i] should be equal to getNumberOfCells(index).

        @param index index of the queried 1D object.
        @param fieldName name of the field.
        @param values list of list of values to set.
        """
