# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class SharedRemapping. """
from __future__ import print_function, division
import pickle

from c3po.medcouplingCompat import MEDCouplingRemapper
from c3po.exchangeMethods.ExchangeMethod import ExchangeMethod


def computeCellsToScreenOut(mesh1, mesh2):
    """! INTERNAL """
    bary = []
    try:
        bary = mesh1.computeCellCenterOfMass()  # MEDCoupling 9
    except:
        bary = mesh1.getBarycenterAndOwner()  # MEDCoupling 7
    _, cellsId = mesh2.getCellsContainingPoints(bary, 1.0e-8)
    dsi = cellsId.deltaShiftIndex()
    try:
        return dsi.findIdsEqual(0)  # MEDCoupling 9
    except:
        return dsi.getIdsEqual(0)  # MEDCoupling 7


class Remapper(object):
    """! Allow to share the mesh projection for different SharedRemapping objects by building them with the same instance of this class. """

    def __init__(self, meshAlignment=False, offset=None, rescaling=1., rotation=0., outsideCellsScreening=False, reverseTransformations=True):
        """! Build a Remapper object.

        @param meshAlignment If set to True, at the initialization phase of the Remapper object, meshes are translated such as their "bounding
            box" are radially centred on (x = 0., y = 0.) and, if the meshes are 3D, have zmin = 0.
        @param offset Value of the offset between the source and the target meshes (>0 on z means that the source mesh is above the target one).
            The given vector is used to translate the source mesh (after the mesh alignment, if any). The dimension of offset must be >= the
            dimension of the meshes (we use only the first components).
        @param rescaling Value of a rescaling factor to be applied between the source and the target meshes (>1 means that the source mesh is
            initially larger than the target one). The scaling is centered on [0., 0.(, 0.)] and is applied to the source mesh after mesh
            alignment or translation, if any.
        @param rotation Value of the rotation between the source and the target meshes. The rotation is centered on [0., 0.(, 0.)] and is about
            the vertical axis. >0 means that the source mesh is rotated of the given angle compared to the target one. The inverse rotation is
            applied to the source mesh, after mesh alignment or translation, if any. pi means half turn.
        @param outsideCellsScreening If set to True, target (and source) cells whose barycentre is outside of source (or target) mesh are screen
            out (defaultValue is assigned to them). It can be useful to screen out cells that are in contact with the other mesh, but that should
            not be intersected by it. On the other hand, it will screen out cells actually intersected if their barycenter is outside of the other
            mesh ! Be careful with this option.
        @param reverseTransformations If set to True, all the transformations (translation, rescaling and rotation) applied in initialize() on
            the provided meshes are reversed at the end of initialize().

        @warning There seems to be a bug in MEDCoupling that may cause wrong results when rescaling is used with a source mesh of nature
            ExtensiveMaximum or IntensiveConservation. In this case, it is necessary to use reverseTransformations=False and to never perform a
            remapping on a field whose underling mesh has not been rescaled.
        """
        self.isInit = False
        self._meshAlignment = meshAlignment
        self._offset = offset
        if rescaling <= 0.:
            raise ValueError("Remapper: rescaling must be > 0!")
        self._rescaling = rescaling
        self._rotation = rotation
        self._outsideCellsScreening = outsideCellsScreening
        self._reverseTransformations = reverseTransformations
        self._cellsToScreenOutSource = []
        self._cellsToScreenOutTarget = []
        self._loadedMatrix = None
        self._remapper = MEDCouplingRemapper()

    def initialize(self, sourceMesh, targetMesh):
        """! INTERNAL """
        meshDimension = sourceMesh.getMeshDimension()
        if targetMesh.getMeshDimension() != meshDimension:
            raise ValueError("Remapper : the dimension of source and target meshes are not the same ({} : {} and {} : {} respectively).".format(
                sourceMesh.getName(), meshDimension, targetMesh.getName(), targetMesh.getMeshDimension()))
        offsetAlign = []
        userOffset = None
        if self._meshAlignment:
            for mesh in [sourceMesh, targetMesh]:
                if meshDimension == 2:
                    [(xmin, xmax), (ymin, ymax)] = mesh.getBoundingBox()
                else:
                    [(xmin, xmax), (ymin, ymax), (zmin, _)] = mesh.getBoundingBox()
                offsetAlign.append([-0.5 * (xmin + xmax), -0.5 * (ymin + ymax)] + ([-zmin] if meshDimension == 3 else []))
                mesh.translate(offsetAlign[-1])
        if self._offset is not None:
            if len(self._offset) < meshDimension:
                raise ValueError("Remapper : the dimension the provided offset vector ({}) is not >= the mesh dimension ({}).".format(len(self._offset), meshDimension))
            userOffset = self._offset[:meshDimension]
            if userOffset != [0.] * meshDimension:
                sourceMesh.translate([-x for x in userOffset])
        if self._rescaling != 1.:
            sourceMesh.scale([0.] * meshDimension, 1. / self._rescaling)
        if self._rotation != 0.:
            if meshDimension == 2:
                sourceMesh.rotate([0., 0.], self._rotation)
            else:
                sourceMesh.rotate([0., 0., 0.], [0., 0., 1.], self._rotation)

        if self._loadedMatrix is not None:
            self._remapper.setCrudeMatrix(sourceMesh, targetMesh, "P0P0", self._loadedMatrix)
            self._loadedMatrix = None
        else:
            self._remapper.prepare(sourceMesh, targetMesh, "P0P0")

        if self._outsideCellsScreening:
            self._cellsToScreenOutTarget = computeCellsToScreenOut(targetMesh, sourceMesh)
            self._cellsToScreenOutSource = computeCellsToScreenOut(sourceMesh, targetMesh)

        if self._reverseTransformations:
            if self._rotation != 0.:
                if meshDimension == 2:
                    sourceMesh.rotate([0., 0.], -self._rotation)
                else:
                    sourceMesh.rotate([0., 0., 0.], [0., 0., 1.], -self._rotation)
            if self._rescaling != 1.:
                sourceMesh.scale([0.] * meshDimension, self._rescaling)
            if userOffset is not None and userOffset != [0.] * meshDimension:
                sourceMesh.translate(userOffset)
            if self._meshAlignment:
                sourceMesh.translate([-x for x in offsetAlign[0]])
                targetMesh.translate([-x for x in offsetAlign[1]])

        self.isInit = True

    def directRemap(self, field, defaultValue):
        """! INTERNAL """
        outputField = self._remapper.transferField(field, defaultValue)
        outputField.getArray()[self._cellsToScreenOutTarget] = defaultValue
        return outputField

    def reverseRemap(self, field, defaultValue):
        """! INTERNAL """
        outputField = self._remapper.reverseTransferField(field, defaultValue)
        outputField.getArray()[self._cellsToScreenOutSource] = defaultValue
        return outputField

    def getMatrix(self):
        """! Export remapping matrix.

        The matrix can be serialized using pickle, then it can be loaded using setMatrix() method in order to save initialization time.

        @note This method requires scipy.

        @param matrix object.
        """
        if not self.isInit:
            raise AssertionError("Remapper.getMatrix: the object is not initialized! Remapper is usually initialized by the SharedRemapping object using it at the first call.")
        return self._remapper.getCrudeMatrix()

    def setMatrix(self, matrix):
        """! Load remapping matrix.

        This matrix is usually obtained by exportMatrix() method.

        @note This method requires scipy.

        @param matrix object.
        """
        if self.isInit:
            raise AssertionError("Remapper.setMatrix: the object is already initialized! You can set matrix only before initialization.")
        self._loadedMatrix = matrix

    def exportMatrix(self, fileName):
        """! Export remapping matrix on file.

        This file can be loaded using loadMatrix() method in order to save initialization time.

        @param fileName name of the file to write in.
        """
        with open(fileName, 'wb') as matrixFile:
            matrix = self.getMatrix()
            pickle.dump(matrix, matrixFile)

    def loadMatrix(self, fileName):
        """! Load remapping matrix from file.

        This file is usually written by exportMatrix() method.

        @note This method requires scipy.

        @param fileName name of the file to read from.
        """
        with open(fileName, 'rb') as matrixFile:
            self.setMatrix(pickle.load(matrixFile))


class SharedRemapping(ExchangeMethod):
    """! SharedRemapping is an ExchangeMethod which projects the input fields one by one before returning them as outputs,
    in the same order.

    See c3po.Exchanger.Exchanger.__init__().

    The method assumes that all input fields have the same mesh, and produces output fields on identical meshes.

    This output mesh is the one of the first field passed to the method (obtained by getInputMEDFieldTemplate).

    The input scalars are returned in the same order, without modification.

    The initialization of the projection method (long operation) is done only once, and can be shared with other instances of
    SharedRemapping through a Remapper object.
    """

    def __init__(self, remapper, reverse=False, defaultValue=0., linearTransform=(1., 0.)):
        """! Build an SharedRemapping object, to be given to an Exchanger.

        @param remapper A Remapper object (defined in C3PO) performing the projection. It can thus be shared with other instances of
               SharedRemapping (its initialization will always be done only once).
        @param reverse Allows the Remapper to be shared with an instance of SharedRemapping performing the reverse exchange (the projection
               will be done in the reverse direction if reverse is set to True).
        @param defaultValue This is the default value to be assigned, during the projection, in the meshes of the target mesh that are not
               intersected by the source mesh.
        @param linearTransform Tuple (a,b): apply a linear function to all output fields f such as they become a * f + b. The transformation
               is applied after the mesh projection.
        """
        self._remapper = remapper
        self._isReverse = reverse
        self._defaultValue = defaultValue
        self._linearTransform = linearTransform

    def initialize(self, fieldsToGet, fieldsToSet):
        """! INTERNAL """
        if not self._remapper.isInit:
            sourceField = fieldsToSet[0] if self._isReverse else fieldsToGet[0]
            targetField = fieldsToGet[0] if self._isReverse else fieldsToSet[0]
            try:
                self._remapper.initialize(sourceField.getMesh(), targetField.getMesh())
            except ValueError as exception:
                raise ValueError("SharedRemapping : the following error occured during remapper initialization with the fields {} and {}:\n    {}".format(sourceField.getName(), targetField.getName(), exception))

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! Project the input fields one by one before returning them as outputs, in the same order. """
        if len(fieldsToSet) != len(fieldsToGet):
            raise ValueError("SharedRemapping : there must be the same number of input and output MED fields")

        transformedMED = []

        if len(fieldsToSet) > 0:
            self.initialize(fieldsToGet, fieldsToSet)
            for field in fieldsToGet:
                if self._isReverse:
                    transformedMED.append(self._remapper.reverseRemap(field, self._defaultValue))
                else:
                    transformedMED.append(self._remapper.directRemap(field, self._defaultValue))
            if self._linearTransform != (1., 0.):
                for med in transformedMED:
                    med.applyLin(*(self._linearTransform))

        return transformedMED, valuesToGet

    def getPatterns(self):
        """! See ExchangeMethod.getPatterns. """
        return [(1, 1, 0, 0), (0, 0, 1, 1)]

    def clean(self):
        """! See ExchangeMethod.clean. """
        self._remapper.isInit = False
