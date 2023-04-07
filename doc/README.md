C3PO's documentation uses Doxygen. It can be generated using:

```sh
./makedoc.sh
```

It is placed in a **html** folder.

The folder **online** is dedicated to the generation of online documentation be readTheDocs (see https://salome-c3po.readthedocs.io ). It contains a dummy sphinx documentation: running sphinx generates the Doxygen documentation and substistutes (from sphinx v1.2) the empty sphinx documentation with the Doxygen one.

