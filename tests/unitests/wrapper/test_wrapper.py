# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest

import c3po


def test_wrapper():
    class classA:
        def __init__(self, privateA, publicA):
            self._privateA = privateA
            self.publicA = publicA

        def somme(self, c):
            return self._privateA + self.publicA + c

    class classB(classA):
        def __init__(self, privateA, publicA, privateB, publicB):
            super().__init__(privateA, publicA)
            self._privateB = privateB
            self.publicB = publicB

        def sommePrivate(self):
            return self._privateA + self._privateB

    class classC(classB):
        def __init__(self, privateA, publicA, privateB, publicB, privateC, publicC):
            super().__init__(privateA, publicA, privateB, publicB)
            self._privateC = privateC
            self.publicC = publicC

        def sommePublic(self):
            return self.publicA + self.publicB + self.publicC

        def sommePrivate(self):
            return super().sommePrivate() + self._privateC

    def checkObject(toCheck):
        print("verification objet de type", type(toCheck))
        assert toCheck.somme(10.) == 13.
        assert toCheck.sommePrivate() == 9.
        assert toCheck.sommePublic() == 12.
        assert toCheck._privateA == 1.
        assert toCheck.publicA == 2.
        assert toCheck._privateB == 3.
        assert toCheck.publicB == 4.
        assert toCheck._privateC == 5.
        assert toCheck.publicC == 6.
        toCheck._privateA += 100
        toCheck.publicA += 100
        toCheck._privateB += 100
        toCheck.publicB += 100
        toCheck._privateC += 100
        toCheck.publicC += 100
        assert toCheck.somme(10.) == 213.
        assert toCheck.sommePrivate() == 309.
        assert toCheck.sommePublic() == 312.
        toCheck._privateA -= 100
        toCheck.publicA -= 100
        toCheck._privateB -= 100
        toCheck.publicB -= 100
        toCheck._privateC -= 100
        toCheck.publicC -= 100

    objectC = classC(1., 2., 3., 4., 5., 6.)
    checkObject(objectC)
    wrapperC = c3po.wrapper(objectC)
    checkObject(wrapperC)

if __name__ == "__main__":
    test_wrapper()
