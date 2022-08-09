# -*- coding: utf-8 -*-
from __future__ import print_function

from pytest_easyMPI import mpi_parallel

from tests.unitests.masterWorkers.main_masterWorkers import main_masterWorkers


@mpi_parallel(3)
def test_mpi_masterWorkers():
    main_masterWorkers()
