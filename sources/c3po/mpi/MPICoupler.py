# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPICoupler. """
from __future__ import print_function, division
from mpi4py import MPI

from c3po.Coupler import Coupler
from c3po.mpi.MPIRemoteProcess import MPIRemoteProcess
from c3po.mpi.MPICollectiveProcess import MPICollectiveProcess


class MPICoupler(Coupler):
    """! MPICoupler is the MPI collaborative version of c3po.Coupler.Coupler.

    The MPI functionalities are used for some collective operations.

    Can replace, without impact, a c3po.Coupler.Coupler for a calculation on a single process, if the MPI environment is available.
    """

    def __init__(self, physics, exchangers, dataManagers=[], mpiComm=None):
        """! Build a MPICoupler object.

        Has the same form than Coupler.__init__() but can also contain MPIRemoteProcess (and MPICollectiveProcess) objects.

        When at least one MPIRemoteProcess or MPICollectiveProcess is present, MPICoupler uses collective MPI communications:
        the object must be built and used in the same way for all the involved processes. They must all share the same communicator,
        and all the processes of this communicator must be involved.

        @param physics list (or dictionary) of c3po.PhysicsDriver.PhysicsDriver objects to be coupled.
        @param exchangers list (or dictionary) of c3po.Exchanger.Exchanger for the coupling.
        @param dataManagers list (or dictionary) of c3po.DataManager.DataManager used in the coupling.
        @param mpiComm The optional mpiComm parameter enables to force MPICoupler to make MPI communications even if no MPIRemoteProcess
        or MPICollectiveProcess are found.
        It has to be given to the constructor of the object on all involved processes.
        If at least one MPIRemoteProcess or MPICollectiveProcess is present, this mpiComm parameter must be the same than theirs.
        """
        Coupler.__init__(self, physics, exchangers, dataManagers)
        self.mpiComm = None
        self._isMPI = False
        for phy in self._physicsDriversList:
            if isinstance(phy, (MPIRemoteProcess, MPICollectiveProcess)):
                if not self._isMPI:
                    if phy.mpiComm == MPI.COMM_NULL:
                        raise Exception("MPICoupler.__init__ All distant process must be part of the communicator (MPI.COMM_NULL found).")
                    self._isMPI = True
                    self.mpiComm = phy.mpiComm
                else:
                    if self.mpiComm != phy.mpiComm:
                        raise Exception("MPIcoupler.__init__ All distant process must used the same MPI communicator")
        if mpiComm is not None:
            if self.mpiComm is not None:
                if mpiComm != self.mpiComm:
                    raise Exception("MPIcoupler.__init__ The given mpiComm parameter is not the same than the one used by the MPI process found.")
            self.mpiComm = mpiComm
            self._isMPI = self.mpiComm.allreduce(self._isMPI, op=MPI.MAX)

    def getMEDCouplingMajorVersion(self):
        """! See Coupler.getMEDCouplingMajorVersion(). """
        version = 0
        try:
            version = Coupler.getMEDCouplingMajorVersion(self)
        except NotImplementedError:
            version = 0
        if self._isMPI:
            versionList = self.mpiComm.allgather(version)
            for ver in versionList:
                if ver != 0:
                    if ver != version:
                        if version == 0:
                            version = ver
                        else:
                            raise Exception("MPICoupler.getMEDCouplingMajorVersion Not a unique version.")
        if version == 0:
            raise NotImplementedError
        return version

    def isMEDCoupling64Bits(self):
        """! See Coupler.isMEDCoupling64Bits(). """
        resu = None
        try:
            resu = Coupler.isMEDCoupling64Bits(self)
        except NotImplementedError:
            resu = None
        if self._isMPI:
            resuList = self.mpiComm.allgather(resu)
            for res in resuList:
                if res is not None:
                    if res != resu:
                        if resu is None:
                            resu = res
                        else:
                            raise Exception("MPICoupler.isMEDCoupling64Bits Not a unique answer.")
        if resu is None:
            raise NotImplementedError
        return resu

    def initialize(self):
        """! See Coupler.initialize(). """
        resu = Coupler.initialize(self)
        if self._isMPI:
            resu = self.mpiComm.allreduce(resu, op=MPI.MIN)
        return resu

    def computeTimeStep(self):
        """! See Coupler.computeTimeStep(). """
        (dt, stop) = Coupler.computeTimeStep(self)
        if self._isMPI:
            dt = self.mpiComm.allreduce(dt, op=MPI.MIN)
            stop = self.mpiComm.allreduce(stop, op=MPI.MIN)
        return (dt, stop)

    def initTimeStep(self, dt):
        """! See Coupler.initTimeStep(). """
        resu = Coupler.initTimeStep(self, dt)
        if self._isMPI:
            resu = self.mpiComm.allreduce(resu, op=MPI.MIN)
        return resu

    def getSolveStatus(self):
        """! See Coupler.getSolveStatus(). """
        resu = Coupler.getSolveStatus(self)
        if self._isMPI:
            resu = self.mpiComm.allreduce(resu, op=MPI.MIN)
        return resu

    def getStationaryMode(self):
        """! See Coupler.getStationaryMode(). """
        resu = Coupler.getStationaryMode(self)
        if self._isMPI:
            resuMin = self.mpiComm.allreduce(resu, op=MPI.MIN)
            resuMax = self.mpiComm.allreduce(resu, op=MPI.MAX)
            if resuMin != resuMax:
                raise Exception("MPICoupler.getStationaryMode Not a unique stationary mode.")
        return resu

    def isStationary(self):
        """! See Coupler.isStationary(). """
        resu = Coupler.isStationary(self)
        if self._isMPI:
            resu = self.mpiComm.allreduce(resu, op=MPI.MIN)
        return resu

    def getIterateStatus(self):
        """! See Coupler.getIterateStatus(). """
        (succeed, converged) = Coupler.getIterateStatus(self)
        if self._isMPI:
            succeed = self.mpiComm.allreduce(succeed, op=MPI.MIN)
            converged = self.mpiComm.allreduce(converged, op=MPI.MIN)
        return (succeed, converged)
