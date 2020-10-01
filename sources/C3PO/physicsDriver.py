# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class physicsDriver. """
from __future__ import print_function, division


class physicsDriver(object):
    """ physicsDriver defines and standardizes the functionalities expected by computer codes. It follows the ICOCO standard.

    In order to integrate a new code in C3PO it is necessary to define a class inheriting from physicsDriver and to overload its methods raising exception.
    """

    def __init__(self):
        self.initStatus_ = True
        self.solveStatus_ = True
        self.iterateStatus_ = (True, True)

    def setDataFile(self, datafile):
        """ Give the name of a data file to the code.
            The call is optional.
            If called, has to be done before initialize.

            :param datafile: name of a data file.
        """
        raise Exception("physicsDriver.setDataFile : not supported")

    def setMPIComm(self, mpicomm):
        """ Give an MPI communicator to the code, for its internal use.
        The communicator should include all the processes to be used by the code.
        For a sequential run, the call to setMPIComm is optional.
        Should be called before initialize.

        :param mpicomm: MPI communicator to be used by the code.
        """
        raise Exception("physicsDriver.setMPIComm : not supported")

    def init(self):
        """ This method calls initialize but store its return value instead of returning it. The output is accessible with getInitStatus.

        .. warning:: This method, in association with getInitStatus, should always be used inside C3PO instead of initialize which is not adapted to C3PO MPI Master-Workers paradigm.
        .. warning:: This method should never be redefined: define initialize instead!
        """
        self.initStatus_ = self.initialize()

    def getInitStatus(self):
        """ Returns the output of the last call to initialize made through init.

        :return: True means OK.

        .. warning:: This method, in association with init, should always be used inside C3PO instead of initialize which is not adapted to C3PO MPI Master-Workers paradigm.
        .. warning:: This method should never be redefined: define initialize instead!
        """
        return self.initStatus_

    def initialize(self):
        """ Initialize the code using the arguments of setDataFile and setMPIComm.
        This method is called once before any other method.
        File reads, memory allocations, and other operations which are likely to fail should be performed here and not in the previous methods.
        It cannot be called again before terminate has been performed.
        If initialize returns false (or raises an exception), nothing else than terminate can be called.

        :return: True means OK.

        ..  warning:: This method is not adapted to MPI Master-Workers paradigm. Init and getInitStatus methods should be used in C3PO instead.
        """
        raise Exception("physicsDriver.initialize : not supported")

    def terminate(self):
        """ Terminate the computation, free the memory and save whatever needs to be saved.
        This method is called once at the end of the computation or after a non-recoverable error.
        After terminate, no method (except setDataFile and setMPIComm) can be called before a new call to initialize.

        :return: True means OK.
        """
        raise Exception("physicsDriver.terminate : not supported")

    def presentTime(self):
        """ Returns the current time t.
        Can be called anytime between initialize and terminate.
        The current time can only change during the call to validateTimeStep.

        :return: the current time t.
        """
        raise Exception("physicsDriver.presentTime : not supported")

    def computeTimeStep(self):
        """ Returns two data : the preferred time step for this code and a boolean = True if the code wants to stop.
        Both data are only indicative, the supervisor is not required to take them into account.
        Can be called whenever the code has been initialized but the computation time step is not defined.

        :return: a tuple (dt, stop). dt is the preferred time step for this code and stop = True if the code wants to stop.
        """
        raise Exception("physicsDriver.computeTimeStep : not supported")

    def initTimeStep(self, dt):
        """ Give the next time step to the code.
        Can be called whenever the computation time step is not defined.
        After this call (if successful), the computation time step is defined to ]t,t+dt] where t is the value which would be returned by presentTime.
        All input and output fields are allocated on ]t,t+dt], initialized, and accessible through field exchange methods.

        :param dt: next time step size.
        :return: False if dt is not compatible with the code time scheme.
        """
        raise Exception("physicsDriver.initTimeStep : not supported")

    def solve(self):
        """ This method calls solveTimeStep but store its return value instead of returning it. The output is accessible with getSolveStatus.

        .. warning:: This method, in association with getSolveStatus, should always be used inside C3PO instead of solveTimeStep. They fit better with MPI use.
        .. warning:: This method should never be redefined: define solveTimeStep instead!
        """
        self.solveStatus_ = self.solveTimeStep()

    def getSolveStatus(self):
        """ Returns the output of the last call to solveTimeStep made through solve.

        :return: False if the computation fails.

        .. warning:: This method, in association with solve, should always be used inside C3PO instead of solveTimeStep. They fit better with MPI use.
        .. warning:: This method should never be redefined: define solveTimeStep instead!
        """
        return self.solveStatus_

    def solveTimeStep(self):
        """ Perform the computation on the current interval, using input data.
        Can be called whenever the computation time step is defined.
        After this call (if successful), the solution on the computation time step is accessible through the output data.

        :return: False if the computation fails.

        ..  warning:: This method is not adapted to MPI Master-Workers paradigm. solve and getSolveStatus methods should be used in C3PO instead.
        """
        raise Exception("physicsDriver.solveTimeStep : not supported")

    def validateTimeStep(self):
        """ Validate the computation performed by solveTimeStep.
        Can be called whenever the computation time step is defined.
        After this call, the present time has been advanced to the end of the computation time step, and the computation time step is undefined, so the input and output data are not accessible any more.
        """
        raise Exception("physicsDriver.validateTimeStep : not supported")

    def abortTimeStep(self):
        """ Abort the computation on the current time-step.
        Can be called whenever the computation timestep is defined, instead of validateTimeStep.
        After this call, the present time is left unchanged, and the computation time step is undefined, so the input and output data are not accessible any more.
        """
        raise Exception("physicsDriver.abortTimeStep : not supported")

    def isStationary(self):
        """ Can be called whenever the computation time step is defined.

        :return: true if the solution is constant on the computation time step. If the solution has not been computed, the return value is of course not meaningful.
        """
        raise Exception("physicsDriver.isStationary : not supported")

    def iterate(self):
        """ This method calls iterateTimeStep but store its return value instead of returning it. The output is accessible with getIterateStatus.

        .. warning:: This method, in association with getIterateStatus, should always be used inside C3PO instead of iterateTimeStep. They fit better with MPI use.
        .. warning:: This method should never be redefined: define iterateTimeStep instead!
        """
        self.iterateStatus_ = self.iterateTimeStep()

    def getIterateStatus(self):
        """ Returns the output of the last call to iterateTimeStep made through iterate.

        :return: a tuple(succeed, converged). succeed = False if the computation fails. converged = True if the solution is not evolving any more.

        .. warning:: This method, in association with iterate, should always be used inside C3PO instead of iterateTimeStep. They fit better with MPI use.
        .. warning:: This method should never be redefined: define iterateTimeStep instead!
        """
        return self.iterateStatus_

    def iterateTimeStep(self):
        """ The implementation of this method is optional.
        Perform a single iteration of computation inside the time-step.
        Can be called whenever the computation timestep is defined.
        Calling iterateTimeStep until converged is true is equivalent to calling solveTimeStep, within the code’s convergence threshold.

        :return: a tuple(succeed, converged). succeed = False if the computation fails. converged = True if the solution is not evolving any more.

        ..  warning:: This method is not adapted to MPI Master-Workers paradigm. iterate and getIterateStatus methods should be used in C3PO instead.
        """
        raise Exception("physicsDriver.iterateTimeStep : not supported")

    def save(self, label, method):
        """ Save the state of the code.
        Can be called at any time between initialize and terminate.

        :param label: an integer identifying, in association with method, the saved state.
        :param method: string specifying which method is used to save the state of the code. A code can provide different methods (for example in memory, on disk,…). At least « default » should be a valid argument.

        .. note:: If save has already been called with the same two arguments, the saved state is overwritten.
        """
        raise Exception("physicsDriver.save : not supported")

    def restore(self, label, method):
        """ Restore a state previously saved with the same couple of arguments.
        Can be called at any time between initialize and terminate.
        After restore, the code should behave exactly like after the corresponding call to save, except for save/restore methods, since the list of saved states may have changed.

        :param label: an integer identifying, in association with method, the saved state to restore.
        :param method: a string identifying, in association with label, the saved state to restore.
        """
        raise Exception("physicsDriver.restore : not supported")

    def forget(self, label, method):
        """Forget a state previously saved with the same couple of arguments.
        Can be called at any time between initialize and terminate.
        After this call, the state cannot be restored anymore.
        It can be used to free the space occupied by unused saved states.

        :param label: an integer identifying, in association with method, the saved state to forget.
        :param method: a string identifying, in association with label, the saved state to forget.
        """
        raise Exception("physicsDriver.forget : not supported")

    def getInputFieldsNames(self):
        """ :return: a list of strings identifying input fields.
        """
        raise Exception("physicsDriver.getInputFieldsNames : not supported")

    def getInputMEDFieldTemplate(self, name):
        """ Get a template of the field expected by the code for a given name.
        This method is useful to know the mesh, discretization… on which an input field is expected.

        :param name: string identifying the asked MEDFieldTemplate.
        :return: a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise Exception("physicsDriver.getInputMEDFieldTemplate : not supported")

    def setInputMEDField(self, name, field):
        """ Provide the input field corresponding to name to the code.
        After this call, the state of the computation and the output fields are invalidated.
        It should always be possible to switch consecutive calls to setInputField.
        At least one call to iterateTimeStep or solveTimeStep must be performed before getOutputField or validateTimeStep can be called.

        :param name: string identifying the input field.
        :param field: a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise Exception("physicsDriver.setInputMEDField : not supported")

    def getOutputFieldsNames(self):
        """ :return: a list of strings identifying output fields.
        """
        raise Exception("physicsDriver.getOutputFieldsNames : not supported")

    def getOutputMEDField(self, name):
        """ Return the output field corresponding to name from the code.

        :param name: string identifying the output field.
        :return: a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise Exception("physicsDriver.getOutputMEDField : not supported")

    def getInputValuesNames(self):
        """ :return: a list of strings identifying input scalars.
        """
        raise Exception("physicsDriver.getInputValuesNames : not supported")

    def setValue(self, name, value):
        """ Provide the input scalar value corresponding to name to the code.

        :param name: string identifying the input scalar.
        :param value: a scalar.
        """
        raise Exception("physicsDriver.setValue is not supported")

    def getOutputValuesNames(self):
        """ :return: a list of strings identifying output scalars.
        """
        raise Exception("physicsDriver.getOutputValuesNames : not supported")

    def getValue(self, name):
        """ Return the output scalar corresponding to name from the code.

        :param name: string identifying the output scalar.
        :return: a scalar.
        """
        raise Exception("physicsDriver.getValue is not supported")

    def solveTransient(self, tmax):
        """ Calls the chain of methods which makes the code to advance in time until it reaches the time tmax or computeTimeStep() asks to stop.

        :param tmax: maximum time to be reached (compared with presentTime()) """
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
                    raise Exception("physicsDriver.solveTransient : we are about to repeat a failed time-step calculation !")
                dt = dt2
