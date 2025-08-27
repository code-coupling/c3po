==================
C3PO documentation
==================

.. _intro_sec:

Introduction
============

C3PO (Collaborative Code Coupling PlatfOrm) is a Python library offering generic services for the
definition of coupled calculations with codes meeting a certain framework. This framework is
defined by:

- Use of Python. Codes have to be wrapped into a Python class, which allows to coordinate them
  in a homogeneous way regardless of their native programming language.

- Use of MEDCoupling for data exchanges. MEDCoupling is the common format choosen for the exchanges
  of space-dependent variables. MEDCoupling is a C++ library, with Python binding, provided by the
  open-source SALOME platform [1].

- If needed, use of MPI as distributed memory parallelization standard. MPI is by far the dominant
  distributed memory parallelization standard. C3PO is compatible with the use of MPI, but does not
  support other distributed memory parallelization standards. On the other hand, full flexibility is
  given for the intra-code shared memory parallelization.

- Implementation of an ICoCo API [2]. ICoCo (V2) is the code API used by C3PO. It includes all
  required capabilities for multiphysics simulations such as initialization, termination, time-step
  control, solving, exchange of variables etc. It is defined by :class:`c3po.PhysicsDriver.PhysicsDriver`.

For more information about code integration, see :ref:`Code_integration_pag`.

The main objective of C3PO is to facilitate and standardize the writing of coupling scripts, in
particular in HPC (High Performance Computing) environment. It also provides generic (and HPC-compatible)
implementations of the main coupling algorithms (Picard iteration, Anderson acceleration, JFNK), and
allows pooling of efforts in the development and verification of multi-physics calculation schemes.

C3PO is code- and physics-agnostic, and therefore constitutes a kernel of generic methods that can
be shared by different multi-physics applications. For this reason, it has been made open-source
under the (highly permissive) 3-Clause BSD License here: https://sourceforge.net/projects/cea-c3po/.

.. _source_sec:

Source overview
===============

The sources directory contains:

- The directory :mod:`c3po` with all C3PO sources. It can be imported without any MPI dependency.

- The file setup.py that can be used to install C3PO via pip: "pip install path --user" (with path
  the path to the setup.py file)

- The file .pylintrc that define coding standards to be followed in C3PO. Install pylint (python3
  module available with pip) and run "pylint c3po" from the sources directory to check your code.
  You must get the grade 10/10!

The directory sources/c3po contains the definition of the following classes:

- :class:`c3po.DataAccessor.DataAccessor` is a class interface (to be implemented) which standardizes
  the accesses to data. It follows the ICOCO standard.

- :class:`c3po.PhysicsDriver.PhysicsDriver` is a class interface (to be implemented) which
  standardizes the functionalities expected by computer codes. It derives from
  :class:`c3po.DataAccessor.DataAccessor` for the data accesses. It follows the ICoCo standard.

- :class:`c3po.CollaborativeObject.CollaborativeObject` is a base class for classes that allow to handle
  a set of objects as a single one.

- :class:`c3po.CollaborativePhysicsDriver.CollaborativePhysicsDriver` handles a set of
  :class:`c3po.PhysicsDriver.PhysicsDriver` as a single one. It inherits
  from :class:`c3po.CollaborativeObject.CollaborativeObject`.

- :class:`c3po.TimeAccumulator.TimeAccumulator` is a class that allows to distinguish a notion of macro
  time steps to be used to drive a :class:`c3po.PhysicsDriver.PhysicsDriver` in a coupling from the notion
  of micro time steps actually used by the :class:`c3po.PhysicsDriver.PhysicsDriver`. It can also be used
  to wrap a stabilized transient loop into a steady state call.

- :class:`c3po.DataManager.DataManager` is a class interface (to be implemented) which standardizes
  methods to handle data outside of codes. This is necessary for some coupling techniques or time schemes.

- :class:`c3po.LocalDataManager.LocalDataManager` implements both :class:`c3po.DataManager.DataManager`
  and :class:`c3po.DataAccessor.DataAccessor`: it can store and handle local data.

- :class:`c3po.CollaborativeDataManager.CollaborativeDataManager` handles a set of
  :class:`c3po.DataManager.DataManager` as a single one. It inherits from
  :class:`c3po.CollaborativeObject.CollaborativeObject`.

- :class:`c3po.Exchanger.Exchanger` is a class interface (to be implemented) which standardizes data
  exchanges between :class:`c3po.DataAccessor.DataAccessor` objects (:class:`c3po.PhysicsDriver.PhysicsDriver`
  or :class:`c3po.LocalDataManager.LocalDataManager`).

- :class:`c3po.LocalExchanger.LocalExchanger` is a :class:`c3po.Exchanger.Exchanger` for local
  data exchanges.

- :class:`c3po.CollaborativeExchanger.CollaborativeExchanger` allows to handle a set of
  :class:`c3po.Exchanger.Exchanger` as a single one. It inherits from
  :class:`c3po.CollaborativeObject.CollaborativeObject`.

- :class:`c3po.Coupler.Coupler` is the base class for the definition of a coupling, based on
  :class:`c3po.PhysicsDriver.PhysicsDriver`, :class:`c3po.DataManager.DataManager` and
  :class:`c3po.Exchanger.Exchanger` concepts. It inherits from :class:`c3po.PhysicsDriver.PhysicsDriver`.

Basic couplings can be made only with these classes.

The directory sources/c3po also contains six directories:

- couplers with specific implementations of :class:`c3po.Coupler.Coupler` for the main coupling
  algorithms. See below.

- exchangeMethods with specific implementations of exchange methods (to be used with a
  :class:`c3po.LocalExchanger.LocalExchanger`). See below.

- medcouplingCompat which deals with various versions of MEDCoupling. Import this module to use
  all versions of MEDCoupling in an identical way (following the last version API).

- physicsDrivers with specific implementations of :class:`c3po.PhysicsDriver.PhysicsDriver`
  for some codes.

- services with some optionnal services (mainly for monitoring of coupled calculations). See below.

- raises for optionnal error handling services. See below.

- multi1D with sources related to the use of a set of 1D models in a 3D coupling. See below.

- mpi with sources related to MPI. See below.

.. note::

    When "import c3po" is made, the classes and functions defined in c3po/couplers,
    c3po/exchangeMethods and c3po/services are imported and made available directly in :mod:`c3po` module.

    "import c3po.medcouplingCompat" must be done if one wants to use directly MEDCoupling (using
    this helper).

    "import c3po.raises" must be done to access raises functionalities. icoco package must be available.

    "import c3po.multi1D" (and if needed "import c3po.multi1D.mpi") must be done to access multi1D
    functionalities.

    "import c3po.mpi" must be done to get access to MPI classes of C3PO (the classes and functions
    defined in c3po/mpi/mpiExchangeMethods are imported and made available directly in :mod:`c3po.mpi`
    module). mpi4py must be available.

    Each class of c3po/physicsDrivers must be imported separately.

    "import c3po.services.checkScope" must be done, as it uses an additionnal prerequisite "icoco".

.. _couplers_sec:

c3po/couplers directory
-----------------------

This directory contains the definition of the following classes (coupling algorithms, they all
inherit from :class:`c3po.Coupler.Coupler`):

- :class:`c3po.couplers.FixedPointCoupler.FixedPointCoupler` proposes a damped fixed point algorithm.

- :class:`c3po.couplers.AndersonCoupler.AndersonCoupler` proposes a fixed point algorithm with
  Anderson acceleration. A QR decomposition is used for the optimization problem.

- :class:`c3po.couplers.JFNKCoupler.JFNKCoupler` proposes a Jacobian-Free Newton Krylov coupling
  algorithm.

- :class:`c3po.couplers.CrossedSecantCoupler.CrossedSecantCoupler` proposes a fixed point algorithm
  with crossed secant acceleration.

- :class:`c3po.couplers.AdaptiveResidualBalanceCoupler.AdaptiveResidualBalanceCoupler` proposes a
  adaptive residual balance algorithm (version proposed by Senecal).

- :class:`c3po.couplers.DynamicResidualBalanceCoupler.DynamicResidualBalanceCoupler` proposes a
  dynamic residual balance algorithm (variant of the adaptive residual balance proposed by R. Delvaux).

.. _exchMeth_sec:

c3po/exchangeMethods directory
------------------------------

This directory contains the definition of the following classes (exchange methods to be used with
a :class:`c3po.LocalExchanger.LocalExchanger`):

- :class:`c3po.exchangeMethods.ExchangeMethod.ExchangeMethod` is a class interface (to be implemented)
  which standardizes exchange methods to be used with :class:`c3po.LocalExchanger.LocalExchanger`
  (or its daughter class :class:`c3po.mpi.MPIExchanger.MPIExchanger`).

- :class:`c3po.exchangeMethods.DirectMatching.DirectMatching` is the most simple exchange method:
  it does nothing else than output = input.

- :class:`c3po.exchangeMethods.SharedRemapping.SharedRemapping` projects the input fields one by
  one before returning them as outputs, in the same order.

.. _services_sec:

c3po/services directory
-----------------------

This directory contains the definition of the following elements:

- :class:`c3po.services.tracer.tracer` is a class wrapper allowing to trace the calls of the methods
  of the base class. It has different functions:

  1. It can write all calls of the methods of the base class in a text file in Python format in
     order to allow to replay what happened from the code point of view outside of the coupling.

  2. It can save in .med files input or output MEDFields.

  3. It can redirect code standard and error outputs in text files.

  4. It can contribute (with :class:`c3po.services.ListingWriter.ListingWriter`) to the writing
     of a global coupling listing file with calculation time measurement.

- :class:`c3po.services.ListingWriter.ListingWriter` allows, in association with
  :class:`c3po.services.tracer.tracer`, to write a global coupling listing file with calculation
  time measurement. Three funtions work with this class:

  1. |mergeListing| which allows to merge listing files produced by
     :class:`c3po.services.ListingWriter.ListingWriter` (or by previous call to |mergeListing|).
     It is designed to produce a comprehensive view of a MPI calculation.

  2. :meth:`getTotalTimePhysicsDriver() <c3po.services.ListingWriter.getTotalTimePhysicsDriver>`
     which reads a listing file produced by :class:`c3po.services.ListingWriter.ListingWriter` or
     |mergeListing| and returns the total time spent by one :class:`c3po.PhysicsDriver.PhysicsDriver`
     in indicated methods.

  3. :meth:`getTimesExchanger() <c3po.services.ListingWriter.getTimesExchanger>` which reads a
     listing file produced by :class:`c3po.services.ListingWriter.ListingWriter` or |mergeListing|
     and returns time information about a chosen exchanger.

- :class:`c3po.services.NameChanger.NameChanger` wraps a :class:`c3po.PhysicsDriver.PhysicsDriver`
  object and changes the names of the values and fields quantities that can be get/set through ICoCo
  methods. The idea is to improve the genericity of coupling scripts by using generic variable names
  without having to modify the names "by hand".

- :class:`c3po.services.PhysicsDriverWrapper.PhysicsDriverWrapper` is a skeleton, intended to
  be overloaded, for modifying the behavior of a PhysicsDriver by composition.

- :class:`c3po.services.wrapper` contain two experimental functions:

  1. :class:`c3po.services.wrapper.buildWrappingClass` which returns a wrapping class for any
     provided one.

  2. :class:`c3po.services.wrapper.wrapper` which returns a wrapping object (built with
     :class:`c3po.services.wrapper.buildWrappingClass`) for any provided one.

- :class:`c3po.services.TransientLogger.TransientLogger` is a class interface (to be implemented)
  for logging (in standard output) information during a transient (method solveTransient() from
  :class:`c3po.PhysicsDriver.PhysicsDriver`). There are two implementations of this class:

  1. :class:`c3po.services.TransientLogger.Timekeeper` provides basic information about transient
     progress. It is the default implementation used by :class:`c3po.PhysicsDriver.PhysicsDriver`
     (but logging is by default desactivated).

  2. :class:`c3po.services.TransientLogger.FortuneTeller` derives from
     :class:`c3po.services.TransientLogger.Timekeeper` and adds an evaluation of the remaining
     computing time to complete the transient.

.. _raises_sec:

c3po/raises directory
---------------------

This directory contains the definition of the following elements:

- :class:`c3po.raises.checkScope.CheckScopeMeta` is a metaclass which adds scope checks required
  by ICoCo standard (and raise appropriate errors).

- :class:`c3po.raises.checkScope.checkScope` is a class wrapper that applies
  :class:`c3po.raises.checkScope.CheckScopeMeta` metaclass.

.. _multi1D_sec:

c3po/multi1D directory
----------------------

This directory contains the definition of the following classes:

- :class:`c3po.multi1D.Grid.Grid` is a class interface that allows to define 2D grids and to assign
  indices to each grid cell. The following daughter classes are available:

  - :class:`c3po.multi1D.Grid.MEDGrid` to import a grid defined as a 2D MEDCoupling field,

  - :class:`c3po.multi1D.Grid.CartesianGrid` for cartesian grids,

  - :class:`c3po.multi1D.Grid.HexagonalGrid` for hexagonal grids,

  - :class:`c3po.multi1D.Grid.MultiLevelGrid` to define nested grids.

- :class:`c3po.multi1D.Multi1DAPI.Multi1DAPI` is a minimalist class interface for handling a set of
  1D components. :class:`c3po.multi1D.Multi1DAPI.Multi1DWithObjectsAPI` is an extension of the previous
  class where each 1D component can hold a set of objects identified by name.

- :class:`c3po.multi1D.MEDInterface.MEDInterface` is a class that can read and write 3D fields by
  associating a :class:`c3po.multi1D.Grid.Grid` and a :class:`c3po.multi1D.Multi1DAPI.Multi1DAPI`.

- :class:`c3po.multi1D.Multi1DPhysicsDriver.Multi1DPhysicsDriver` is the master class of the multi1D
  package. It holds a set of 1D PhysicsDriver (through the non-user class
  c3po.multi1D.Multi1DPhysicsDriver.DriverAPI that implements
  :class:`c3po.multi1D.Multi1DAPI.Multi1DAPI` for 1D PhysicsDriver), and behaves like a unique 3D
  PhysicsDriver (using internally :class:`c3po.multi1D.MEDInterface.MEDInterface`).

When :class:`c3po.multi1D` is imported, the above-mentioned classes are imported and made available
in :class:`c3po.multi1D`.

c3po/multi1D also contains one directory:

- mpi with specializations of :class:`c3po.multi1D` for MPI couplings. See below.

.. _multi1Dmpi_sec:

c3po/multi1D/mpi directory
~~~~~~~~~~~~~~~~~~~~~~~~~~

- :class:`c3po.multi1D.mpi.MPIMulti1DPhysicsDriver` is the MPI collaborative version of
  :class:`c3po.multi1D.Multi1DPhysicsDriver.Multi1DPhysicsDriver`.

.. _C3POMPIsources_sec:

c3po/mpi directory
------------------

This directory contains the definition of C3PO sources related to MPI.

Two parallelization modes are available (and can be mixed):

- Collaborative: all the processes run the same instructions. Instructions that do not concern a
  process (because it does not host a code for example) are ignored.

- Master-workers: a master process executes the highest-level instructions. It controls the
  execution of calculation codes and the data exchanges between worker processes.

These two parallelization modes share a common base of concepts.

.. _CommonMPIsources_sec:

Common base
~~~~~~~~~~~

- :class:`c3po.mpi.MPIRemote.MPIRemote`. It can replaces a remote :class:`c3po.PhysicsDriver.PhysicsDriver`
  and :class:`c3po.DataManager.DataManager` (and inherits from these class) but passes most of
  the methods: it does nothing.

- :class:`c3po.mpi.MPIRemoteProcess.MPIRemoteProcess` identifies a (single) remote process. It
  inherits from :class:`c3po.mpi.MPIRemote.MPIRemote` but contains in addition the rank of the process
  in charge of the real object.

- :class:`c3po.mpi.MPIRemoteProcesses.MPIRemoteProcesses` identifies a set of remote processes. It
  inherits from :class:`c3po.mpi.MPIRemote.MPIRemote` but contains in addition the list of ranks of the
  processes in charge of the real object.

- :class:`c3po.mpi.MPICollectiveProcess.MPICollectiveProcess` defines a collective process. In
  particular, it allows, by inheritance (a new class that inherits from
  :class:`c3po.mpi.MPICollectiveProcess.MPICollectiveProcess` must be defined), to define a
  collective :class:`c3po.PhysicsDriver.PhysicsDriver`: all processors will locally launch this
  component.

- :class:`c3po.mpi.MPIExchanger.MPIExchanger` is the MPI version of
  :class:`c3po.LocalExchanger.LocalExchanger`. The class either use directly a
  :class:`c3po.mpi.mpiExchangeMethods.MPIExchangeMethod.MPIExchangeMethod` or use a
  :class:`c3po.exchangeMethods.ExchangeMethod.ExchangeMethod` (in the case where each code exposes
  its data on a single MPI process). In this last case, it takes in charge data exchanges between
  MPI processes then uses locally :class:`c3po.LocalExchanger.LocalExchanger`.

.. _CollaborativeMPIsources_sec:

Collaborative mode
~~~~~~~~~~~~~~~~~~

- :class:`c3po.mpi.MPICollaborativeDataManager.MPICollaborativeDataManager` is the MPI collaborative
  version of :class:`c3po.CollaborativeDataManager.CollaborativeDataManager`. It allows to handle a
  set of :class:`c3po.DataManager.DataManager` (some of then being remote) as a single one. Thanks
  to this class, data can be distributed on different MPI processes but still used in the same way.

- :class:`c3po.mpi.MPIDomainDecompositionDataManager.MPIDomainDecompositionDataManager` is the
  version of :class:`c3po.DataManager.DataManager` to be used to handle data comming from codes using
  domain decomposition methods. As for :class:`c3po.mpi.MPICollaborativeDataManager.MPICollaborativeDataManager`,
  the data are distributed on different MPI processes.

- :class:`c3po.mpi.MPICollectiveDataManager.MPICollectiveDataManager` is the MPI collaborative
  version of the :class:`c3po.LocalDataManager.LocalDataManager` in which all processes have all
  data locally.

- :class:`c3po.mpi.MPICoupler.MPICoupler` is the MPI collaborative version of :class:`c3po.Coupler.Coupler`.

- :class:`c3po.mpi.MPICollaborativePhysicsDriver.MPICollaborativePhysicsDriver` is the MPI
  collaborative version of :class:`c3po.CollaborativePhysicsDriver.CollaborativePhysicsDriver` (and
  is a specific kind of :class:`c3po.mpi.MPICoupler.MPICoupler`). It allows to handle a set of
  :class:`c3po.PhysicsDriver.PhysicsDriver` as a single one.

.. _MasterWorkersMPIsources_sec:

Master/workers mode
~~~~~~~~~~~~~~~~~~~

- :class:`c3po.mpi.MPIMasterPhysicsDriver.MPIMasterPhysicsDriver` is used by the master
  process to control remote :class:`c3po.PhysicsDriver.PhysicsDriver` as a local one.

- :class:`c3po.mpi.MPIMasterDataManager.MPIMasterDataManager` is used by the master process to
  control remote :class:`c3po.DataManager.DataManager` as a local one.

- :class:`c3po.mpi.MPIMasterExchanger.MPIMasterExchanger` is used by the master to control remote
  :class:`c3po.Exchanger.Exchanger`.

- :class:`c3po.mpi.MPIWorker.MPIWorker` defines the behavior of workers.

The directory sources/c3po/mpi also contains one directories:

- mpiExchangeMethods with specific implementations of MPI exchange methods. See below.

.. _mpiExchMeth_sec:

c3po/mpi/mpiExchangeMethods directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- :class:`c3po.mpi.mpiExchangeMethods.MPIExchangeMethod.MPIExchangeMethod` is a class interface (to
  be implemented) which standardizes MPI exchange methods. Unlike the exchanges methods of
  c3po/exchangeMethods, MPI exchange methods support MPI exchanges. It has to be used with a
  :class:`c3po.mpi.MPIExchanger.MPIExchanger`.

- :class:`c3po.mpi.mpiExchangeMethods.MPISharedRemapping.MPISharedRemapping` this is the MPI
  version of :class:`c3po.exchangeMethods.SharedRemapping.SharedRemapping`. MPI features of
  MEDCoupling must be available. It allows to use MEDCoupling projections between codes using
  domain decomposition methods.

- :class:`c3po.mpi.mpiExchangeMethods.MPIValueBcast.MPIValueBcast` can be used to exchange values
  (not fields) between two sets of processes.

.. _contacts_sec:

Contacts
========

cyril.patricot@cea.fr

.. _ref_introduction_sec:

References
==========

[1] “Salomé: The Open Source Integration Platform for Numerical Simulation”, http://www.salome-platform.org.

[2] E. Deville, F. Perdu, “Documentation of the Interface for Code Coupling : ICoCo”, NURISP technical report D3.3.1.2 (2012).

.. |mergeListing| replace:: :meth:`mergeListing() <c3po.services.ListingWriter.mergeListing>`
