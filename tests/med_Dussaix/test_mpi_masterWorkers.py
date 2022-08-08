# -*- coding: utf-8 -*-
from __future__ import print_function, division

from pytest_easyMPI import mpi_parallel

from tests.med_Dussaix.main_mpi_masterWorkers import main_mpi_masterWorkers


@mpi_parallel(3)
def test_masterWorkers():
    main_mpi_masterWorkers()
