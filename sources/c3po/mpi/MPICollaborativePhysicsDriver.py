# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPICollaborativePhysicsDriver. """
from __future__ import print_function, division

from c3po.mpi.MPICoupler import MPICoupler
from c3po.CollaborativePhysicsDriver import CollaborativePhysicsDriver


class MPICollaborativePhysicsDriver(CollaborativePhysicsDriver, MPICoupler):
    """! MPICollaborativePhysicsDriver is the MPI version of CollaborativePhysicsDriver. """

    def __init__(self, physics, mpiComm=None):
        """! Build an CollaborativePhysicsDriver object.

        @param physics a list (or dictionary) of PhysicsDriver objects.
        @param mpiComm MPI communicator to provide to MPICoupler. See MPICoupler.__init__().
        """
        MPICoupler.__init__(self, physics=physics, exchangers=[], mpiComm=mpiComm)
        CollaborativePhysicsDriver.__init__(self, self._physicsDriversList)
