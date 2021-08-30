# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPIWorker. """
from __future__ import print_function, division
from mpi4py import MPI

from c3po.mpi.MPITag import MPITag
from c3po.mpi.MPIRemoteProcess import MPIRemoteProcess


class MPIWorker(object):
    """! MPIWorker defines the behavior of workers in a master/workers MPI paradimg. """

    def __init__(self, physicsDrivers, exchangers, dataManagers, masterProcess, isCollective=False):
        """! Build a MPIWorker object.

        @param physicsDrivers List of c3po.PhysicsDriver.PhysicsDriver. Only one should not be a MPIRemoteProcess: it is the one the
        worker is responsible for.
        @param exchangers List of c3po.Exchanger.Exchanger. The indices in this list are the numbers identifying the c3po.Exchanger.Exchanger
        for the master.
        @param dataManagers List of c3po.DataManager.DataManager. The indices of this list are the numbers identifying the
        c3po.DataManager.DataManager for the master.
        @param masterProcess A MPIRemoteProcess identifying the master process.
        @param isCollective Put True if the master process uses collective MPI methods (if it has been initialized with a
        c3po.mpi.MPICollectiveProcess.MPICollectiveProcess object as worker).
        """
        found = False
        for phy in physicsDrivers:
            if not isinstance(phy, MPIRemoteProcess):
                if found:
                    raise Exception("MPIWorker.__init__ : we found more than one local PhysicsDriver (not MPIRemoteProcess) : there must be only one.")
                found = True
                self._physicsDriver = phy
        if not found:
            raise Exception("MPIWorker.__init__ : we did not found any local PhysicsDriver : there must be one (and only one).")
        self.mpiComm = masterProcess.mpiComm
        self._isCollective = isCollective
        self._masterRank = masterProcess.rank
        self._exchangers = exchangers
        self._dataManagers = {}  # Used a little bit as a list but the [] operator of a dict is more convenent here.
        for idata in range(len(dataManagers)):
            self._dataManagers[idata] = dataManagers[idata]
        self._idDataFree = []

    def answer(self, data, collectiveOperator=MPI.MIN):
        """! INTERNAL """
        if self._isCollective:
            self.mpiComm.reduce(data, op=collectiveOperator, root=self._masterRank)
        else:
            self.mpiComm.send(data, dest=self._masterRank, tag=MPITag.answer)

    def getIdNewData(self):
        """! INTERNAL """
        idNewDataMan = len(self._dataManagers)
        if len(self._idDataFree) > 0:
            idNewDataMan = self._idDataFree.pop()
        return idNewDataMan

    def checkDataID(self, idList):
        """! INTERNAL """
        for iid in idList:
            if iid >= len(self._dataManagers):
                raise Exception("MPIWorker.checkDataID : the asked DataManager does not exist : ID asked : " + str(iid) + ", maximum ID : " + str(len(self._dataManagers) - 1) + ".")

    def listen(self):
        """! Make the worker waits for instructions from the master.

        The worker gets out of this waiting mode when the master call the terminate method of the related c3po.mpi.MPIMasterPhysicsDriver.MPIMasterPhysicsDriver.
        """
        status = MPI.Status()
        tag = MPITag.init
        while tag != MPITag.terminate:
            if self._isCollective:
                data = self.mpiComm.bcast(0, root=self._masterRank)
                tag = data[0]
                data = data[-1]
            else:
                data = self.mpiComm.recv(source=self._masterRank, tag=MPI.ANY_TAG, status=status)
                tag = status.Get_tag()
            #print "rank ", self.mpiComm.Get_rank(), ", tag = ", tag, "*****************************************************************"
            if tag < MPITag.tagBARRIER:
                if tag == MPITag.init:
                    self._physicsDriver.init()
                elif tag == MPITag.getInitStatus:
                    self.answer(self._physicsDriver.getInitStatus())
                elif tag == MPITag.presentTime:
                    self.answer(self._physicsDriver.presentTime())
                elif tag == MPITag.computeTimeStep:
                    (dt, stop) = self._physicsDriver.computeTimeStep()
                    self.answer(dt)
                    self.answer(stop)
                elif tag == MPITag.initTimeStep:
                    self.answer(self._physicsDriver.initTimeStep(data))
                elif tag == MPITag.solve:
                    self._physicsDriver.solve()
                elif tag == MPITag.getSolveStatus:
                    self.answer(self._physicsDriver.getSolveStatus())
                elif tag == MPITag.validateTimeStep:
                    self._physicsDriver.validateTimeStep()
                elif tag == MPITag.setStationaryMode:
                    self._physicsDriver.setStationaryMode(data)
                elif tag == MPITag.getStationaryMode:
                    self.answer(self._physicsDriver.getStationaryMode(), collectiveOperator=MPI.MIN)
                    self.answer(self._physicsDriver.getStationaryMode(), collectiveOperator=MPI.MAX)
                elif tag == MPITag.abortTimeStep:
                    self._physicsDriver.abortTimeStep()
                elif tag == MPITag.isStationary:
                    self.answer(self._physicsDriver.isStationary())
                elif tag == MPITag.resetTime:
                    self._physicsDriver.resetTime(data)
                elif tag == MPITag.iterate:
                    self._physicsDriver.iterate()
                elif tag == MPITag.getIterateStatus:
                    (succeed, converged) = self._physicsDriver.computeTimeStep()
                    self.answer(succeed)
                    self.answer(converged)
                elif tag == MPITag.save:
                    self._physicsDriver.save(*data)
                elif tag == MPITag.restore:
                    self._physicsDriver.restore(*data)
                elif tag == MPITag.forget:
                    self._physicsDriver.forget(*data)
                elif tag == MPITag.setInputDoubleValue:
                    self._physicsDriver.setInputDoubleValue(*data)
                elif tag == MPITag.setInputIntValue:
                    self._physicsDriver.setInputIntValue(*data)
                elif tag == MPITag.setInputStringValue:
                    self._physicsDriver.setInputStringValue(*data)
            else:
                if tag == MPITag.deleteDataManager:
                    self.checkDataID(data)
                    self._idDataFree += data
                elif tag == MPITag.cloneEmptyData:
                    idNewDataMan = self.getIdNewData()
                    self._dataManagers[idNewDataMan] = self._dataManagers[data].cloneEmpty()
                    self.answer(idNewDataMan)
                elif tag == MPITag.copyData:
                    self.checkDataID(data)
                    self._dataManagers[data[0]].copy(self._dataManagers[data[1]])
                elif tag == MPITag.normMax:
                    self.answer(self._dataManagers[data].normMax(), collectiveOperator=MPI.MAX)
                elif tag == MPITag.norm2:
                    norm = self._dataManagers[data].norm2()
                    self.answer(norm * norm, collectiveOperator=MPI.SUM)
                elif tag == MPITag.addData:
                    self.checkDataID(data)
                    idNewDataMan = self.getIdNewData()
                    self._dataManagers[idNewDataMan] = self._dataManagers[data[0]] + self._dataManagers[data[1]]
                    self.answer(idNewDataMan)
                elif tag == MPITag.iaddData:
                    self.checkDataID(data)
                    self._dataManagers[data[0]] += self._dataManagers[data[1]]
                elif tag == MPITag.subData:
                    self.checkDataID(data)
                    idNewDataMan = self.getIdNewData()
                    self._dataManagers[idNewDataMan] = self._dataManagers[data[0]] - self._dataManagers[data[1]]
                    self.answer(idNewDataMan)
                elif tag == MPITag.isubData:
                    self.checkDataID(data)
                    self._dataManagers[data[0]] -= self._dataManagers[data[1]]
                elif tag == MPITag.mulData:
                    self.checkDataID([data[0]])
                    idNewDataMan = self.getIdNewData()
                    self._dataManagers[idNewDataMan] = self._dataManagers[data[0]] * data[1]
                    self.answer(idNewDataMan)
                elif tag == MPITag.imulData:
                    self.checkDataID([data[0]])
                    self._dataManagers[data[0]] *= data[1]
                elif tag == MPITag.imuladdData:
                    self.checkDataID([data[0], data[2]])
                    self._dataManagers[data[0]].imuladd(data[1], self._dataManagers[data[2]])
                elif tag == MPITag.dotData:
                    self.checkDataID(data)
                    self.answer(self._dataManagers[data[0]].dot(self._dataManagers[data[1]]), collectiveOperator=MPI.SUM)

                elif tag == MPITag.exchange:
                    self._exchangers[data].exchange()
        self._physicsDriver.terminate()
