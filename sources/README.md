
# Collaborative Code Coupling PlatfOrm

C3PO (Collaborative Code Coupling PlatfOrm) is part of
[Salome platform](https://www.salome-platform.org/?lang=en).

It is a Python library offering generic services for the
definition of coupled calculations with codes meeting a certain framework
(use of [MEDCoupling](https://docs.salome-platform.org/latest/dev/MEDCoupling/tutorial/index.html),
MPI and [ICoCo](https://pypi.org/project/icoco/)).

The main objective of C3PO is to facilitate and standardize the writing of coupling scripts, in
particular in HPC (High Performance Computing) environment. It also provides generic (and HPC-compatible)
implementations of the main coupling algorithms (Picard iteration, Anderson acceleration, JFNK), and
allows pooling of efforts in the development and verification of multi-physics calculation schemes.

C3PO is code- and physics-agnostic, and therefore constitutes a kernel of generic methods that can
be shared by different multi-physics applications. For this reason, it has been made open-source
under the (highly permissive) 3-Clause BSD License and available [here](https://github.com/code-coupling/c3po).
