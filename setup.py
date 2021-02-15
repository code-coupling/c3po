# -*- coding: utf-8 -*-

from setuptools import (
    setup,
    find_packages,
    )

setup(name="C3PO",
      packages = find_packages(where = 'sources'),
      package_dir = {"":"sources"},
      )

