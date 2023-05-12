# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class PhysicsDriver. """
from __future__ import print_function, division

from c3po.DataAccessor import DataAccessor
from c3po.services.TransientLogger import NoLog


class PhysicsDriver(DataAccessor):
    """! PhysicsDriver is an abstract class which standardizes the functionalities expected by computer codes.

    It follows the ICoCo (Interface for Code Coupling) V2 standard.
    The ICoCo V2 I/O (in/out) methods are defined in the mother class DataAccessor.

    ICoCo V2 is originally defined for C++ here: https://github.com/cea-trust-platform/icoco-coupling.
    PhysicsDriver (together with DataAccessor) can be seen as the translation in Python of ICoCo V2.

    In order to use a code with C3PO it is necessary to define a class that inherits from PhysicsDriver and to overload
    needed methods (including the ones of DataAccessor).
    Note that not all the methods need to be implemented! Mandatory methods are marked as such.

    Some of the methods may not be called when some conditions are not met (i.e. when not in the correct context). Thus
    in this documentation we define the "TIME_STEP_DEFINED context" as the context that the code finds itself, when the method
    initTimeStep() has been called, and the method validateTimeStep() (or abortTimeStep()) has not yet been called.
    This is the status in which the current computation time step is well defined.

    Within the computation of a time step (so within TIME_STEP_DEFINED), the temporal semantic of the fields (and
    scalar values) is not imposed by the norm. Said differently, it does not require the fields to be defined at the
    start/middle/end of the current time step, this semantic must be agreed on between the codes being coupled.
    Fields and scalar values that are set within the TIME_STEP_DEFINED context are invalidated (undefined behavior)
    after a call to validateTimeStep() (or abortTimeStep()). They need to be set at each time step. However, fields and scalar
    values that are set outside of this context (before the first time step for example, or after the resolution of the last
    time step) are permanent (unless modified afterward within the TIME_STEP_DEFINED context).
    """

    def __init__(self):
        """! Default constructor.

        Internal set up and initialization of the code should not be done here, but rather in initialize().
        """
        self._initStatus = True
        self._solveStatus = True
        self._iterateStatus = (True, True)
        self._initNb = 0

        self._transientLogger = NoLog()

    @staticmethod
    def GetICoCoMajorVersion():  # pylint: disable=invalid-name
        """! (Mandatory) Return ICoCo interface major version number.

        @return (int) ICoCo interface major version number (2 at present)
        """
        return 2

    def getMEDCouplingMajorVersion(self):
        """! (Optional) Get MEDCoupling major version, if the code was built with MEDCoupling support.

        Mandatory if the code is built with MEDCoupling support.
        This can be used to assess compatibility between codes when coupling them.

        @return (int) the MEDCoupling major version number (typically 7, 8, 9, ...).
        """
        raise NotImplementedError

    def isMEDCoupling64Bits(self):
        """! (Optional) Indicate whether the code was built with a 64-bits version of MEDCoupling.

        Mandatory if the code is built with MEDCoupling support.
        This can be used to assess compatibility between codes when coupling them.

        @return (bool) True if the code was built with a 64-bits version of MEDCoupling.
        """
        raise NotImplementedError

    def setDataFile(self, datafile):
        """! (Optional) Provide the relative path of a data file to be used by the code.

        This method must be called before initialize().

        @param datafile (string) relative path to the data file.
        @throws AssertionError if called multiple times or after initialize().
        @throws ValueError if an invalid path is provided.
        """
        raise NotImplementedError

    def setMPIComm(self, mpicomm):
        """! (Optional) Provide the MPI communicator to be used by the code for parallel computations.

        This method must be called before initialize(). The communicator should include all the processes
        to be used by the code. For a sequential code, the call to setMPIComm is optional or mpicomm should be None.

        @param mpicomm (mpi4py.Comm) mpi4py communicator.
        @throws AssertionError if called multiple times or after initialize().
        """
        raise NotImplementedError

    def init(self):
        """! This is a recommanded wrapper for initialize().

        It works with term() in order to guarantee that initialize() and terminate() are called only once:
            - initialize() is called at the first call of init().
            - terminate() is called when the number of calls to term() is equal to the number of calls to init().

        init() also stores the return value of initialize() instead of returning it. The output is accessible with getInitStatus().

        @warning This method, in association with getInitStatus(), should always be used inside C3PO instead of initialize()
        which is not adapted to MPI Master-Workers paradigm.
        @warning This method should never be redefined: define initialize() instead!
        """
        if self._initNb == 0:
            self._initStatus = self.initialize()
        self._initNb += 1

    def getInitStatus(self):
        """! Return the output status of the last call to initialize() made through init().

        @return (bool) True if all OK, otherwise False.

        @warning This method, in association with init(), should always be used inside C3PO instead of initialize() which
        is not adapted to MPI Master-Workers paradigm.
        @warning This method should never be redefined: define initialize() instead!
        """
        return self._initStatus

    def initialize(self):
        """! (Mandatory) Initialize the current problem instance.

        In this method the code should allocate all its internal structures and be ready to execute. File reads, memory
        allocations, and other operations likely to fail should be performed here, and not in the constructor (and not in
        the setDataFile() or in the setMPIComm() methods either).
        This method must be called only once (after a potential call to setMPIComm() and/or setDataFile()) and cannot be
        called again before terminate() has been performed.

        @return (bool) True if all OK, otherwise False.
        @throws AssertionError if called multiple times.

        @warning This method is not adapted to MPI Master-Workers paradigm. init() and getInitStatus() methods should
        be used in C3PO instead.
        """
        raise NotImplementedError

    def term(self):
        """! This is a recommanded wrapper for terminate().

        It works with init() in order to guarantee that initialize() and terminate() are called only once:
            - initialize() is called at the first call of init().
            - terminate() is called when the number of calls to term() is equal to the number of calls to init().

        @warning This method should be used inside C3PO instead of terminate().
        @warning This method should never be redefined: define terminate() instead!
        """
        self._initNb = self._initNb - 1 if self._initNb > 0 else 0
        if self._initNb <= 0:
            self.terminate()

    def terminate(self):
        """! (Mandatory) Terminate the current problem instance and release all allocated resources.

        Terminate the computation, free the memory and save whatever needs to be saved. This method is called once
        at the end of the computation or after a non-recoverable error.
        No other ICoCo method except setDataFile(), setMPIComm() and initialize() may be called after this.

        @throws AssertionError if called before initialize() or after terminate().
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        """
        raise NotImplementedError

    def getInitNb(self):
        """! Return the number of times init() has been called but not term().

        This method is made to work with the wrappers init() and term(). It indicates the number of term() that are
        still needed to trigger terminate().

        @return (int) The number of times init() has been called but not term().
        """
        return self._initNb

    def presentTime(self):
        """! (Mandatory) Return the current time of the simulation.

        Can be called any time between initialize() and terminate().
        The current time can only change during a call to validateTimeStep() or to resetTime().

        @return (float) the current (physical) time of the simulation.
        @throws AssertionError if called before initialize() or after terminate().
        """
        raise NotImplementedError

    def computeTimeStep(self):
        """! (Mandatory) Return the next preferred time step (time increment) for this code, and whether the code
        wants to stop.

        Both data are only indicative, the supervisor is not required to take them into account. This method is
        however marked as mandatory, since most of the coupling schemes expect the code to provide this
        information (those schemes then typically compute the minimum of the time steps of all the codes being coupled).
        Hence a possible implementation is to return a huge value, if a precise figure can not be computed.

        Can be called whenever the code is outside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).

        @return (float, bool) a tuple (dt, stop).
        dt is the preferred time step for this code (only valid if stop is False).
        stop is True if the code wants to stop. It can be used for example to indicate that, according to
        a certain criterion, the end of the transient computation is reached from the code point of view.
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        @throws AssertionError if called before initialize() or after terminate().
        """
        raise NotImplementedError

    def initTimeStep(self, dt):
        """! (Mandatory) Provide the next time step (time increment) to be used by the code.

        After this call (if successful), the computation time step is defined to ]t, t + dt] where t is the value
        returned by presentTime(). The code enters the TIME_STEP_DEFINED context.
        A time step = 0. may be used when the stationaryMode is set to True for codes solving directly for
        the steady-state.

        @param dt (float) the time step to be used by the code.
        @return (bool) False means that given time step is not compatible with the code time scheme.
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        @throws AssertionError if called before initialize() or after terminate().
        @throws ValueError if dt is invalid (dt < 0.0).
        """
        raise NotImplementedError

    def solve(self):
        """! Call solveTimeStep() but store its return value instead of returning it.
        The output is accessible with getSolveStatus().

        @warning This method, in association with getSolveStatus(), should always be used inside C3PO instead of
        solveTimeStep(). They fit better with MPI use.
        @warning This method should never be redefined: define solveTimeStep() instead!
        """
        self._solveStatus = self.solveTimeStep()

    def getSolveStatus(self):
        """! Return the output of the last call to solveTimeStep() made through solve().

        @return (bool) True if computation was successful, False otherwise.

        @warning This method, in association with solve(), should always be used inside C3PO instead of solveTimeStep().
        They fit better with MPI use.
        @warning This method should never be redefined: define solveTimeStep() instead!
        """
        return self._solveStatus

    def solveTimeStep(self):
        """! (Mandatory) Perform the computation on the current time interval.

        Can be called whenever the code is inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).

        @return (bool) True if computation was successful, False otherwise.
        @throws AssertionError if called outside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        @throws AssertionError if called several times without a call to validateTimeStep() or to abortTimeStep().

        @warning This method is not adapted to MPI Master-Workers paradigm. solve() and getSolveStatus() methods should be
        used with C3PO instead.
        """
        raise NotImplementedError

    def validateTimeStep(self):
        """! (Mandatory) Validate the computation performed by solveTimeStep().

        Can be called whenever the code is inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        After this call:
        - the present time has been advanced to the end of the computation time step
        - the computation time step is undefined (the code leaves the TIME_STEP_DEFINED context).

        @throws AssertionError if called outside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        @throws AssertionError if called before the solveTimeStep() method.
        """
        raise NotImplementedError

    def setStationaryMode(self, stationaryMode):
        """! (Mandatory) Set whether the code should compute a stationary solution or a transient one.

        New in version 2 of ICoCo. By default the code is assumed to be in stationary mode False (i.e. set up
        for a transient computation).
        If set to True, solveTimeStep() can be used either to solve a time step in view of an asymptotic solution,
        or to solve directly for the steady-state. In this last case, a time step = 0. can be used with initTimeStep()
        (whose call is always needed).
        The stationary mode status of the code can only be modified by this method (or by a call to terminate()
        followed by initialize()).

        Can be called whenever the code is outside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).

        @param stationaryMode (bool) True if the code should compute a stationary solution.
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        @throws AssertionError if called before initialize() or after terminate().
        """
        raise NotImplementedError

    def getStationaryMode(self):
        """! (Mandatory) Indicate whether the code should compute a stationary solution or a transient one.

        See also setStationaryMode().

        Can be called whenever the code is outside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).

        @return (bool) True if the code has been set to compute a stationary solution.
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        @throws AssertionError if called before initialize() or after terminate().
        """
        raise NotImplementedError

    def isStationary(self):
        """! (Optional) Return whether the solution is constant on the computation time step.

        Used to know if the steady-state has been reached. This method can be called whenever the computation time step
        is not defined.

        @return (bool) True if the solution is constant on the computation time step.
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation),
        meaning we shouldn't request this information while the computation of a new time step is in progress.
        @throws AssertionError if called before initialize() or after terminate().
        """
        raise NotImplementedError

    def abortTimeStep(self):
        """! (Optional) Abort the computation on the current time step.

        Can be called whenever the computation time step is defined, instead of validateTimeStep().
        After this call, the present time is left unchanged, and the computation time step is undefined
        (the code leaves the TIME_STEP_DEFINED context).

        @throws AssertionError if called outside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        """
        raise NotImplementedError

    def resetTime(self, time_):
        """! (Optional) Reset the current time of the PhysicsDriver to a given value.

        New in version 2 of ICoCo.
        Particularly useful for the initialization of complex transients: the starting point of the transient
        of interest is computed first, the time is reset to 0, and then the actual transient of interest starts with proper
        initial conditions, and global time 0.

        Can be called outside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).

        @param time_ (float) the new current time.
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).
        @throws AssertionError if called before initialize() or after terminate().
        """
        raise NotImplementedError

    def iterate(self):
        """! Call iterateTimeStep() but store its return value instead of returning it.
        The output is accessible with getIterateStatus().

        @warning This method, in association with getIterateStatus(), should always be used inside C3PO instead
        of iterateTimeStep(). They fit better with MPI use.
        @warning This method should never be redefined: define iterateTimeStep() instead!
        """
        self._iterateStatus = self.iterateTimeStep()

    def getIterateStatus(self):
        """! Return the output of the last call to iterateTimeStep() made through iterate().

        @return (bool, bool) a tuple (succeed, converged).
        succeed = False if the computation fails.
        converged = True if the solution is not evolving any more.

        @warning This method, in association with iterate(), should always be used inside C3PO instead of iterateTimeStep().
        They fit better with MPI use.
        @warning This method should never be redefined: define iterateTimeStep() instead!
        """
        return self._iterateStatus

    def iterateTimeStep(self):
        """! (Optional) Perform a single iteration of computation inside the time step.

        This method is relevant for codes having inner iterations for the computation of a single time step.
        Calling iterateTimeStep() until converged is True is equivalent to calling solveTimeStep(), within the code's
        convergence threshold.
        Can be called (potentially several times) inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).

        @return (bool, bool) a tuple (succeed, converged).
        succeed = False if the computation fails.
        converged = True if the solution is not evolving any more.
        @throws AssertionError if called outside the TIME_STEP_DEFINED context (see PhysicsDriver documentation).

        @warning This method is not adapted to MPI Master-Workers paradigm.
        iterate() and getIterateStatus() methods should be used with C3PO instead.
        """
        raise NotImplementedError

    def save(self, label, method):
        """! (Optional) Save the state of the code.

        The saved state is identified by the combination of label and method arguments.
        If save() has already been called with the same two arguments, the saved state is overwritten.

        @param label (int) a user- (or code-) defined value identifying the state.
        @param method (string) a string specifying which method is used to save the state of the code. A code can provide
        different methods (for example in memory, on disk, etc.).
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation),
        meaning we shouldn't save a previous time step while the computation of a new time step is in progress.
        @throws AssertionError if called before initialize() or after terminate().
        @throws ValueError if the method or label argument is invalid.
        """
        raise NotImplementedError

    def restore(self, label, method):
        """! (Optional) Restore the state of the code.

        After restore, the code should behave exactly like after the corresponding call to save (except of course for
        save/restore methods, since the list of saved states may have changed).
        The state to be restored is identified by the combination of label and method arguments.
        The save() method must have been called at some point or in some previous run with this combination.

        @param label (int) a user- (or code-) defined value identifying the state.
        @param method (string) a string specifying which method was used to save the state of the code. A code can provide
        different methods (for example in memory, on disk, etc.).
        @throws AssertionError if called inside the TIME_STEP_DEFINED context (see PhysicsDriver documentation),
        meaning we shouldn't restore a previous time step while the computation of a new time step is in progress.
        @throws AssertionError if called before initialize() or after terminate().
        @throws ValueError if the method or label argument is invalid.
        """
        raise NotImplementedError

    def forget(self, label, method):
        """! (Optional) Discard a previously saved state of the code.

        After this call, the save-point cannot be restored anymore. This method can be used to free the space occupied by
        unused saved states.

        @param label (int) a user- (or code-) defined value identifying the state.
        @param method (string) a string specifying which method was used to save the state of the code. A code can provide
        different methods (for example in memory, on disk, etc.).
        @throws AssertionError if called before initialize() or after terminate().
        @throws ValueError if the method or label argument is invalid.
        """
        raise NotImplementedError

    def setTransientLogger(self, transientLogger):
        """! Defines the logger for solveTransient method.

        @param transientLogger (services.TransientLogger.TransientLogger) logger instance.
        """
        self._transientLogger = transientLogger

    def solveTransient(self, tmax, finishAtTmax=False, stopIfStationary=False):
        """! Make the PhysicsDriver to advance in time until it reaches the time tmax or it asks to stop.

        The PhysicsDriver can ask to stop either with computeTimeStep() (always checked) or with isStationary() (only if stopIfStationary is set to True).

        @param tmax (float) maximum time to be reached (compared with presentTime()).
        @param finishAtTmax (bool) if set to True, the method ends with time = tmax (instead of time >= tmax).
        In case the PhysicsDriver asks to stop before tmax is reached, resetTime(tmax) is called.
        @param stopIfStationary (bool) if set to True, the method stops also if isStationary() returns True.
        """
        self._transientLogger.init(driver=self, tmax=tmax, presentTime=self.presentTime())

        (dt, stop) = self.computeTimeStep()
        while (self.presentTime() < tmax - 1.E-8 * min(tmax, dt) and not stop):
            if finishAtTmax:
                if self.presentTime() + 1.5 * dt >= tmax:
                    if self.presentTime() + dt >= tmax - dt * 1.E-4:
                        dt = tmax - self.presentTime()
                    else:
                        dt = 0.5 * (tmax - self.presentTime())
            self.initTimeStep(dt)
            self.solve()
            ok = self.getSolveStatus()
            if ok:
                self.validateTimeStep()
                self._transientLogger.validate(dt=dt, presentTime=self.presentTime())
                (dt, stop) = self.computeTimeStep()
                if stopIfStationary:
                    stop = stop or self.isStationary()
            else:
                self.abortTimeStep()
                (dt2, stop) = self.computeTimeStep()
                self._transientLogger.abort(dt, dt2, stop, self.presentTime())
                if dt == dt2:
                    raise Exception("PhysicsDriver.solveTransient : we are about to repeat a failed time-step calculation !")
                dt = dt2
        if stop and finishAtTmax:
            self.resetTime(tmax)

        self._transientLogger.terminate(presentTime=self.presentTime())
