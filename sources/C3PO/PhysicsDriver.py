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


class PhysicsDriver(object):
    """! PhysicsDriver defines and standardizes the functionalities expected by computer codes. It follows the ICOCO standard.

    In order to integrate a new code in C3PO it is necessary to define a class inheriting from PhysicsDriver and to overload 
    its methods raising exception.
    """

    def __init__(self):
        """! Default constructor """
        self.initStatus_ = True
        self.solveStatus_ = True
        self.iterateStatus_ = (True, True)

    def setDataFile(self, datafile):
        """! Give the path of a data file to the code.

        The call is optional.
        If called, has to be done before initialize().

        @param datafile path to a data file.
        """
        raise Exception("PhysicsDriver.setDataFile : not supported")

    def setMPIComm(self, mpicomm):
        """! Give an MPI communicator to the code, for its internal use.

        The communicator should include all the processes to be used by the code.
        For a sequential run, the call to this method is optional.
        Should be called before initialize().

        @param mpicomm MPI communicator to be used by the code.
        """
        raise Exception("PhysicsDriver.setMPIComm : not supported")

    def init(self):
        """! Call initialize() but store its return value instead of returning it. The output is accessible with getInitStatus().

        @warning This method, in association with getInitStatus(), should always be used inside C3PO instead of initialize() which 
        is not adapted to C3PO MPI Master-Workers paradigm.
        @warning This method should never be redefined: define initialize() instead!
        """
        self.initStatus_ = self.initialize()

    def getInitStatus(self):
        """! Return the output status of the last call to initialize() made through init().

        @return True means OK.

        @warning This method, in association with init(), should always be used inside C3PO instead of initialize() which is not 
        adapted to C3PO MPI Master-Workers paradigm.
        @warning This method should never be redefined: define initialize() instead!
        """
        return self.initStatus_

    def initialize(self):
        """! Initialize the code using the arguments of setDataFile() and setMPIComm().

        This method is called once before any other method.
        File reads, memory allocations, and other operations which are likely to fail should be performed here and not in the 
        previous methods.
        It cannot be called again before terminate() has been performed.
        If initialize() returns False (or raises an exception), nothing else than terminate() can be called.

        @return True means OK.

        @warning This method is not adapted to MPI Master-Workers paradigm. init() and getInitStatus() methods should be used 
        in C3PO instead.
        """
        raise Exception("PhysicsDriver.initialize : not supported")

    def terminate(self):
        """! Terminate the computation, free the memory and save whatever needs to be saved.

        This method is called once at the end of the computation or after a non-recoverable error.
        After terminate(), no method (except setDataFile() and setMPIComm()) can be called before a new call to initialize().
        """
        raise Exception("PhysicsDriver.terminate : not supported")

    def presentTime(self):
        """! Return the current time t.

        Can be called anytime between initialize() and terminate().
        The current time can only change during the call to validateTimeStep().

        @return the current time t.
        """
        raise Exception("PhysicsDriver.presentTime : not supported")

    def computeTimeStep(self):
        """! Return two things : the preferred time step for this code and a boolean = True if the code wants to stop.

        Both are only indicative, the supervisor is not required to take them into account.
        Can be called whenever the code has been initialized but the computation time step is not defined.

        @return a tuple (dt, stop). dt is the preferred time step for this code and stop = True if the code wants to stop.
        """
        raise Exception("PhysicsDriver.computeTimeStep : not supported")

    def initTimeStep(self, dt):
        """! Give the next time step to the code.

        Can be called whenever the computation time step is not defined.
        After this call (if successful), the computation time step is defined to ]t,t+dt] where t is the value which would 
        be returned by presentTime().
        All input and output fields are allocated on ]t,t+dt], initialized, and accessible through field exchange methods.

        @param dt next time step size.
        @return False if dt is not compatible with the code time scheme.
        """
        raise Exception("PhysicsDriver.initTimeStep : not supported")

    def solve(self):
        """! Call solveTimeStep() but store its return value instead of returning it. The output is accessible with getSolveStatus().

        @warning This method, in association with getSolveStatus(), should always be used inside C3PO instead of solveTimeStep(). 
        They fit better with MPI use.
        @warning This method should never be redefined: define solveTimeStep() instead!
        """
        self.solveStatus_ = self.solveTimeStep()

    def getSolveStatus(self):
        """! Return the output of the last call to solveTimeStep() made through solve().

        @return False if the computation fails.

        @warning This method, in association with solve(), should always be used inside C3PO instead of solveTimeStep(). 
        They fit better with MPI use.
        @warning This method should never be redefined: define solveTimeStep() instead!
        """
        return self.solveStatus_

    def solveTimeStep(self):
        """! Perform the computation on the current interval, using input data.

        Can be called whenever the computation time step is defined.
        After this call (if successful), the solution on the computation time step is accessible through the output data.

        @return False if the computation fails.

        @warning This method is not adapted to MPI Master-Workers paradigm. solve() and getSolveStatus() methods should be 
        used in C3PO instead.
        """
        raise Exception("PhysicsDriver.solveTimeStep : not supported")

    def validateTimeStep(self):
        """! Validate the computation performed by solveTimeStep().

        Can be called whenever the computation time step is defined.
        After this call, the present time has been advanced to the end of the computation time step, and the computation time 
        step is undefined, so the input and output data are not accessible any more.
        """
        raise Exception("PhysicsDriver.validateTimeStep : not supported")

    def abortTimeStep(self):
        """! Abort the computation on the current time-step.

        Can be called whenever the computation timestep is defined, instead of validateTimeStep().
        After this call, the present time is left unchanged, and the computation time step is undefined, so the input and output 
        data are not accessible any more.
        """
        raise Exception("PhysicsDriver.abortTimeStep : not supported")

    def isStationary(self):
        """! Return True if the solution is constant on the last computed time step.

        Can be called whenever the computation time step is defined.

        @return True if the solution is constant on the last computed time step. If the solution has not been computed, the return 
        value is of course not meaningful.
        """
        raise Exception("PhysicsDriver.isStationary : not supported")

    def iterate(self):
        """! Call iterateTimeStep() but store its return value instead of returning it. The output is accessible with getIterateStatus().

        @warning This method, in association with getIterateStatus(), should always be used inside C3PO instead of iterateTimeStep(). 
        They fit better with MPI use.
        @warning This method should never be redefined: define iterateTimeStep() instead!
        """
        self.iterateStatus_ = self.iterateTimeStep()

    def getIterateStatus(self):
        """! Return the output of the last call to iterateTimeStep() made through iterate().

        @return a tuple(succeed, converged). succeed = False if the computation fails. converged = True if the solution is not evolving any more.

        @warning This method, in association with iterate(), should always be used inside C3PO instead of iterateTimeStep(). They fit 
        better with MPI use.
        @warning This method should never be redefined: define iterateTimeStep() instead!
        """
        return self.iterateStatus_

    def iterateTimeStep(self):
        """! Perform a single solving iteration of the current time-step.

        The implementation of this method is optional.
        Can be called whenever the computation timestep is defined.
        Calling iterateTimeStep() until converged is True is equivalent to calling solveTimeStep(), within the code’s convergence threshold.

        @return a tuple(succeed, converged). succeed = False if the computation fails. converged = True if the solution is not evolving any more.

        @warning This method is not adapted to MPI Master-Workers paradigm. iterate() and getIterateStatus() methods should be used in C3PO instead.
        """
        raise Exception("PhysicsDriver.iterateTimeStep : not supported")

    def save(self, label, method):
        """! Save the state of the code.

        Can be called at any time between initialize() and terminate().

        @param label an integer identifying, in association with method, the saved state.
        @param method string specifying which method is used to save the state of the code. A code can provide different methods 
        (for example in memory, on disk,…). At least « default » should be a valid argument.

        @note If save() has already been called with the same two arguments, the saved state is overwritten.
        """
        raise Exception("PhysicsDriver.save : not supported")

    def restore(self, label, method):
        """! Restore a state previously saved with the same couple of arguments.

        Can be called at any time between initialize() and terminate().
        After restore(), the code should behave exactly like after the corresponding call to save(), except for save/restore methods, 
        since the list of saved states may have changed.

        @param label an integer identifying, in association with method, the saved state to restore.
        @param method a string identifying, in association with label, the saved state to restore.
        """
        raise Exception("PhysicsDriver.restore : not supported")

    def forget(self, label, method):
        """! Forget a state previously saved with the same couple of arguments.

        Can be called at any time between initialize() and terminate().
        After this call, the state cannot be restored anymore.
        It can be used to free the space occupied by unused saved states.

        @param label an integer identifying, in association with method, the saved state to forget.
        @param method a string identifying, in association with label, the saved state to forget.
        """
        raise Exception("PhysicsDriver.forget : not supported")

    def getInputFieldsNames(self):
        """! Return a list of strings identifying input fields. 

        @return a list of strings identifying input fields.
        """
        raise Exception("PhysicsDriver.getInputFieldsNames : not supported")

    def getInputMEDFieldTemplate(self, name):
        """! Get a template of the field expected by the code for a given name.

        This method is useful to know the mesh, discretization… on which an input field is expected.

        @param name string identifying the asked MEDField template.
        @return a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise Exception("PhysicsDriver.getInputMEDFieldTemplate : not supported")

    def setInputMEDField(self, name, field):
        """! Provide the input field corresponding to name to the code.

        After this call, the state of the computation and of the output fields are invalidated.
        It should always be possible to switch consecutive calls to setInputMEDField().
        At least one call to iterateTimeStep() or solveTimeStep() must be performed before getOutputMEDField() or validateTimeStep() can be called.

        @param name string identifying the input field.
        @param field a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise Exception("PhysicsDriver.setInputMEDField : not supported")

    def getOutputFieldsNames(self):
        """! Return a list of strings identifying output fields.

        @return a list of strings identifying output fields.
        """
        raise Exception("PhysicsDriver.getOutputFieldsNames : not supported")

    def getOutputMEDField(self, name):
        """! Return the output field corresponding to name from the code.

        @param name string identifying the output field.
        @return a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise Exception("PhysicsDriver.getOutputMEDField : not supported")

    def getInputValuesNames(self):
        """! Return a list of strings identifying input scalars.

        @return a list of strings identifying input scalars.
        """
        raise Exception("PhysicsDriver.getInputValuesNames : not supported")

    def setValue(self, name, value):
        """! Provide the input scalar value corresponding to name to the code.

        @param name string identifying the input scalar.
        @param value a scalar.
        """
        raise Exception("PhysicsDriver.setValue is not supported")

    def getOutputValuesNames(self):
        """! Return a list of strings identifying output scalars.

        @return a list of strings identifying output scalars.
        """
        raise Exception("PhysicsDriver.getOutputValuesNames : not supported")

    def getValue(self, name):
        """! Return the output scalar corresponding to name from the code.

        @param name string identifying the output scalar.
        @return a scalar.
        """
        raise Exception("PhysicsDriver.getValue is not supported")

    def solveTransient(self, tmax):
        """! Call the methods that makes the code to advance in time until it reaches the time tmax or computeTimeStep() asks to stop.

        @param tmax maximum time to be reached (compared with presentTime()) """
        (dt, stop) = self.computeTimeStep()
        while (self.presentTime() < tmax and not stop):
            self.initTimeStep(dt)
            self.solve()
            ok = self.getSolveStatus()
            if ok:
                self.validateTimeStep()
                (dt, stop) = self.computeTimeStep()
            else:
                self.abortTimeStep()
                (dt2, stop) = self.computeTimeStep()
                if (dt == dt2):
                    raise Exception("PhysicsDriver.solveTransient : we are about to repeat a failed time-step calculation !")
                dt = dt2
