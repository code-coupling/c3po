# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest

import icoco
import icoco.utils

import c3po
import c3po.raises

def _raise_outside_time_step(implem):
    """Test raise WrongContext outside time step"""
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.solveTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.validateTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.abortTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.iterateTimeStep()

def _raise_inside_time_step(implem):
    """Test raise WrongContext inside time step"""
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.computeTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.initTimeStep(dt=0.0)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setStationaryMode(stationaryMode=True)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.isStationary()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.resetTime(time=0.0)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.save(label=0, method="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.restore(label=0, method="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.terminate()

def _raises_after_initialize(implem):
    """Test raise WrongContext after initialize"""
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.initialize()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setDataFile(__file__)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setMPIComm(None)

def _raises_before_initialize(implem):
    """Test raise WrongContext before initialize"""
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.computeTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.initTimeStep(dt=0.0)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.solveTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.validateTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setStationaryMode(stationaryMode=True)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getStationaryMode()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.presentTime()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.terminate()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.isStationary()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.abortTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.resetTime(time=0.0)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.iterateTimeStep()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.save(label=0, method="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.restore(label=0, method="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.forget(label=0, method="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getInputFieldsNames()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getOutputFieldsNames()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getFieldType(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getMeshUnit()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getFieldUnit(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getInputMEDDoubleFieldTemplate(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setInputMEDDoubleField(name="", afield=None)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getOutputMEDDoubleField(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.updateOutputMEDDoubleField(name="", afield=None)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getInputMEDIntFieldTemplate(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setInputMEDIntField(name="", afield=None)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getOutputMEDIntField(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.updateOutputMEDIntField(name="", afield=None)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getInputMEDStringFieldTemplate(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setInputMEDStringField(name="", afield=None)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getOutputMEDStringField(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.updateOutputMEDStringField(name="", afield=None)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getInputValuesNames()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getOutputValuesNames()
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getValueType(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getValueUnit(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setInputDoubleValue(name="", val=0.0)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getOutputDoubleValue(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setInputIntValue(name="", val=0)
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getOutputIntValue(name="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.setInputStringValue(name="", val="")
    with pytest.raises(expected_exception=icoco.WrongContext):
        implem.getOutputStringValue(name="")

def test_checkScope():
    def buildUselessMethod(name):
        def useless(self, *args, **kwargs):
            pass
        useless.__name__ = name
        return useless

    dictICoCo = {}
    for nameMethod in icoco.utils.ICoCoMethods.ALL:
        dictICoCo[nameMethod] = buildUselessMethod(nameMethod)
    DummyICoCo = type("DummyICoCo", (), dictICoCo)
    CheckedDommyICoCo = c3po.raises.checkScope(DummyICoCo)

    dummyIcoco = CheckedDommyICoCo()
    dummyIcoco.problemName = "dummyProblem"

    with pytest.raises(expected_exception=icoco.WrongContext) as excinfo:
        dummyIcoco.computeTimeStep()
    assert str(excinfo.value) == "WrongContext in Problem instance with name: 'dummyProblem' in method 'computeTimeStep' : called before initialize() or after terminate()."

    _raises_before_initialize(implem=dummyIcoco)
    print("Verification des methodes a ne pas appeler avant initialisation faite.")

    dummyIcoco.setDataFile()
    dummyIcoco.initialize()

    _raises_after_initialize(implem=dummyIcoco)
    print("Verification des methodes a ne pas appeler apres initialisation faite.")

    _raise_outside_time_step(implem=dummyIcoco)
    print("Verification des methodes a ne pas appeler en dehors du contexte TIME_STEP_DEFINED faite.")

    dummyIcoco.initTimeStep(dt=1.)
    _raise_inside_time_step(implem=dummyIcoco)
    print("Verification des methodes a ne pas appeler a l'interieur du contexte TIME_STEP_DEFINED faite.")

    dummyIcoco.iCoCoEnsureScope = False
    dummyIcoco.computeTimeStep()
    dummyIcoco.iCoCoEnsureScope = True
    with pytest.raises(expected_exception=icoco.WrongContext):
        dummyIcoco.computeTimeStep()

@c3po.raises.checkScope
class decoredICoCo:
    def __init__(self):
        pass

    def initTimeStep(self, dt):
        pass

class metaICoCo(metaclass=c3po.raises.CheckScopeMeta): #python3
    #__metaclass__ = c3po.raises.CheckScopeMeta        #python2
    def initTimeStep(self, dt):
        pass

def test_decorator():
    dummyIcoco = decoredICoCo()
    with pytest.raises(expected_exception=icoco.WrongContext):
        dummyIcoco.initTimeStep(1.)

def test_metaUse():
    dummyIcoco = metaICoCo()
    with pytest.raises(expected_exception=icoco.WrongContext):
        dummyIcoco.initTimeStep(1.)

if __name__ == "__main__":
    test_checkScope()
    test_decorator()
    test_metaUse()
