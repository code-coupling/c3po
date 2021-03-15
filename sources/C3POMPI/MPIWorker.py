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

from C3POMPI.MPITag import MPITag
from C3POMPI.MPIRemoteProcess import MPIRemoteProcess
from C3POMPI.MPIMasterCollectivePhysicsDriver import MPIMasterCollectivePhysicsDriver


class MPIWorker(object):
    """! MPIWorker defines the behavior of workers in a master/workers MPI paradimg. """

    def __init__(self, physicsDrivers, exchangers, dataManagers, MasterProcess):
        """! Build a MPIWorker object.

        @param physicsDrivers List of C3PO.PhysicsDriver.PhysicsDriver. Only one should not be a MPIRemoteProcess: it is the one the worker is responsible for.
        @param exchangers List of C3PO.Exchanger.Exchanger. The indices in this list are the numbers identifying the C3PO.Exchanger.Exchanger for the master.
        @param dataManagers List of C3PO.DataManager.DataManager. The indices in this list are the numbers identifying the C3PO.DataManager.DataManager for the master.
        @param MasterProcess Either a MPIRemoteProcess or a MPIMasterCollectivePhysicsDriver identifying the master process. In the first case point-to-point communications are used, in the second case collective communications are used. 
        """
        found = False
        for p in physicsDrivers:
            if not isinstance(p, MPIRemoteProcess):
                if found:
                    raise Exception("MPIWorker.__init__ : we found more than one local PhysicsDriver (not MPIRemoteProcess) : there must be only one.")
                found = True
                self.physicsDriver_ = p
        if not found:
            raise Exception("MPIWorker.__init__ : we did not found any local PhysicsDriver : there must be one (and only one).")
        self.MPIComm_ = MasterProcess.MPIComm_
        self.masterRank_ = 0
        self.isCollective_ = False
        if isinstance(MasterProcess, MPIRemoteProcess):
            self.masterRank_ = MasterProcess.rank_
        elif isinstance(MasterProcess, MPIMasterCollectivePhysicsDriver):
            self.masterRank_ = MasterProcess.masterRank_
            self.isCollective_ = True
        else:
            raise Exception("MPIWorker.__init__ : MasterProcess type unknown.")
        self.exchangers_ = exchangers
        self.dataManagers_ = {}  # Used a little bit as a list but the [] operator of a dict is more convenent here.
        for idata in range(len(dataManagers)):
            self.dataManagers_[idata] = dataManagers[idata]
        self.IdDataFree_ = []

    def answer(self, data, CollectiveOperator=MPI.MIN):
        """! INTERNAL """
        if self.isCollective_:
            self.MPIComm_.reduce(data, op=CollectiveOperator, root=self.masterRank_)
        else:
            self.MPIComm_.send(data, dest=self.masterRank_, tag=MPITag.answer)

    def getIdNewData(self):
        """! INTERNAL """
        IdNewDataMan = len(self.dataManagers_)
        if len(self.IdDataFree_) > 0:
            IdNewDataMan = self.IdDataFree_.pop()
        return IdNewDataMan

    def checkDataID(self, idList):
        """! INTERNAL """
        for id in idList:
            if id >= len(self.dataManagers_):
                raise Exception("MPIWorker.checkDataID : the asked DataManager does not exist : ID asked : " + str(id) + ", maximum ID : " + str(len(self.dataManagers_) - 1) + ".")

    def listen(self):
        """! Make the worker waits for instructions from the master. 

        The worker gets out of this waiting mode when the master call the terminate method of the related MPIMasterPhysicsDriver.
        """
        status = MPI.Status()
        tag = MPITag.init
        while tag != MPITag.terminate:
            if self.isCollective_:
                data = self.MPIComm_.bcast(0, root=self.masterRank_)
                tag = data[0]
                data = data[-1]
            else:
                data = self.MPIComm_.recv(source=self.masterRank_, tag=MPI.ANY_TAG, status=status)
                tag = status.Get_tag()
            #print "rank ", self.MPIComm_.Get_rank(), ", tag = ", tag, "*****************************************************************"
            if tag == MPITag.init:
                self.physicsDriver_.init()
            elif tag == MPITag.getInitStatus:
                self.answer(self.physicsDriver_.getInitStatus())
            elif tag == MPITag.presentTime:
                self.answer(self.physicsDriver_.presentTime())
            elif tag == MPITag.computeTimeStep:
                (dt, stop) = self.physicsDriver_.computeTimeStep()
                self.answer(dt)
                self.answer(stop)
            elif tag == MPITag.initTimeStep:
                self.answer(self.physicsDriver_.initTimeStep(data))
            elif tag == MPITag.solve:
                self.physicsDriver_.solve()
            elif tag == MPITag.getSolveStatus:
                self.answer(self.physicsDriver_.getSolveStatus())
            elif tag == MPITag.validateTimeStep:
                self.physicsDriver_.validateTimeStep()
            elif tag == MPITag.abortTimeStep:
                self.physicsDriver_.abortTimeStep()
            elif tag == MPITag.isStationary:
                self.answer(self.physicsDriver_.isStationary())
            elif tag == MPITag.iterate:
                self.physicsDriver_.iterate()
            elif tag == MPITag.getIterateStatus:
                (succed, converged) = self.physicsDriver_.computeTimeStep()
                self.answer(succeed)
                self.answer(converged)
            elif tag == MPITag.save:
                self.physicsDriver_.save(*data)
            elif tag == MPITag.restore:
                self.physicsDriver_.restore(*data)
            elif tag == MPITag.forget:
                self.physicsDriver_.forget(*data)
            elif tag == MPITag.getInputFieldsNames:
                self.answer(self.physicsDriver_.getInputFieldsNames())
            elif tag == MPITag.getInputMEDFieldTemplate:
                self.answer(self.physicsDriver_.getInputMEDFieldTemplate(data))
            elif tag == MPITag.setInputMEDField:
                self.physicsDriver_.setInputMEDField(*data)
            elif tag == MPITag.getOutputFieldsNames:
                self.answer(self.physicsDriver_.getOutputFieldsNames())
            elif tag == MPITag.getOutputMEDField:
                self.answer(self.physicsDriver_.getOutputMEDField(data))
            elif tag == MPITag.getInputValuesNames:
                self.answer(self.physicsDriver_.getInputValuesNames())
            elif tag == MPITag.setValue:
                self.physicsDriver_.setValue(*data)
            elif tag == MPITag.getOutputValuesNames:
                self.answer(self.physicsDriver_.getOutputValuesNames())
            elif tag == MPITag.getValue:
                self.answer(self.physicsDriver_.getValue(data))

            elif tag == MPITag.deleteDataManager:
                self.checkDataID(data)
                self.IdDataFree_ += data
            elif tag == MPITag.cloneEmptyData:
                IdNewDataMan = self.getIdNewData()
                self.dataManagers_[IdNewDataMan] = self.dataManagers_[data].cloneEmpty()
                self.answer(IdNewDataMan)
            elif tag == MPITag.copyData:
                self.checkDataID(data)
                self.dataManagers_[data[0]].copy(self.dataManagers_[data[1]])
            elif tag == MPITag.normMax:
                self.answer(self.dataManagers_[data].normMax(), CollectiveOperator=MPI.MAX)
            elif tag == MPITag.norm2:
                norm = self.dataManagers_[data].norm2()
                self.answer(norm * norm, CollectiveOperator=MPI.SUM)
            elif tag == MPITag.addData:
                self.checkDataID(data)
                IdNewDataMan = self.getIdNewData()
                self.dataManagers_[IdNewDataMan] = self.dataManagers_[data[0]] + self.dataManagers_[data[1]]
                self.answer(IdNewDataMan)
            elif tag == MPITag.iaddData:
                self.checkDataID(data)
                self.dataManagers_[data[0]] += self.dataManagers_[data[1]]
            elif tag == MPITag.subData:
                self.checkDataID(data)
                IdNewDataMan = self.getIdNewData()
                self.dataManagers_[IdNewDataMan] = self.dataManagers_[data[0]] - self.dataManagers_[data[1]]
                self.answer(IdNewDataMan)
            elif tag == MPITag.isubData:
                self.checkDataID(data)
                self.dataManagers_[data[0]] -= self.dataManagers_[data[1]]
            elif tag == MPITag.mulData:
                self.checkDataID([data[0]])
                IdNewDataMan = self.getIdNewData()
                self.dataManagers_[IdNewDataMan] = self.dataManagers_[data[0]] * data[1]
                self.answer(IdNewDataMan)
            elif tag == MPITag.imulData:
                self.checkDataID([data[0]])
                self.dataManagers_[data[0]] *= data[1]
            elif tag == MPITag.imuladdData:
                self.checkDataID([data[0], data[2]])
                self.dataManagers_[data[0]].imuladd(data[1], self.dataManagers_[data[2]])
            elif tag == MPITag.dotData:
                self.checkDataID(data)
                self.answer(self.dataManagers_[data[0]].dot(self.dataManagers_[data[1]]), CollectiveOperator=MPI.SUM)

            elif tag == MPITag.exchange:
                self.exchangers_[data].exchange()

        self.answer(self.physicsDriver_.terminate())
