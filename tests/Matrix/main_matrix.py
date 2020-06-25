# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np

import C3PO
from physicsMatrix import physicsMatrix

myPhysics = physicsMatrix()
taille = myPhysics.getValue("taille")

Transformer = C3PO.directMatching()

DataCoupler = C3PO.dataManager()
Physics2Data = C3PO.exchanger(Transformer, [], [], [(myPhysics, str(i)) for i in range(taille)], [(DataCoupler, str(i)) for i in range(taille)])
Data2Physics = C3PO.exchanger(Transformer, [], [], [(DataCoupler, str(i)) for i in range(taille)], [(myPhysics, str(i)) for i in range(taille)])

CouplerGS = C3PO.GaussSeidelCoupler([myPhysics], [Physics2Data, Data2Physics], [DataCoupler])
CouplerGS.setDampingFactor(0.5)
CouplerAnderson = C3PO.AndersonQRCoupler([myPhysics], [Physics2Data, Data2Physics], [DataCoupler])
CouplerAnderson.setOrder(3)
CouplerJFNK = C3PO.JFNKCoupler([myPhysics], [Physics2Data, Data2Physics], [DataCoupler])
CouplerJFNK.setKrylovConvergenceParameters(1E-4, 3)

CouplerGS.init()
print(myPhysics.A_)
CouplerGS.solve()
print(myPhysics.result_)
print("valeur propre :", myPhysics.getValue("valeur_propre"))
resu = np.dot(myPhysics.A_, myPhysics.result_) + myPhysics.b_
print(resu / np.linalg.norm(resu))
vpGS = myPhysics.getValue("valeur_propre")
CouplerGS.terminate()

CouplerAnderson.init()
CouplerAnderson.solve()
print(myPhysics.result_)
print("valeur propre :", myPhysics.getValue("valeur_propre"))
resu = np.dot(myPhysics.A_, myPhysics.result_) + myPhysics.b_
print(resu / np.linalg.norm(resu))
vpAnderson = myPhysics.getValue("valeur_propre")
CouplerAnderson.terminate()

CouplerJFNK.init()
CouplerJFNK.solve()
print(myPhysics.result_)
print("valeur propre :", myPhysics.getValue("valeur_propre"))
resu = np.dot(myPhysics.A_, myPhysics.result_) + myPhysics.b_
print(resu / np.linalg.norm(resu))
vpJFNK = myPhysics.getValue("valeur_propre")
CouplerJFNK.terminate()

assert round(vpGS, 3) == round(15.2654890812, 3) and round(vpAnderson, 3) == round(15.2654890812, 3) and round(vpJFNK, 3) == round(15.2654890812, 3), "Results not good!"
