# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPISharedRemappingMulti1D3D. """
from __future__ import print_function, division

from c3po.exchangeMethods.SharedRemappingMulti1D3D import shift1DFields, Multi1D3DRemapper
from c3po.CollaborativeObject import CollaborativeObject
from c3po.mpi.MPIRemote import MPIRemote
from c3po.mpi.mpiExchangeMethods.MPISharedRemapping import MPISharedRemapping, MPIRemapper
from c3po.services.Printer import warning


class MPIMulti1D3DRemapper(MPIRemapper):
    """! Allow to share the mesh projection for different MPISharedRemappingMulti1D3D objects by building them with the same instance of this class. """

    def __init__(self, xCoordinates, yCoordinates, indexTable, weights, physics, meshAlignment=False, offset=None, rescaling=1., rotation=0., outsideCellsScreening=False, reverseTransformations=True):
        """! Build a MPIMulti1D3DRemapper object, the MPI version of c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.

        The constructor has the same form than c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__() with one additional mandatory parameter: physics.

        @param xCoordinates see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__().
        @param yCoordinates see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__().
        @param indexTable see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__().
        @param weights see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__().
        @param physics The list (or a c3po.mpi.MPICollaborativePhysicsDriver.MPICollaborativePhysicsDriver) of the 1D c3po.PhysicsDriver.PhysicsDriver involved in the coupling. We just use it to identify remote ones.
        @param meshAlignment see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper. The source mesh is the multi1D one and the target mesh the 3D one.
        @param offset see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__(). The source mesh is the multi1D one and the target mesh the 3D one.
        @param rescaling see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__(). The source mesh is the multi1D one and the target mesh the 3D one.
        @param rotation see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__(). The source mesh is the multi1D one and the target mesh the 3D one.
        @param outsideCellsScreening see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__().
        @param reverseTransformations see c3po.exchangeMethods.SharedRemappingMulti1D3D.Multi1D3DRemapper.__init__().

        @warning There seems to be a bug in MEDCoupling that may cause wrong results when rescaling is used with a source mesh (multi1D) of
            nature IntensiveConservation. In this case, using reverseTransformations=False should be enough to solve the problem.
        """
        MPIRemapper.__init__(self, meshAlignment, offset, rescaling, rotation, outsideCellsScreening, reverseTransformations)
        physicsList = []
        if isinstance(physics, CollaborativeObject):
            physics = [physics]
        for physic in physics:
            if isinstance(physic, CollaborativeObject):
                physicsList += physic.getElementsRecursively()
            else:
                physicsList.append(physic)
        if len(physicsList) != max(indexTable) + 1:
            raise Exception("MPIMulti1D3DRemapper.__init__ the number of elements of physics ({}) is not coherent with indexTable (whose max + 1 value is {}).".format(len(physicsList), max(indexTable) + 1))

        self._globalToLocal = [0] * len(physicsList)
        nextIndex = 0
        newWeights = []
        for iphy, physic in enumerate(physicsList):
            if isinstance(physic, MPIRemote):
                self._globalToLocal[iphy] = -1
            else:
                self._globalToLocal[iphy] = nextIndex
                newWeights.append(weights[iphy])
                nextIndex += 1
        self._nbLocal1DFields = nextIndex

        newIndexTable = [0] * len(indexTable)
        for position, index1D in enumerate(indexTable):
            newIndexTable[position] = self._globalToLocal[index1D]

        self._localMulti1D3DRemapper = Multi1D3DRemapper(xCoordinates, yCoordinates, newIndexTable, newWeights)
        self.isInnerFieldBuilt = False

        self._globalIndexTable = [[] for _ in range(max(indexTable) + 1)]
        for position, index1D in enumerate(indexTable):
            if index1D >= 0:
                self._globalIndexTable[index1D].append(position)
        self._shiftedFieldPositions = list(range(len(self._globalIndexTable)))

    def buildInnerField(self, meshes1D):
        """! INTERNAL """
        self._localMulti1D3DRemapper.buildInnerField(meshes1D)
        self.isInnerFieldBuilt = True
        self.isInit = False

    def getInnerField(self):
        """! INTERNAL """
        return self._localMulti1D3DRemapper.getInnerField()

    def build3DField(self, fields1D, defaultValue=0.):
        """! INTERNAL """
        return self._localMulti1D3DRemapper.build3DField(fields1D, defaultValue)

    def build1DFields(self, field3D):
        """! INTERNAL """
        return self._localMulti1D3DRemapper.build1DFields(field3D)

    def getNumberOf1DFields(self):
        """! INTERNAL """
        return self._nbLocal1DFields

    def shift1DFields(self, shiftMap):
        """! See Multi1D3DRemapper.shift1DFields() """
        availableFields, self._shiftedFieldPositions, self._globalIndexTable = shift1DFields(shiftMap, self._shiftedFieldPositions, self._globalIndexTable)
        tmpIndexTable = [[] for _ in range(self._nbLocal1DFields)]
        for index1D, positions in enumerate(self._globalIndexTable):
            if self._globalToLocal[index1D] >= 0:
                tmpIndexTable[self._globalToLocal[index1D]] = positions
        self._localMulti1D3DRemapper.setShiftedIndex([], tmpIndexTable)
        self.isInnerFieldBuilt = False
        return availableFields


class MPISharedRemappingMulti1D3D(MPISharedRemapping):
    """! MPISharedRemappingMulti1D3D is the MPI version of c3po.exchangeMethods.SharedRemappingMulti1D3D.SharedRemappingMulti1D3D. """

    def __init__(self, remapper, reverse=False, defaultValue=0., linearTransform=(1., 0.)):
        """! Build a MPISharedRemappingMulti1D3D object, to be given to an c3po.mpi.MPIExchanger.MPIExchanger.

        @param remapper A MPIMulti1D3DRemapper object performing the projection. It can thus be shared with other instances of
               MPISharedRemappingMulti1D3D (its initialization will always be done only once).
        @param reverse see c3po.exchangeMethods.SharedRemappingMulti1D3D.SharedRemappingMulti1D3D.__init__(). Direct is multi1D -> 3D, reverse is 3D -> multi1D.
        @param defaultValue see c3po.exchangeMethods.SharedRemappingMulti1D3D.SharedRemappingMulti1D3D.__init__().
        @param linearTransform see c3po.exchangeMethods.SharedRemappingMulti1D3D.SharedRemappingMulti1D3D.__init__().
        """
        warning("MPISharedRemappingMulti1D3D is deprecated and will soon by deleted. Please use c3po.mpi.multi1D package instead.")

        MPISharedRemapping.__init__(self, remapper, reverse, defaultValue, linearTransform)
        self._numberOf1DFields = self._remapper.getNumberOf1DFields()

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! Project the input fields one by one before returning them as outputs, in the same order. """
        numberOf1DFields = len(fieldsToSet) if self._isReverse else len(fieldsToGet)
        if (numberOf1DFields != 0) if self._numberOf1DFields == 0 else (numberOf1DFields % self._numberOf1DFields != 0):
            msg = "The number of provided 1D fields ({}) is wrong.\n".format(numberOf1DFields)
            msg += "According to the provided remapper object, the number of 1D fields must be a multiple of {}.".format(self._numberOf1DFields)
            raise Exception(msg)
        if len(valuesToGet) != 0:
            raise Exception("MPISharedRemappingMulti1D3D: we cannot deal with scalar values.")

        if not self._remapper.isInnerFieldBuilt:
            self._remapper.buildInnerField([field.getMesh() for field in (fieldsToSet if self._isReverse else fieldsToGet)])  # pylint: disable=superfluous-parens
        if self._isReverse:
            numberRemapping = 0 if numberOf1DFields == 0 else numberOf1DFields // self._numberOf1DFields
            innerField = self._remapper.getInnerField()
            if numberOf1DFields > 0:
                innerField.setNature(fieldsToSet[0].getNature())
            outputFields, outputValues = MPISharedRemapping.__call__(self, fieldsToGet, [innerField] * numberRemapping, valuesToGet)
            resu = []
            for field3D in outputFields:
                resu += self._remapper.build1DFields(field3D)
            return resu, outputValues
        indexFirst = 0
        intermediate3DField = []
        if len(fieldsToGet) > 0:
            while indexFirst + self._numberOf1DFields <= len(fieldsToGet):
                fields1D = fieldsToGet[indexFirst:indexFirst + self._numberOf1DFields]
                intermediate3DField.append(self._remapper.build3DField(fields1D, self._defaultValue))
                indexFirst += self._numberOf1DFields
        return MPISharedRemapping.__call__(self, intermediate3DField, fieldsToSet, valuesToGet)

    def getPatterns(self):
        """! See ExchangeMethod.getPatterns. """
        if self._isReverse:
            return [(0, self._numberOf1DFields, 0, 0), (1, 0, 0, 0)]
        return [(self._numberOf1DFields, 0, 0, 0), (0, 1, 0, 0)]

    def clean(self):
        """! See ExchangeMethod.clean. """
        self._remapper.isInnerFieldBuilt = False
