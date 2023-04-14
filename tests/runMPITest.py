# -*- coding: utf-8 -*-
from __future__ import print_function

import subprocess


def runMPITest(nbProcesses, fileAbspath):
    subprocessError = None
    try:
        result = subprocess.run(args=['mpirun', '-n', str(nbProcesses), 'python', fileAbspath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, universal_newlines=True)
        print(result.stdout)
    except subprocess.CalledProcessError as error:
        print(error.stdout)
        subprocessError = AssertionError(error.stderr)
    if subprocessError:
        raise subprocessError
