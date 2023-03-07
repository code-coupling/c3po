# -*- coding: utf-8 -*-
from __future__ import print_function, division

from pytest_easyMPI import mpi_parallel

from tests.med_Dussaix.main_mpi_remapper import main_mpi_remapper


@mpi_parallel(4)
def test_mpi_remapper():
    main_mpi_remapper()
