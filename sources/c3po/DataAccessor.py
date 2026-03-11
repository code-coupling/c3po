# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class :class:`.DataAccessor`. """
from __future__ import print_function, division


class DataAccessor(object):
    """ :class:`.DataAccessor` is an abstract class which standardizes I/O (in/out) methods.

    It follows the ICOCO V2 standard.
    See also :class:`.PhysicsDriver`.
    """

    class ValueType:
        """ The various possible types for fields or scalar values. """
        Double = "Double"
        Int = "Int"
        String = "String"

    def getMPIComm(self):
        """ (Optional) Return the MPI communicator used by the code for parallel computations.

        Returns
        -------
        mpi4py.MPI.Comm
            mpi4py communicator.
        """
        raise NotImplementedError

    def getInputFieldsNames(self):
        """ (Optional) Get the list of input fields accepted by the code.

        Returns
        -------
        list
            The list of field names that represent inputs of the code.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        """
        raise NotImplementedError

    def getOutputFieldsNames(self):
        """ (Optional) Get the list of output fields that can be provided by the code.

        Returns
        -------
        list
            The list of field names that can be produced by the code.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        """
        raise NotImplementedError

    def getFieldType(self, name):
        """ (Optional) Get the type of a field managed by the code.

        (New in version 2) The three possible types are 'Double', 'Int' and 'String', as defined
        by :class:`ValueType`.

        Parameters
        ----------
        name : str
            Field name.

        Returns
        -------
        str
            'Double', 'Int' or 'String', as defined by :class:`ValueType`.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the field ``name`` is invalid.
        """
        raise NotImplementedError

    def getMeshUnit(self):
        """ (Optional) Get the (length) unit used to define the meshes supporting the fields.

        (New in version 2)

        Returns
        -------
        str
            Length unit in which the mesh coordinates should be understood (e.g. 'm', 'cm', ...).

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        """
        raise NotImplementedError

    def getFieldUnit(self, name):
        """ (Optional) Get the physical unit used for a given field.

        (New in version 2)

        Parameters
        ----------
        name : str
            Field name.

        Returns
        -------
        str
            Unit in which the field values should be understood (e.g. 'W', 'J', 'Pa', ...).

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the field ``name`` is invalid.
        """
        raise NotImplementedError

    def getInputMEDDoubleFieldTemplate(self, name):
        """ (Optional) Retrieve an empty shell for an input field.

        This shell can be filled by the caller and then be given to the code
        via :meth:`setInputMEDDoubleField`.

        The code returns a field with all the data that represents the context of the field (i.e.
        its support mesh, its discretization -- on nodes, on elements, ...).
        The remaining job for the caller of this method is to fill the actual values of the field
        itself.
        When this is done the field can be sent back to the code through the
        method :meth:`setInputMEDDoubleField`.
        This method is not mandatory but is useful to know the mesh, discretization... on which an
        input field is expected. Is is required by C3PO remapping functionalities.

        See :class:`.PhysicsDriver` documentation for more details on the time semantic of a field.

        Parameters
        ----------
        name : str
            Name of the field for which we would like the empty shell.

        Returns
        -------
        medcoupling.MEDCouplingFieldDouble
            Field with all the contextual information.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the field ``name`` is invalid.
        """
        raise NotImplementedError

    def setInputMEDDoubleField(self, name, field):
        """ (Optional) Provide the code with input data in the form of a ``MEDCouplingFieldDouble``.

        The method :meth:`getInputMEDDoubleFieldTemplate`, if implemented, may be used first to
        prepare an empty shell of the field to pass to the code.

        See :class:`.PhysicsDriver` documentation for more details on the time semantic of a field.

        Parameters
        ----------
        name : str
            Name of the field that is given to the code.
        field : medcoupling.MEDCouplingFieldDouble
            Field containing the input data to be read by the code. The name
            of the field set on this instance (with the ``Field::setName`` method) should not be
            checked. However its time value should be to ensure it is within the proper time
            interval ``]t, t+dt]``.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the field ``name`` ('name' parameter) is invalid.
        ValueError
            If the time property of ``field`` does not belong to the currently computed time step
            ``]t, t + dt]``.
        """
        raise NotImplementedError

    def getOutputMEDDoubleField(self, name):
        """ (Optional) Return output data from the code in the form of a ``MEDCouplingFieldDouble``.

        See :class:`.PhysicsDriver` documentation for more details on the time semantic of a field.

        Parameters
        ----------
        name : str
            Name of the field that the caller requests from the code.

        Returns
        -------
        medcoupling.MEDCouplingFieldDouble
            Field with the data read by the code. The name and time properties of the field should
            be set in accordance with the 'name' parameter and with the current time step being
            computed.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the field ``name`` is invalid.
        """
        raise NotImplementedError

    def updateOutputMEDDoubleField(self, name, field):
        """ (Optional) Update a previously retrieved output field.

        (New in version 2) This method allows the code to implement a more efficient update of a
        given output field, thus avoiding the caller to invoke :meth:`getOutputMEDDoubleField`
        each time.
        A previous call to :meth:`getOutputMEDDoubleField` with the same name must have been done
        prior to this call.
        The code should check the consistency of the field object with the requested data (same
        support mesh, discretization -- on nodes, on elements, etc.).

        See :class:`.PhysicsDriver` documentation for more details on the time semantic of a field.

        Parameters
        ----------
        name : str
            Name of the field that the caller requests from the code.
        field : medcoupling.MEDCouplingFieldDouble
            Object updated with the data read from the code. Notably
            the time indicated in the field should be updated to be within the current time step
            being computed.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the field name (``name`` parameter) is invalid.
        ValueError
            If the field object is inconsistent with the field being requested.
        """
        raise NotImplementedError

    def getInputMEDIntFieldTemplate(self, name):
        """ Similar to :meth:`getInputMEDDoubleFieldTemplate` but for ``MEDCouplingFieldInt``. """
        raise NotImplementedError

    def setInputMEDIntField(self, name, field):
        """ Similar to :meth:`setInputMEDDoubleField` but for ``MEDCouplingFieldInt``. """
        raise NotImplementedError

    def getOutputMEDIntField(self, name):
        """ Similar to :meth:`getOutputMEDDoubleField` but for ``MEDCouplingFieldInt``. """
        raise NotImplementedError

    def updateOutputMEDIntField(self, name, field):
        """ Similar to :meth:`updateOutputMEDDoubleField` but for ``MEDCouplingFieldInt``. """
        raise NotImplementedError

    def getInputMEDStringFieldTemplate(self, name):
        """ Similar to :meth:`getInputMEDDoubleFieldTemplate` but for ``MEDCouplingFieldString``.

        .. warning::

            At the time of writing, ``MEDCouplingFieldString`` are not yet implemented anywhere.
        """
        raise NotImplementedError

    def setInputMEDStringField(self, name, field):
        """ Similar to :meth:`setInputMEDDoubleField` but for ``MEDCouplingFieldString``.

        .. warning::

            At the time of writing, ``MEDCouplingFieldString`` are not yet implemented anywhere.
        """
        raise NotImplementedError

    def getOutputMEDStringField(self, name):
        """ Similar to :meth:`getOutputMEDDoubleField` but for ``MEDCouplingFieldString``.

        .. warning::

            At the time of writing, ``MEDCouplingFieldString`` are not yet implemented anywhere.
        """
        raise NotImplementedError

    def updateOutputMEDStringField(self, name, field):
        """ Similar to :meth:`updateOutputMEDDoubleField` but for ``MEDCouplingFieldString``.

        .. warning::

            At the time of writing, ``MEDCouplingFieldString`` are not yet implemented anywhere.
        """
        raise NotImplementedError

    def getInputValuesNames(self):
        """ (Optional) Get the list of input scalars accepted by the code.

        Returns
        -------
        list
            The list of scalar names that represent inputs of the code.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        """
        raise NotImplementedError

    def getOutputValuesNames(self):
        """ (Optional) Get the list of output scalars that can be provided by the code.

        Returns
        -------
        list
            The list of scalar names that can be returned by the code.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        """
        raise NotImplementedError

    def getValueType(self, name):
        """ (Optional) Get the type of a scalar managed by the code.

        (New in version 2) The three possible types are 'Double', 'Int' and 'String', as defined
        by :class:`ValueType`.

        Parameters
        ----------
        name : str
            Scalar value name.

        Returns
        -------
        str
            'Double', 'Int' or 'String', as defined by :class:`ValueType`.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the scalar name is invalid.
        """
        raise NotImplementedError

    def getValueUnit(self, name):
        """ (Optional) Get the physical unit used for a given value.

        (New in version 2)

        Parameters
        ----------
        name : str
            Scalar value name.

        Returns
        -------
        str
            Unit in which the scalar value should be understood (e.g. 'W', 'J', 'Pa', ...).

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the scalar name is invalid.
        """
        raise NotImplementedError

    def setInputDoubleValue(self, name, value):
        """ (Optional) Provide the code with a scalar :py:class:`float` data.

        See :class:`.PhysicsDriver` documentation for more details on the time semantic of a
        scalar value.

        Parameters
        ----------
        name : str
            Name of the scalar value that is given to the code.
        value : float
            Value passed to the code.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the scalar name is invalid.
        """
        raise NotImplementedError

    def getOutputDoubleValue(self, name):
        """ (Optional) Retrieve a scalar :py:class:`float` value from the code.

        See :class:`.PhysicsDriver` documentation for more details on the time semantic of a
        scalar value.

        Parameters
        ----------
        name : str
            Name of the scalar value to be read from the code.

        Returns
        -------
        float
            The value read from the code.

        Raises
        ------
        AssertionError
            If implemented in a :class:`.PhysicsDriver` and called before :meth:`initialize` or
            after :meth:`terminate`.
        ValueError
            If the scalar name is invalid.
        """
        raise NotImplementedError

    def setInputIntValue(self, name, value):
        """ (Optional) Similar to :meth:`setInputDoubleValue` but for an :py:class:`int` value. """
        raise NotImplementedError

    def getOutputIntValue(self, name):
        """ (Optional) Similar to :meth:`getOutputDoubleValue` but for an :py:class:`int` value. """
        raise NotImplementedError

    def setInputStringValue(self, name, value):
        """ (Optional) Similar to :meth:`setInputDoubleValue` but for an :py:class:`str` value. """
        raise NotImplementedError

    def getOutputStringValue(self, name):
        """ (Optional) Similar to :meth:`getOutputDoubleValue` but for an :py:class:`str` value. """
        raise NotImplementedError
