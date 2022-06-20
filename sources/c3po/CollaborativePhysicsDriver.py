# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class CollaborativePhysicsDriver. """
from __future__ import print_function, division

from c3po.Coupler import Coupler
from c3po.CollaborativeObject import CollaborativeObject


class CollaborativePhysicsDriver(Coupler, CollaborativeObject):
    """! CollaborativePhysicsDriver is a PhysicsDriver (a Coupler in fact) that handles a set of PhysicsDriver as a single one.

    The solving methods of the CollaborativePhysicsDriver call the ones of the held PhysicsDriver in a row.
    """

    def __init__(self, physics):
        """! Build an CollaborativePhysicsDriver object.

        @param physics a list (or dictionary) of PhysicsDriver objects.
        """
        Coupler.__init__(self, physics=physics, exchangers=[])
        CollaborativeObject.__init__(self, self._physicsDriversList)

    def solveTimeStep(self):
        """! See PhysicsDriver.solveTimeStep(). """
        for physics in self._physicsDriversList:
            physics.solve()
        return self.getSolveStatus()

    def iterateTimeStep(self):
        """! See PhysicsDriver.iterateTimeStep(). """
        for physics in self._physicsDriversList:
            physics.iterate()
        return self.getIterateStatus()
