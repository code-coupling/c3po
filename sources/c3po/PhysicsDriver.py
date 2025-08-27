# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class :class:`.PhysicsDriver`. """
from __future__ import print_function, division

from c3po.DataAccessor import DataAccessor
from c3po.services.TransientLogger import Timekeeper, TransientPrinter


class PhysicsDriver(DataAccessor):
    """:class:`.PhysicsDriver` is an abstract class which standardizes the functionalities expected by computer codes.

    It follows the ICoCo (Interface for Code Coupling) V2 standard.
    The ICoCo V2 I/O (in/out) methods are defined in the mother class :class:`.DataAccessor`.

    ICoCo V2 is originally defined for C++ here: https://github.com/cea-trust-platform/icoco-coupling.
    :class:`.PhysicsDriver` (together with :class:`.DataAccessor`) can be seen as the translation in Python of ICoCo V2.

    In order to use a code with C3PO it is necessary to define a class that inherits from
    :class:`.PhysicsDriver` and to overload needed methods (including the ones of :class:`.DataAccessor`).
    Note that not all the methods need to be implemented! Mandatory methods are marked as such.

    Some of the methods may not be called when some conditions are not met (i.e. when not in the correct context). Thus
    in this documentation we define the "``TIME_STEP_DEFINED`` context"
    as the context that the code finds itself, when the method :meth:`initTimeStep` has been called, and the method
    :meth:`validateTimeStep` (or :meth:`abortTimeStep`) has not yet been called.
    This is the status in which the current computation time step is well defined.

    Within the computation of a time step (so within ``TIME_STEP_DEFINED``), the temporal semantic of the fields (and
    scalar values) is not imposed by the norm. Said differently, it does not require the fields to be defined at the
    start/middle/end of the current time step, this semantic must be agreed on between the codes being coupled.
    Fields and scalar values that are set within the ``TIME_STEP_DEFINED`` context are invalidated (undefined behavior)
    after a call to :meth:`validateTimeStep` (or :meth:`abortTimeStep`).
    They need to be set at each time step. However, fields and scalar values that are set outside of this context
    (before the first time step for example, or after the resolution of the last time step) are permanent
    (unless modified afterward within the ``TIME_STEP_DEFINED`` context).
    """

    def __init__(self):
        """ Default constructor.

        Internal set up and initialization of the code should not be done here, but rather in :meth:`initialize`.
        """
        self._initStatus = True
        self._solveStatus = True
        self._iterateStatus = (True, True)
        self._initNb = 0

        self._transientPrinter = TransientPrinter(Timekeeper())

    @staticmethod
    def GetICoCoMajorVersion():  # pylint: disable=invalid-name
        """ (Mandatory) Return ICoCo interface major version number.

        Returns
        -------
        int
            ICoCo interface major version number (2 at present)
        """
        return 2

    def getMEDCouplingMajorVersion(self):
        """ (Optional) Get MEDCoupling major version, if the code was built with MEDCoupling support.

        Mandatory if the code is built with MEDCoupling support.
        This can be used to assess compatibility between codes when coupling them.

        Returns
        -------
        int
            The MEDCoupling major version number (typically 7, 8, 9, ...).
        """
        raise NotImplementedError

    def isMEDCoupling64Bits(self):
        """ (Optional) Indicate whether the code was built with a 64-bits version of MEDCoupling.

        Mandatory if the code is built with MEDCoupling support.
        This can be used to assess compatibility between codes when coupling them.

        Returns
        -------
        bool
            True if the code was built with a 64-bits version of MEDCoupling.
        """
        raise NotImplementedError

    def setDataFile(self, datafile):
        """ (Optional) Provide the relative path of a data file to be used by the code.

        This method must be called before :meth:`initialize`.

        Parameters
        ----------
        datafile : str
            Relative path to the data file.

        Raises
        ------
        AssertionError
            If called multiple times or after :meth:`initialize`.
        ValueError
            If an invalid path is provided.
        """
        raise NotImplementedError

    def setMPIComm(self, mpicomm):
        """ (Optional) Provide the MPI communicator to be used by the code for parallel computations.

        This method must be called before :meth:`initialize`. The communicator should include all the processes
        to be used by the code. For a sequential code, the call to :meth:`setMPIComm` is optional or
        ``mpicomm`` should be None.

        Parameters
        ----------
        mpicomm : mpi4py.MPI.Comm
            mpi4py communicator.

        Raises
        ------
        AssertionError
            If called multiple times or after :meth:`initialize`.
        """
        raise NotImplementedError

    def init(self):
        """ This is a recommanded wrapper for :meth:`initialize`.

        It works with :meth:`term` in order to guarantee that :meth:`initialize` and :meth:`terminate` are called only once:
            - :meth:`initialize` is called at the first call of |PD_init|.
            - :meth:`terminate` is called when the number of calls to :meth:`term` is equal to the number of calls to |PD_init|.

        |PD_init| also stores the return value of :meth:`initialize` instead of returning it.
        The output is accessible with |PD_getInitStatus|.

        .. warning:: This method, in association with |PD_getInitStatus|,
            should always be used inside C3PO instead of :meth:`initialize` which is not adapted to MPI Master-Workers paradigm.

        .. warning:: This method should never be redefined: define :meth:`initialize` instead!
        """
        if self._initNb == 0:
            self._initStatus = self.initialize()
        self._initNb += 1

    def getInitStatus(self):
        """ Return the output status of the last call to :meth:`initialize` made through |PD_init|.

        .. warning::

            This method, in association with |PD_init|, should always be used inside C3PO instead
            of :meth:`initialize` which is not adapted to MPI Master-Workers paradigm.

            This method should never be redefined: define :meth:`initialize` instead!

        Returns
        -------
        bool
            True if all OK, otherwise False.
        """
        return self._initStatus

    def initialize(self):
        """ (Mandatory) Initialize the current problem instance.

        In this method the code should allocate all its internal structures and be ready to execute. File reads, memory
        allocations, and other operations likely to fail should be performed here, and not in the constructor (and not in
        the |PD_setDataFile| or in the |PD_setMPIComm| methods either).
        This method must be called only once (after a potential call to |PD_setMPIComm| and/or |PD_setDataFile|)
        and cannot be called again before :meth:`terminate` has been performed.

        .. warning:: This method is not adapted to MPI Master-Workers paradigm. |PD_init| and |PD_getInitStatus|
            methods should be used in C3PO instead.

        Returns
        -------
        bool
            True if all OK, otherwise False.

        Raises
        ------
        AssertionError
            If called multiple times.
        """
        raise NotImplementedError

    def term(self):
        """ This is a recommanded wrapper for :meth:`terminate`.

        It works with |PD_init| in order to guarantee that :meth:`initialize` and :meth:`terminate` are called only once:
            - :meth:`initialize` is called at the first call of |PD_init|.
            - :meth:`terminate` is called when the number of calls to :meth:`term`
                is equal to the number of calls to |PD_init|.

        .. warning::

            This method should be used inside C3PO instead of :meth:`terminate`.

            This method should never be redefined: define :meth:`terminate` instead!
        """
        self._initNb = self._initNb - 1 if self._initNb > 0 else 0
        if self._initNb <= 0:
            self.terminate()

    def terminate(self):
        """ (Mandatory) Terminate the current problem instance and release all allocated resources.

        Terminate the computation, free the memory and save whatever needs to be saved. This method is called once
        at the end of the computation or after a non-recoverable error.
        No other ICoCo method except |PD_setDataFile|, |PD_setMPIComm| and :meth:`initialize`
        may be called after this.

        Raises
        ------
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        AssertionError
            If called inside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        """
        raise NotImplementedError

    def getInitNb(self):
        """ Return the number of times |PD_init| has been called but not :meth:`term`.

        This method is made to work with the wrappers |PD_init| and :meth:`term`.
        It indicates the number of :meth:`term` that are still needed to trigger :meth:`terminate`.

        Returns
        -------
        int
            The number of times |PD_init| has been called but not :meth:`term`.
        """
        return self._initNb

    def presentTime(self):
        """ (Mandatory) Return the current time of the simulation.

        Can be called any time between :meth:`initialize` and :meth:`terminate`.
        The current time can only change during a call to :meth:`validateTimeStep` or to :meth:`resetTime`.

        Returns
        -------
        float
            The current (physical) time of the simulation.

        Raises
        ------
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        """
        raise NotImplementedError

    def computeTimeStep(self):
        """ (Mandatory) Return the next preferred time step (time increment) for this code, and whether the code
        wants to stop.

        Both data are only indicative, the supervisor is not required to take them into account. This method is
        however marked as mandatory, since most of the coupling schemes expect the code to provide this
        information (those schemes then typically compute the minimum of the time steps of all the codes being coupled).
        Hence a possible implementation is to return a huge value, if a precise figure can not be computed.

        Can be called whenever the code is outside the ``TIME_STEP_DEFINED`` context
        (see :class:`.PhysicsDriver` documentation).

        Returns
        -------
        tuple(float, bool)
            A tuple ``(dt, stop)``.
            ``dt`` is the preferred time step for this code (only valid if ``stop`` is False).
            ``stop`` is True if the code wants to stop. It can be used for example to indicate that, according to
            a certain criterion, the end of the transient computation is reached from the code point of view.

        Raises
        ------
        AssertionError
            If called inside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        """
        raise NotImplementedError

    def initTimeStep(self, dt):
        """ (Mandatory) Provide the next time step (time increment) to be used by the code.

        After this call (if successful), the computation time step is defined to ``]t, t + dt]``
        where ``t`` is the value returned by :meth:`presentTime`. The code enters the
        ``TIME_STEP_DEFINED`` context. A time ``step = 0``. may be used when the
        stationaryMode is set to True for codes solving directly for the steady-state.

        Parameters
        ----------
        dt : float
            The time step to be used by the code.

        Returns
        -------
        bool
            False means that the given time step is not compatible with the code time scheme.

        Raises
        ------
        AssertionError
            If called inside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        ValueError
            If ``dt`` is invalid (``dt < 0.0``).
        """
        raise NotImplementedError

    def solve(self):
        """ Call :meth:`solveTimeStep` but store its return value instead of returning it.
        
        The output is accessible with |PD_getSolveStatus|.

        .. warning:: This method, in association with |PD_getSolveStatus|,
            should always be used inside C3PO instead of :meth:`solveTimeStep`.
            They fit better with MPI use.

            This method should never be redefined: define :meth:`solveTimeStep` instead!
        """
        self._solveStatus = self.solveTimeStep()

    def getSolveStatus(self):
        """ Return the output of the last call to :meth:`solveTimeStep` made through |PD_solve|.

        .. warning:: This method, in association with |PD_solve|,
            should always be used inside C3PO instead of :meth:`solveTimeStep`.
            They fit better with MPI use.

            This method should never be redefined: define :meth:`solveTimeStep` instead!

        Returns
        -------
        bool
            True if computation was successful, False otherwise.
        """
        return self._solveStatus

    def solveTimeStep(self):
        """ (Mandatory) Perform the computation on the current time interval.

        Can be called whenever the code is inside the ``TIME_STEP_DEFINED``
        context (see :class:`.PhysicsDriver` documentation).

        .. warning:: This method is not adapted to MPI Master-Workers paradigm.
            |PD_solve| and |PD_getSolveStatus| methods should be used with C3PO instead.

        Returns
        -------
        bool
            True if computation was successful, False otherwise.

        Raises
        ------
        AssertionError
            If called outside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        AssertionError
            If called several times without a call to :meth:`validateTimeStep` or to :meth:`abortTimeStep`.
        """
        raise NotImplementedError

    def validateTimeStep(self):
        """ (Mandatory) Validate the computation performed by :meth:`solveTimeStep`.

        Can be called whenever the code is inside the ``TIME_STEP_DEFINED``
        context (see :class:`.PhysicsDriver` documentation). After this call:

        - the present time has been advanced to the end of the computation time step
        - the computation time step is undefined (the code leaves the ``TIME_STEP_DEFINED`` context).

        Raises
        ------
        AssertionError
            If called outside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        AssertionError
            If called before the :meth:`solveTimeStep` method.
        """
        raise NotImplementedError

    def setStationaryMode(self, stationaryMode):
        """ (Mandatory) Set whether the code should compute a stationary solution or a transient one.

        New in version 2 of ICoCo. By default the code is assumed to be in stationary mode False (i.e. set up
        for a transient computation).
        If set to True, :meth:`solveTimeStep` can be used either to solve a time step in view of an
        asymptotic solution, or to solve directly for the steady-state. In this last case, a time step = 0.
        can be used with :meth:`initTimeStep` (whose call is always needed).
        The stationary mode status of the code can only be modified by this method (or by a call to
        :meth:`terminate` followed by :meth:`initialize`).

        Can be called whenever the code is outside the ``TIME_STEP_DEFINED``
        context (see :class:`.PhysicsDriver` documentation).

        Parameters
        ----------
        stationaryMode : bool
            True if the code should compute a stationary solution.

        Raises
        ------
        AssertionError
            If called outside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        """
        raise NotImplementedError

    def getStationaryMode(self):
        """ (Mandatory) Indicate whether the code should compute a stationary solution or a transient one.

        See also :meth:`setStationaryMode`.

        Can be called whenever the code is outside the ``TIME_STEP_DEFINED``
        context (see :class:`.PhysicsDriver` documentation).

        Returns
        -------
        bool
            True if the code has been set to compute a stationary solution.

        Raises
        ------
        AssertionError
            If called inside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        """
        raise NotImplementedError

    def isStationary(self):
        """ (Optional) Return whether the solution is constant on the computation time step.

        Used to know if the steady-state has been reached. This method can be called whenever the computation time step
        is not defined.

        Returns
        -------
        bool
            True if the solution is constant on the computation time step.

        Raises
        ------
        AssertionError
            If called inside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation),
            meaning we shouldn't request this information while the computation of a new time step is in progress.
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        """
        raise NotImplementedError

    def abortTimeStep(self):
        """ (Optional) Abort the computation on the current time step.

        Can be called whenever the computation time step is defined, instead of :meth:`validateTimeStep`.
        After this call, the present time is left unchanged, and the computation time step is undefined
        (the code leaves the ``TIME_STEP_DEFINED`` context).

        Raises
        ------
        AssertionError
            If called outside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        """
        raise NotImplementedError

    def resetTime(self, time_):
        """ (Optional) Reset the current time of the :class:`.PhysicsDriver` to a given value.

        New in version 2 of ICoCo.
        Particularly useful for the initialization of complex transients: the starting point of
        the transient of interest is computed first, the time is reset to 0, and then the actual
        transient of interest starts with proper initial conditions, and global time 0.

        Can be called outside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).

        Parameters
        ----------
        time\_ : float
            The new current time.

        Raises
        ------
        AssertionError
            If called inside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver`
            documentation).
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        """
        raise NotImplementedError

    def iterate(self):
        """ Call :meth:`iterateTimeStep` but store its return value instead of returning it.

        The output is accessible with |PD_getIterateStatus|.

        .. warning:: This method, in association with |PD_getIterateStatus|,
            should always be used inside C3PO instead of :meth:`iterateTimeStep`. They fit better with MPI use.

            This method should never be redefined: define :meth:`iterateTimeStep` instead!
        """
        self._iterateStatus = self.iterateTimeStep()

    def getIterateStatus(self):
        """ Return the output of the last call to :meth:`iterateTimeStep` made through |PD_iterate|.

        .. warning:: This method, in association with |PD_iterate|,
            should always be used inside C3PO instead of :meth:`iterateTimeStep`.
            They fit better with MPI use.

            This method should never be redefined: define :meth:`iterateTimeStep` instead!

        Returns
        -------
        tuple(bool,bool)
            A tuple ``(succeed, converged)``.
            ``succeed = False`` if the computation fails.
            ``converged = True`` if the solution is not evolving any more.
        """
        return self._iterateStatus

    def iterateTimeStep(self):
        """ (Optional) Perform a single iteration of computation inside the time step.

        This method is relevant for codes having inner iterations for the computation of a single time step.
        Calling :meth:`iterateTimeStep` until ``converged`` is True is equivalent to calling :meth:`solveTimeStep`,
        within the code's convergence threshold.
        Can be called (potentially several times) inside the ``TIME_STEP_DEFINED``
        context (see :class:`.PhysicsDriver` documentation).

        .. warning:: This method is not adapted to MPI Master-Workers paradigm.
            |PD_iterate| and |PD_getIterateStatus| methods should be used with C3PO instead.

        Returns
        -------
        tuple(bool, bool)
            A tuple ``(succeed, converged)``.
            ``succeed = False`` if the computation fails.
            ``converged = True`` if the solution is not evolving any more.

        Raises
        ------
        AssertionError
            If called outside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation).
        """
        raise NotImplementedError

    def save(self, label, method):
        """ (Optional) Save the state of the code.

        The saved state is identified by the combination of ``label`` and ``method`` arguments.
        If :meth:`save` has already been called with the same two arguments, the saved state is overwritten.

        Parameters
        ----------
        label : int
            A user- (or code-) defined value identifying the state.
        method : str
            A string specifying which method is used to save the state of the code. A code can provide
            different methods (for example in memory, on disk, etc.).

        Raises
        ------
        AssertionError
            If called inside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation),
            meaning we shouldn't save a previous time step while the computation of a new time step is
            in progress.
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        ValueError
            If the ``method`` or ``label`` argument is invalid.
        """
        raise NotImplementedError

    def restore(self, label, method):
        """ (Optional) Restore the state of the code.

        After restore, the code should behave exactly like after the corresponding call to save (except of course for
        save/restore methods, since the list of saved states may have changed).
        The state to be restored is identified by the combination of ``label`` and ``method`` arguments.
        The :meth:`save` method must have been called at some point or in some previous run with this combination.

        Parameters
        ----------
        label : int
            A user- (or code-) defined value identifying the state.
        method : str
            A string specifying which method was used to save the state of the code. A code can provide
            different methods (for example in memory, on disk, etc.).

        Raises
        ------
        AssertionError
            If called inside the ``TIME_STEP_DEFINED`` context (see :class:`.PhysicsDriver` documentation),
            meaning we shouldn't restore a previous time step while the computation of a new time step is in progress.
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        ValueError
            If the ``method`` or ``label`` argument is invalid.
        """
        raise NotImplementedError

    def forget(self, label, method):
        """ (Optional) Discard a previously saved state of the code.

        After this call, the save-point cannot be restored anymore. This method can be used to free the space occupied by
        unused saved states.

        Parameters
        ----------
        label : int
            A user- (or code-) defined value identifying the state.
        method : str
            A string specifying which method was used to save the state of the code. A code can provide
            different methods (for example in memory, on disk, etc.).

        Raises
        ------
        AssertionError
            If called before :meth:`initialize` or after :meth:`terminate`.
        ValueError
            If the ``method`` or ``label`` argument is invalid.
        """
        raise NotImplementedError

    def setTransientLogger(self, transientLogger):
        """ Defines the logger for :meth:`solveTransient` method.

        Parameters
        ----------
        transientLogger : c3po.services.TransientLogger.TransientLogger
            Logger instance.
        """
        self._transientPrinter.setLogger(transientLogger)

    def setTransientPrintLevel(self, level):
        """ Set the print level for :meth:`solveTransient` method
        (0=None, 1 keeps only the first and last lines, 2 keeps everything).

        Parameters
        ----------
        level : int
            Integer in range [0;2]. Default = 0.
        """
        self._transientPrinter.getPrinter().setPrintLevel(level)

    def solveTransient(self, tmax, finishAtTmax=False, stopIfStationary=False):
        """ Make the :class:`.PhysicsDriver` to advance in time until it reaches the time ``tmax`` or it asks to stop.

        The :class:`.PhysicsDriver` can ask to stop either with :meth:`computeTimeStep`
        (always checked) or with :meth:`isStationary` (only if ``stopIfStationary`` is set to True).

        Parameters
        ----------
        tmax : float
            Maximum time to be reached (compared with :meth:`presentTime`).
        finishAtTmax : bool
            If set to True, the method ends with ``time = tmax`` (instead of ``time >= tmax``).
        stopIfStationary : bool
            If set to True, the method stops also if :meth:`isStationary` returns True.
        """

        presentTime = self.presentTime()
        self._transientPrinter.initTransient(self, tmax, finishAtTmax, stopIfStationary, presentTime)

        (dt, stop) = self.computeTimeStep()
        while (presentTime < tmax - 1.E-8 * min(tmax, dt) and not stop):
            if finishAtTmax:
                if presentTime + 1.5 * dt >= tmax:
                    if presentTime + dt >= tmax - dt * 1.E-4:
                        dt = tmax - presentTime
                    else:
                        dt = 0.5 * (tmax - presentTime)
            self.initTimeStep(dt)
            self.solve()
            ok = self.getSolveStatus()
            if ok:
                self.validateTimeStep()
                presentTime = self.presentTime()
                self._transientPrinter.logValidate(dt, presentTime)
                (dt, stop) = self.computeTimeStep()
                if stopIfStationary:
                    stop = stop or self.isStationary()
            else:
                self.abortTimeStep()
                presentTime = self.presentTime()
                self._transientPrinter.logAbort(dt, presentTime)
                (dt2, stop) = self.computeTimeStep()
                if dt == dt2:
                    raise Exception("PhysicsDriver.solveTransient : we are about to repeat a failed time-step calculation !")
                dt = dt2

        self._transientPrinter.terminateTransient(presentTime, stop, stopIfStationary and self.isStationary())

    def getMPIComm(self):
        pass
