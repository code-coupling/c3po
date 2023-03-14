# -*- coding: utf-8 -*-
from __future__ import print_function, division

from pytest_easyMPI import mpi_parallel

from tests.med_1D3D.main_medmpi_collaborative import main_medmpi_collaborative


@mpi_parallel(5)
def test_medmpi_collaborative():
    main_medmpi_collaborative()
