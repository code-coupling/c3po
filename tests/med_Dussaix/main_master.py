# -*- coding: utf-8 -*-
from __future__ import print_function, division

import pytest

def main_master():
    import mpi4py.MPI as mpi

    import c3po
    import c3po.mpi


    class OneIterationCoupler(c3po.Coupler):
        def __init__(self, physics, exchangers, dataManagers=[]):
            c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

        def solveTimeStep(self):
            self._physicsDrivers[0].solve()
            self._exchangers[0].exchange()
            self._physicsDrivers[1].solve()
            return self.getSolveStatus()


    comm = mpi.COMM_WORLD

    ThermoProcess = c3po.mpi.MPIRemoteProcess(comm, 1)
    NeutroProcess = c3po.mpi.MPIRemoteProcess(comm, 2)

    myThermoDriver = c3po.mpi.MPIMasterPhysicsDriver(ThermoProcess)
    myThermoDriver.init()
    myThermoDriver.setInputDoubleValue("Vv_Vl", 10.)

    myNeutroDriver = c3po.mpi.MPIMasterPhysicsDriver(NeutroProcess)
    myNeutroDriver.init()
    myNeutroDriver.setInputDoubleValue("meanT", 1000.)

    dataResu = c3po.LocalDataManager()

    DataCoupler = c3po.mpi.MPIMasterDataManager(myThermoDriver, 0)
    ExchangerNeutro2Thermo = c3po.mpi.MPIMasterExchanger([ThermoProcess, NeutroProcess], 0)
    ExchangerThermo2Data = c3po.mpi.MPIMasterExchanger([ThermoProcess, NeutroProcess], 1)
    ExchangerData2Neutro = c3po.mpi.MPIMasterExchanger([ThermoProcess, NeutroProcess], 2)
    ExchangerNeutro2MasterLocal = c3po.mpi.MPIExchanger(c3po.DirectMatching(), [(NeutroProcess, "Temperatures")], [(dataResu, "Temperatures")])
    ExchangerNeutro2Master = c3po.mpi.MPIMasterExchanger([NeutroProcess], 3, ExchangerNeutro2MasterLocal)
    ExchangerThermo2MasterLocal = c3po.mpi.MPIExchanger(c3po.DirectMatching(), [(ThermoProcess, "Densities")], [(dataResu, "Densities")])
    ExchangerThermo2Master = c3po.mpi.MPIMasterExchanger([ThermoProcess], 3, ExchangerThermo2MasterLocal)

    OneIteration = OneIterationCoupler([myNeutroDriver, myThermoDriver], [ExchangerNeutro2Thermo])

    mycoupler = c3po.FixedPointCoupler([OneIteration], [ExchangerThermo2Data, ExchangerData2Neutro], [DataCoupler])
    mycoupler.init()
    mycoupler.setDampingFactor(0.125)
    mycoupler.setConvergenceParameters(1E-5, 100)

    mycoupler.solve()
    ExchangerNeutro2Master.exchange()
    ExchangerThermo2Master.exchange()
    FieldT = dataResu.getOutputMEDDoubleField("Temperatures")
    ArrayT = FieldT.getArray()
    FieldRho = dataResu.getOutputMEDDoubleField("Densities")
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

main_master()