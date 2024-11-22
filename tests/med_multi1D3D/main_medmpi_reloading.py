# -*- coding: utf-8 -*-
from __future__ import print_function, division
import math
import pytest
from mpi4py import MPI as mpi

import c3po.medcouplingCompat as mc

import c3po
import c3po.multi1D
import c3po.mpi
import c3po.multi1D.mpi

from tests.med_1D3D.NeutroDriver import NeutroDriver
from tests.med_1D3D.ThermoDriver import ThermoDriver

refBuEnd = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 2.064129366763822, 2.064129366763822, 0.6879904187922314, 0.6879904187922314, 2.064129366763822, 2.0641293667638223,
            0.6879904187922316, 0.6879904187922314, 1.3760335412091462, 1.3760335412091462, 2.7521468266803595, 2.752146826680359, 1.3760335412091462,
            1.376033541209146, 2.7521468266803595, 2.7521468266803595, 2.38585879490339, 2.38585879490339, 0.7952358025270865, 0.7952358025270866,
            2.3858587949033905, 2.3858587949033905, 0.7952358025270865, 0.7952358025270865, 1.590522070004066, 1.5905220700040659, 3.1811010724757245,
            3.1811010724757245, 1.5905220700040659, 1.590522070004066, 3.1811010724757245, 3.181101072475725, 2.5758247325320576, 2.575824732532057,
            0.8585306530409631, 0.8585306530409631, 2.575824732532057, 2.575824732532057, 0.8585306530409631, 0.8585306530409631, 1.7171389000146409,
            1.7171389000146409, 3.4343718149609197, 3.4343718149609197, 1.7171389000146409, 1.7171389000146409, 3.43437181496092, 3.4343718149609197,
            2.575720639245638, 2.5757206392456387, 0.858496190140823, 0.8584961901408231, 2.575720639245638, 2.575720639245638, 0.858496190140823,
            0.858496190140823, 1.717069739338362, 1.717069739338362, 3.4342331972527704, 3.4342331972527704, 1.7170697393383625, 1.717069739338362,
            3.4342331972527695, 3.4342331972527704, 2.3862161561979165, 2.386216156197916, 0.7953548021691755, 0.7953548021691756, 2.386216156197916,
            2.386216156197916, 0.7953548021691758, 0.7953548021691754, 1.5907601900782256, 1.590760190078226, 3.181577487796652, 3.181577487796652,
            1.5907601900782258, 1.5907601900782256, 3.1815774877966523, 3.181577487796652, 2.0627679696599195, 2.062767969659919, 0.6875364381429541,
            0.6875364381429541, 2.062767969659919, 2.062767969659919, 0.6875364381429541, 0.6875364381429541, 1.3751257615280938, 1.375125761528094,
            2.7503315776003414, 2.750331577600341, 1.375125761528094, 1.375125761528094, 2.750331577600341, 2.750331577600341, 2.0080609311280084,
            2.0080609311280084, 0.669299429112106, 0.669299429112106, 2.0080609311280084, 2.0080609311280084, 0.669299429112106, 0.669299429112106,
            1.3386530725571695, 1.3386530725571695, 2.677391719989136, 2.677391719989136, 1.3386530725571695, 1.3386530725571695, 2.677391719989136,
            2.677391719989136, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


class OneIterationCoupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


def main_medmpi_reloading():
    world = mpi.COMM_WORLD
    rankWorld = world.Get_rank()
    commThermo = world.Split(color=mpi.UNDEFINED if rankWorld == 0 else 0, key=rankWorld)

    myNeutroDriver = c3po.mpi.MPIRemoteProcess(world, 0)
    myThermoDriver = c3po.mpi.MPIRemoteProcesses(world, [1, 2, 3, 4])
    thermoData = c3po.mpi.MPIRemoteProcesses(world, [1, 2, 3, 4])
    myThermoDrivers = []
    for i in range(4):
        myThermoDrivers.append(c3po.mpi.MPIRemoteProcess(world, i + 1))
    if rankWorld == 0:
        myNeutroDriver = NeutroDriver()
    else:
        iThermo = commThermo.Get_rank()
        myThermoDrivers[iThermo] = ThermoDriver()
        myThermoDrivers[iThermo].setT0(273.15)

        grid = c3po.multi1D.CartesianGrid([0.5] * 2, [0.5] * 2)
        grid.setCorrespondences(list(range(4)))

        myThermoDriver = c3po.multi1D.mpi.MPIMulti1DPhysicsDriver(myThermoDrivers, grid, mpiComm=commThermo)
        thermoData = c3po.mpi.MPIDomainDecompositionDataManager(commThermo)

    dataCoupler = c3po.mpi.MPICollaborativeDataManager([thermoData], world)

    myRemapper = c3po.mpi.MPIRemapper(meshAlignment=True, offset=[0., 0., -1.], rescaling=1. / 100., rotation=math.pi / 2., outsideCellsScreening=False)
    neutroToThermo = c3po.mpi.MPISharedRemapping(myRemapper, reverse=True)
    thermoToNeutro = c3po.mpi.MPISharedRemapping(myRemapper, reverse=False, defaultValue=0., linearTransform=(1., -273.15))

    exchangerNeutro2Thermo = c3po.mpi.MPIExchanger(neutroToThermo, [(myNeutroDriver, "Power")], [(myThermoDriver, "Power")])
    exchangerThermo2Data = c3po.mpi.MPIExchanger(c3po.DirectMatching(), [(myThermoDriver, "Temperature")], [(thermoData, "Temperature")])
    exchangerData2Neutro = c3po.mpi.MPIExchanger(thermoToNeutro, [(thermoData, "Temperature")], [(myNeutroDriver, "Temperature")], mpiComm=world)

    oneIteration = OneIterationCoupler([myNeutroDriver, myThermoDriver], [exchangerNeutro2Thermo])

    mycoupler = c3po.FixedPointCoupler([oneIteration], [exchangerThermo2Data, exchangerData2Neutro], [dataCoupler])
    mycoupler.init()
    mycoupler.setDampingFactor(0.75)
    mycoupler.setConvergenceParameters(1E-5, 100)

    thermoTodataBu = c3po.mpi.MPISharedRemapping(myRemapper, reverse=False)
    dataBu = c3po.mpi.MPIRemoteProcess(world, 0)
    if rankWorld == 0:
        dataBu = c3po.LocalDataManager()
        fieldBUTemplate = myNeutroDriver.getInputMEDDoubleFieldTemplate("Burn-up")
        dataBu.setInputMEDDoubleFieldTemplate("Burn-up", fieldBUTemplate)
    exchangerData2Bu = c3po.mpi.MPIExchanger(thermoTodataBu, [(myThermoDriver, "Burn-up")], [(dataBu, "Burn-up")], mpiComm=world)

    for icycle in range(4):
        mycoupler.initTimeStep(1.)
        mycoupler.solve()
        mycoupler.validateTimeStep()

        exchangerData2Bu.exchange()
        if rankWorld == 0 and icycle == 3:
            buField = dataBu.getOutputMEDDoubleField("Burn-up")
            resuBu = buField.getArray().toNumPyArray().tolist()
            assert len(refBuEnd) == len(resuBu)
            for i in range(len(refBuEnd)):
                assert pytest.approx(resuBu[i], abs=1.E-3) == refBuEnd[i]

        if rankWorld > 0:
            shiftMap = [3, "wherever", 1, 2]
            newThermo = myThermoDriver.shiftPhysicsDrivers(shiftMap)
            for thermo in newThermo:
                thermo.term()
                thermo.init()
        #Exchangers have to be cleaned because the 3D mesh of myThermoDriver is modified on each MPI process.
        exchangerNeutro2Thermo.clean()
        exchangerThermo2Data.clean()
        exchangerData2Neutro.clean()
        exchangerData2Bu.clean()

    mycoupler.term()
    myRemapper.terminate()

if __name__ == "__main__":
    main_medmpi_reloading()
