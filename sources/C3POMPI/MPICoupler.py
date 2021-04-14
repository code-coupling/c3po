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

from C3PO.Coupler import Coupler
from C3POMPI.MPIRemoteProcess import MPIRemoteProcess
from C3POMPI.MPICollectiveProcess import MPICollectiveProcess


class MPICoupler(Coupler):
    """! MPICoupler is the MPI collaborative version of C3PO.Coupler.Coupler.

    The MPI functionalities are used for some collective operations.

    Can replace, without impact, a C3PO.Coupler.Coupler for a calculation on a single process, if the MPI environment is available.
    """

    def __init__(self, physics, exchangers, dataManagers=[], MPIComm=None):
        """! Build a MPICoupler object.

        Has the same form than Coupler.__init__() but can also contain MPIRemoteProcess (and MPICollectiveProcess) objects.

        When at least one MPIRemoteProcess or MPICollectiveProcess is present, MPICoupler uses collective MPI communications: the object must be built and used in the same way for all the involved processes. They must all share the same communicator, and all the processes of this communicator must be involved.

        @param physics list (or dictionary) of C3PO.PhysicsDriver.PhysicsDriver objects to be coupled.
        @param exchangers list (or dictionary) of C3PO.Exchanger.Exchanger for the coupling.
        @param dataManagers list (or dictionary) of C3PO.DataManager.DataManager used in the coupling.
        @param MPIComm The optional MPIComm parameter enables to force MPICoupler to make MPI communications even if no MPIRemoteProcess or MPICollectiveProcess are found.
                        It has to be given to the constructor of the object on all involved processes.
                        If at least one MPIRemoteProcess or MPICollectiveProcess is present, this MPIComm parameter must be the same than theirs.
        """
        Coupler.__init__(self, physics, exchangers, dataManagers)
        self.MPIComm_ = None
        self.isMPI_ = False
        for p in self.physicsDriversList_:
            if isinstance(p, MPIRemoteProcess) or isinstance(p, MPICollectiveProcess):
                if not self.isMPI_:
                    if p.MPIComm_ == MPI.COMM_NULL:
                        raise Exception("MPICoupler.__init__ All distant process must be part of the communicator (MPI.COMM_NULL found).")
                    self.isMPI_ = True
                    self.MPIComm_ = p.MPIComm_
                else:
                    if self.MPIComm_ != p.MPIComm_:
                        raise Exception("MPIcoupler.__init__ All distant process must used the same MPI communicator")
        if MPIComm is not None:
            if self.MPIComm_ is not None:
                if MPIComm != self.MPIComm_:
                    raise Exception("MPIcoupler.__init__ The given MPIComm parameter is not the same than the one used by the MPI process found.")
            self.MPIComm_ = MPIComm
            self.isMPI_ = self.MPIComm_.allreduce(self.isMPI_, op=MPI.MAX)

    def initialize(self):
        """! See Coupler.initialize(). """
        resu = Coupler.initialize(self)
        if self.isMPI_:
            resu = self.MPIComm_.allreduce(resu, op=MPI.MIN)
        return resu

    def computeTimeStep(self):
        """! See Coupler.computeTimeStep(). """
        (dt, stop) = Coupler.computeTimeStep(self)
        if self.isMPI_:
            dt = self.MPIComm_.allreduce(dt, op=MPI.MIN)
            stop = self.MPIComm_.allreduce(stop, op=MPI.MIN)
        return (dt, stop)

    def initTimeStep(self, dt):
        """! See Coupler.initTimeStep(). """
        resu = Coupler.initTimeStep(self, dt)
        if self.isMPI_:
            resu = self.MPIComm_.allreduce(resu, op=MPI.MIN)
        return resu

    def getSolveStatus(self):
        """! See Coupler.getSolveStatus(). """
        resu = Coupler.getSolveStatus(self)
        if self.isMPI_:
            resu = self.MPIComm_.allreduce(resu, op=MPI.MIN)
        return resu

    def isStationary(self):
        """! See Coupler.isStationary(). """
        resu = Coupler.isStationary(self)
        if self.isMPI_:
            resu = self.MPIComm_.allreduce(resu, op=MPI.MIN)
        return resu

    def getIterateStatus(self):
        """! See Coupler.getIterateStatus(). """
        (succeed, converged) = Coupler.getIterateStatus(self)
        if self.isMPI_:
            succeed = self.MPIComm_.allreduce(succeed, op=MPI.MIN)
            converged = self.MPIComm_.allreduce(converged, op=MPI.MIN)
        return (succeed, converged)
