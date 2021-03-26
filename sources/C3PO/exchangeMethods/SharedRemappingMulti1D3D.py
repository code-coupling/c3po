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

import MEDCoupling
from MEDCouplingRemapper import MEDCouplingRemapper


class Multi1D3DRemapper(MEDCouplingRemapper):
    """! Allow to share the mesh projection for different SharedRemappingMulti1D3D objects by building them with the same instance of this class. """

    def __init__(self, XCoordinates, YCoordinates, indexTable, weights):
        """! Build a Multi1D3DRemapper object.

        An intermediate inner 3D mesh is built from a 2D grid defined by the parameters.

        The axial coordinates will be read from the 1D fields passed to the remapper (there are assumed to all share the same axial mesh).

        Each cell of this 2D grid is associated to a 1D field.

        @param XCoordinates x coordinates of the inner mesh to build.
        @param YCoordinates y coordinates of the inner mesh to build.
        @param indexTable For each position of the 2D grid (x coordinate changes first), the index of the 1D field to associate. Put -1 to associate to nothing.
        @param weights Weigh of each 1D field to take into account for extensive variables.
        """
        MEDCouplingRemapper.__init__(self)

        self.indexTable_ = [[] for k in range(max(indexTable) + 1)]
        for position, indice1D in enumerate(indexTable):
            if indice1D >= 0:
                self.indexTable_[indice1D].append(position)

        if len(self.indexTable_) != len(weights):
            raise Exception("Multi1D3DRemapper.__init__ we give " + str(len(weights)) + "weight values instead of " + str(len(self.indexTable_)) + ", the number of 1D calculations.")
        self.weights_ = weights
        self.arrayX_ = MEDCoupling.DataArrayDouble(XCoordinates)
        self.arrayX_.setInfoOnComponent(0, "X [m]")
        self.arrayY_ = MEDCoupling.DataArrayDouble(YCoordinates)
        self.arrayY_.setInfoOnComponent(0, "Y [m]")
        self.arrayZ_ = 0
        self.numberOf1DPositions_ = (self.arrayX_.getNumberOfTuples() - 1) * (self.arrayY_.getNumberOfTuples() - 1)
        self.numberOfCellsIn1D_ = 0
        self.innerMesh_ = MEDCoupling.MEDCouplingCMesh("3DMeshFromMulti1D")
        self.innerField_ = MEDCoupling.MEDCouplingFieldDouble(MEDCoupling.ON_CELLS, MEDCoupling.ONE_TIME)
        self.innerField_.setName("3DFieldFromMulti1D")
        self.isInit_ = False
        self.cellsToScreenOut3DMesh_ = []
        self.cellsToScreenOutInnerMesh_ = []

    def initialize(self, Mesh1D, Mesh3D, meshAlignment, offset, rescaling):
        """! INTERNAL """
        self.arrayZ_ = Mesh1D.getCoordsAt(0)
        self.innerMesh_.setCoords(self.arrayX_, self.arrayY_, self.arrayZ_)
        self.numberOfCellsIn1D_ = Mesh1D.getNumberOfCells()
        self.innerField_.setMesh(self.innerMesh_)
        array = MEDCoupling.DataArrayDouble()
        array.alloc(self.numberOfCellsIn1D_ * self.numberOf1DPositions_)
        array.fillWithValue(0.)
        self.innerField_.setArray(array)
        if meshAlignment:
            for mesh in [self.innerMesh_, Mesh3D]:
                [(xmin, xmax), (ymin, ymax), (zmin, _)] = mesh.getBoundingBox()
                offsettmp = [-0.5 * (xmin + xmax), -0.5 * (ymin + ymax), -zmin]
                mesh.translate(offsettmp)
        if offset != [0., 0., 0.]:
            self.innerMesh_.translate([-x for x in offset])
        if rescaling != 1.:
            self.innerMesh_.scale([0., 0., 0.], 1. / rescaling)
        self.prepare(self.innerMesh_, Mesh3D, "P0P0")

        bary = []
        try:
            bary = self.innerMesh_.computeCellCenterOfMass()        #MEDCoupling 9
        except:
            bary = self.innerMesh_.getBarycenterAndOwner()          #MEDCoupling 7
        c, cI = Mesh3D.getCellsContainingPoints(bary, 1.0e-8)
        dsi = cI.deltaShiftIndex()
        try:
            self.cellsToScreenOutInnerMesh_ = dsi.findIdsEqual(0)   #MEDCoupling 9
        except:
            self.cellsToScreenOutInnerMesh_ = dsi.getIdsEqual(0)    #MEDCoupling 7
        try:
            bary = Mesh3D.computeCellCenterOfMass()
        except:
            bary = Mesh3D.getBarycenterAndOwner()
        c, cI = self.innerMesh_.getCellsContainingPoints(bary, 1.0e-8)
        dsi = cI.deltaShiftIndex()
        try:
            self.cellsToScreenOut3DMesh_ = dsi.findIdsEqual(0)
        except:
            self.cellsToScreenOut3DMesh_ = dsi.getIdsEqual(0)

        self.isInit_ = True

    def Build3DField(self, Fields1D, defaultValue, outsideCellsScreening):
        """! INTERNAL """
        if len(Fields1D) > 0:
            self.innerField_.setNature(Fields1D[0].getNature())
        Array3D = self.innerField_.getArray()
        NbOfElems3D = Array3D.getNbOfElems()
        for i, field in enumerate(Fields1D):
            Array1D = field.getArray()
            if self.innerField_.getNature() == MEDCoupling.Integral or self.innerField_.getNature() == MEDCoupling.IntegralGlobConstraint:
                Array1D *= self.weights_[i]
            for position in self.indexTable_[i]:
                Array3D.setPartOfValues1(Array1D, position, NbOfElems3D, self.numberOf1DPositions_, 0, 1, 1)
        resuField = self.transferField(self.innerField_, defaultValue)
        if outsideCellsScreening:
            resuField.getArray()[self.cellsToScreenOut3DMesh_] = defaultValue
        return resuField

    def Build1DFields(self, Field3D, defaultValue, outsideCellsScreening):
        """! INTERNAL """
        self.innerField_ = self.reverseTransferField(Field3D, defaultValue)
        Array3D = self.innerField_.getArray()
        if outsideCellsScreening:
            Array3D[self.cellsToScreenOutInnerMesh_] = defaultValue
        Fields1D = []
        for i, List1D in enumerate(self.indexTable_):
            Fields1D.append(MEDCoupling.MEDCouplingFieldDouble(MEDCoupling.ON_CELLS, MEDCoupling.ONE_TIME))
            Fields1D[-1].setName(Field3D.getName())
            Mesh1D = MEDCoupling.MEDCouplingCMesh("Mesh1D")
            Mesh1D.setCoords(self.arrayZ_)
            Fields1D[-1].setMesh(Mesh1D)
            Array1D = MEDCoupling.DataArrayDouble()
            Array1D.alloc(self.numberOfCellsIn1D_)
            Array1D.fillWithValue(0.)
            for position in List1D:
                Array1Dtmp = MEDCoupling.DataArrayDouble()
                Array1Dtmp.alloc(self.numberOfCellsIn1D_)
                Array1Dtmp.setContigPartOfSelectedValues2(0, Array3D, position, Array3D.getNumberOfTuples(), self.numberOf1DPositions_)
                Array1D.addEqual(Array1Dtmp)
            if len(List1D) > 0:
                Array1D *= 1. / len(List1D)
            if Field3D.getNature() == MEDCoupling.Integral or Field3D.getNature() == MEDCoupling.IntegralGlobConstraint:
                Array1D *= 1. / self.weights_[i]
            Fields1D[-1].setArray(Array1D)
        return Fields1D


class SharedRemappingMulti1D3D(object):
    """! SharedRemappingMulti1D3D projects the input fields one by one before returning them as outputs, in the same order.

    See C3PO.Exchanger.Exchanger.__init__().

    1D fields are processed in packets using the intermediate mesh defined by the Multi1D3DRemapper object.

    The method assumes that all input fields (or packets) have the same mesh, and produces output fields on identical meshes.

    This output mesh is the one of the first field (or packet) passed to the method (obtained by getInputMEDFieldTemplate).

    The input scalars are returned in the same order, without modification.

    The initialization of the projection method (long operation) is done only once, and can be shared with other instances of SharedRemappingMulti1D3D.
    """

    def __init__(self, remapper, reverse=False, defaultValue=0., linearTransform=(1., 0.), meshAlignment=False, offset=[0., 0., 0.], rescaling=1., outsideCellsScreening=False):
        """! Build a SharedRemappingMulti1D3D object, to be given to an Exchanger.

        @param remapper A Multi1D3DRemapper object performing the projection. It can thus be shared with other instances of SharedRemappingMulti1D3D (its initialization will always be done only once).
        @param reverse Allows the remapper to be shared with an instance of SharedRemappingMulti1D3D performing the reverse exchange (the projection will be done in the reverse direction if reverse is set to True). Direct is multi1D -> 3D, reverse is 3D -> multi1D.
        @param defaultValue This is the default value to be assigned, during the projection, in the meshes of the target mesh which are not intersected by the source mesh.
        @param linearTransform Tuple (a,b): apply a linear function to all output fields f such as they become a * f + b. The transformation is applied after the mesh projection.
        @param meshAlignment If set to True, at the initialization phase of the remapper object, meshes are translated such as their "bounding box" are radially centred on (x = 0., y = 0.) and have zmin = 0.
        @param offset Value of the 3D offset between the source and the target meshes (>0 on z means that the source mesh is above the target one). The given vector is used to translate the source mesh (after the mesh alignment, if any).
        @param rescaling Value of a rescaling factor to be applied between the source and the target meshes (>1 means that the source mesh is initially larger than the target one). The scaling is centered on [0., 0., 0.] and is applied to the source mesh after mesh alignment or translation, if any.
        @param outsideCellsScreening If set to True, target cells whose barycentre is outside of source mesh are screen out (defaultValue is assigned to them). It can be useful to screen out cells that are in contact with the source mesh, but that should not be intersected by it. On the other hand, it will screen out cells actually intersected if their barycenter is outside of source mesh ! Be careful with this option.
        """
        self.remapper_ = remapper
        self.isReverse_ = reverse
        self.defaultValue_ = defaultValue
        self.linearTransform_ = linearTransform
        self.meshAlignment_ = meshAlignment
        self.offset_ = offset
        if rescaling <= 0.:
            raise Exception("SharedRemappingMulti1D3D : rescaling must be > 0!")
        self.rescaling_ = rescaling
        self.outsideCellsScreening_ = outsideCellsScreening

    def initialize(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! INTERNAL """
        if not self.remapper_.isInit_:
            if self.isReverse_:
                self.remapper_.initialize(fieldsToSet[0].getMesh(), fieldsToGet[0].getMesh(), self.meshAlignment_, [-x for x in self.offset_], 1. / self.rescaling_)
            else:
                self.remapper_.initialize(fieldsToGet[0].getMesh(), fieldsToSet[0].getMesh(), self.meshAlignment_, self.offset_, self.rescaling_)

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! Project the input fields one by one before returning them as outputs, in the same order. """
        self.initialize(fieldsToGet, fieldsToSet, valuesToGet)
        resu = []
        if self.isReverse_:
            for field3D in fieldsToGet:
                resu += self.remapper_.Build1DFields(field3D, self.defaultValue_, self.outsideCellsScreening_)
        else:
            index_first = 0
            while index_first + len(self.remapper_.indexTable_) <= len(fieldsToGet):
                Fields1D = [fieldsToGet[index_first + k] for k in range(len(self.remapper_.indexTable_))]
                resu += [self.remapper_.Build3DField(Fields1D, self.defaultValue_, self.outsideCellsScreening_)]
                index_first += len(self.remapper_.indexTable_)
        if self.linearTransform_ != (1., 0.):
            for med in resu:
                med.applyLin(*(self.linearTransform_))
        return resu, valuesToGet
