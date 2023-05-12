# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import time


class TransientLogger(ABC):
    """! TransientLogger is a class which follows transient.
    """

    @abstractmethod
    def init(self, driver, tmax, presentTime):
        """Method called before transient starts.

        Parameters
        ----------
        driver : c3po.PhysicsDriver
            PhysicsDriver calling ``solveTransient``.
        tmax : float
            ``tmax`` given to ``solveTransient``.
        presentTime : float
            Present time when calling ``solveTransient``.
        """
        raise NotImplementedError

    @abstractmethod
    def abort(self, dt, dt2, stop, presentTime):
        """Method when time step is aborted.

        Parameters
        ----------
        dt : float
            Time step failed.
        dt2 : float
            ``dt``value returned by ``computeTimeStep`` adter ``abortTimeStep``.
        stop : bool
            ``stop``value returned by ``computeTimeStep`` adter ``abortTimeStep``.
        presentTime : float
            Present time after calling ``abortTimeStep``.
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self, dt, presentTime):
        """Method when time step is validated.

        Parameters
        ----------
        dt : float
            Time step achieved.
        presentTime : float
            Present time after calling ``validateTimeStep``.
        """
        raise NotImplementedError

    @abstractmethod
    def terminate(self, presentTime):
        """Method called after the transient.

        Parameters
        ----------
        presentTime : float
            Present time after the transient.
        """
        raise NotImplementedError


class NoLog(TransientLogger):

    def init(self, driver, tmax, presentTime):
        """Just pass"""
        pass

    def abort(self, dt, dt2, stop, presentTime):
        """Just pass"""
        pass

    def validate(self, dt, presentTime):
        """Just pass"""
        pass

    def terminate(self, presentTime):
        """Just pass"""
        pass


class FinalTimeEstimator(TransientLogger):
    """! TransientLogger which estimates the duration of the transient
    with Exponential Moving Average.
    """
    def __init__(self, relaxation = 0.3, level = 1) -> None:
        """Constructor.

        Parameters
        ----------
        relaxation : float, optional
            Relaxation factor for the moving average, by default 0.3
        level : int, optional
            The print level during iterations (0=None, 1 keeps last iteration, 2 prints every iteration).
        """

        self._relaxation = min(1.0, relaxation)
        self._level = level

        self._name = __class__.__name__
        self._initialTime = 0.0
        self._tmax = 1e30

        self._simu_rate = 0.0
        self._real_t0 = 0.0
        self._total_abort = 0
        self._step_abort = 0

        self._dt_range = (1.e30, 0.0)
        self._ert = 1e30

    def init(self, driver, tmax, presentTime):
        """See ``TransientLogger.init``"""

        self._name = driver.__class__.__name__
        self._initialTime = presentTime
        self._tmax = tmax

        self._simu_rate = None
        self._real_t0 = time.perf_counter()
        self._total_abort = 0
        self._step_abort = 0

        self._dt_range = (1.e30, 0.0)
        self._ert = 1e30

        self._print_level("{}: starts transient".format(self._name))

    def abort(self, dt, dt2, stop, presentTime):
        """See ``TransientLogger.abort``"""

        if self._level > 0:
            print("{}: abort at {:9.3e}s{}, failed dt = {:9.3e}s, new dt = {:9.3e}s, stop = {}".format(
                self._name, presentTime, "\U0001F614", dt, dt2, stop))
        self._step_abort += 1

    def _getProgression(self, presentTime):
        return (presentTime - self._initialTime) / (self._tmax - self._initialTime) * 100.0

    def _getProgressionStr(self, presentTime):
        return ( "{}: transient simulation time = {:9.3e}s ({:6.2f} %)".format(
            self._name, presentTime, self._getProgression(presentTime)))

    def _getEstimatedRemainingTime(self, dt, presentTime):
        real_t1 = time.perf_counter()
        simu_rate = (real_t1 - self._real_t0) / dt
        self._real_t0 = real_t1
        if self._simu_rate is None:
            self._simu_rate = simu_rate
        self._simu_rate = simu_rate * self._relaxation + self._simu_rate * (1. - self._relaxation)
        return self._simu_rate * (self._tmax - presentTime)

    def validate(self, dt, presentTime):
        """See ``TransientLogger.validate``"""

        self._dt_range = (min(dt, self._dt_range[0]), max(dt, self._dt_range[1]))
        to_print = (self._getProgressionStr(presentTime) +
                    ", dt = {:9.3e}s (#aborts={}{})".format(
                        dt, self._step_abort, "\U0001F928" if self._step_abort else ""))
        if self._level > 0:
            ert0 = self._ert
            self._ert = self._getEstimatedRemainingTime(dt=dt, presentTime=presentTime)
            if self._ert > 1.e-3:
                to_print += ", estimated final time {} {} {}".format(
                    (datetime.now() +
                        timedelta(seconds=int(self._ert))).strftime('%Y-%m-%d %H:%M:%S'),
                    "↗" if ert0 < self._ert else "↘",
                    "\U0001F634" if self._getProgression(presentTime) < 80.0 else "\U0001F600")
        self._print_level(to_print)
        self._total_abort += self._step_abort
        self._step_abort = 0

    def terminate(self, presentTime):
        """See ``TransientLogger.terminate``"""

        self._print_level("{}, total #aborts = {}, dt range = {}s.\U0001F973".format(
            self._getProgressionStr(presentTime), self._total_abort, self._dt_range))

    def _print_level(self, to_print):
        if self._level == 1:
            print("\x1b[80D\x1b[1A\x1b[K{}".format(to_print))
        elif self._level >= 2:
            print(to_print)
