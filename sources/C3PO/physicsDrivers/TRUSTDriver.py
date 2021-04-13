# -*- coding: utf-8 -*-
from __future__ import print_function, division

import trusticoco as ti
from C3PO.PhysicsDriver import PhysicsDriver


class TRUSTDriver(ti.ProblemTrio, PhysicsDriver):
    """! This is the implementation of PhysicsDriver for TRUST. """
    def __init__(self):
        ti.ProblemTrio.__init__(self)
        PhysicsDriver.__init__(self)

    initialize = ti.ProblemTrio.initialize
    computeTimeStep = ti.ProblemTrio.computeTimeStep

    def initTimeStep(self, dt):
        self._dt = dt
        return ti.ProblemTrio.initTimeStep(self, dt)

    solveTimeStep = ti.ProblemTrio.solveTimeStep
    validateTimeStep = ti.ProblemTrio.validateTimeStep
    abortTimeStep = ti.ProblemTrio.abortTimeStep

    def terminate(self):
        ti.ProblemTrio.terminate(self)
        return True

    getInputMEDFieldTemplate = ti.ProblemTrio.getInputMEDFieldTemplate
    setInputMEDField = ti.ProblemTrio.setInputMEDField
    getOutputMEDField = ti.ProblemTrio.getOutputMEDField
