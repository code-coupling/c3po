# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the classes Multi1DPhysicsDriver and DriversAPI and the function shiftList. """
import c3po.medcouplingCompat as mc

from c3po.services.PhysicsDriverWrapper import PhysicsDriverWrapper
from c3po.CollaborativePhysicsDriver import CollaborativePhysicsDriver
from c3po.multi1D.Multi1DAPI import Multi1DAPI
from c3po.multi1D.MEDInterface import MEDInterface


class Multi1DPhysicsDriver(PhysicsDriverWrapper):
    """! Multi1DPhysicsDriver allows to handle as a unique PhysicsDriver that reads and writes 3D fields a list of 1D PhysicsDriver. """

    def __init__(self, physics, grid, weights=None):
        """! Build a Multi1DPhysicsDriver object.

        @param physics a list of 1D PhysicsDriver objects.
        @param grid a c3po.multi1D.Grid object that defines the 2D base of the 3D meshes used by Multi1DPhysicsDriver, and associates an element of physics to each cell of this 2D base.
        @param weights if provided, weights should be a list (of same length than physics) of floats.
            They are used as multiplication factors for extensive variables, thus allowing to choose the weigh of each PhysicsDriver in the 3D model.
            For exemple, a weigh of 10. means that the associated PhysicsDriver represents 10 identical PhysicsDriver.
        """
        super().__init__(CollaborativePhysicsDriver(physics))
        self._grid = grid
        self._weights = weights
        self._driverAPI = None
        self._medInterface = None
        self._testIndex = 0

    def _initMEDInterface(self, withTemplateField, fieldName):
        """! INTERNAL """
        if self._medInterface is None:
            meshes = []
            for physics in self.getPhysicsDrivers():
                field = physics.getInputMEDDoubleFieldTemplate(fieldName) if withTemplateField else physics.getOutputMEDDoubleField(fieldName)
                meshes.append(field.getMesh().getCoordsAt(0))
            self._driverAPI = DriversAPI(self.getPhysicsDrivers(), meshes, self._testIndex, self._weights)
            self._medInterface = MEDInterface(self._driverAPI, self._grid)

    def getPhysicsDrivers(self):
        """! Return the wrapped PhysicsDriver list.

        @return the wrapped PhysicsDriver list.
        """
        return self.getPhysicsDriver().getElements()

    def shiftPhysicsDrivers(self, shiftMap):
        """! Shift the hold PhysicsDriver according to shiftMap.

        @param shiftMap a list of integers of same length than physics. shiftMap[i] is the new position of physics[i].
            'out' can be used to indicate that this element is no more used. In this case, the associated PhysicsDriver is moved to one of the free positions.

        @return the list of PhysicsDriver that were associated to 'out' in the shiftMap.

        For example, shiftMap=[3, 'out', 1, 2] indicates that at first call physics_0 goes to position 3, physics_1 is discharged, physics_2 goes to 1 and physics_3 goes to 2. It returns [physics_1] (and physics_1 goes to position 0).
        At the second call with the same input, physics_0 (now at position 3) goes to 2, physics_1 (at 0) goes to 3, physics_2 (at 1) is discharged and physics_3 (at 2) goes to 1. It returns [physics_2].
        The thrid call returns [physics_3], the fourth call [physics_0], the fifth call [physics_1].
        """
        self._medInterface = None
        if self._weights is not None:
            _, self._weights = shiftList(self._weights, shiftMap)
        physicsList = self.getPhysicsDrivers()
        discharged, newList = shiftList(physicsList, shiftMap)
        physicsList[:] = newList[:]
        return discharged

    def getInputFieldsNames(self):
        """! See c3po.DataAccessor.DataAccessor.getInputFieldsNames(). """
        if len(self.getPhysicsDrivers()) > 0:
            return self.getPhysicsDrivers()[self._testIndex].getInputFieldsNames()
        return []

    def getOutputFieldsNames(self):
        """! See c3po.DataAccessor.DataAccessor.getOutputFieldsNames(). """
        if len(self.getPhysicsDrivers()) > 0:
            return self.getPhysicsDrivers()[self._testIndex].getOutputFieldsNames()
        return []

    def getFieldType(self, name):
        """! See c3po.DataAccessor.DataAccessor.getFieldType(). """
        if len(self.getPhysicsDrivers()) > 0:
            return self.getPhysicsDrivers()[self._testIndex].getFieldType(name)
        raise Exception("We have no PhysicsDriver, we cannot answer.")

    def getMeshUnit(self):
        """! See c3po.DataAccessor.DataAccessor.getMeshUnit(). """
        if len(self.getPhysicsDrivers()) > 0:
            return self.getPhysicsDrivers()[self._testIndex].getMeshUnit()
        raise Exception("We have no PhysicsDriver, we cannot answer.")

    def getFieldUnit(self, name):
        """! See c3po.DataAccessor.DataAccessor.getFieldUnit(). """
        if len(self.getPhysicsDrivers()) > 0:
            return self.getPhysicsDrivers()[self._testIndex].getFieldUnit(name)
        raise Exception("We have no PhysicsDriver, we cannot answer.")

    def getInputMEDDoubleFieldTemplate(self, name):
        """! See c3po.DataAccessor.DataAccessor.getInputMEDDoubleFieldTemplate(). """
        self._initMEDInterface(True, name)
        field = mc.MEDCouplingFieldDouble(mc.ON_CELLS, mc.ONE_TIME)
        mesh = self._medInterface.getBaseMEDMesh()
        field.setMesh(mesh.deepCopy())
        array = mc.DataArrayDouble(mesh.getNumberOfCells())
        array.fillWithZero()
        field.setArray(array)
        field.setName(name)
        nature = mc.NoNature
        if len(self.getPhysicsDrivers()) > 0:
            nature = self.getPhysicsDrivers()[self._testIndex].getInputMEDDoubleFieldTemplate(name).getNature()
        field.setNature(nature)
        return field

    def setInputMEDDoubleField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.setInputMEDDoubleField(). """
        self._initMEDInterface(True, name)
        self._medInterface.setField(name, field)

    def getOutputMEDDoubleField(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputMEDDoubleField(). """
        self._initMEDInterface(False, name)
        field = self._medInterface.getField(name)
        field.setMesh(field.getMesh().deepCopy())
        return field

    def updateOutputMEDDoubleField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.updateOutputMEDDoubleField(). """
        self._initMEDInterface(False, name)
        outputField = self._medInterface.getField(name)
        field.setArray(outputField.getArray())


class DriversAPI(Multi1DAPI):
    """! DriversAPI implements Multi1DAPI with 1D PhysicsDriver. """

    def __init__(self, physics, meshes, testIndex, weights=None):
        """! Build a DriversAPI object.

        @param physics a list of 1D PhysicsDriver objects.
        @param meshes a list (of same length than physics) of axial meshes. Each mesh is expected to be a list of z coordinates.
        @param testIndex index to be used when a required information is shared by all elements of physics (the value from physics[testIndex] is then used).
        @param weights if provided, weights should be a list (of same length than physics) of floats.
            They are used as multiplication factors for extensive variables, thus allowing to choose the weigh of each PhysicsDriver in the 3D model.
            For exemple, a weigh of 10. means that the associated PhysicsDriver represents 10 identical PhysicsDriver.
        """
        if len(physics) != len(meshes):
            raise Exception(f"We got {len(physics)} PhysicsDrivers and {len(meshes)} 1D meshes. We need to have a mesh for each PhysicsDriver.")
        self._physicsDrivers = physics
        self._testIndex = testIndex
        self._weights = weights
        self._numCells = []
        self._cellSizes = []
        for mesh in meshes:
            self._numCells.append(max(0, len(mesh) - 1))
            self._cellSizes.append([0.] * self._numCells[-1])
            for iCell in range(len(self._cellSizes[-1])):
                self._cellSizes[-1][iCell] = mesh[iCell + 1] - mesh[iCell]

    def getSize(self):
        """! See Multi1DAPI.getSize(). """
        return len(self._physicsDrivers)

    def getNumberOfCells(self, index):
        """! See Multi1DAPI.getNumberOfCells(). """
        return self._numCells[index]

    def getCellSizes(self, index):
        """! See Multi1DAPI.getCellSizes(). """
        return self._cellSizes[index]

    def getNature(self, fieldName):
        """! See Multi1DAPI.getNature(). """
        if self.getSize() < 1:
            raise Exception("We have no PhysicsDriver, we cannot answer.")
        field = self._physicsDrivers[self._testIndex].getOutputMEDDoubleField(fieldName)
        return field.getNature()

    def getValues(self, index, fieldName):
        """! See Multi1DAPI.getValues(). """
        field = self._physicsDrivers[index].getOutputMEDDoubleField(fieldName)
        array = field.getArray()
        if self._weights is not None and (field.getNature() == mc.ExtensiveMaximum or field.getNature() == mc.ExtensiveConservation):
            array *= self._weights[index]
        return array.getValues()

    def setValues(self, index, fieldName, values):
        """! See Multi1DAPI.setValues(). """
        field = self._physicsDrivers[index].getInputMEDDoubleFieldTemplate(fieldName)
        array = field.getArray()
        if array.getNbOfElems() != len(values):
            array = mc.DataArrayDouble(len(values), 1)
            field.setArray(array)
        array[:] = values
        if self._weights is not None and (field.getNature() == mc.ExtensiveMaximum or field.getNature() == mc.ExtensiveConservation):
            array /= self._weights[index]
        self._physicsDrivers[index].setInputMEDDoubleField(fieldName, field)


def shiftList(listToShift, shiftMap):
    """! Return a new list where elements of listToShift are shifted according to shiftMap.

    @note Users should not need to call this function directly.

    @param listToShift the list to shift.
    @param shiftMap a list of integers of same length than listToShift. shiftMap[i] is the new position of listToShift[i].
        'out' can be used to indicate that this element is no more used. In this case, the associated element is moved to one of the free positions.

    @return the list of listToShift elements that were associated to 'out' in the shiftMap and the new list with shifted elements.

    For example, shiftMap=[3, 'out', 1, 2] indicates that at first call listToShift[0] goes to position 3, listToShift[1] is discharged, listToShift[2] goes to 1 and listToShift[3] goes to 2. It returns ([listToShift[1]], newlist).
    At the second call with the same input, listToShift[0] (now at position 3) goes to 2, listToShift[1] (at 0) goes to 3, listToShift[2] (at 1) is discharged and listToShift[3] (at 2) goes to 1. Its first return is now [listToShift[2]].
    The thrid call first return is [listToShift[3]], the fourth call first return [listToShift[0]], the fifth call first return [listToShift[1]] etc.
    """
    if len(listToShift) != len(shiftMap):
        raise ValueError(f"The length of the shift map {len(shiftMap)} is not equal to the length of the list to shift {len(listToShift)}")
    newList = ["empty"] * len(listToShift)
    removedElems = []
    for i, toShift in enumerate(listToShift):
        if shiftMap[i] == "out":
            removedElems.append(toShift)
        else:
            if newList[shiftMap[i]] != "empty":
                raise ValueError("The shift map ({}) appears to contain the same value ({}) twice. It may be for example (size - 1) and -1, leading to the same index.".format(shiftMap, shiftMap[i]))
            newList[shiftMap[i]] = toShift
    count = 0
    for i, newElem in enumerate(newList):
        if newElem == "empty":
            newList[i] = removedElems[count]
            count += 1
    return removedElems, newList
