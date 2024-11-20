# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MEDInterface. """
import c3po.medcouplingCompat as mc

from c3po.multi1D.Multi1DAPI import Multi1DAPI, Multi1DWithObjectsAPI
from c3po.multi1D.Grid import NO_CORRESPONDENCE


def _buildColumnMesh(nameMesh, numCells, numBaseNodes, coordinates):
    """! INTERNAL

    Return a MEDCoupling "column" mesh, built on a 2D base (with only one cell).

    @param nameMesh name of the mesh to be built.
    @param numCells number of axial cells of the column.
    @param numBaseNodes number of nodes of the base.
    @param coordinates 3D coordinates of all nodes of the mesh to be built.

    @return The required mesh.
    """
    mesh = mc.MEDCouplingUMesh(nameMesh, 3)
    mesh.allocateCells(numCells)
    for i in range(numCells):
        connectivities = [0] * (2 * numBaseNodes)
        for j in range(numBaseNodes):
            connectivities[j] = j + numBaseNodes * i
            connectivities[j + numBaseNodes] = j + numBaseNodes * (i + 1)
        mesh.insertNextCell(mc.NORM_POLYHED, len(connectivities), connectivities)
    mesh.finishInsertingCells()
    mesh.setCoords(coordinates)
    mesh.checkConsistencyLight()
    mesh.convertExtrudedPolyhedra()
    return mesh


def _buildGridMesh(grid, height):
    """! INTERNAL

    Return a MEDCoupling "flat" mesh, from a 2D grid, and with only one cell in z.

    @param grid a c3po.multi1D.Grid object.
    @param height Size in z of the mesh to built.

    @return The required mesh (or None if grid is empty).
    """
    meshes = []
    for iObjectCell in range(grid.getNumberOfCells()):
        iObject = grid.getCorrespondence(iObjectCell)
        if iObject < NO_CORRESPONDENCE:
            baseCoordinates = grid.getNodeCoordinates(iObjectCell)
            numNodes = len(baseCoordinates) // 2
            coordinates = mc.DataArrayDouble(2 * numNodes, 3)
            iNodeGlobal = 0
            for iNode in range(numNodes):
                coordinates.setIJ(iNodeGlobal, 0, baseCoordinates[2 * iNode + 0])
                coordinates.setIJ(iNodeGlobal, 1, baseCoordinates[2 * iNode + 1])
                coordinates.setIJ(iNodeGlobal, 2, 0.)
                iNodeGlobal += 1
            for iNode in range(numNodes):
                coordinates.setIJ(iNodeGlobal, 0, baseCoordinates[2 * iNode + 0])
                coordinates.setIJ(iNodeGlobal, 1, baseCoordinates[2 * iNode + 1])
                coordinates.setIJ(iNodeGlobal, 2, height)
                iNodeGlobal += 1
            meshes.append(_buildColumnMesh("tmpMesh", 1, numNodes, coordinates))
    return mc.MEDCouplingMesh.MergeMeshes(meshes) if len(meshes) > 0 else None


class MEDInterface:
    """! @brief MEDInterface links a set of 1D objects with 3D MEDCoupling meshes. """

    def __init__(self, multi1DAPI, baseGrid, objectGrids=None):
        """! Build a MEDInterface object.

        @param multi1DAPI a Multi1DAPI object holding the 1D objects. Should derive from c3po.multi1D.Multi1DAPI.Multi1DWithObjectsAPI if objectGrids is provided.
        @param baseGrid a Grid object positioning the components of multi1DAPI in space.
        @param objectGrids a list of list of Grid objects. The first dimension is associated with baseGrid : len(objectGrids) should be == baseGrid.getNumberOfCells().
               The second dimension is associated with the mesh of the associated component of multi1DAPI : len(objectGrids[i]) should be == multi1DAPI.getNumberOfCells(j) where j = baseGrid.getCorrespondence(i).
               Finally, the grid objects provide the positioning in space of the "internal objects" (see c3po.multi1D.Multi1DAPI.Multi1DWithObjectsAPI) hold by the associated component of multi1DAPI, at the given position.
        """
        if not isinstance(multi1DAPI, Multi1DAPI):
            raise ValueError("The provided multi1DAPI object should derive from multi1DAPI.Multi1DAPI.")
        if objectGrids is not None and not isinstance(multi1DAPI, Multi1DWithObjectsAPI):
            raise ValueError("When objectGrids is provided, the provided multi1DAPI object should derive from multi1DAPI.Multi1DWithObjectsAPI.")

        numCells = baseGrid.getNumberOfCells()
        numChannels = multi1DAPI.getSize()
        if numCells < 1:
            raise ValueError("baseGrid object was not initialized.")
        if numChannels < 1:
            raise ValueError("multi1DAPI object does not have any component.")

        self._multi1DAPI = multi1DAPI
        self._channelCorrespondences = [[] for _ in range(numChannels)]
        self._channelExtensiveFactors = [[] for _ in range(numChannels)]
        self._channelMEDMesh = None
        self._objectCorrespondences = [{} for _ in range(numChannels)]
        self._objectExtensiveFactors = [{} for _ in range(numChannels)]
        self._objectMEDMesh = None

        channelMEDMeshName = "BaseMesh"
        objectMEDMeshName = "ObjectMesh"

        xShift = [0.] * numCells
        yShift = [0.] * numCells
        correspondenceIndex = 0
        meshes = []
        for iCell in range(numCells):
            iChannel = baseGrid.getCorrespondence(iCell)
            if iChannel < NO_CORRESPONDENCE:
                if iChannel >= numChannels:
                    raise ValueError(f"The provided baseGrid object has a correspondence value {iChannel} higher than the number of 1D components {numChannels} of the provided multi1DAPI object.")
                cellSizes = self._multi1DAPI.getCellSizes(iChannel)
                numAxialCells = len(cellSizes)
                if self._multi1DAPI.getNumberOfCells(iChannel) != numAxialCells:
                    raise ValueError(f"Output of getNumberOfCells() method of provided multi1DAPI object ({self._multi1DAPI.getNumberOfCells(iChannel)}) is not equal to the number of cells provided by getCellSizes() ({numAxialCells}) for component {iChannel}.")
                if numAxialCells > 0:
                    baseCoordinates = baseGrid.getNodeCoordinates(iCell)
                    numNodes = len(baseCoordinates) // 2
                    coordinates = mc.DataArrayDouble((numAxialCells + 1) * numNodes, 3)
                    zPosition = 0.0
                    iNodeGlobal = 0
                    for iNode in range(numNodes):
                        coordinates.setIJ(iNodeGlobal, 0, baseCoordinates[2 * iNode + 0])
                        xShift[iCell] += baseCoordinates[2 * iNode + 0]
                        coordinates.setIJ(iNodeGlobal, 1, baseCoordinates[2 * iNode + 1])
                        yShift[iCell] += baseCoordinates[2 * iNode + 1]
                        coordinates.setIJ(iNodeGlobal, 2, zPosition)
                        iNodeGlobal += 1
                    xShift[iCell] /= numNodes
                    yShift[iCell] /= numNodes
                    for iAxialCell in range(numAxialCells):
                        zPosition += cellSizes[iAxialCell]
                        for iNode in range(numNodes):
                            coordinates.setIJ(iNodeGlobal, 0, baseCoordinates[2 * iNode + 0])
                            coordinates.setIJ(iNodeGlobal, 1, baseCoordinates[2 * iNode + 1])
                            coordinates.setIJ(iNodeGlobal, 2, zPosition)
                            iNodeGlobal += 1

                    tmpMesh = _buildColumnMesh("tmpMesh", numAxialCells, numNodes, coordinates)
                    meshes.append(tmpMesh)

                    self._channelCorrespondences[iChannel].append(correspondenceIndex)
                    self._channelExtensiveFactors[iChannel].append(0.)
                    correspondenceIndex += numAxialCells

        self._channelMEDMesh = mc.MEDCouplingMesh.MergeMeshes(meshes)
        self._channelMEDMesh.mergeNodes(1.E-8)
        self._channelMEDMesh.setName(channelMEDMeshName)

        channelMEDMeshVolumes = self._channelMEDMesh.getMeasureField(True)
        volumeArray = channelMEDMeshVolumes.getArray()
        for iChannel in range(len(self._channelCorrespondences)):
            channelVolume = 0.
            for iCell in range(len(self._channelCorrespondences[iChannel])):
                self._channelExtensiveFactors[iChannel][iCell] = volumeArray[self._channelCorrespondences[iChannel][iCell]]
                channelVolume += self._channelExtensiveFactors[iChannel][iCell]
            if channelVolume > 0.:
                for iCell in range(len(self._channelCorrespondences[iChannel])):
                    self._channelExtensiveFactors[iChannel][iCell] /= channelVolume

        if objectGrids is not None:
            if len(objectGrids) != numCells:
                raise ValueError(f"If provided, len(objectGrids) (here {len(objectGrids)}) must be equal to the number of cells in baseGrid (here {numCells}).")
            builtMEDGrids = {}
            meshes = []
            correspondenceIndex = 0
            for iCell in range(numCells):
                iChannel = baseGrid.getCorrespondence(iCell)
                if iChannel < NO_CORRESPONDENCE and len(objectGrids[iCell]) > 0:
                    cellSizes = self._multi1DAPI.getCellSizes(iChannel)
                    numAxialCells = len(cellSizes)
                    if len(objectGrids[iCell]) != numAxialCells:
                        raise ValueError(f"We found in objectGrids, for the cell {iCell} (associated to the component {iChannel}), {len(objectGrids[iCell])} Grids, whereas we need {numAxialCells} of them (the number of axial meshes in the component).")
                    channelObjectNames = self._multi1DAPI.getObjectNames(iChannel)
                    zPosition = 0.
                    for iAxialCell in range(numAxialCells):

                        for objectName in channelObjectNames[iAxialCell]:
                            if objectName not in self._objectCorrespondences[iChannel]:
                                self._objectCorrespondences[iChannel][objectName] = [[] for _ in range(numAxialCells)]
                                self._objectExtensiveFactors[iChannel][objectName] = [[] for _ in range(numAxialCells)]

                        if (objectGrids[iCell][iAxialCell], cellSizes[iAxialCell]) not in builtMEDGrids:
                            builtMEDGrids[(objectGrids[iCell][iAxialCell], cellSizes[iAxialCell])] = _buildGridMesh(objectGrids[iCell][iAxialCell], cellSizes[iAxialCell])
                        if builtMEDGrids[(objectGrids[iCell][iAxialCell], cellSizes[iAxialCell])] is not None:
                            tmpMesh = builtMEDGrids[(objectGrids[iCell][iAxialCell], cellSizes[iAxialCell])].deepCopy()
                            tmpMesh.translate([xShift[iCell], yShift[iCell], zPosition])
                            meshes.append(tmpMesh)

                        for iObjectCell in range(objectGrids[iCell][iAxialCell].getNumberOfCells()):
                            iObject = objectGrids[iCell][iAxialCell].getCorrespondence(iObjectCell)
                            if iObject < NO_CORRESPONDENCE:
                                if iObject >= len(channelObjectNames[iAxialCell]):
                                    raise ValueError(f"We found in the objectGrids associated with component {iChannel}, at the axial cell {iAxialCell}, a wrong object index {iObject}. It must be < {len(channelObjectNames[iAxialCell])}, the number of objects in this axial cell of this component.")
                                objectName = channelObjectNames[iAxialCell][iObject]
                                self._objectCorrespondences[iChannel][objectName][iAxialCell].append(correspondenceIndex)
                                self._objectExtensiveFactors[iChannel][objectName][iAxialCell].append(0.)

                                correspondenceIndex += 1
                        zPosition += cellSizes[iAxialCell]
            self._objectMEDMesh = mc.MEDCouplingMesh.MergeMeshes(meshes)
            self._objectMEDMesh.mergeNodes(1.E-8)
            self._objectMEDMesh.setName(objectMEDMeshName)

            objectMEDMeshVolumes = self._objectMEDMesh.getMeasureField(True)
            volumeArray = objectMEDMeshVolumes.getArray()
            for iChannel in range(len(self._objectCorrespondences)):
                for objectName in self._objectCorrespondences[iChannel]:
                    correspondences = self._objectCorrespondences[iChannel][objectName]
                    extensiveFactors = self._objectExtensiveFactors[iChannel][objectName]
                    for iAxialCell in range(len(correspondences)):
                        objectVolume = 0.
                        for iCell in range(len(correspondences[iAxialCell])):
                            extensiveFactors[iAxialCell][iCell] = volumeArray[correspondences[iAxialCell][iCell]]
                            objectVolume += extensiveFactors[iAxialCell][iCell]
                        if objectVolume > 0.:
                            for iCell in range(len(correspondences[iAxialCell])):
                                extensiveFactors[iAxialCell][iCell] /= objectVolume

    def getBaseMEDMesh(self):
        """! Return the 3D MEDCouling first level mesh (whose 2D base is baseGrid).

        @return the 3D MEDCouling first level mesh.
        """
        return self._channelMEDMesh

    def getObjectMEDMesh(self):
        """! Return the 3D MEDCouling second level mesh (built using objectGrids[i][j] at each cell of the BaseMEDMesh).

        @return the 3D MEDCouling second level mesh (and None if not defined).
        """
        return self._objectMEDMesh

    def getPartOfObjectMEDMesh(self, objectNames):
        """! Return the part of the 3D MEDCouling second level mesh associated with the provided object names.

        @param objectNames list of object names for which the mesh is required.
        @return the part of the 3D MEDCouling second level mesh, associated with the provided object names.
        """
        if self._objectMEDMesh is None:
            return self.getBaseMEDMesh()
        iCellToInclude = []
        for correspondenceLevel0 in self._objectCorrespondences:
            for objectName in objectNames:
                if objectName in correspondenceLevel0:
                    for correspondenceLevel1 in correspondenceLevel0[objectName]:
                        iCellToInclude += correspondenceLevel1

        meshPart = self._objectMEDMesh.buildPartAndReduceNodes(iCellToInclude)[0]
        meshPart.setName(self._objectMEDMesh.getName())
        return meshPart

    def getField(self, fieldName):
        """! Return the 3D MEDCoupling field associated with fieldName.

        @note the field underlying mesh is either the same than getBaseMEDMesh(), or the same than getObjectMEDMesh(), depending on fieldName.

        @param fieldName name of the required field.
        @return the required 3D MEDCoupling field.
        """
        fieldNature = self._multi1DAPI.getNature(fieldName)
        isIntensive = fieldNature in (mc.IntensiveConservation, mc.IntensiveMaximum)

        requiredObjects = []
        try:
            requiredObjects = self._multi1DAPI.getObjectNamesInField(fieldName)
        except:
            pass
        isObjectField = len(requiredObjects) > 0
        numComponents = len(requiredObjects) if isObjectField else 1

        valuesArray = mc.DataArrayDouble()
        if isObjectField and self._objectMEDMesh is not None:
            numComponents = 1
            valuesArray.alloc(self._objectMEDMesh.getNumberOfCells(), numComponents)
        else:
            valuesArray.alloc(self._channelMEDMesh.getNumberOfCells(), numComponents)
        valuesArray.fillWithValue(-1.)

        for iChannel, cellList in enumerate(self._channelCorrespondences):
            numCells = 0
            if len(cellList) > 0:
                numCells = self._multi1DAPI.getNumberOfCells(iChannel)
                if isObjectField:
                    values = self._multi1DAPI.getObjectValues(iChannel, fieldName)
                    if self._objectMEDMesh is None:
                        for j, iCell in enumerate(cellList):
                            extensiveFactor = self._channelExtensiveFactors[iChannel][j] if not isIntensive else 1.
                            for iCompo in range(numComponents):
                                if len(values[iCompo]) == numCells:
                                    for iAxialCell in range(numCells):
                                        valuesArray.setIJ(iCell + iAxialCell, iCompo, values[iCompo][iAxialCell] * extensiveFactor)
                                else:
                                    for iAxialCell in range(numCells):
                                        valuesArray.setIJ(iCell + iAxialCell, iCompo, -1.)
                    else:
                        for iObject, objectName in enumerate(requiredObjects):
                            if objectName in self._objectCorrespondences[iChannel]:
                                if len(values[iObject]) == numCells:
                                    correspondences = self._objectCorrespondences[iChannel][objectName]
                                    if isIntensive:
                                        for iCell in range(numCells):
                                            for j, jCell in enumerate(correspondences[iCell]):
                                                valuesArray.setIJ(jCell, 0, values[iObject][iCell])
                                    else:
                                        extensiveFactors = self._objectExtensiveFactors[iChannel][objectName]
                                        for iCell in range(numCells):
                                            for j, jCell in enumerate(correspondences[iCell]):
                                                extensiveFactor = extensiveFactors[iCell][j]
                                                valuesArray.setIJ(jCell, 0, values[iObject][iCell] * extensiveFactor)
                                else:
                                    for iCell in range(numCells):
                                        for jCell in correspondences[iCell]:
                                            valuesArray.setIJ(jCell, 0, -1.)
                else:
                    values = self._multi1DAPI.getValues(iChannel, fieldName)
                    for j, iCell in enumerate(cellList):
                        factor = self._channelExtensiveFactors[iChannel][j] if not isIntensive else 1.
                        for iAxialCell in range(numCells):
                            valuesArray.setIJ(iCell + iAxialCell, 0, values[iAxialCell] * factor)
        if isObjectField and self._objectMEDMesh is None:
            valuesArray.setInfoOnComponents(requiredObjects)
        field = mc.MEDCouplingFieldDouble(mc.ON_CELLS, mc.ONE_TIME)
        if isObjectField and self._objectMEDMesh is not None:
            field.setMesh(self._objectMEDMesh)
        else:
            field.setMesh(self._channelMEDMesh)
        field.setName(fieldName)
        field.setTime(1, 1, 0)
        field.setArray(valuesArray)
        field.setNature(fieldNature)
        return field

    def setField(self, fieldName, field):
        """! Set a 3D MEDCoupling field.

        @note The field underlying mesh must be the base one (getBaseMEDMesh()) or the object one (getObjectMEDMesh()), depending on fieldName. No projection is made.

        @param fieldName name of the field to set.
        @param field MEDCoupling field with data to be set.
        """
        fieldNature = field.getNature()
        if fieldNature == mc.NoNature:
            raise Exception("The nature of the provided field is not defined ('NoNature' found). Please define one.")
        isIntensive = fieldNature in (mc.IntensiveConservation, mc.IntensiveMaximum)

        valuesArray = field.getArray()

        requiredObjects = []
        try:
            requiredObjects = self._multi1DAPI.getObjectNamesInField(fieldName)
        except:
            pass
        isObjectField = len(requiredObjects) > 0
        numComponents = len(requiredObjects) if isObjectField and self._objectMEDMesh is None else 1

        if valuesArray.getNumberOfComponents() != numComponents:
            raise ValueError(f"The number of components of the provided field ({valuesArray.getNumberOfComponents()}) is not equal to the number of expected components ({numComponents}).")

        values = []
        for iChannel, cellList in enumerate(self._channelCorrespondences):
            if len(cellList) > 0:
                numCells = self._multi1DAPI.getNumberOfCells(iChannel)
                if isObjectField:
                    values = [[0.] * numCells for _ in range(len(requiredObjects))]
                    if self._objectMEDMesh is None:
                        intensiveFactor = 1. / len(cellList) if isIntensive else 1.
                        for iCell in cellList:
                            for iAxialCell in range(numCells):
                                for iCompo in range(numComponents):
                                    values[iCompo][iAxialCell] += valuesArray.getIJ(iCell + iAxialCell, iCompo) * intensiveFactor
                    else:
                        for iObject, objectName in enumerate(requiredObjects):
                            if objectName in self._objectCorrespondences[iChannel]:
                                correspondences = self._objectCorrespondences[iChannel][objectName]
                                for iCell in range(numCells):
                                    if len(correspondences[iCell]) > 0:
                                        intensiveFactor = 1. / len(correspondences[iCell]) if isIntensive else 1.
                                        for jCell in correspondences[iCell]:
                                            values[iObject][iCell] += valuesArray.getIJ(jCell, 0) * intensiveFactor
                    self._multi1DAPI.setObjectValues(iChannel, fieldName, values)
                else:
                    values = [0.] * numCells
                    intensiveFactor = 1. / len(cellList) if isIntensive else 1.
                    for iCell in cellList:
                        for iAxialCell in range(numCells):
                            values[iAxialCell] += valuesArray.getIJ(iCell + iAxialCell, 0) * intensiveFactor
                    self._multi1DAPI.setValues(iChannel, fieldName, values)
