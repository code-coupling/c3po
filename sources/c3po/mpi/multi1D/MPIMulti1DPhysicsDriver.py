# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the classes MPIMulti1DPhysicsDriver. """
from c3po.multi1D.MEDInterface import MEDInterface
from c3po.multi1D.Multi1DPhysicsDriver import DriversAPI, Multi1DPhysicsDriver
from c3po.mpi.MPIRemote import MPIRemote
from c3po.mpi.MPICollaborativePhysicsDriver import MPICollaborativePhysicsDriver


class MPIMulti1DPhysicsDriver(Multi1DPhysicsDriver):
    """! MPIMulti1DPhysicsDriver is the MPI collaborative version of c3po.multi1D.Multi1DPhysicsDriver. """
    def __init__(self, physics, grid, weights=None, mpiComm=None):
        """! Build a MPIMulti1DPhysicsDriver.

        @param physics same than in Multi1DPhysicsDriver.__init__(), but some elements can be MPIRemote.
        @param grid see Multi1DPhysicsDriver.__init__().
        @param weights see Multi1DPhysicsDriver.__init__().
        @param mpiComm If not None, forces MPIMulti1DPhysicsDriver to make MPI communications and to use this communicator (can also be done with setMPIComm()).
        """
        super().__init__(physics, grid, weights)
        self._physics = MPICollaborativePhysicsDriver(physics, mpiComm=mpiComm)
        for i, phy in enumerate(self.getPhysicsDrivers()):
            if not isinstance(phy, MPIRemote):
                self._testIndex = i
                break

    def _initMEDInterface(self, withTemplateField, fieldName):
        """! See Multi1DPhysicsDriver._initMEDInterface(). """
        if self._medInterface is None:
            meshes = []
            for physics in self.getPhysicsDrivers():
                if isinstance(physics, MPIRemote):
                    meshes.append([])
                else:
                    field = physics.getInputMEDDoubleFieldTemplate(fieldName) if withTemplateField else physics.getOutputMEDDoubleField(fieldName)
                    meshes.append(field.getMesh().getCoordsAt(0))
            self._driverAPI = DriversAPI(self.getPhysicsDrivers(), meshes, self._testIndex, self._weights)
            self._medInterface = MEDInterface(self._driverAPI, self._grid)

    def shiftPhysicsDrivers(self, shiftMap):
        """! See Multi1DPhysicsDriver.shiftPhysicsDrivers(). """
        removed = super().shiftPhysicsDrivers(shiftMap)
        for i, physics in enumerate(self.getPhysicsDrivers()):
            if not isinstance(physics, MPIRemote):
                self._testIndex = i
                break
        return removed
