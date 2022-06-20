# -*- coding: utf-8 -*-
from __future__ import print_function, division
import os, math, glob
import pytest

import c3po.medcouplingCompat as mc

import c3po

refT = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    1.5304669563087145, 1.5304669563087145, 1.376243629593887, 1.376243629593887, 1.5304669563087145, 1.5304669563087145, 1.3762436295939438, 1.3762436295939438, 1.6075786196661284,
    1.6075786196661284, 1.4533552929513576, 1.4533552929513576, 1.6075786196661284, 1.6075786196661284, 1.4533552929514144, 1.4533552929513576, 1.7378276038375589, 1.7378276038375589,
    1.5908149357994148, 1.5908149357994148, 1.7378276038375589, 1.7378276038375589, 1.590814935799358, 1.5908149357994148, 1.8113339378566593, 1.8113339378566025, 1.6643212698185152,
    1.6643212698185152, 1.8113339378566593, 1.8113339378566593, 1.6643212698185152, 1.6643212698185152, 1.8603643181424445, 1.8603643181424445, 1.7175315794357857, 1.7175315794357857,
    1.8603643181424445, 1.8603643181424445, 1.7175315794358426, 1.7175315794358426, 1.9317806874958023, 1.9317806874958023, 1.7889479487892004, 1.7889479487892004, 1.9317806874958023,
    1.9317806874957455, 1.7889479487892004, 1.7889479487892004, 1.8602960210313313, 1.8602960210313313, 1.717461210659053, 1.717461210659053, 1.8602960210313313, 1.8602960210313313,
    1.717461210659053, 1.717461210659053, 1.9317134262174704, 1.9317134262174704, 1.788878615845249, 1.788878615845249, 1.9317134262174704, 1.9317134262174704, 1.788878615845249,
    1.788878615845249, 1.738045266043855, 1.738045266043855, 1.5910419557933437, 1.5910419557933437, 1.738045266043855, 1.738045266043855, 1.5910419557933437, 1.5910419557934006,
    1.811546921168997, 1.811546921168997, 1.6645436109185994, 1.6645436109185425, 1.8115469211690538, 1.8115469211690538, 1.6645436109185994, 1.6645436109185994, 1.5300350576194433,
    1.5300350576194433, 1.3757340976492856, 1.3757340976492856, 1.5300350576194433, 1.5300350576194433, 1.3757340976492856, 1.3757340976492856, 1.6071855376045505, 1.6071855376045505,
    1.452884577634336, 1.4528845776343928, 1.6071855376045505, 1.6071855376045505, 1.452884577634336, 1.452884577634336, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

refP = [0.02749115639939625, 0.06636952262474233, 0.06636952262474233, 0.02749115639939625, 0.06636952262474233, 0.16023020164888085, 0.16023020164888085, 0.06636952262474233,
    0.06636952262474233, 0.16023020164888085, 0.16023020164888085, 0.06636952262474233, 0.02749115639939625, 0.06636952262474233, 0.06636952262474233, 0.02749115639939625,
    0.07978244326766626, 0.1926118565760619, 0.1926118565760619, 0.07978244326766626, 0.1926118565760619, 0.4650061564197899, 0.4650061564197899, 0.1926118565760619, 0.1926118565760619,
    0.4650061564197899, 0.4650061564197899, 0.1926118565760619, 0.07978244326766626, 0.1926118565760619, 0.1926118565760619, 0.07978244326766626, 0.09256706020858153,
    0.22347665218456433, 0.2311878185203057, 0.09576112988656045, 0.22347665218456433, 0.53952036457771, 0.5581367669271649, 0.23118781852030287, 0.21962106901669365, 0.5302121634029792,
    0.548828565752434, 0.2273322353524322, 0.09097002536959208, 0.21962106901669365, 0.22733223535242933, 0.09416409504756981, 0.11122981450395025, 0.2685325267156803,
    0.27779486515207036, 0.11506640070359264, 0.2685325267156803, 0.6482948679353105, 0.6706561310077418, 0.27779486515207036, 0.2639013574974834, 0.6371142363991036, 0.6594754994715175,
    0.2731636959338735, 0.10931152140412831, 0.2639013574974834, 0.2731636959338735, 0.11314810760377071, 0.11975436868806845, 0.2891126210401627, 0.29908807555631883,
    0.12388633723949626, 0.2891126210401627, 0.6979796107683937, 0.722062488352124, 0.29908807555631484, 0.2841248937820827, 0.6859381719765189, 0.7100210495602493, 0.29410034829823484,
    0.11768838441235374, 0.28412489378208666, 0.29410034829823484, 0.12182035296377988, 0.11975634443619053, 0.28911739091807487, 0.29909299011959056, 0.12388837291825654,
    0.28911739091807487, 0.6979911262723401, 0.7220743531574374, 0.29909299011959056, 0.2841295913173171, 0.6859495128297914, 0.7100327397148791, 0.2941051905188288, 0.11769033019515752,
    0.2841295913173171, 0.2941051905188288, 0.1218223586772219, 0.11122413417838373, 0.2685188131966588, 0.27778056205803325, 0.11506047616805858, 0.2685188131966588, 0.6482617605717013,
    0.6706216002841249, 0.2777805620580297, 0.2638879387659788, 0.6370818407155068, 0.6594416804279131, 0.27314968762734965, 0.10930596318354778, 0.2638879387659752, 0.2731496876273461,
    0.11314230517322116, 0.09257600512331489, 0.22349824711902788, 0.23121329511753577, 0.09577168263865626, 0.22349824711902788, 0.5395724993613704, 0.5581982728737276,
    0.23121329511753577, 0.21964072311977254, 0.5302596126051885, 0.5488853861175524, 0.22735577111828043, 0.09097816636564363, 0.21964072311977254, 0.22735577111828326,
    0.09417384388098617, 0.07978244326766626, 0.1926118565760619, 0.1926118565760619, 0.07978244326766626, 0.1926118565760619, 0.4650061564197899, 0.4650061564197899, 0.1926118565760619,
    0.1926118565760619, 0.4650061564197899, 0.4650061564197899, 0.1926118565760619, 0.07978244326766626, 0.1926118565760619, 0.1926118565760619, 0.07978244326766626, 0.027491156399396293,
    0.06636952262474241, 0.06636952262474241, 0.027491156399396293, 0.06636952262474241, 0.1602302016488811, 0.1602302016488811, 0.06636952262474241, 0.06636952262474241,
    0.1602302016488811, 0.1602302016488811, 0.06636952262474241, 0.027491156399396293, 0.06636952262474241, 0.06636952262474241, 0.027491156399396293]


class OneIterationCoupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


def test_sequential():
    from tests.med_1D3D.NeutroDriver import NeutroDriver
    from tests.med_1D3D.ThermoDriver import ThermoDriver

    tracedNeutro = c3po.tracer(saveInputMED=True, saveOutputMED=True)(NeutroDriver)
    tracedThermo = c3po.tracer(saveInputMED=True, saveOutputMED=True)(ThermoDriver)

    myThermoDrivers = []
    for i in range(4):
        myThermoDrivers.append(tracedThermo())
    myThermoDriver = c3po.CollaborativePhysicsDriver(myThermoDrivers)
    myNeutroDriver = tracedNeutro()

    cote_ass = 0.5
    cote = [-cote_ass, 0, cote_ass]
    indexTable = [0, 1,
                  2, 3]
    myRemapper = c3po.Multi1D3DRemapper(cote, cote, indexTable, [1] * len(myThermoDrivers), meshAlignment=True, offset=[0., 0., -1.], rescaling=1./100., rotation=math.pi/2., outsideCellsScreening=True)
    neutroToThermo = c3po.SharedRemappingMulti1D3D(myRemapper, reverse=True)
    thermoToNeutro = c3po.SharedRemappingMulti1D3D(myRemapper, reverse=False, defaultValue=273.15, linearTransform=(1., -273.15))

    dataCouplers = []
    for i in range(4):
        dataCouplers.append(c3po.LocalDataManager())
    dataCoupler = c3po.CollaborativeDataManager(dataCouplers)
    #exchangerNeutro2Thermo = c3po.LocalExchanger(neutroToThermo, [(myNeutroDriver, "Power")], [(thermo, "Power") for thermo in myThermoDrivers])
    #exchangerThermo2Data = c3po.LocalExchanger(c3po.DirectMatching(), [(thermo, "Temperature") for thermo in myThermoDrivers], [(data, "Temperature") for data in dataCouplers])
    #exchangerData2Neutro = c3po.LocalExchanger(thermoToNeutro, [(data, "Temperature") for data in dataCouplers], [(myNeutroDriver, "Temperature")])

    exchangerNeutro2Thermo = c3po.LocalExchanger(neutroToThermo, [(myNeutroDriver, "Power")], [(myThermoDriver, "Power")])
    exchangerThermo2Data = c3po.LocalExchanger(c3po.DirectMatching(), [(myThermoDriver, "Temperature")], [(dataCoupler, "Temperature")])
    exchangerData2Neutro = c3po.LocalExchanger(thermoToNeutro, [(dataCoupler, "Temperature")], [(myNeutroDriver, "Temperature")])

    oneIteration = OneIterationCoupler([myNeutroDriver, myThermoDriver], [exchangerNeutro2Thermo])

    mycoupler = c3po.FixedPointCoupler([oneIteration], [exchangerThermo2Data, exchangerData2Neutro], [dataCoupler])
    mycoupler.init()
    mycoupler.setDampingFactor(0.75)
    mycoupler.setConvergenceParameters(1E-5, 100)

    for i in range(4):
        myThermoDrivers[i].setT0(273.15 + i*0.1)

    mycoupler.solve()

    mycoupler.term()

    fieldT = mc.ReadField(mc.ON_CELLS, "NeutroDriver_input_Temperature_2.med", "3DMesh", 0, "3DFieldFromMulti1D", -1, -1)
    resuT = fieldT.getArray().toNumPyArray().tolist()

    assert len(refT) == len(resuT)
    for i in range(len(refT)):
        assert pytest.approx(resuT[i], abs=1.E-3) == refT[i]

    fieldP = mc.ReadField(mc.ON_CELLS, "NeutroDriver_output_Power_3.med", "3DMesh", 0, "P", -1, -1)
    resuP = fieldP.getArray().toNumPyArray().tolist()

    assert len(refP) == len(resuP)
    for i in range(len(refP)):
        assert pytest.approx(resuP[i], abs=1.E-3) == refP[i]

    medFiles = glob.glob("*.med")
    for medFile in medFiles:
        os.remove(medFile)

    myRemapper.exportMatrix("matrix_remapper.med")

def test_load_matrix():
    from tests.med_1D3D.NeutroDriver import NeutroDriver
    from tests.med_1D3D.ThermoDriver import ThermoDriver

    myThermoDrivers2 = []
    for i in range(4):
        myThermoDrivers2.append(ThermoDriver())
    myThermoDriver2 = c3po.CollaborativePhysicsDriver(myThermoDrivers2)
    myNeutroDriver2 = NeutroDriver()

    cote_ass = 0.5
    cote = [-cote_ass, 0, cote_ass]
    indexTable = [0, 1,
                  2, 3]
    myRemapper2 = c3po.Multi1D3DRemapper(cote, cote, indexTable, [1] * len(myThermoDrivers2), meshAlignment=True, offset=[0., 0., -1.], rescaling=1./100., rotation=math.pi/2., outsideCellsScreening=True)
    myRemapper2.loadMatrix("matrix_remapper.med")

    neutroToThermo2 = c3po.SharedRemappingMulti1D3D(myRemapper2, reverse=True)
    thermoToNeutro2 = c3po.SharedRemappingMulti1D3D(myRemapper2, reverse=False, defaultValue=273.15, linearTransform=(1., -273.15))

    dataCouplers2 = []
    for i in range(4):
        dataCouplers2.append(c3po.LocalDataManager())
    dataCoupler2 = c3po.CollaborativeDataManager(dataCouplers2)
    exchangerNeutro2Thermo2 = c3po.LocalExchanger(neutroToThermo2, [(myNeutroDriver2, "Power")], [(thermo, "Power") for thermo in myThermoDrivers2])
    exchangerThermo2Data2 = c3po.LocalExchanger(c3po.DirectMatching(), [(thermo, "Temperature") for thermo in myThermoDrivers2], [(data, "Temperature") for data in dataCouplers2])
    exchangerData2Neutro2 = c3po.LocalExchanger(thermoToNeutro2, [(data, "Temperature") for data in dataCouplers2], [(myNeutroDriver2, "Temperature")])

    oneIteration2 = OneIterationCoupler([myNeutroDriver2, myThermoDriver2], [exchangerNeutro2Thermo2])

    mycoupler2 = c3po.FixedPointCoupler([oneIteration2], [exchangerThermo2Data2, exchangerData2Neutro2], [dataCoupler2])
    mycoupler2.init()
    mycoupler2.setDampingFactor(0.75)
    mycoupler2.setConvergenceParameters(1E-5, 100)

    for i in range(4):
        myThermoDrivers2[i].setT0(273.15 + i*0.1)

    mycoupler2.solve()

    fieldP = myNeutroDriver2.getOutputMEDDoubleField("Power")
    resuP = fieldP.getArray().toNumPyArray().tolist()
    assert len(refP) == len(resuP)
    for i in range(len(refP)):
        assert pytest.approx(resuP[i], abs=1.E-3) == refP[i]

    mycoupler2.term()
    os.remove("matrix_remapper.med")

if __name__ == "__main__":
    test_sequential()
    test_load_matrix()
