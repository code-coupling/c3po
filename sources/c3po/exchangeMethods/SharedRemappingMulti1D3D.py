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
from c3po.medcouplingCompat import MEDCouplingRemapper
from c3po.exchangeMethods.ExchangeMethod import ExchangeMethod


class Multi1D3DRemapper(MEDCouplingRemapper):
    """! Allow to share the mesh projection for different SharedRemappingMulti1D3D objects by building them with the same instance of this class. """

    def __init__(self, xCoordinates, yCoordinates, indexTable, weights, meshAlignment=False, offset=[0., 0., 0.], rescaling=1., rotation=0.):
        """! Build a Multi1D3DRemapper object.

        An intermediate inner 3D mesh is built from a 2D grid defined by the parameters.

        The axial coordinates will be read from the 1D fields passed to the remapper (there are assumed to all share the same axial mesh).

        Each cell of this 2D grid is associated to a 1D field.

        @param xCoordinates x coordinates of the inner mesh to build.
        @param yCoordinates y coordinates of the inner mesh to build.
        @param indexTable For each position of the 2D grid (x coordinate changes first), the index of the 1D field to associate. Put -1 to
        associate to nothing.
        @param weights Weigh of each 1D field to take into account for extensive variables.
        @param meshAlignment If set to True, at the initialization phase of the remapper object, meshes are translated such as their "bounding box"
               are radially centred on (x = 0., y = 0.) and have zmin = 0.
        @param offset Value of the 3D offset between the source (multi1D) and the target (3D) meshes (>0 on z means that the source mesh is above the
               target one). The given vector is used to translate the source mesh (after the mesh alignment, if any).
        @param rescaling Value of a rescaling factor to be applied between the source (multi1D) and the target (3D) meshes (>1 means that the source
               mesh is initially larger than the target one). The scaling is centered on [0., 0., 0.] and is applied to the source mesh after mesh
               alignment or translation, if any.
        @param rotation Value of the rotation between the source (multi1D) and the target (3D) meshes. The rotation is centered on [0., 0., 0.] and
            is about the vertical axis. >0 means that the source mesh is rotated of the given angle compared to the target one. The inverse rotation
            is applied to the source mesh, after mesh alignment or translation, if any. pi means half turn.
        """
        MEDCouplingRemapper.__init__(self)

        self._indexTable = [[] for k in range(max(indexTable) + 1)]
        for position, indice1D in enumerate(indexTable):
            if indice1D >= 0:
                self._indexTable[indice1D].append(position)

        if len(self._indexTable) != len(weights):
            raise Exception("Multi1D3DRemapper.__init__ we give " + str(len(weights)) + "weight values instead of " + str(len(self._indexTable))
                            + ", the number of 1D calculations.")
        self._weights = weights
        self._arrayX = mc.DataArrayDouble(xCoordinates)
        self._arrayX.setInfoOnComponent(0, "X [m]")
        self._arrayY = mc.DataArrayDouble(yCoordinates)
        self._arrayY.setInfoOnComponent(0, "Y [m]")
        self._arrayZ = 0
        self._numberOf1DPositions = (self._arrayX.getNumberOfTuples() - 1) * (self._arrayY.getNumberOfTuples() - 1)
        self._numberOfCellsIn1D = 0
        self._innerMesh = mc.MEDCouplingCMesh("3DMeshFromMulti1D")
        self._innerField = mc.MEDCouplingFieldDouble(mc.ON_CELLS, mc.ONE_TIME)
        self._innerField.setName("3DFieldFromMulti1D")
        self.isInit = False
        self._meshAlignment = meshAlignment
        self._offset = offset
        if rescaling <= 0.:
            raise Exception("Multi1D3DRemapper: rescaling must be > 0!")
        self._rescaling = rescaling
        self._rotation = rotation
        self._cellsToScreenOut3DMesh = []
        self._cellsToScreenOutInnerMesh = []

    def initialize(self, mesh1D, mesh3D):
        """! INTERNAL """
        self._arrayZ = mesh1D.getCoordsAt(0)
        self._innerMesh.setCoords(self._arrayX, self._arrayY, self._arrayZ)
        self._numberOfCellsIn1D = mesh1D.getNumberOfCells()
        self._innerField.setMesh(self._innerMesh)
        array = mc.DataArrayDouble()
        array.alloc(self._numberOfCellsIn1D * self._numberOf1DPositions)
        array.fillWithValue(0.)
        self._innerField.setArray(array)
        if self._meshAlignment:
            for mesh in [self._innerMesh, mesh3D]:
                [(xmin, xmax), (ymin, ymax), (zmin, _)] = mesh.getBoundingBox()
                offsettmp = [-0.5 * (xmin + xmax), -0.5 * (ymin + ymax), -zmin]
                mesh.translate(offsettmp)
        if self._offset != [0., 0., 0.]:
            self._innerMesh.translate([-x for x in self._offset])
        if self._rescaling != 1.:
            self._innerMesh.scale([0., 0., 0.], 1. / self._rescaling)
        if self._rotation != 0.:
            self._innerMesh.rotate([0., 0., 0.], [0., 0., 1.], self._rotation)
        self.prepare(self._innerMesh, mesh3D, "P0P0")

        bary = []
        try:
            bary = self._innerMesh.computeCellCenterOfMass()  # MEDCoupling 9
        except:
            bary = self._innerMesh.getBarycenterAndOwner()  # MEDCoupling 7
        _, cellsId = mesh3D.getCellsContainingPoints(bary, 1.0e-8)
        dsi = cellsId.deltaShiftIndex()
        try:
            self._cellsToScreenOutInnerMesh = dsi.findIdsEqual(0)  # MEDCoupling 9
        except:
            self._cellsToScreenOutInnerMesh = dsi.getIdsEqual(0)  # MEDCoupling 7
        try:
            bary = mesh3D.computeCellCenterOfMass()
        except:
            bary = mesh3D.getBarycenterAndOwner()
        _, cellsId = self._innerMesh.getCellsContainingPoints(bary, 1.0e-8)
        dsi = cellsId.deltaShiftIndex()
        try:
            self._cellsToScreenOut3DMesh = dsi.findIdsEqual(0)
        except:
            self._cellsToScreenOut3DMesh = dsi.getIdsEqual(0)

        self.isInit = True

    def build3DField(self, fields1D, defaultValue, outsideCellsScreening):
        """! INTERNAL """
        if len(fields1D) > 0:
            self._innerField.setNature(fields1D[0].getNature())
        array3D = self._innerField.getArray()
        nbOfElems3D = array3D.getNbOfElems()
        for i, field in enumerate(fields1D):
            array1D = field.getArray()
            if self._innerField.getNature() == mc.ExtensiveMaximum or self._innerField.getNature() == mc.ExtensiveConservation:
                array1D *= self._weights[i]
            for position in self._indexTable[i]:
                array3D.setPartOfValues1(array1D, position, nbOfElems3D, self._numberOf1DPositions, 0, 1, 1)
        resuField = self.transferField(self._innerField, defaultValue)
        if outsideCellsScreening:
            resuField.getArray()[self._cellsToScreenOut3DMesh] = defaultValue
        return resuField

    def build1DFields(self, field3D, defaultValue, outsideCellsScreening):
        """! INTERNAL """
        self._innerField = self.reverseTransferField(field3D, defaultValue)
        array3D = self._innerField.getArray()
        if outsideCellsScreening:
            array3D[self._cellsToScreenOutInnerMesh] = defaultValue
        fields1D = []
        for i, list1D in enumerate(self._indexTable):
            fields1D.append(mc.MEDCouplingFieldDouble(mc.ON_CELLS, mc.ONE_TIME))
            fields1D[-1].setName(field3D.getName())
            mesh1D = mc.MEDCouplingCMesh("mesh1D")
            mesh1D.setCoords(self._arrayZ)
            fields1D[-1].setMesh(mesh1D)
            array1D = mc.DataArrayDouble()
            array1D.alloc(self._numberOfCellsIn1D)
            array1D.fillWithValue(0.)
            for position in list1D:
                array1Dtmp = mc.DataArrayDouble()
                array1Dtmp.alloc(self._numberOfCellsIn1D)
                array1Dtmp.setContigPartOfSelectedValuesSlice(0, array3D, position, array3D.getNumberOfTuples(), self._numberOf1DPositions)
                array1D.addEqual(array1Dtmp)
            if len(list1D) > 0:
                array1D *= 1. / len(list1D)
            if field3D.getNature() == mc.ExtensiveMaximum or field3D.getNature() == mc.ExtensiveConservation:
                array1D *= 1. / self._weights[i]
            fields1D[-1].setArray(array1D)
        return fields1D


class SharedRemappingMulti1D3D(ExchangeMethod):
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

    def __init__(self, remapper, reverse=False, defaultValue=0., linearTransform=(1., 0.), outsideCellsScreening=False):
        """! Build a SharedRemappingMulti1D3D object, to be given to an Exchanger.

        @param remapper A Multi1D3DRemapper object performing the projection. It can thus be shared with other instances of
               SharedRemappingMulti1D3D (its initialization will always be done only once).
        @param reverse Allows the remapper to be shared with an instance of SharedRemappingMulti1D3D performing the reverse exchange
               (the projection will be done in the reverse direction if reverse is set to True). Direct is multi1D -> 3D, reverse is 3D -> multi1D.
        @param defaultValue This is the default value to be assigned, during the projection, in the meshes of the target mesh which are not
               intersected by the source mesh.
        @param linearTransform Tuple (a,b): apply a linear function to all output fields f such as they become a * f + b. The transformation
               is applied after the mesh projection.
        @param outsideCellsScreening If set to True, target cells whose barycentre is outside of source mesh are screen out (defaultValue is assigned
            to them). It can be useful to screen out cells that are in contact with the source mesh, but that should not be intersected by it.
            On the other hand, it will screen out cells actually intersected if their barycenter is outside of source mesh! Be careful with this
            option.
        """
        self._remapper = remapper
        self._isReverse = reverse
        self._defaultValue = defaultValue
        self._linearTransform = linearTransform
        self._outsideCellsScreening = outsideCellsScreening

    def initialize(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! INTERNAL """
        if not self._remapper.isInit:
            if self._isReverse:
                self._remapper.initialize(fieldsToSet[0].getMesh(), fieldsToGet[0].getMesh())
            else:
                self._remapper.initialize(fieldsToGet[0].getMesh(), fieldsToSet[0].getMesh())

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! Project the input fields one by one before returning them as outputs, in the same order. """
        self.initialize(fieldsToGet, fieldsToSet, valuesToGet)
        resu = []
        if self._isReverse:
            for field3D in fieldsToGet:
                resu += self._remapper.build1DFields(field3D, self._defaultValue, self._outsideCellsScreening)
        else:
            indexFirst = 0
            while indexFirst + len(self._remapper._indexTable) <= len(fieldsToGet):
                fields1D = [fieldsToGet[indexFirst + k] for k in range(len(self._remapper._indexTable))]
                resu += [self._remapper.build3DField(fields1D, self._defaultValue, self._outsideCellsScreening)]
                indexFirst += len(self._remapper._indexTable)
        if self._linearTransform != (1., 0.):
            for med in resu:
                med.applyLin(*(self._linearTransform))
        return resu, valuesToGet
