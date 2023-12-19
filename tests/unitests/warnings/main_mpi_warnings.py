# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest

import c3po.mpi


def main_mpi_warnings():
    c3po.mpi.MPISharedRemappingMulti1D3D(c3po.Multi1D3DRemapper([0., 1.], [0., 1.], [0], [1.]))


if __name__ == "__main__":
    main_mpi_warnings()
