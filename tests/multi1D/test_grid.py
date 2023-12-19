# -*- coding: utf-8 -*-
from __future__ import print_function, division

import pytest

import c3po.multi1D

def test_grid():

    def checkGridIndex(grid, index, resu):
        refCoord, refCorr = resu
        coord = grid.getNodeCoordinates(index)
        assert len(coord) == len(refCoord)
        for val, ref in zip(coord, refCoord):
            assert pytest.approx(val, abs=1.E-10) == ref
        assert grid.getCorrespondence(index) == refCorr

    #Test CartesianGrid
    cart1 = c3po.multi1D.CartesianGrid([1.]*5, [0.1, 0.5, 2., 4.])
    cart1.setCorrespondences(range(cart1.getNumberOfCells()))
    cart2 = cart1.clone()
    cart2.setCorrespondence(1, 5)
    cart2.setCorrespondence(10, -1)
    cart2.setCorrespondenceCartesian(1, 2, -1) #should be position 11
    cart2.setCorrespondence(16, 50)
    cart2.shift(2., 4.)
    checkGridIndex(cart1, 0, ([-1.5, -3.3, -2.5, -3.3, -2.5, -3.2, -1.5, -3.2], 0))
    checkGridIndex(cart1, 1, ([-0.5, -3.3, -1.5, -3.3, -1.5, -3.2, -0.5, -3.2], 1))
    checkGridIndex(cart1, 2, ([0.5, -3.3, -0.5, -3.3, -0.5, -3.2, 0.5, -3.2], 2))
    checkGridIndex(cart1, 10, ([-1.5, -2.7, -2.5, -2.7, -2.5, -0.7, -1.5, -0.7], 10))
    checkGridIndex(cart1, 11, ([-0.5, -2.7, -1.5, -2.7, -1.5, -0.7, -0.5, -0.7], 11))
    checkGridIndex(cart1, 16, ([-0.5, -0.7, -1.5, -0.7, -1.5, 3.3, -0.5, 3.3], 16))
    checkGridIndex(cart2, 0, ([-1.5 + 2., -3.3 + 4, -2.5 + 2., -3.3 + 4, -2.5 + 2., -3.2 + 4, -1.5 + 2., -3.2 + 4], 0))
    checkGridIndex(cart2, 1, ([-0.5 + 2., -3.3 + 4, -1.5 + 2., -3.3 + 4, -1.5 + 2., -3.2 + 4, -0.5 + 2., -3.2 + 4], 5))
    checkGridIndex(cart2, 2, ([0.5 + 2., -3.3 + 4, -0.5 + 2., -3.3 + 4, -0.5 + 2., -3.2 + 4, 0.5 + 2., -3.2 + 4], 2))
    checkGridIndex(cart2, 10, ([-1.5 + 2., -2.7 + 4, -2.5 + 2., -2.7 + 4, -2.5 + 2., -0.7 + 4, -1.5 + 2., -0.7 + 4], -1))
    checkGridIndex(cart2, 11, ([-0.5 + 2., -2.7 + 4, -1.5 + 2., -2.7 + 4, -1.5 + 2., -0.7 + 4, -0.5 + 2., -0.7 + 4], -1))
    checkGridIndex(cart2, 16, ([-0.5 + 2., -0.7 + 4, -1.5 + 2., -0.7 + 4, -1.5 + 2., 3.3 + 4, -0.5 + 2., 3.3 + 4], 50))
    fieldCart1 = cart1.toMED()
    fieldCart2 = cart2.toMED()
    #mc.WriteField("fieldCart1.med", fieldCart1, True)
    #mc.WriteField("fieldCart2.med", fieldCart2, True)

    #Test HexagonalGrid
    hexa1 = c3po.multi1D.HexagonalGrid(3, 1.)
    hexa1.setCorrespondences(range(hexa1.getNumberOfCells()))
    hexa2 = hexa1.clone()
    hexa2.setCorrespondence(1, 5)
    hexa2.setCorrespondence(10, -1)
    hexa2.setCorrespondenceHexagonal(2, 5, -1) #should be position 11
    hexa2.setCorrespondence(11, -1)
    hexa2.setCorrespondence(16, 50)
    hexa2.shift(2., 4.)
    checkGridIndex(hexa1, 1, ([0.28867513459481176, -0.5, 0.5773502691896257, 0., 1.1547005383792515, 0., 1.4433756729740645, -0.5, 1.1547005383792497, -1., 0.577350269189624, -1.], 1))
    checkGridIndex(hexa1, 10, ([0.2886751345948133, 1.5, 0.5773502691896261, 2., 1.1547005383792524, 2., 1.4433756729740645, 1.5, 1.1547005383792521, 1., 0.577350269189626, 1.], 10))
    checkGridIndex(hexa1, 11, ([-0.5773502691896254, 2., -0.28867513459481275, 2.5, 0.28867513459481337, 2.5, 0.5773502691896261, 2., 0.2886751345948133, 1.5, -0.28867513459481287, 1.5], 11))
    checkGridIndex(hexa1, 16, ([-1.4433756729740652, -1.5, -1.1547005383792524, -1.0, -0.5773502691896264, -1., -0.28867513459481514, -1.5, -0.5773502691896268, -2.0, -1.1547005383792528, -2.0], 16))
    checkGridIndex(hexa2, 1, ([0.28867513459481176 + 2, -0.5 + 4, 0.5773502691896257 + 2, 0. + 4, 1.1547005383792515 + 2, 0. + 4, 1.4433756729740645 + 2, -0.5 + 4, 1.1547005383792497 + 2, -1. + 4, 0.577350269189624 + 2, -1. + 4], 5))
    checkGridIndex(hexa2, 10, ([0.2886751345948133 + 2, 1.5 + 4, 0.5773502691896261 + 2, 2. + 4, 1.1547005383792524 + 2, 2. + 4, 1.4433756729740645 + 2, 1.5 + 4, 1.1547005383792521 + 2, 1. + 4, 0.577350269189626 + 2, 1. + 4], -1))
    checkGridIndex(hexa2, 11, ([-0.5773502691896254 + 2, 2. + 4, -0.28867513459481275 + 2, 2.5 + 4, 0.28867513459481337 + 2, 2.5 + 4, 0.5773502691896261 + 2, 2. + 4, 0.2886751345948133 + 2, 1.5 + 4, -0.28867513459481287 + 2, 1.5 + 4], -1))
    checkGridIndex(hexa2, 16, ([-1.4433756729740652 + 2, -1.5 + 4, -1.1547005383792524 + 2, -1.0 + 4, -0.5773502691896264 + 2, -1. + 4, -0.28867513459481514 + 2, -1.5 + 4, -0.5773502691896268 + 2, -2.0 + 4, -1.1547005383792528 + 2, -2.0 + 4], 50))
    fieldHexa1 = hexa1.toMED()
    fieldHexa2 = hexa2.toMED()
    #mc.WriteField("fieldHexa1.med", fieldHexa1, True)
    #mc.WriteField("fieldHexa2.med", fieldHexa2, True)

    #Test MEDGrid
    med1 = c3po.multi1D.MEDGrid(fieldHexa1)
    med1.setCorrespondence(32, 0)
    med1.shift(3., 6.)
    med2 = med1.clone()
    med2.shift(1., 2.)
    med2.setCorrespondence(35, 4)
    med2.setCorrespondence(33, -1)
    checkGridIndex(med1, 1, ([0.28867513459481176 + 3., -0.5 + 6., 0.5773502691896257 + 3., 0. + 6., 1.1547005383792515 + 3., 0. + 6., 1.4433756729740645 + 3., -0.5 + 6., 1.1547005383792497 + 3., -1. + 6., 0.577350269189624 + 3., -1. + 6.], 1))
    checkGridIndex(med1, 32, ([0.6905989232414962, 4.0, 0.9792740578363088, 4.5, 1.5566243270259348, 4.5, 1.8452994616207472, 4.0, 1.5566243270259346, 3.5, 0.9792740578363088, 3.5], 0))
    checkGridIndex(med2, 1, ([0.28867513459481176 + 3. + 1., -0.5 + 6. + 2., 0.5773502691896257 + 3. + 1., 0. + 6. + 2., 1.1547005383792515 + 3. + 1., 0. + 6. + 2., 1.4433756729740645 + 3. + 1., -0.5 + 6. + 2., 1.1547005383792497 + 3. + 1., -1. + 6. + 2., 0.577350269189624 + 3. + 1., -1. + 6. + 2.], 1))
    checkGridIndex(med2, 32, ([0.6905989232414962 + 1., 4.0 + 2., 0.9792740578363088 + 1., 4.5 + 2., 1.5566243270259348 + 1., 4.5 + 2., 1.8452994616207472 + 1., 4.0 + 2., 1.5566243270259346 + 1., 3.5 + 2., 0.9792740578363088 + 1., 3.5 + 2.], 0))
    checkGridIndex(med2, 33, ([2.5566243270259346, 5.5, 2.845299461620747, 6.0, 3.422649730810373, 6.0, 3.711324865405184, 5.5, 3.422649730810371, 5.0, 2.845299461620747, 5.0], -1))
    checkGridIndex(med2, 35, ([4.2886751345948095, 5.5, 4.577350269189623, 6., 5.154700538379249, 6., 5.443375672974062, 5.5, 5.154700538379249, 5., 4.577350269189623, 5.], 4))
    fieldmed1 = med1.toMED()
    fieldmed2 = med2.toMED()
    #mc.WriteField("fieldmed1.med", fieldmed1, True)
    #mc.WriteField("fieldmed2.med", fieldmed2, True)

    #Test MultiLevelGrid
    toutepetitGrid = c3po.multi1D.HexagonalGrid(1, 0.3)
    emptyGrid = c3po.multi1D.CartesianGrid([], [])
    fuelGrid = c3po.multi1D.CartesianGrid([1.]*5, [1.]*5)
    fuelHexaGrid = c3po.multi1D.MultiLevelGrid(fuelGrid, [toutepetitGrid.clone() for _ in range(12)] + [emptyGrid.clone()] + [toutepetitGrid.clone() for _ in range(12)])
    assemblyGrid = c3po.multi1D.CartesianGrid([5.5]*2, [5.5]*2)
    coreGrid = c3po.multi1D.CartesianGrid([11.5]*4, [11.5]*4)
    hexaassembly = c3po.multi1D.MultiLevelGrid(assemblyGrid, [fuelHexaGrid.clone() for _ in range(4)])
    emptyAssembly = c3po.multi1D.MultiLevelGrid(emptyGrid, [])
    core = c3po.multi1D.MultiLevelGrid(coreGrid, [emptyAssembly.clone(), hexaassembly.clone(), hexaassembly.clone(), emptyAssembly.clone()] + [hexaassembly.clone() for _ in range(8)] + [emptyAssembly.clone(), hexaassembly.clone(), hexaassembly.clone(), emptyAssembly.clone()])
    core.shift(1., 2.)
    ref = []
    ref.append(([0.0 + 1., -23.0 + 2., -11.5 + 1., -23.0 + 2., -11.5 + 1., -11.5 + 2., 0.0 + 1., -11.5 + 2.], 50))
    ref.append(([-0.25 + 1., -22.75 + 2., -5.75 + 1., -22.75 + 2., -5.75 + 1., -17.25 + 2., -0.25 + 1., -17.25 + 2.], 50))
    ref.append(([-9.0 + 1., -22.5 + 2., -10.0 + 1., -22.5 + 2., -10.0 + 1., -21.5 + 2., -9.0 + 1., -21.5 + 2.], 50))
    ref.append(([-10.413397459621557 + 1., -22.15 + 2., -10.326794919243113 + 1., -22.0 + 2., -10.153589838486225 + 1., -22.0 + 2., -10.06698729810778 + 1., -22.15 + 2., -10.153589838486225 + 1., -22.3 + 2., -10.326794919243113 + 1., -22.3 + 2.], 50))
    refNumCells = [16, 48, 1200, 8064]
    for level in range(4):
        core.setCurrentLevel(level)
        core.setCorrespondences(list(range(core.getNumberOfCells())))
        core.setCorrespondence(1, 50)
        assert core.getNumberOfCells() == refNumCells[level]
        checkGridIndex(core, 1, ref[level])
    medfield = []
    for level in range(4):
        core.setCurrentLevel(level)
        medfield.append(core.toMED())
    #mc.WriteField("level0.med", medfield[0], True)
    #mc.WriteField("level1.med", medfield[1], True)
    #mc.WriteField("level2.med", medfield[2], True)
    #mc.WriteField("level3.med", medfield[3], True)

if __name__ == "__main__":
    test_grid()
