# -*- coding: utf-8 -*-
from __future__ import print_function, division

from pytest_easyMPI import mpi_parallel

from tests.med_Dussaix.main_mpi_collaborative import main_mpi_collaborative


@mpi_parallel(2)
def test_collaborative():
    main_mpi_collaborative()
