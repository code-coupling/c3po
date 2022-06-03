This folder contains C3PO basic tests.

They do not require any additional prerequisites than C3PO.

## Contact ##

 Cyril PATRICOT (cyril.patricot@cea.fr)

## Description ##

### scalar_linear ###

Very basic coupling between two scalar functions.

### matrix ###

Calculation of the first eigenvalue and eigenvector of a small matrix using fixed-point method, Anderson acceleration and JFNK method.

### med_Dussaix ###

Coupling between two steady-state PhysicsDrivers working on two (different) meshes with two cells.

The same calculation is made:

- in sequential;
- using SPMD (Single Programm Multiple Data) paradimg with 2 MPI processes;
- using a master - workers paradigm with 3 MPI processes.

### listing ###

Coupling, in steady-state and in time-dependent calculations, between two scalar models, with the writing of different listings.

The ability to mask variable names by new ones is also tested.

The same calculation is made:

- in sequential;
- using SPMD (Single Programm Multiple Data) paradimg with 2 MPI processes;

### transient ###

Coupling between two scalar models.

First a steady-state is sought, with one of the models requiring to perform a stabilized-transient in order to reach equilibrium.

Then, a time-dependant calculation is made, with exchanges only every n time-steps.

### med_1D3D ###

Steady-state coupling between one 3D model and four 1D models.

The same calculation is made:

- in sequential;
- using a hybrid SPMD (Single Programm Multiple Data) and master - workers paradigm with 5 MPI processes: a master process is chosen among the four calculating the 1D models; it drives the three others and is coupled using SPMD paradigm with the process running the 3D model.
