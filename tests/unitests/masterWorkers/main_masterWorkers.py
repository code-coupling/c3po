# -*- coding: utf-8 -*-
from __future__ import print_function

import pytest

def main_master_data(masterData):
    newData = masterData.clone()
    newData *= 2.
    refNorm2 = masterData.norm2()
    refNormMax = masterData.normMax()
    assert newData.normMax() == 2. * refNormMax
    assert newData.norm2() == 2. * refNorm2
    addData = newData + masterData
    assert addData.normMax() == 3. * refNormMax
    addData += newData
    assert addData.normMax() == 5. * refNormMax
    subData = addData - masterData
    assert subData.normMax() == 4. * refNormMax
    subData -= newData
    assert subData.normMax() == 2. * refNormMax
    mulData = newData * 3.
    assert mulData.normMax() == 6. * refNormMax
    newData.imuladd(3., subData)
    assert newData.normMax() == 8. * refNormMax
    assert pytest.approx(newData.dot(masterData), abs=1.E-8) == 8. * refNorm2 * refNorm2

def main_master(masterDriver, masterData):
    masterDriver.initialize()
    masterDriver.init()
    assert masterDriver.getInitStatus() == True
    assert masterDriver.getInputValuesNames() == ["inputDouble", "inputInt", "inputString"]
    assert masterDriver.getOutputValuesNames() == ["outputDouble", "outputInt", "outputString", "result"]
    assert masterDriver.getValueType("inputDouble") == "Double"
    assert masterDriver.getValueType("result") == "Double"
    assert masterDriver.getValueType("outputInt") == "Int"
    assert masterDriver.getValueType("outputString") == "String"
    assert masterDriver.getValueUnit("result") == "totoUnit"
    masterDriver.setInputDoubleValue("inputDouble", 3.)
    assert masterDriver.getOutputDoubleValue("outputDouble") == 3.
    masterDriver.setInputIntValue("inputInt", 5)
    assert masterDriver.getOutputIntValue("outputInt") == 5
    masterDriver.setInputStringValue("inputString", "toto")
    assert masterDriver.getOutputStringValue("outputString") == "toto"
    masterDriver.setStationaryMode(True)
    assert masterDriver.getStationaryMode() == True
    masterDriver.setStationaryMode(False)
    assert masterDriver.computeTimeStep() == (0.2, False)
    assert masterDriver.isStationary() == True
    masterDriver.initTimeStep(1.)
    assert masterDriver.solveTimeStep() == True
    masterDriver.validateTimeStep()
    masterDriver.save(2, "INTERNAL")
    masterDriver.initTimeStep(1.)
    masterDriver.solve()
    assert masterDriver.getSolveStatus() == True
    masterDriver.abortTimeStep()
    assert masterDriver.presentTime() == 1.
    masterDriver.initTimeStep(1.)
    assert (masterData + masterData).normMax() == 2.
    assert masterDriver.iterateTimeStep() == (True, True)
    masterDriver.iterate()
    assert masterDriver.getIterateStatus() == (True, True)
    masterDriver.validateTimeStep()
    assert masterDriver.presentTime() == 2.
    assert masterDriver.getOutputDoubleValue("result") == 6.
    masterDriver.resetTime(5.)
    masterDriver.initTimeStep(1.)
    masterDriver.solve()
    masterDriver.validateTimeStep()
    assert masterDriver.presentTime() == 6.
    assert masterDriver.getOutputDoubleValue("result") == 18.
    masterDriver.restore(2, "INTERNAL")
    assert masterDriver.presentTime() == 1.
    assert masterDriver.getOutputDoubleValue("result") == 3.

    main_master_data(masterData)

    masterDriver.initTimeStep(1.)
    masterDriver.solve()
    masterDriver.validateTimeStep()

    masterDriver.forget(2, "INTERNAL")

    masterDriver.term()
    masterDriver.terminate()

def main_masterWorkers():
    import mpi4py.MPI as mpi
    import c3po
    import c3po.mpi
    from tests.unitests.masterWorkers.WorkerDriver import WorkerDriver

    comm = mpi.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        workerProcess = c3po.mpi.MPIRemoteProcess(comm, 1)
        masterDriver = c3po.mpi.MPIMasterPhysicsDriver(workerProcess)
        masterData = c3po.mpi.MPIMasterDataManager(masterDriver, 0)
        main_master(masterDriver, masterData)

    elif rank == 1:
        masterProcess = c3po.mpi.MPIRemoteProcess(comm, 0)
        worker = WorkerDriver()
        data = c3po.LocalDataManager()
        data.setInputDoubleValue("data", 1.)
        Worker = c3po.mpi.MPIWorker([worker], [], [data], masterProcess)
        Worker.listen()

    if rank == 0:
        workerProcess = c3po.mpi.MPICollectiveProcess(comm)
        localWorker = WorkerDriver()
        localData = c3po.LocalDataManager()
        localData.setInputDoubleValue("data", 1.)
        masterDriver = c3po.mpi.MPIMasterPhysicsDriver(workerProcess, localPhysicsDriver=localWorker)
        masterData = c3po.mpi.MPIMasterDataManager(masterDriver, 0, localDataManager=localData)
        main_master(masterDriver, masterData)

    else:
        masterProcess = c3po.mpi.MPIRemoteProcess(comm, 0)
        worker = WorkerDriver()
        data = c3po.LocalDataManager()
        data.setInputDoubleValue("data", 1.)
        Worker = c3po.mpi.MPIWorker([worker], [], [data], masterProcess, isCollective=True)
        Worker.listen()

if __name__ == "__main__":
    main_masterWorkers()
