# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the classes Grid, MEDGrid, CartesianGrid, HexagonalGrid and MultiLevelGrid. """
from abc import ABC, abstractmethod
import math

import c3po.medcouplingCompat as mc

NO_CORRESPONDENCE = 2**62


class Grid(ABC):
    """! Grid is an abstract class defining a 2D mesh to be used by MEDInterface.

    Each cell is associated with an integer (correspondence) that will be used to identify a 1D object.
    """

    @abstractmethod
    def clone(self):
        """! Return a clone of self.

        @return a clone of self.
        """

    @abstractmethod
    def getCorrespondence(self, cellId):
        """! Return the correspondence associated with the required cell.

        @param cellId Index of the cell in the mesh.
        @return correspondence associated with the cell.
        """

    @abstractmethod
    def getNumberOfCells(self):
        """! Return the number of cells in the grid.

        @return the number of cells in the grid.
        """

    @abstractmethod
    def setCorrespondences(self, correspondences):
        """! Set the whole table of correspondences.

        @note Use c3po.multi1D.NO_CORRESPONDENCE as correspondence value in empty positions.

        @param correspondences Table of correspondence to be copied. correspondences[i] will be associated with the cell i.
        """

    @abstractmethod
    def setCorrespondence(self, cellId, correspondence):
        """! Set one correspondence in one cell.

        @note Use c3po.multi1D.NO_CORRESPONDENCE as correspondence value in empty positions.

        @param cellId Index of the cell in the mesh.
        @param correspondence value to set in the cell.
        """

    @abstractmethod
    def getNodeCoordinates(self, cellId):
        """! Return the coordinate of the nodes of one cell.

        @param cellId Index of the cell in the mesh.
        @return a list with the 2D coordinates of the nodes of the cell.
        """

    @abstractmethod
    def shift(self, xShift, yShift):
        """! Shift (geometric translation) the grid.

        @param xShift shift to be applied on x coordinate.
        @param yShift shift to be applied on y coordinate.
        """

    @abstractmethod
    def getMEDMesh(self):
        """! Return a MEDCoupling mesh image of the grid (but without correspondences).

        @note it should be the same result than toMED().getMesh().

        @return a MEDCoupling 2D mesh.
        """

    def toMED(self):
        """! Return a MEDCoupling field image of self.

        @return a MEDCoupling field image of self.
        """
        mesh = self.getMEDMesh()
        field = mc.MEDCouplingFieldInt(mc.ON_CELLS)
        field.setMesh(mesh)
        array = mc.DataArrayInt32()
        array.alloc(mesh.getNumberOfCells())
        for iCell in range(mesh.getNumberOfCells()):
            array.setIJ(iCell, 0, self.getCorrespondence(iCell))
        field.setArray(array)
        field.setName("MEDGrid")
        return field


class MEDGrid(Grid):
    """! @brief MEDGrid allows to handle a 2D grid defined with a MEDCoupling mesh or field. """

    def __init__(self, field):
        """! Build a MEDgrid from the provided MEDCoupling field. This field could have been written by Grid.toMED().

        @param field MEDCoupling field (should be a MEDCouplingFieldInt). It may have one component providing the correspondences (see Grid).
        """
        if field.getArray().getNumberOfComponents() > 1:
            raise ValueError(f"The number of field components must be less than or equal to 1. We found {field.getNumberOfComponents()} of then.")

        if field.getMesh().getMeshDimension() > 0 and field.getMesh().getMeshDimension() != 2:
            raise ValueError(f"The mesh dimension should be 2 (it is {field.getMesh().getMeshDimension()}).")

        self._medMesh = field.getMesh()
        self._correspondences = [NO_CORRESPONDENCE] * (self._medMesh.getNumberOfCells() if field.getMesh().getMeshDimension() == 2 else 0)
        if field.getArray().getNumberOfComponents() == 1:
            array = field.getArray()
            for i in range(len(self._correspondences)):
                self._correspondences[i] = array[i]

    def clone(self):
        """! See Grid.clone(). """
        output = MEDGrid(self.toMED())
        output._medMesh = output._medMesh.deepCopy()  # pylint: disable=protected-access
        return output

    def getCorrespondence(self, cellId):
        """! See Grid.getCorrespondence(). """
        try:
            return self._correspondences[cellId]
        except IndexError:
            raise ValueError(f"The provided cell index ({cellId}) is greater than the number of cells ({self.getNumberOfCells()})")

    def getNumberOfCells(self):
        """! See Grid.getNumberOfCells(). """
        return len(self._correspondences)

    def setCorrespondences(self, correspondences):
        """! See Grid.setCorrespondences(). """
        if len(correspondences) != self.getNumberOfCells():
            raise ValueError(f"The size of the provided table ({len(correspondences)}) is not equal to the number of cells ({self.getNumberOfCells()})")
        self._correspondences[:] = correspondences[:]

    def setCorrespondence(self, cellId, correspondence):
        """! See Grid.setCorrespondence(). """
        try:
            self._correspondences[cellId] = correspondence
        except IndexError:
            raise ValueError(f"The provided cell index ({cellId}) is greater than the number of cells ({self.getNumberOfCells()})")

    def getNodeCoordinates(self, cellId):
        """! See Grid.getNodeCoordinates(). """
        coordinates = []
        nodeList = self._medMesh.getNodeIdsOfCell(cellId)
        for iNode in nodeList:
            nodeCoordinates = self._medMesh.getCoordinatesOfNode(iNode)
            coordinates.append(nodeCoordinates[0])
            coordinates.append(nodeCoordinates[1])
        return coordinates

    def shift(self, xShift, yShift):
        """! See Grid.translate(). """
        self._medMesh.translate([xShift, yShift])

    def getMEDMesh(self):
        return self._medMesh


class CartesianGrid(MEDGrid):
    """! CartesianGrid allows to define and handle a cartesian 2D mesh.

    Cells are numbered along the x axis first, then along the y axis ( loop(yDim){ loop(xDim) {i++}} ).
    The mesh is centered on (0., 0.).
    """

    def __init__(self, xSizes, ySizes):
        """! Build a cartesian grid (centered on (0., 0.)) from the sizes of the cells.

        @param xSizes List with the sizes of the cells in the x direction.
        @param ySizes List with the sizes of the cells in the y direction.
        """
        self._xSizes = []
        self._xSizes[:] = xSizes[:]
        self._ySizes = []
        self._ySizes[:] = ySizes[:]

        xCoordinates = [0.] * (len(xSizes) + 1)
        yCoordinates = [0.] * (len(ySizes) + 1)

        totalSize = sum(xSizes)
        xCoordinates[0] = -0.5 * totalSize
        for i, size in enumerate(xSizes):
            xCoordinates[i + 1] = xCoordinates[i] + size

        totalSize = sum(ySizes)
        yCoordinates[0] = -0.5 * totalSize
        for i, size in enumerate(ySizes):
            yCoordinates[i + 1] = yCoordinates[i] + size

        arrayX = mc.DataArrayDouble(xCoordinates)
        arrayX.setInfoOnComponent(0, "X [m]")
        arrayY = mc.DataArrayDouble(yCoordinates)
        arrayY.setInfoOnComponent(0, "Y [m]")
        mesh = mc.MEDCouplingCMesh("CartesianMesh")
        mesh.setCoords(arrayX, arrayY)
        mesh = mesh.buildUnstructured()

        field = mc.MEDCouplingFieldInt(mc.ON_CELLS)
        field.setMesh(mesh)
        array = mc.DataArrayInt32()
        field.setArray(array)
        field.setName("CartesianGrid")

        super().__init__(field)

    def clone(self):
        """! see Grid.clone() """
        output = CartesianGrid(self._xSizes, self._ySizes)
        output._correspondences[:] = self._correspondences[:]  # pylint: disable=protected-access
        return output

    def setCorrespondenceCartesian(self, xIndex, yIndex, correspondence):
        """! Set one correspondence from the indexes of the cell in the cartesian grid.

        @note Use c3po.multi1D.NO_CORRESPONDENCE as correspondence value in empty positions.

        @param xIndex Index of the cell along the x axis.
        @param yIndex Index of the cell along the y axis.
        @param correspondence value to associate with the cell.
        """
        cellId = xIndex + len(self._xSizes) * yIndex
        self.setCorrespondence(cellId, correspondence)


class HexagonalGrid(MEDGrid):
    """! HexagonalGrid allows to define and handle an hexagonal 2D mesh.

    Cells are numbered in a "snail" way, from inside to outside. The central cell is numbered 0. The first cell of each ring makes an angle of -pi/6 with x axis.
    The mesh is centered on (0., 0.).
    """

    def __init__(self, numRings, pitch):
        """! Build a hexagonal grid (centered on (0., 0.)).

        @param numRings Number of rings (use 0 for only one cell, 1 to get 7 etc.)
        @param pitch flat-to-flat distance.
        """
        self._numRings = numRings
        self._pitch = pitch
        radius = pitch / math.sqrt(3.0)

        numCells = 0
        for i in range(1, self._numRings + 1):
            numCells += i
        numCells = numCells * 6 + 1

        coordinatesOfCellCenters = [[]] * numCells

        cellId = 0
        angle = math.pi / 3.0

        coordinatesOfCellCenters[0] = [0., 0.]
        cellId += 1
        for i in range(1, self._numRings + 1):
            for j in range(0, i * 6):
                isector = j // i
                theta = -angle * 0.5 + isector * angle       # angle entre Ox et le debut du secteur
                alpha = 2.0 * angle + theta                  # angle entre l'axe passant par l'origine et le premier assemblage du secteur avec l'axe du secteur.
                iside = j - ((j // i) * i)               # numero sur la rangee.
                xCoord = (pitch * i) * math.cos(theta) + (pitch * iside) * math.cos(alpha)
                yCoord = (pitch * i) * math.sin(theta) + (pitch * iside) * math.sin(alpha)
                coordinatesOfCellCenters[cellId] = [0., 0.]
                coordinatesOfCellCenters[cellId][0] = xCoord
                coordinatesOfCellCenters[cellId][1] = yCoord
                cellId += 1

        group = mc.DataArrayInt.New()
        group.alloc(1, 7)
        group.setIJ(0, 0, mc.NORM_POLYGON)
        inds = mc.DataArrayInt.New()
        inds.alloc(2, 1)
        inds.setIJ(0, 0, 0)
        inds.setIJ(1, 0, 7)
        medCells = []
        for cellId in range(numCells):
            data = mc.DataArrayDouble.New()
            data.alloc(6, 2)
            for ivertex in range(6):
                xCoord = coordinatesOfCellCenters[cellId][0] - radius * math.cos(-ivertex * math.pi / 3.)
                yCoord = coordinatesOfCellCenters[cellId][1] - radius * math.sin(-ivertex * math.pi / 3.)
                data.setIJ(ivertex, 0, xCoord)
                data.setIJ(ivertex, 1, yCoord)
                group.setIJ(0, ivertex + 1, ivertex)
            cellHexa = mc.MEDCouplingUMesh.New()
            cellHexa.setMeshDimension(2)
            cellHexa.setCoords(data)
            cellHexa.setConnectivity(group, inds)
            medCells.append(cellHexa)
        mesh = mc.MEDCouplingUMesh.MergeUMeshes(medCells)
        mesh.mergeNodes(1.E-8)
        mesh.setName("HexagonalMesh")

        field = mc.MEDCouplingFieldInt(mc.ON_CELLS)
        field.setMesh(mesh)
        array = mc.DataArrayInt32()
        field.setArray(array)
        field.setName("HexagonalGrid")

        super().__init__(field)

    def clone(self):
        """! see Grid.clone() """
        output = HexagonalGrid(self._numRings, self._pitch)
        output._correspondences[:] = self._correspondences[:]  # pylint: disable=protected-access
        return output

    def setCorrespondenceHexagonal(self, ringIndex, positionIndex, correspondence):
        """! Set one correspondence from the indexes of the cell in the hexagonal grid.

        @note Use c3po.multi1D.NO_CORRESPONDENCE as correspondence value in empty positions.

        @param ringIndex Index of the ring.
        @param positionIndex Index of the cell on the ring.
        @param correspondence value to associate with the cell.
        """
        numCells = 0
        for i in range(1, ringIndex):
            numCells += i
        cellId = 0 if ringIndex == 0 else numCells * 6 + positionIndex + 1
        self.setCorrespondence(cellId, correspondence)


class MultiLevelGrid(Grid):
    """! MultiLevelGrid allows to define and handle grids inside other grids. """

    def __init__(self, rootGrid, leafGrids):
        """! Build a multi-level grid.

        @param rootGrid Root level Grid. Cannot be a MultiLevelGrid.
        @param leafGrids List of second level grids. There must be as many leaf grids than cells in the rootGrid. /
        Leaf grids can be MultiLevelGrid: in this case, all of them should be MultiLevelGrid, and those that are non-empty should all have the same number of levels.
        """
        if isinstance(rootGrid, MultiLevelGrid):
            raise ValueError("The root Grid cannot be a MultiLevelGrid.")
        if len(leafGrids) != rootGrid.getNumberOfCells():
            raise ValueError(f"There must be as many leaf Grids that there are cells in the root Grid. We found instead {len(leafGrids)} leaf grids and {rootGrid.getNumberOfCells()} cells in the root Grid.")
        self._rootGrid = rootGrid
        self._leafGrids = leafGrids
        self._numLevels = 0
        if len(leafGrids) > 0:
            multiLevel = isinstance(leafGrids[0], MultiLevelGrid)
            for leaf in leafGrids:
                if isinstance(leaf, MultiLevelGrid) != multiLevel:
                    raise ValueError("All leaf grids must be MultiLevelGrid, or none of them can be.")
            if multiLevel:
                self._numLevels = leafGrids[0].getNumLevels() + 1
            else:
                self._numLevels = 1
            if multiLevel:
                for leaf in leafGrids:
                    if self._numLevels != leaf.getNumLevels() + 1:
                        if self._numLevels == 1:
                            self._numLevels = leaf.getNumLevels() + 1
                        elif leaf.getNumLevels() + 1 > 1:
                            raise ValueError(f"In case leaf grids are non-empty MultiLevelGrid, they must all have the same number of levels (we found {self._numLevels - 1} and {leaf.getNumLevels()}).")
        self._currentLevel = self._numLevels

    def clone(self):
        """! see Grid.clone() """
        return MultiLevelGrid(self._rootGrid.clone(), [leaf.clone() for leaf in self._leafGrids])

    def getNumLevels(self):
        """! Return the number of level.

        @details level = 0 if empty (rootGrid with no cells), 1 if leaf grids are not themselves MultiLevelGrid, and n + 1 with n the level of leaf grids otherwise.

        @return Number of level.
        """
        return self._numLevels

    def setCurrentLevel(self, level):
        """! Set the current level.

        @details all methods inherited from Grid will address this level. At level 0, the MultiLevelGrid behaves like the rootGrid. /
        At level n > 0, it behaves like the juxtaposition of leaf grids with current level n - 1. Defaut : the value returned be getNumLevels().

        @param level New current level.
        """
        if level > self._numLevels and len(self._leafGrids) > 0:
            raise ValueError(f"The required level ({level}) is higher than maximal one ({self._numLevels}).")
        self._currentLevel = level
        if self._numLevels > 0 and level > 0:
            if isinstance(self._leafGrids[0], MultiLevelGrid):
                for leaf in self._leafGrids:
                    leaf.setCurrentLevel(level - 1)

    def getCurrentLevel(self):
        """! Return the current level (see setCurrentLevel()).

        @return The current level.
        """
        return self._currentLevel

    def _shiftIndex(self, cellId):
        """! Return the leaf grid index and cell index (in this leaf grid) associated with a provided global cell index (for current level). """
        leafId = 0
        if cellId < 0 or cellId >= self.getNumberOfCells():
            raise ValueError(f"The required cellId, {cellId}, is invalid. It should be >= 0 and < {self.getNumberOfCells()}.")
        leafNumCell = self._leafGrids[leafId].getNumberOfCells()
        while cellId >= leafNumCell:
            leafId += 1
            cellId -= leafNumCell
            leafNumCell = self._leafGrids[leafId].getNumberOfCells()
        return leafId, cellId

    def getCorrespondence(self, cellId):
        """! See Grid.getCorrespondence() """
        if self._currentLevel == 0:
            return self._rootGrid.getCorrespondence(cellId)
        leafId, cellId = self._shiftIndex(cellId)
        return self._leafGrids[leafId].getCorrespondence(cellId)

    def getNumberOfCells(self):
        """! See Grid.getNumberOfCells() """
        if self._currentLevel == 0:
            return self._rootGrid.getNumberOfCells()
        numCells = 0
        for leaf in self._leafGrids:
            numCells += leaf.getNumberOfCells()
        return numCells

    def setCorrespondences(self, correspondences):
        """! See Grid.setCorrespondences() """
        if len(correspondences) != self.getNumberOfCells():
            raise ValueError(f"The size of the provided table ({len(correspondences)}) is not equal to the number of cells ({self.getNumberOfCells()})")
        if self._currentLevel == 0:
            self._rootGrid.setCorrespondences(correspondences)
        else:
            shift = 0
            for leaf in self._leafGrids:
                leaf.setCorrespondences(correspondences[shift:shift + leaf.getNumberOfCells()])
                shift += leaf.getNumberOfCells()

    def setCorrespondence(self, cellId, correspondence):
        """! See Grid.setCorrespondence() """
        if self._currentLevel == 0:
            self._rootGrid.setCorrespondence(cellId, correspondence)
        else:
            leafId, cellId = self._shiftIndex(cellId)
            self._leafGrids[leafId].setCorrespondence(cellId, correspondence)

    def getNodeCoordinates(self, cellId):
        """! See Grid.getNodeCoordinates() """
        if self._currentLevel == 0:
            return self._rootGrid.getNodeCoordinates(cellId)
        leafId, cellId = self._shiftIndex(cellId)
        rootCoordinates = self._rootGrid.getNodeCoordinates(leafId)
        xBary = 0
        yBary = 0
        numNodes = 0
        for ipoint in range(0, len(rootCoordinates), 2):
            xBary += rootCoordinates[ipoint]
            yBary += rootCoordinates[ipoint + 1]
            numNodes += 1
        xBary /= numNodes
        yBary /= numNodes
        leafCoordinates = self._leafGrids[leafId].getNodeCoordinates(cellId)
        for ipoint in range(0, len(leafCoordinates), 2):
            leafCoordinates[ipoint] += xBary
            leafCoordinates[ipoint + 1] += yBary
        return leafCoordinates

    def shift(self, xShift, yShift):
        """! See Grid.shift() """
        self._rootGrid.shift(xShift, yShift)

    def getMEDMesh(self):
        medCells = []
        for iCell in range(self.getNumberOfCells()):
            coordinates = self.getNodeCoordinates(iCell)
            numPoints = len(coordinates) // 2
            group = mc.DataArrayInt.New()
            group.alloc(1, numPoints + 1)
            group.setIJ(0, 0, mc.NORM_POLYGON)
            inds = mc.DataArrayInt.New()
            inds.alloc(2, 1)
            inds.setIJ(0, 0, 0)
            inds.setIJ(1, 0, numPoints + 1)
            data = mc.DataArrayDouble.New()
            data.alloc(numPoints, 2)
            for ivertex in range(numPoints):
                data.setIJ(ivertex, 0, coordinates[ivertex * 2])
                data.setIJ(ivertex, 1, coordinates[ivertex * 2 + 1])
                group.setIJ(0, ivertex + 1, ivertex)
            cell = mc.MEDCouplingUMesh.New()
            cell.setMeshDimension(2)
            cell.setCoords(data)
            cell.setConnectivity(group, inds)
            medCells.append(cell)
        mesh = mc.MEDCouplingUMesh.MergeUMeshes(medCells)
        mesh.mergeNodes(1.E-8)
        mesh.setName(f"level{self.getCurrentLevel()}Mesh")
        return mesh