# -*- coding: utf-8 -*-
from __future__ import print_function, division

import pytest

import c3po.medcouplingCompat as mc

import c3po.multi1D

def test_interface ():

    class DummyChannels(c3po.multi1D.Multi1DAPI):
        def __init__(self, numChannels):
            self._numChannels = numChannels
            self._valuesSet = {}

        def getSize(self):
            return self._numChannels

        def getNumberOfCells(self, index):
            return index

        def getCellSizes(self, index):
            return [1.] * index

        def getNature(self, fieldName):
            return mc.IntensiveMaximum

        def getValues(self, index, fieldName):
            if fieldName in self._valuesSet:
                return self._valuesSet[fieldName][index]
            return [i + index * 100. for i in range(index)]

        def setValues(self, index, fieldName, values):
            if fieldName not in self._valuesSet:
                self._valuesSet[fieldName] = {}
            self._valuesSet[fieldName][index] = values


    class DummyChannelObjects(DummyChannels, c3po.multi1D.Multi1DWithObjectsAPI):
        def __init__(self, numChannels):
            super().__init__(numChannels)
            self._valuesObjectSet = {}

        def getObjectNames(self, index):
            return [["OBJECT_0", "OBJECT_1", "OBJECT_2", "OBJECT_3"] for _ in range(index)]

        def getObjectNamesInField(self, fieldName):
            if fieldName == "temperatureObject" or fieldName == "TObject":
                return ["OBJECT_0", "OBJECT_1", "OBJECT_3"]
            else:
                return []

        def getObjectValues(self, index, fieldName):
            if fieldName in self._valuesObjectSet:
                return self._valuesObjectSet[fieldName][index]
            return [[j + index * 100. + i * 10. for j in range(index)] for i in [0, 1, 3]]

        def setObjectValues(self, index, fieldName, values):
            if fieldName not in self._valuesObjectSet:
                self._valuesObjectSet[fieldName] = {}
            self._valuesObjectSet[fieldName][index] = values


    gridChannel = c3po.multi1D.CartesianGrid([1.]*5, [1.]*5)
    gridChannel.setCorrespondences(list(range(25)))

    gridObject = c3po.multi1D.CartesianGrid([0.5]*2, [0.5]*2)
    gridObject.setCorrespondences(list(range(4)))
    channelObjects = DummyChannelObjects(25)

    interface1 = c3po.multi1D.MEDInterface(channelObjects, gridChannel)
    interface2 = c3po.multi1D.MEDInterface(channelObjects, gridChannel, [[gridObject for _ in range(i)] for i in range(25)])

    fieldChannel = interface1.getField("temperatureChannel")
    fieldObject1 = interface1.getField("temperatureObject")
    fieldObject2 = interface2.getField("temperatureObject")

    #Verif
    array = fieldChannel.getArray()
    count = 0
    for iChannel in range(25):
        for iCell in range(iChannel):
            assert pytest.approx(array[count], abs=1.E-10) == iCell + iChannel * 100.
            count += 1
    array = fieldObject1.getArray()[0]
    assert pytest.approx(array.getIJ(0, 0), abs=1.E-10) == 100.
    assert pytest.approx(array.getIJ(0, 1), abs=1.E-10) == 110.
    assert pytest.approx(array.getIJ(0, 2), abs=1.E-10) == 130.
    array = fieldObject1.getArray()[4]
    assert pytest.approx(array.getIJ(0, 0), abs=1.E-10) == 301.
    assert pytest.approx(array.getIJ(0, 1), abs=1.E-10) == 311.
    assert pytest.approx(array.getIJ(0, 2), abs=1.E-10) == 331.
    array = fieldObject2.getArray()
    count = 0
    for iChannel in range(25):
        for iCell in range(iChannel):
            for iObject in range(4):
                if iObject == 2:
                    assert array[count] == -1.
                else:
                    assert pytest.approx(array[count], abs=1.E-10) == iCell + iChannel * 100. + iObject * 10.
                count += 1

    interface1.setField("TChannel", fieldChannel * 10)
    interface1.setField("TObject", fieldObject1 * 10)
    interface2.setField("TObject", fieldObject2 * 10)

    checkChannel = interface1.getField("TChannel")
    checkObject1 = interface1.getField("TObject")
    checkObject2 = interface2.getField("TObject")

    #Verif
    array = checkChannel.getArray()
    count = 0
    for iChannel in range(25):
        for iCell in range(iChannel):
            assert pytest.approx(array[count], abs=1.E-10) == (iCell + iChannel * 100.) * 10.
            count += 1
    array = checkObject1.getArray()[0]
    assert pytest.approx(array.getIJ(0, 0), abs=1.E-10) == 1000.
    assert pytest.approx(array.getIJ(0, 1), abs=1.E-10) == 1100.
    assert pytest.approx(array.getIJ(0, 2), abs=1.E-10) == 1300.
    array = checkObject1.getArray()[4]
    assert pytest.approx(array.getIJ(0, 0), abs=1.E-10) == 3010.
    assert pytest.approx(array.getIJ(0, 1), abs=1.E-10) == 3110.
    assert pytest.approx(array.getIJ(0, 2), abs=1.E-10) == 3310.
    array = checkObject2.getArray()
    count = 0
    for iChannel in range(25):
        for iCell in range(iChannel):
            for iObject in range(4):
                if iObject == 2:
                    assert array[count] == -1.
                else:
                    assert pytest.approx(array[count], abs=1.E-10) == (iCell + iChannel * 100. + iObject * 10.) * 10.
                count += 1

    #mc.WriteField("checkChannel.med", checkChannel, True)
    #mc.WriteField("checkObject1.med", checkObject1, True)
    #mc.WriteField("checkObject2.med", checkObject2, True)

    ChannelMEDMesh = interface2.getBaseMEDMesh()
    assert ChannelMEDMesh.getNumberOfCells() == 300
    ObjectMEDMesh = interface2.getObjectMEDMesh()
    assert ObjectMEDMesh.getNumberOfCells() == 1200
    Object12MEDMesh = interface2.getPartOfObjectMEDMesh(["OBJECT_1", "OBJECT_2"])
    assert Object12MEDMesh.getNumberOfCells() == 600

    #mc.WriteMesh("interfaceChannels.med", interface2.getBaseMEDMesh(), True)
    #mc.WriteMesh("interfaceObjects.med", interface2.getObjectMEDMesh(), True)
    #mc.WriteMesh("interfaceObjects_OBJECT_1_2.med", interface2.getPartOfObjectMEDMesh(["OBJECT_1", "OBJECT_2"]), True)


if __name__ == "__main__":
    test_interface()
