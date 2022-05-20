# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import pytest

import c3po

def test_matrix():
    from tests.Matrix.PhysicsMatrix import PhysicsMatrix

    myPhysics = PhysicsMatrix()
    myPhysics.init()
    taille = myPhysics.getOutputDoubleValue("taille")
    myPhysics.term()

    Transformer = c3po.DirectMatching()

    DataCoupler = c3po.LocalDataManager()
    Physics2Data = c3po.LocalExchanger(Transformer, [], [], [(myPhysics, str(i)) for i in range(taille)], [(DataCoupler, str(i)) for i in range(taille)])
    Data2Physics = c3po.LocalExchanger(Transformer, [], [], [(DataCoupler, str(i)) for i in range(taille)], [(myPhysics, str(i)) for i in range(taille)])

    CouplerGS = c3po.FixedPointCoupler([myPhysics], [Physics2Data, Data2Physics], [DataCoupler])
    CouplerGS.setDampingFactor(0.5)
    CouplerAnderson = c3po.AndersonCoupler([myPhysics], [Physics2Data, Data2Physics], [DataCoupler])
    CouplerAnderson.setOrder(3)
    CouplerJFNK = c3po.JFNKCoupler([myPhysics], [Physics2Data, Data2Physics], [DataCoupler])
    CouplerJFNK.setKrylovConvergenceParameters(1E-4, 3)

    CouplerGS.init()
    print(myPhysics.A_)
    CouplerGS.solve()
    print(myPhysics.result_)
    print("valeur propre :", myPhysics.getOutputDoubleValue("valeur_propre"))
    resu = np.dot(myPhysics.A_, myPhysics.result_) + myPhysics.b_
    print(resu / np.linalg.norm(resu))
    vpGS = myPhysics.getOutputDoubleValue("valeur_propre")
    CouplerGS.term()

    CouplerAnderson.init()
    CouplerAnderson.solve()
    print(myPhysics.result_)
    print("valeur propre :", myPhysics.getOutputDoubleValue("valeur_propre"))
    resu = np.dot(myPhysics.A_, myPhysics.result_) + myPhysics.b_
    print(resu / np.linalg.norm(resu))
    vpAnderson = myPhysics.getOutputDoubleValue("valeur_propre")
    CouplerAnderson.term()

    CouplerJFNK.init()
    CouplerJFNK.solve()
    print(myPhysics.result_)
    print("valeur propre :", myPhysics.getOutputDoubleValue("valeur_propre"))
    resu = np.dot(myPhysics.A_, myPhysics.result_) + myPhysics.b_
    print(resu / np.linalg.norm(resu))
    vpJFNK = myPhysics.getOutputDoubleValue("valeur_propre")
    CouplerJFNK.term()

    refVal = 15.2654890812
    assert pytest.approx(vpGS, abs=1.E-3) == refVal
    assert pytest.approx(vpGS, abs=1.E-3) == refVal
    assert pytest.approx(vpGS, abs=1.E-3) == refVal

if __name__ == "__main__":
    test_matrix()
