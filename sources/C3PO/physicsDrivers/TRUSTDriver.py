# -*- coding: utf-8 -*-
from __future__ import print_function, division

import trusticoco_V2 as ti
from C3PO.physicsDriver import physicsDriver


class PBT(ti.ProblemTrio, physicsDriver):

    def __init__(self):
        ti.ProblemTrio.__init__(self)
        physicsDriver.__init__(self)

    def solveTimeStep(self):
        return ti.ProblemTrio.solveTimeStep(self)

    def computeTimeStep(self):
        return ti.ProblemTrio.computeTimeStep(self)

    def initTimeStep(self, dt):
        self._dt = dt
        return ti.ProblemTrio.initTimeStep(self, dt)

    def validateTimeStep(self):
        return ti.ProblemTrio.validateTimeStep(self)

    def abortTimeStep(self):
        return ti.ProblemTrio.abortTimeStep(self)

    def initialize(self):
        ti.ProblemTrio.initialize(self)

    def terminate(self):
        ti.ProblemTrio.terminate(self)

    def setInputMEDField(self, name, field):
        mf = ti.MEDField(field)
        ti.ProblemTrio.setInputMEDFieldAsMF(self, name, mf)
