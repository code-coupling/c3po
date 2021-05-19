# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class TRUSTDriver. """
from __future__ import print_function, division

import trusticoco as ti
from c3po.PhysicsDriver import PhysicsDriver


class TRUSTDriver(ti.ProblemTrio, PhysicsDriver):
    """! This is the implementation of PhysicsDriver for TRUST. Since TRUST is ICoCo-compliant, not much
    to be done! """

    def __init__(self):
        ti.ProblemTrio.__init__(self)
        PhysicsDriver.__init__(self)
        self._dt = 0.

    def initialize(self):
        return ti.ProblemTrio.initialize(self)

    def terminate(self):
        ti.ProblemTrio.terminate(self)

    def computeTimeStep(self):
        return ti.ProblemTrio.computeTimeStep(self)

    def initTimeStep(self, dt):
        self._dt = dt
        return ti.ProblemTrio.initTimeStep(self, dt)

    def solveTimeStep(self):
        return ti.ProblemTrio.solveTimeStep(self)

    def validateTimeStep(self):
        ti.ProblemTrio.validateTimeStep(self)

    def abortTimeStep(self):
        ti.ProblemTrio.abortTimeStep(self)

    def setInputMEDField(self, name, field):
        medField = ti.MEDField(field)
        ti.ProblemTrio.setInputMEDFieldAsMF(self, name, medField)
