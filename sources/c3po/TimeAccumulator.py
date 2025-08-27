# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class :class:`.TimeAccumulator`. """
from __future__ import print_function, division

from c3po.services.PhysicsDriverWrapper import PhysicsDriverWrapper
from c3po.services.Printer import warning


class SaveAtInitTimeStep(object):
    """ Enum defining :class:`.TimeAccumulator` saving mode.

    Values:
        - ``never``:
            :class:`.TimeAccumulator` never calls the :meth:`save() <.PhysicsDriverWrapper.save>` /
            :meth:`restore() <.PhysicsDriverWrapper.restore>` methods.
            :meth:`abortTimeStep() <.TimeAccumulator.abortTimeStep>` is not available if not in
            StationaryMode.
        - ``always``:
            :class:`.TimeAccumulator` saves at every :meth:`initTimeStep()
            <.TimeAccumulator.initTimeStep>` call and restores at every
            :meth:`abortTimeStep <.TimeAccumulator.abortTimeStep>`, even in StationaryMode.
        - ``transient``:
            :class:`.TimeAccumulator` saves at every :meth:`initTimeStep()
            <.TimeAccumulator.initTimeStep>` call and restores at every
            :meth:`abortTimeStep() <.TimeAccumulator.abortTimeStep>`, if not in StationaryMode.
        - ``transientExceptAfterAbort``:
            If not in StationaryMode:
                - :class:`.TimeAccumulator` saves at every :meth:`initTimeStep()
                  <.TimeAccumulator.initTimeStep>` call that does not
                  follow an :meth:`abortTimeStep() <.TimeAccumulator.abortTimeStep>` (the first
                  attempt to compute a time-step).
                - It restores at every :meth:`abortTimeStep() <.TimeAccumulator.abortTimeStep>`, if
                  not in StationaryMode.
    """
    never = 0
    always = 1
    transient = 2
    transientExceptAfterAbort = 3


class TimeAccumulator(PhysicsDriverWrapper):
    """ :class:`.TimeAccumulator` wraps a :class:`.PhysicsDriver` into a macro time step procedure
    (for transients or stationaries (through stabilized transients)).

    In transient calculations, the :class:`.TimeAccumulator` object is driven like any
    :class:`.PhysicsDriver`, but it will use macro time steps (chosen with
    :meth:`initTimeStep`) whereas the wraped :class:`.PhysicsDriver` may use smaller internal time
    steps (given by its own :meth:`computeTimeStep` method).

    In stationary calculations, if the stabilizedTransient mode is activated, when a steady-state is
    asked to the :class:`.TimeAccumulator` object
    (``initTimeStep(0)`` in stationaryMode), a time loop over the wraped :class:`.PhysicsDriver`
    object is run until steady-state is reached (:meth:`isStationary()
    <.PhysicsDriverWrapper.isStationary>` return True).
    If the stabilizedTransient mode is not activated, steady-state calculations (``initTimeStep(0)``
    in stationaryMode) are directly asked to the wraped :class:`.PhysicsDriver`.
    """

    def __init__(self, physics, saveParameters=None, stabilizedTransient=(False, 100.)):
        """ Build a :class:`.TimeAccumulator` object.

        Parameters
        ----------
        physics : PhysicsDriver
            The :class:`.PhysicsDriver` to wrap.
        saveParameters : tuple
            The tuple ``(label, method)`` that can be used to save / restore results in order to provide
            :meth:`abortTimeStep` capabilities in transient.
            The method :meth:`setSavingMode` allows to choose when saving is done.
        stabilizedTransient : tuple
            A tuple ``(activated, tMax)``. If ``activated`` is set to True, it computes steady states (``dt
            = 0``) as stabilized transients (until ``physics.isStationary()``
            returns True or the current time reaches ``tInit + tMax``) and then uses
            ``resetTime(tInit)`` in order to keep time consistency (``tInit`` is the returned value of
            ``physics.presentTime()`` before solving). If ``activated`` is set to False (default value),
            steady-states (``dt = 0``) are directly asked to ``physics``.
            The method :meth:`setStabilizedTransient` allows to modify these data.
        """
        PhysicsDriverWrapper.__init__(self, physics)
        self._dt = None
        self._timeDifference = 0.
        self._macrodt = None
        self._saveParameters = saveParameters
        self._savingMode = SaveAtInitTimeStep.transient
        self._stabilizedTransient = stabilizedTransient
        self._afterAbort = False

    def setSavingMode(self, savingMode):
        """ Set a saving mode.

        Parameters
        ----------
        savingMode
            See :class:`.SaveAtInitTimeStep` documentation for available options. Default value is
            :attr:`.SaveAtInitTimeStep.transient`.
        """
        self._savingMode = savingMode

    def setStabilizedTransient(self, stabilizedTransient):
        """ Set stabilized transient data.

        Parameters
        ----------
        stabilizedTransient
            See parameter ``stabilizedTransient`` of the :meth:`__init__` method.
        """
        self._stabilizedTransient = stabilizedTransient

    def setComputedTimeStep(self, dt):
        """ Set time-step size returned by :meth:`computeTimeStep`.

        Parameters
        ----------
        dt : float
            Time-step size returned by :meth:`computeTimeStep`. None can be set to use the time step
            recommended by the hold :class:`.PhysicsDriver`. Default: None.
        """
        self._macrodt = dt

    def initialize(self):
        """ See :meth:`.PhysicsDriver.initialize`. """
        self._timeDifference = 0.
        self._afterAbort = False
        self._physics.init()
        return self._physics.getInitStatus()

    def terminate(self):
        """ See :meth:`.PhysicsDriver.terminate`. """
        if self._saveParameters is not None:
            try:
                self._physics.forget(*self._saveParameters)
            except:
                pass
        self._physics.term()

    def presentTime(self):
        """ See :meth:`.PhysicsDriver.presentTime`. """
        return self._physics.presentTime() - self._timeDifference

    def computeTimeStep(self):
        """ See :meth:`.PhysicsDriver.computeTimeStep`.

        Return the asked macro time step if set (by ``setValue("macrodt", dt)``), the preferred time
        step of the :class:`.PhysicsDriver` otherwise.
        """
        (dtPhysics, stop) = self._physics.computeTimeStep()
        if self._macrodt is not None:
            dtPhysics = self._macrodt
        return (dtPhysics, stop)

    def initTimeStep(self, dt):
        """ See :meth:`.PhysicsDriver.initTimeStep`. """
        self._dt = dt
        if self._dt <= 0 and not self._stabilizedTransient[0]:
            return self._physics.initTimeStep(dt)
        if self._dt == 0 and self._stabilizedTransient[0] and not self.getStationaryMode():
            raise AssertionError("TimeAccumulator.initTimeStep : Stationary mode must be activated (setStationaryMode(True)) in order to use a stabilized transient to reach a steady state solution.")
        if self._saveParameters is not None:
            if self._savingMode == SaveAtInitTimeStep.always or (not self.getStationaryMode() and
                                                                 (self._savingMode == SaveAtInitTimeStep.transient or (not self._afterAbort and self._savingMode == SaveAtInitTimeStep.transientExceptAfterAbort))):
                self._physics.save(*self._saveParameters)
        return True

    def solveTimeStep(self):
        """ Make the :class:`.PhysicsDriver` to reach the end of the macro time step asked to
        :class:`.TimeAccumulator` using its own time advance procedure.
        """
        timeInit = self._physics.presentTime()
        if self._dt > 0.:
            self._physics.solveTransient(timeInit + self._dt, finishAtTmax=True)
            self._timeDifference += self._physics.presentTime() - timeInit
            return abs(self._timeDifference - self._dt) < 1.E-8 * self._dt
        if self._stabilizedTransient[0]:
            self._physics.solveTransient(timeInit + self._stabilizedTransient[1], stopIfStationary=True)
            self.resetTime(timeInit)
            return self.isStationary()
        self._physics.solve()
        return self._physics.getSolveStatus()

    def validateTimeStep(self):
        """ See :meth:`.PhysicsDriver.validateTimeStep`. """
        if self._dt <= 0 and not self._stabilizedTransient[0]:
            self._physics.validateTimeStep()
        self._dt = None
        self._timeDifference = 0.
        self._afterAbort = False

    def abortTimeStep(self):
        """ See :meth:`.PhysicsDriver.abortTimeStep`. """
        if not self.getStationaryMode():
            if self._saveParameters is not None and self._savingMode != SaveAtInitTimeStep.never:
                self._physics.restore(*self._saveParameters)
            else:
                raise Exception("TimeAccumulator.abortTimeStep : not available in transient mode without saveParameters.")
        elif self._saveParameters is not None and self._savingMode == SaveAtInitTimeStep.always:
            self._physics.restore(*self._saveParameters)
        else:
            self._physics.abortTimeStep()
        self._dt = None
        self._timeDifference = 0.
        self._afterAbort = True

    def getInputValuesNames(self):
        """ See :meth:`.c3po.DataAccessor.DataAccessor.getInputValuesNames`. """
        return self._physics.getInputValuesNames() + ["macrodt"]

    def getValueType(self, name):
        """ See :meth:`.c3po.DataAccessor.DataAccessor.getValueType`. """
        if name == "macrodt":
            return "Double"
        return self._physics.getValueType(name)

    def getValueUnit(self, name):
        """ See :meth:`.c3po.DataAccessor.DataAccessor.getValueUnit`. """
        if name == "macrodt":
            return "s"
        return self._physics.getValueUnit(name)

    def setInputDoubleValue(self, name, value):
        """ See :meth:`.c3po.DataAccessor.DataAccessor.setInputDoubleValue`.

        The value associated with the name "macrodt" can be used to set the time-step size returned
        by :meth:`computeTimeStep`.
        """
        if name == "macrodt":
            warning('setInputDoubleValue("macrodt", value) is deprecated and will soon by deleted. '
                    + "Please use setComputedTimeStep(dt).")
            self._macrodt = value
        else:
            self._physics.setInputDoubleValue(name, value)
