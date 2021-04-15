# -*- coding: utf-8 -*-
from __future__ import print_function, division

import trusticoco as ti
from C3PO.PhysicsDriver import PhysicsDriver


class TRUSTDriver(ti.ProblemTrio, PhysicsDriver):
    """! This is the implementation of PhysicsDriver for TRUST. Since TRUST is ICoCo-compliant, not much
    to be done! """
    def __init__(self):
        ti.ProblemTrio.__init__(self)
        PhysicsDriver.__init__(self)

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
        mf = ti.MEDField(field)
        ti.ProblemTrio.setInputMEDFieldAsMF(self, name, mf)
