# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class SharedRemappingMulti1D3D. """
from __future__ import print_function, division

import c3po.medcouplingCompat as mc
from c3po.exchangeMethods.SharedRemapping import Remapper, SharedRemapping


def shift1DFields(shiftMap, shiftedFieldPositions, indexTable):
    """! INTERNAL """
    newFieldPositions = [-1] * len(shiftedFieldPositions)
    availableFields = []

    if len(shiftMap) != len(shiftedFieldPositions):
        raise Exception("shift1DFields: the provided shiftMap must contain as many values ({} provided) than the number of 1D fields ({}).".format(len(shiftMap), len(shiftedFieldPositions)))
    if max(shiftMap) > len(shiftedFieldPositions) - 1:
        raise Exception("shift1DFields: the provided shiftMap contains values ({}) greater than the number of 1D fields - 1 ({}).".format(max(shiftMap), len(shiftedFieldPositions) - 1))

    for ipos, ifield in enumerate(shiftedFieldPositions):
        if shiftMap[ipos] >= 0:
            if newFieldPositions[shiftMap[ipos]] >= 0:
                raise Exception("shift1DFields: the provided shiftMap contains twice the positive value ({}).".format(shiftMap[ipos]))
            newFieldPositions[shiftMap[ipos]] = ifield
        else:
            availableFields.append(ifield)

    count = 0
    for ipos, ifield in enumerate(newFieldPositions):
        if ifield < 0:
            newFieldPositions[ipos] = availableFields[count]
            count += 1

    newIndexTable = [[] for _ in range(len(indexTable))]

    for ipos, ifield in enumerate(newFieldPositions):
        newIndexTable[ifield] = indexTable[shiftedFieldPositions[ipos]]

    return availableFields, newFieldPositions, newIndexTable


class Multi1D3DRemapper(Remapper):
    """! Allow to share the mesh projection for different SharedRemappingMulti1D3D objects by building them with the same instance of this class. """

    def __init__(self, xCoordinates, yCoordinates, indexTable, weights, meshAlignment=False, offset=[0., 0., 0.], rescaling=1., rotation=0., outsideCellsScreening=False):
        """! Build a Multi1D3DRemapper object.

        An intermediate inner 3D mesh is built from a 2D grid defined by the parameters.

        The axial coordinates will be read from the 1D fields passed to the remapper.

        Each cell of this 2D grid is associated to a 1D field.

        @param xCoordinates x coordinates of the inner mesh to build.
        @param yCoordinates y coordinates of the inner mesh to build.
        @param indexTable For each position of the 2D grid (x coordinate changes first), the index of the 1D field to associate. Put -1 to
        associate to nothing.
        @param weights Weigh of each 1D field to take into account for extensive variables.
        @param meshAlignment see Remapper. The source mesh is the multi1D one and the target mesh the 3D one.
        @param offset see Remapper. The source mesh is the multi1D one and the target mesh the 3D one.
        @param rescaling see Remapper. The source mesh is the multi1D one and the target mesh the 3D one.
        @param rotation see Remapper. The source mesh is the multi1D one and the target mesh the 3D one.
        @param outsideCellsScreening see Remapper.
        """
        Remapper.__init__(self, meshAlignment, offset, rescaling, rotation, outsideCellsScreening)
        self._indexTable = [[] for _ in range(max(indexTable) + 1)]
        for position, indice1D in enumerate(indexTable):
            if indice1D >= 0:
                self._indexTable[indice1D].append(position)
        self._shiftedFieldPositions = list(range(len(self._indexTable)))

        if len(self._indexTable) != len(weights):
            raise Exception("Multi1D3DRemapper.__init__ we give " + str(len(weights)) + "weight values instead of " + str(len(self._indexTable))
                            + ", the number of 1D calculations.")
        self._weights = weights
        self._xCoordinates = xCoordinates
        self._yCoordinates = yCoordinates
        self._zCoordinateArrays = [[] for _ in range(len(self._indexTable))]
        self._numberOfCellsIn1D = [0] * len(self._indexTable)
        self._innerMesh = None
        self._innerField = mc.MEDCouplingFieldDouble(mc.ON_CELLS, mc.ONE_TIME)
        self._innerField.setName("3DFieldFromMulti1D")
        self.isInnerFieldBuilt = False

    def buildInnerField(self, meshes1D):
        """! INTERNAL """
        internal1DMeshes = []
        if len(meshes1D) != len(self._indexTable):
            raise Exception("Multi1D3DRemapper.buildInnerField we give " + str(len(meshes1D)) + " 1D meshes instead of " + str(len(self._indexTable)) + ".")
        for imesh, mesh1D in enumerate(meshes1D):
            self._zCoordinateArrays[imesh] = mesh1D.getCoordsAt(0)
            self._numberOfCellsIn1D[imesh] = mesh1D.getNumberOfCells()
            for fieldIndex in self._indexTable[imesh]:
                internal1DMeshes.append(mc.MEDCouplingCMesh("3DMeshFromMulti1D"))
                xIndex = fieldIndex % (len(self._xCoordinates) - 1)
                yIndex = fieldIndex // (len(self._xCoordinates) - 1)
                arrayX = mc.DataArrayDouble([self._xCoordinates[xIndex], self._xCoordinates[xIndex + 1]])
                arrayX.setInfoOnComponent(0, "X [m]")
                arrayY = mc.DataArrayDouble([self._yCoordinates[yIndex], self._yCoordinates[yIndex + 1]])
                arrayY.setInfoOnComponent(0, "Y [m]")
                internal1DMeshes[-1].setCoords(arrayX, arrayY, self._zCoordinateArrays[imesh])
        if len(internal1DMeshes) > 0:
            self._innerMesh = mc.MEDCouplingMesh.MergeMeshes(internal1DMeshes)
        else:
            self._innerMesh = mc.MEDCouplingUMesh()
        self._innerMesh.setName("3DMeshFromMulti1D")
        self._innerField.setMesh(self._innerMesh)
        array = mc.DataArrayDouble()
        if len(internal1DMeshes) > 0:
            array.alloc(self._innerMesh.getNumberOfCells())
            array.fillWithValue(0.)
        self._innerField.setArray(array)
        self.isInnerFieldBuilt = True
        self.isInit = False

    def getInnerField(self):
        """! INTERNAL """
        return self._innerField

    def build3DField(self, fields1D, defaultValue=0.):
        """! INTERNAL """
        resuField = self._innerField.clone(True)
        if len(fields1D) > 0:
            resuField.setNature(fields1D[0].getNature())
        array3D = resuField.getArray()
        array3D.fillWithValue(defaultValue)
        indexMin = 0
        for i, field in enumerate(fields1D):
            array1D = field.getArray()
            if resuField.getNature() == mc.ExtensiveMaximum or resuField.getNature() == mc.ExtensiveConservation:
                array1D *= self._weights[i]
            for _ in self._indexTable[i]:
                array3D.setPartOfValues1(array1D, indexMin, indexMin + self._numberOfCellsIn1D[i], 1, 0, 1, 1)
                indexMin += self._numberOfCellsIn1D[i]
        return resuField

    def build1DFields(self, field3D):
        """! INTERNAL """
        array3D = field3D.getArray()
        fields1D = []
        indexMin = 0
        for i, list1D in enumerate(self._indexTable):
            fields1D.append(mc.MEDCouplingFieldDouble(mc.ON_CELLS, mc.ONE_TIME))
            fields1D[-1].setName(field3D.getName())
            mesh1D = mc.MEDCouplingCMesh("mesh1D")
            mesh1D.setCoords(self._zCoordinateArrays[i])
            fields1D[-1].setMesh(mesh1D)
            array1D = mc.DataArrayDouble()
            array1D.alloc(self._numberOfCellsIn1D[i])
            array1D.fillWithValue(0.)
            for _ in list1D:
                array1Dtmp = mc.DataArrayDouble()
                array1Dtmp.alloc(self._numberOfCellsIn1D[i])
                array1Dtmp.setContigPartOfSelectedValuesSlice(0, array3D, indexMin, indexMin + self._numberOfCellsIn1D[i], 1)
                indexMin += self._numberOfCellsIn1D[i]
                array1D.addEqual(array1Dtmp)
            if len(list1D) > 0:
                array1D *= 1. / len(list1D)
            if field3D.getNature() == mc.ExtensiveMaximum or field3D.getNature() == mc.ExtensiveConservation:
                array1D *= 1. / self._weights[i]
            fields1D[-1].setArray(array1D)
        return fields1D

    def getNumberOf1DFields(self):
        """! INTERNAL """
        return len(self._indexTable)

    def shift1DFields(self, shiftMap):
        """! This method allows to shift the index of the 1D fields provided through the indexTable parameter of constructor.

        @param shiftMap a list providing for each 1D fields the index (in indexTable) of its new position (-1 can be used to indicate that the field is no more used).

        @return the list of the indexes no more used.

        For example, shiftMap=[3, -1, 1, 2] indicates that at first call field_0 goes to position 3, field_1 is discharged, field_2 goes to 1 and field_3 goes to 2. It returns [1].
        At the second call with the same input, field_0 (now at position 3) goes to 2, field_1 (at 0) goes to 3, field_2 (at 1) is discharged and field_3 (at 2) goes to 1. It returns [2].
        The thrid call returns [3], the fourth call [0].
        """
        availableFields, shiftedFieldPositions, indexTable = shift1DFields(shiftMap, self._shiftedFieldPositions, self._indexTable)
        self.setShiftedIndex(shiftedFieldPositions, indexTable)
        return availableFields

    def setShiftedIndex(self, shiftedFieldPositions, indexTable):
        """ ! INTERNAL """
        self._shiftedFieldPositions = shiftedFieldPositions
        self._indexTable = indexTable
        self.isInnerFieldBuilt = False


class SharedRemappingMulti1D3D(SharedRemapping):
    """! SharedRemappingMulti1D3D is an ExchangeMethod which projects the input fields one by one before returning them as
    outputs, in the same order.

    See c3po.Exchanger.Exchanger.__init__().

    1D fields are processed in packets using the intermediate mesh defined by the Multi1D3DRemapper object.

    The method assumes that all input fields (or packets) have the same mesh, and produces output fields on identical meshes.

    This output mesh is the one of the first field (or packet) passed to the method (obtained by getInputMEDFieldTemplate).

    The input scalars are returned in the same order, without modification.

    The initialization of the projection method (long operation) is done only once, and can be shared with other instances
    of SharedRemappingMulti1D3D.
    """

    def __init__(self, remapper, reverse=False, defaultValue=0., linearTransform=(1., 0.)):
        """! Build a SharedRemappingMulti1D3D object, to be given to an Exchanger.

        @param remapper A Multi1D3DRemapper object performing the projection. It can thus be shared with other instances of
               SharedRemappingMulti1D3D (its initialization will always be done only once).
        @param reverse see SharedRemapping. Direct is multi1D -> 3D, reverse is 3D -> multi1D.
        @param defaultValue see SharedRemapping.
        @param linearTransform see SharedRemapping.
        """
        SharedRemapping.__init__(self, remapper, reverse, defaultValue, linearTransform)
        self._numberOf1DFields = self._remapper.getNumberOf1DFields()

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! Project the input fields one by one before returning them as outputs, in the same order. """
        numberOf3DFields = len(fieldsToGet) if self._isReverse else len(fieldsToSet)
        numberOf1DFields = len(fieldsToSet) if self._isReverse else len(fieldsToGet)
        if numberOf3DFields * self._numberOf1DFields != numberOf1DFields:
            msg = "The number of provided fields ({} 3D fields and {} 1D fields) is wrong.\n".format(numberOf3DFields, numberOf1DFields)
            msg += "According to the provided remapper object, there must be {} 1D fields for each 3D fields.".format(self._numberOf1DFields)
            raise Exception(msg)
        if numberOf3DFields == 0:
            return [], valuesToGet

        if not self._remapper.isInnerFieldBuilt:
            self._remapper.buildInnerField([field.getMesh() for field in (fieldsToSet if self._isReverse else fieldsToGet)])
        if self._isReverse:
            outputFields, outputValues = SharedRemapping.__call__(self, fieldsToGet, [self._remapper.getInnerField()] * len(fieldsToGet), valuesToGet)
            resu = []
            for field3D in outputFields:
                resu += self._remapper.build1DFields(field3D)
            return resu, outputValues
        indexFirst = 0
        intermediate3DField = []
        while indexFirst + self._numberOf1DFields <= len(fieldsToGet):
            fields1D = fieldsToGet[indexFirst:indexFirst + self._numberOf1DFields]
            intermediate3DField.append(self._remapper.build3DField(fields1D, self._defaultValue))
            indexFirst += self._numberOf1DFields
        return SharedRemapping.__call__(self, intermediate3DField, fieldsToSet, valuesToGet)

    def getPatterns(self):
        """! See ExchangeMethod.getPatterns. """
        if self._isReverse:
            return [(1, self._numberOf1DFields, 0, 0), (0, 0, 1, 1)]
        return [(self._numberOf1DFields, 1, 0, 0), (0, 0, 1, 1)]
