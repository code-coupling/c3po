# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
from typing import List, Tuple

# -- Project requirements -----------------------------------------------------

if sys.version_info[:2] < (3,11):
    raise RuntimeError(
        "Only a Python version higher than 3.11 is allowed to generate C3PO documentation.")

# -- Project tools ------------------------------------------------------------

def scan(path: Path, workdir: Path) -> Tuple[List[Path], List[Path]]:
    """
    Parameters
    ----------
    path : Path
        Absolute path of the C3PO sources.
    workdir : Path
        Absolute path of the documentation sources.

    Returns
    -------
    Tuple[List[Path], List[Path]]
        Returns the tuple (list_py,list_dir), with:
        - list_py : A list of absolute paths of all the Python files that C3PO sources contain (in a
          list list_py).
        - list_dir : A list of absolute paths of all the directories that C3PO sources contain (in a
          list list_dir).
    """
    list_py = []
    list_dir = []

    for path_name in path.iterdir():
        if path_name.is_file():
            if path_name.suffix == ".py" and path_name.name != "__init__.py":
                list_py.append(path_name)
        if path_name.is_dir():
            if path_name.name != "__pycache__" and path_name.name != "c3po.egg-info":
                modulepathdir = workdir / path_name.name
                if not modulepathdir.is_dir():
                    modulepathdir.mkdir()
                list_dir.append(path_name)
                files, dirs = scan(path_name, modulepathdir)
                list_py += files
                list_dir += dirs
    return list_py, list_dir

# -- Project construction -----------------------------------------------------

# Gets the current working directory.
current_path = Path(__file__).parent.resolve()

# Sets temporary directory where C3PO sources will be copied.
tmp_path = current_path.parent / "tmp"

# Copies C3PO sources in the tmp/ directory.
shutil.copytree(current_path.parent.parent / "sources", tmp_path, dirs_exist_ok=True)

# Generates all the .rst files from C3PO sources.
subprocess.run(["sphinx-apidoc",
                "-fe",
                "-o",
                str(current_path),
                str(tmp_path),
                "--templatedir="+str(current_path / "_apidoc_templates")],
                capture_output=True)

# Adds copied C3PO sources into the PATH environment variable.
sys.path.insert(0, str(tmp_path))

# Scans C3PO sources.
# Saves absolute paths of all the Python files that C3PO sources contain (in a list list_py).
# Saves absolute paths of all the directories that C3PO sources contain (in a list list_dir).
# Reproduces the tree structure of C3PO sources into the documentation source directory.
list_py, list_dir = scan(tmp_path, current_path)

dict_class = {}
# Loops over the Python files
for pyfile in list_py:
    # Gets the relative path of each Python file. It looks like "c3po/<path-to-file>".
    relative_pathfile = pyfile.relative_to(tmp_path)

    # Gets the parent directory of the file.
    pathdir = relative_pathfile.parent

    # Tranforms the path synthax "<path>/<to>/<the>/<file>" into "<path>.<to>.<the>.<file>".
    # The new synthax corresponds to the one of .rst files created by the command "sphinx-apidoc".
    # Moves .rst file to the good location into the tree structure of the documentation.
    rst = relative_pathfile.with_suffix("")
    rst = ".".join(rst.parts)
    rst_ext = rst + ".rst"
    shutil.move(current_path / rst_ext, pathdir / rst_ext)

    # Scans the content of each Python files and extract the name of all the classes.
    # <file_name1> : [<class1>, <class2>, ...]
    # <file_name2> : [...]
    # ...
    with open(pyfile, "r") as file:
        content = file.readlines()
        r = re.compile("^class ")
        newlist = list(filter(r.match, content))
        for i in range(len(newlist)):
            newlist[i] = re.search(r"\s\w+[(|:]",newlist[i]).group()[1:-1]
        dict_class[rst] = newlist

sourceInit = None
listLoadModule = []

for d in list_dir:
    # Gets the relative path of each directory. It looks like "c3po/<path-to-directory>".
    relative_pathfile = d.relative_to(tmp_path)
    pathdir = current_path / relative_pathfile.parent

    # Transforms the path synthax "<path>/<to>/<the>/<directory>" into "<path>.<to>.<the>.<directory>".
    # Moves .rst file to the good location into the tree structure of the documentation.
    rst = relative_pathfile.with_suffix("")
    rst = ".".join(rst.with_suffix(".rst").parts)
    shutil.move(current_path / rst, pathdir / rst)

    if str(relative_pathfile) == "c3po":
        sourceInit = d

# Scans the file tmp/c3po/__init__.py
# Checks if all the modules are loaded by this file.
# If not, adds the lines :
# from <file_name> import <class1>, <class2>, ...
alreadyload = []
with open((sourceInit / "__init__.py"), "r") as file:
    content = file.readlines()
    for line in content:
        splitline = line.split()
        if splitline and splitline[0] == 'from':
            alreadyload.append(splitline[1])

with open((sourceInit / "__init__.py"), "a") as file:
    for key in dict_class.keys():
        add = True
        for mod in alreadyload:
            if mod in key:
                add = False
                break
        value = dict_class.get(key)
        if add and value != None:
            file.write('from {} import {}\n'.format(key, ", ".join(value)))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'C3PO documentation'
copyright = '2025, TMA-GRP4'
author = 'TMA-GRP4'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx'
]

graphviz_output_format = 'svg'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'mpi4py': ('https://mpi4py.readthedocs.io/en/stable/', None),
    'icoco': ('https://icoco-python.readthedocs.io/en/latest/', None)
    }

autodoc_mock_imports = ["CATHARE2SWIG", "CATHARE3SWIG", "Access", "FlicaICoCo",
                        "trusticoco", "MEDconvert", "MEDtsetpt", "pleiades",
                        "pleiadesMPI", "Alcyone2Init", "mpi4py", "medcoupling",
                        "MEDLoader", "c3po.medcouplingCompat", "numpy", "icoco"]

if os.getenv("DATADIR") == None:
    autodoc_mock_imports.append("c3po.physicsDrivers.FLICA4Driver")
elif not (os.path.isfile(os.path.join(os.getenv("DATADIR"), "flica4_static.dat")) or
    os.path.isfile(os.path.join(os.getenv("DATADIR"), "flica4_transient.dat"))):

    autodoc_mock_imports.append("c3po.physicsDrivers.FLICA4Driver")

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {'sidebarwidth': 450, 'body_min_width': 850}
html_static_path = ['_static']
