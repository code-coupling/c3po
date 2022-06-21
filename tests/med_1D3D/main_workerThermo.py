# -*- coding: utf-8 -*-
from __future__ import print_function, division
import mpi4py.MPI as mpi
import os, math

import c3po
import c3po.mpi

from tests.med_1D3D.ThermoDriver import ThermoDriver

def main_workerThermo():
    world = mpi.COMM_WORLD
    rankWorld = world.Get_rank()
    commMasters = world.Split(color=mpi.UNDEFINED, key=rankWorld)
    commThermo = world.Split(color=0, key=rankWorld)
    rankThermo = commThermo.Get_rank()

    tracedThermo = c3po.tracer(saveInputMED=True, saveOutputMED=True)(ThermoDriver)

    masterProcess = c3po.mpi.MPIRemoteProcess(commThermo, 0)
    myNeutroDriver = c3po.mpi.MPIRemoteProcess(world, 0)
    myThermoDrivers = []
    for i in range(4):
        myThermoDrivers.append(c3po.mpi.MPIRemoteProcess(world, i+1))
    myThermoDrivers[rankThermo] = tracedThermo()
    myThermoDrivers[rankThermo].setT0(273.15 + rankThermo*0.1)
    myThermoDriver = c3po.CollaborativePhysicsDriver(myThermoDrivers)

    cote_ass = 0.5
    cote = [-cote_ass, 0, cote_ass]
    indexTable = [0, 1,
                  2, 3]
    myRemapper = c3po.Multi1D3DRemapper(cote, cote, indexTable, [1] * len(myThermoDrivers), meshAlignment=True, offset=[0., 0., -1.], rescaling=1./100., rotation=math.pi/2., outsideCellsScreening=True)
    neutroToThermo = c3po.SharedRemappingMulti1D3D(myRemapper, reverse=True)
    thermoToNeutro = c3po.SharedRemappingMulti1D3D(myRemapper, reverse=False, defaultValue=273.15, linearTransform=(1., -273.15))

    dataThermos = []
    for i in range(4):
        dataThermos.append(c3po.mpi.MPIRemoteProcess(world, i+1))
    dataThermos[rankThermo] = c3po.LocalDataManager()
    dataThermo = c3po.CollaborativeDataManager(dataThermos)
    dataNeutro = c3po.mpi.MPIRemoteProcess(world, 0)
    dataCoupler = c3po.mpi.MPICollaborativeDataManager(dataThermos + [dataNeutro])

    exchangerNeutro2Thermo = c3po.mpi.MPIExchanger(neutroToThermo, [(myNeutroDriver, "Power")], [(myThermoDriver, "Power")])
    exchangerThermo2Data = c3po.mpi.MPIExchanger(c3po.DirectMatching(), [(myThermoDriver, "Temperature")], [(dataThermo, "Temperature")])
    exchangerData2Neutro = c3po.mpi.MPIExchanger(thermoToNeutro, [(dataThermo, "Temperature")], [(myNeutroDriver, "Temperature")])

    Worker = c3po.mpi.MPIWorker([myThermoDrivers[rankThermo]], [exchangerNeutro2Thermo, exchangerThermo2Data, exchangerData2Neutro], [dataCoupler], masterProcess, isCollective=True)

    Worker.listen()
