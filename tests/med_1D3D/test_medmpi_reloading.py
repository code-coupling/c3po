# -*- coding: utf-8 -*-
from __future__ import print_function, division

from pytest_easyMPI import mpi_parallel

from tests.med_1D3D.main_medmpi_reloading import main_medmpi_reloading


@mpi_parallel(5)
def test_medmpi_reloading():
    main_medmpi_reloading()
