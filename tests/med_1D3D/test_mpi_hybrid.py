# -*- coding: utf-8 -*-
from __future__ import print_function, division

from pytest_easyMPI import mpi_parallel

from tests.med_1D3D.main_mpi_hybrid import main_mpi_hybrid


@mpi_parallel(5)
def test_mpi_hybrid():
    main_mpi_hybrid()
