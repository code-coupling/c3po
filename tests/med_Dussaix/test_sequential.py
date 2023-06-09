# -*- coding: utf-8 -*-
from __future__ import print_function, division
import pytest

import c3po.medcouplingCompat as mc

import c3po


class OneIterationCoupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


def test_sequential():
    from tests.med_Dussaix.NeutroDriver import NeutroDriver
    from tests.med_Dussaix.ThermoDriver import ThermoDriver

    myThermoDriver = ThermoDriver()
    myThermoDriver.init()
    myThermoDriver.setInputDoubleValue("Vv_Vl", 10.)

    myNeutroDriver = NeutroDriver()
    myNeutroDriver.init()
    myNeutroDriver.setInputDoubleValue("meanT", 1000.)

    basicTransformer = c3po.Remapper()
    Thermo2DataTransformer = c3po.DirectMatching()
    Data2NeutroTransformer = c3po.SharedRemapping(basicTransformer, reverse=False)
    Neutro2ThermoTransformer = c3po.SharedRemapping(basicTransformer, reverse=True)

    DataCoupler = c3po.LocalDataManager()
    ExchangerNeutro2Thermo = c3po.LocalExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
    ExchangerThermo2Data = c3po.LocalExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(DataCoupler, "Densities")])
    ExchangerData2Neutro = c3po.LocalExchanger(Data2NeutroTransformer, [(DataCoupler, "Densities")], [(myNeutroDriver, "Densities")])

    OneIteration = OneIterationCoupler([myNeutroDriver, myThermoDriver], [ExchangerNeutro2Thermo])

    mycoupler = c3po.FixedPointCoupler([OneIteration], [ExchangerThermo2Data, ExchangerData2Neutro], [DataCoupler])
    mycoupler.init()
    mycoupler.setDampingFactor(0.125)
    mycoupler.setConvergenceParameters(1E-5, 100)

    mycoupler.solve()
    FieldT = myNeutroDriver.getOutputMEDDoubleField("Temperatures")
    ArrayT = FieldT.getArray()
    FieldRho = myThermoDriver.getOutputMEDDoubleField("Densities")
    ArrayRho = FieldRho.getArray()

    print("Convergence :", mycoupler.getSolveStatus())
    print("Temperatures :", ArrayT.getIJ(0, 0), ArrayT.getIJ(1, 0))
    print("Densities :", ArrayRho.getIJ(0, 0), ArrayRho.getIJ(1, 0))

    assert pytest.approx(ArrayT.getIJ(0, 0), abs=1.E-3) == 1032.46971894
    assert pytest.approx(ArrayT.getIJ(1, 0), abs=1.E-3) == 967.530281064
    assert pytest.approx(ArrayRho.getIJ(0, 0), abs=1.E-3) == 822.372079129
    assert pytest.approx(ArrayRho.getIJ(1, 0), abs=1.E-3) == 700.711939405

    mycoupler.term()
    myNeutroDriver.term()
    myThermoDriver.term()


if __name__ == "__main__":
    test_sequential()
