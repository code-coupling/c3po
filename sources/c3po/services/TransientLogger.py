# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class TransientLogger and its daughters Timekeeper and FortuneTeller. """
from __future__ import print_function, division
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import time

from c3po.services.Printer import Printer


class TransientLogger(object):
    """! TransientLogger is the base class for the production of transient logging strings. """
    __metaclass__ = ABCMeta

    @abstractmethod
    def initTransient(self, driver, tmax, finishAtTmax, stopIfStationary, presentTime):
        """! Method called before transient starts.

        @param driver (c3po.PhysicsDriver.PhysicsDriver) The caller of solveTransient().
        @param tmax (float) tmax argument given to solveTransient().
        @param finishAtTmax (bool) finishAtTmax argument given to solveTransient().
        @param stopIfStationary (bool) stopIfStationary argument given to solveTransient().
        @param presentTime (float) Present time when calling solveTransient().
        """
        raise NotImplementedError

    @abstractmethod
    def logAbort(self, dt, presentTime):
        """! Method called when time step is aborted.

        @param dt (float) Size of the failed time step.
        @param presentTime (float) Present time after calling abortTimeStep().
        """
        raise NotImplementedError

    @abstractmethod
    def logValidate(self, dt, presentTime):
        """! Method called when time step is validated.

        @param dt (float) Size of the validated time step.
        @param presentTime (float) Present time after calling validateTimeStep().
        """
        raise NotImplementedError

    @abstractmethod
    def terminateTransient(self, presentTime, stop, isStationary):
        """! Method called after the transient ends.

        @param presentTime (float) Present time after the transient.
        @param stop (bool) Indicate if the transient ends because of a stopping criteria.
        @param isStationary (bool) Indicate if the stopping criteria is due to isStationary().
        """
        raise NotImplementedError


class Timekeeper(TransientLogger):
    """! TransientLogger which provides information about transient progress. """

    def __init__(self):
        self._name = ""
        self._initialTime = 0.0
        self._tmax = 1e30
        self._totalAbort = 0
        self._stepAbort = 0
        self._dtRange = (1.e30, 0.0)

    def initTransient(self, driver, tmax, finishAtTmax, stopIfStationary, presentTime):
        """! See ``TransientLogger.initTransient``"""
        self._name = driver.__class__.__name__
        self._initialTime = presentTime
        self._tmax = tmax
        self._totalAbort = 0
        self._stepAbort = 0
        self._dtRange = (1.e30, 0.0)
        return "{}: transient starts at {:9.3e}s, finishAtTmax = {}, stopIfStationary = {}".format(self._name, presentTime, finishAtTmax, stopIfStationary)

    def logAbort(self, dt, presentTime):
        """! See ``TransientLogger.logAbort``"""
        self._stepAbort += 1
        return "{}: abort at {:9.3e}s, failed dt = {:9.3e}s".format(
            self._name, presentTime, dt)

    def _getProgressionStr(self, presentTime):
        """! INTERNAL """
        return "{:9.3e}s".format(presentTime)

    def logValidate(self, dt, presentTime):
        """! See ``TransientLogger.logValidate``"""
        self._dtRange = (min(dt, self._dtRange[0]), max(dt, self._dtRange[1]))
        toPrint = ("{}: validate at {}, dt = {:9.3e}s (#aborts={})".format(
            self._name, self._getProgressionStr(presentTime), dt, self._stepAbort))

        self._totalAbort += self._stepAbort
        self._stepAbort = 0
        return toPrint

    def terminateTransient(self, presentTime, stop, isStationary):
        """! See ``TransientLogger.terminateTransient``"""
        stopReason = "tmax is reached" if not stop else ("stationary is found" if isStationary else "computeTimeStep asks to stop")
        toPrint = "{}: transient ends at {} because {}. Total #aborts = {}, dt range = {}s.".format(
            self._name, self._getProgressionStr(presentTime), stopReason, self._totalAbort, self._dtRange)
        return toPrint


class FortuneTeller(Timekeeper):
    """! Timekeeper which estimates in addition the duration of the transient
    with Exponential Moving Average.
    """

    def __init__(self, relaxation=0.3):
        """! Build a FortuneTeller object.

        @param relaxation (float) Relaxation factor for the Exponential Moving Average. Default: 0.3.
        """
        Timekeeper.__init__(self)
        self._relaxation = min(1.0, relaxation)
        self._simuRate = 0.0
        self._realT0 = 0.0
        self._ert = 1e30

    def initTransient(self, driver, tmax, finishAtTmax, stopIfStationary, presentTime):
        """! See ``TransientLogger.initTransient``"""
        self._simuRate = None
        self._realT0 = time.time()
        self._ert = 1e30
        return Timekeeper.initTransient(self, driver, tmax, finishAtTmax, stopIfStationary, presentTime)

    def _getProgression(self, presentTime):
        """! INTERNAL """
        return min(1., (presentTime - self._initialTime) / (self._tmax - self._initialTime)) * 100.0

    def _getProgressionStr(self, presentTime):
        """! INTERNAL """
        return Timekeeper._getProgressionStr(self, presentTime) + " ({:6.2f} %)".format(
            self._getProgression(presentTime))

    def _getEstimatedRemainingTime(self, dt, presentTime):
        """! INTERNAL """
        realT1 = time.time()
        simuRate = (realT1 - self._realT0) / dt
        self._realT0 = realT1
        if self._simuRate is None:
            self._simuRate = simuRate
        self._simuRate = simuRate * self._relaxation + self._simuRate * (1. - self._relaxation)
        return self._simuRate * (self._tmax - presentTime)

    def logValidate(self, dt, presentTime):
        """! See ``TransientLogger.logValidate``"""
        toPrint = Timekeeper.logValidate(self, dt, presentTime)
        self._ert = self._getEstimatedRemainingTime(dt=dt, presentTime=presentTime)
        if self._ert > 1.e-3:
            toPrint += ", estimated final time {}".format(
                (datetime.now() +
                 timedelta(seconds=int(self._ert))).strftime('%Y-%m-%d %H:%M:%S'))
        return toPrint


class TransientPrinter(object):
    """! INTERNAL.

    TransientPrinter writes information about transient in the standard output. """

    def __init__(self, transientLogger):
        """! Build a TransientPrinter object.

        @param transientLogger (c3po.services.TransientLogger.TransientLogger) The TransientLogger object to use.
        """
        self._printer = Printer(0)
        self._logger = transientLogger

    def initTransient(self, driver, tmax, finishAtTmax, stopIfStationary, presentTime):
        """! See TransientLogger.initTransient. """
        if self._printer.getPrintLevel() > 0:
            self._printer.print(self._logger.initTransient(driver, tmax, finishAtTmax, stopIfStationary, presentTime), tmplevel=2)

    def logAbort(self, dt, presentTime):
        """! See TransientLogger.logAbort. """
        if self._printer.getPrintLevel() > 0:
            self._printer.print(self._logger.logAbort(dt, presentTime))

    def logValidate(self, dt, presentTime):
        """! See TransientLogger.logValidate. """
        if self._printer.getPrintLevel() > 0:
            self._printer.print(self._logger.logValidate(dt, presentTime))

    def terminateTransient(self, presentTime, stop, isStationary):
        """! See TransientLogger.terminateTransient. """
        if self._printer.getPrintLevel() > 0:
            self._printer.print(self._logger.terminateTransient(presentTime, stop, isStationary), tmplevel=2)

    def getPrinter(self):
        """! Return the Printer object used.

        @return (c3po.services.Printer.Printer) the Printer object used.
        """
        return self._printer

    def setLogger(self, transientLogger):
        """! Set a new TransientLogger object.

        @param transientLogger (c3po.services.TransientLogger.TransientLogger) The TransientLogger object to use.
        """
        self._logger = transientLogger

    def getLogger(self):
        """! Return the TransientLogger object used.

        @return (c3po.services.TransientLogger.TransientLogger) The used TransientLogger object.
        """
        return self._logger
