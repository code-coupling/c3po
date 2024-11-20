# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest

import c3po


class Alphabetic(c3po.PhysicsDriver):
    """This is the test case PhysicsDriver.

    It accepts only alphabetic characters as names for io.

    see `get[Output/Inputs][Fields/Values]Names` for avaliable keys.

    `chr(65)` is `'A'`. `range(65, 70)` is the integer range to get 'A B C D E' from `int`.

    variable naming:
        "o" -> "output"
        "i" -> "input"
        "f" -> "field"
        "e" -> "exclusive"
    """

    of_range = range(65, 70)
    """numeric range for o(utput)f(ield)"""
    if_range = range(68, 73)
    """numeric range for i(nput)f(ield)"""
    iof_range = range(if_range.start, of_range.stop)
    """common field range"""
    oef_range = range(of_range.start, if_range.start)
    """exclusive field output"""
    ief_range = range(of_range.stop, if_range.stop)
    """exclusive field inpout"""
    f_range = range(of_range.start, if_range.stop)
    """full field range"""
    ov_range = range(73, 78)
    """numeric range for o(utput)v(alue)"""
    iv_range = range(76, 81)
    """numeric range for i(nput)v(alue)"""
    iov_range = range(iv_range.start, ov_range.stop)
    """common value range"""
    oev_range = range(ov_range.start, iv_range.start)
    """exclusive value output"""
    iev_range = range(ov_range.stop, iv_range.stop)
    """exclusive value inpout"""
    v_range = range(ov_range.start, iv_range.stop)
    """full value range"""

    def getOutputFieldsNames(self):
        "returns `['A', 'B', 'C', 'D', 'E']`"
        return list(map(chr, Alphabetic.of_range))

    def getInputFieldsNames(self):
        "returns `['D', 'E', 'F', 'G', 'H']`"
        return list(map(chr, Alphabetic.if_range))

    def getOutputValuesNames(self):
        "returns `['I', 'J', 'K', 'L', 'M']`"
        return list(map(chr, Alphabetic.ov_range))

    def getInputValuesNames(self):
        "returns `['N', 'O', 'P', 'Q', 'R']`"
        return list(map(chr, Alphabetic.iv_range))

    def _getAllFieldsNames(self):
        return set(self.getOutputFieldsNames() + self.getInputFieldsNames())

    def getFieldType(self, name):
        """ A devient a, B b etc. """
        return {_name: _name.lower() for _name in self._getAllFieldsNames()}[name]

    def getFieldUnit(self, name):
        """ A devient A_a, B B_b etc. """
        return {_name: f"{_name}_{_name.lower()}" for _name in self._getAllFieldsNames()}[name]

    def _getAllValuesNames(self):
        return set(self.getOutputValuesNames() + self.getInputValuesNames())

    def getValueType(self, name):
        return {_name: _name.lower() for _name in self._getAllValuesNames()}[name]

    def getValueUnit(self, name):
        return {_name: f"{_name}_{_name.lower()}" for _name in self._getAllValuesNames()}[name]

    def getInputMEDDoubleFieldTemplate(self, name):
        if name not in self.getInputFieldsNames():
            raise ValueError(f"name {name} not in {self.getInputFieldsNames()}")
        return f"DoubleField_template_{name}"

    def setInputMEDDoubleField(self, name, field):
        if name not in self.getInputFieldsNames():
            raise ValueError(f"name {name} not in {self.getInputFieldsNames()}")

    def getOutputMEDDoubleField(self, name):
        if name not in self.getOutputFieldsNames():
            raise ValueError(f"name {name} not in {self.getOutputFieldsNames()}")
        return f"DoubleField_{name}"

    def updateOutputMEDDoubleField(self, name, field):
        if name not in self.getOutputFieldsNames():
            raise ValueError(f"name {name} not in {self.getOutputFieldsNames()}")

    def getInputMEDIntFieldTemplate(self, name):
        if name not in self.getInputFieldsNames():
            raise ValueError(f"name {name} not in {self.getInputFieldsNames()}")
        return f"IntField__template_{name}"

    def setInputMEDIntField(self, name, field):
        if name not in self.getInputFieldsNames():
            raise ValueError(f"name {name} not in {self.getInputFieldsNames()}")

    def getOutputMEDIntField(self, name):
        if name not in self.getOutputFieldsNames():
            raise ValueError(f"name {name} not in {self.getOutputFieldsNames()}")
        return f"IntField_{name}"

    def updateOutputMEDIntField(self, name, field):
        if name not in self.getOutputFieldsNames():
            raise ValueError(f"name {name} not in {self.getOutputFieldsNames()}")

    def setInputDoubleValue(self, name, value):
        if name not in self.getInputValuesNames():
            raise ValueError(f"name {name} not in {self.getInputValuesNames()}")

    def getOutputDoubleValue(self, name):
        if name not in self.getOutputValuesNames():
            raise ValueError(f"name {name} not in {self.getOutputValuesNames()}")

    def setInputIntValue(self, name, value):
        if name not in self.getInputValuesNames():
            raise ValueError(f"name {name} not in {self.getInputValuesNames()}")

    def getOutputIntValue(self, name):
        if name not in self.getOutputValuesNames():
            raise ValueError(f"name {name} not in {self.getOutputValuesNames()}")

    def setInputStringValue(self, name, value):
        if name not in self.getInputValuesNames():
            raise ValueError(f"name {name} not in {self.getInputValuesNames()}")

    def getOutputStringValue(self, name):
        if name not in self.getOutputValuesNames():
            raise ValueError(f"name {name} not in {self.getOutputValuesNames()}")


def test_name_changer():

    def check_names(numeric_method, alphabetic_method, io_range, exclusive, full_range):
        """check names of the numeric and alphabetic APIs

        Parameters
        ----------
        numeric_method : Callable
            get...Names method for numeric (name changed) API
        alphabetic_method : Callable
            get...Names method for alphabetic (initial) API
        io_range : range
            expected range for the test
        exclusive : bool
            is the API excluding initial API of not
        full_range : range
            full theoretical range if API is not restricted
        """

        for name in numeric_method(): #On verifie qu'avec les chiffres plutot que les lettres, que les listes renvoyees contiennent des elements licites.
            if not exclusive:
                assert (name in [str(i) for i in io_range] or name in [chr(i) for i in full_range]) #chr(65) -> A
            else:
                assert name in [str(i) for i in io_range]

        for i in (full_range if full_range is not None else io_range):  #On va passer en revue tous les elements possibles.
            assert chr(i) in alphabetic_method()        #On verifie que le retrouve bien dans la methode d'origine.
            if not exclusive:
                assert chr(i) in numeric_method()       #On verifie que 'A' est toujours renvoye
            else:
                with pytest.raises(AssertionError):
                    assert chr(i) in numeric_method()   #Et la on verifie que ce n'est pas le cas.
            if i in io_range:
                assert str(i) in numeric_method()       #S'il est dans la liste demandee, on verifie que 65 est bien renvoye.
            else:
                with pytest.raises(AssertionError):
                    assert str(i) in numeric_method()   #Et la on verifie qu'il n'y est pas.


    def check_unit_or_type(numeric_method, alphabetic_method, io_range, exclusive, to_check, full_range):
        """check units or types of the numeric and alphabetic APIs

        Parameters
        ----------
        numeric_method : Callable
            get...Names method for numeric (name changed) API
        alphabetic_method : Callable
            get...Names method for alphabetic (initial) API
        io_range : range
            expected range for the test
        exclusive : bool
            is the API excluding initial API of not
        to_check : str
            "unit" or "type"
        full_range : range
            full theoretical range if API is not restricted
        """

        for i in (full_range if full_range is not None else io_range):  #On va passer en revue tous les elements possibles.
            alphabetic_name = chr(i)
            numeric_name = str(i)
            if to_check == "unit":
                ref_name = f"{alphabetic_name}_{alphabetic_name.lower()}"
            elif to_check == "type":
                ref_name = alphabetic_name.lower()
            assert ref_name == alphabetic_method(alphabetic_name)       #On verifie que le resultat est correct avec les methodes d'origine ('A').
            if not exclusive:
                assert ref_name == numeric_method(alphabetic_name)      #On verifie qu'on peut obtenir le meme resultat a partir des lettres si pas exclusif.
            else:
                with pytest.raises(ValueError):
                    numeric_method(alphabetic_name)                     #et que sinon non.
            if i in io_range:
                assert ref_name == numeric_method(numeric_name)         #Si dans le range demande, on regarde que c'est aussi correct avec les chiffres.
            else:
                with pytest.raises(ValueError):
                    numeric_method(numeric_name)                        #Indisponible avec les chiffres.


    def check_unit(numeric_method, alphabetic_method, io_range, exclusive, full_range = None):
        """check units of the numeric and alphabetic APIs"""
        check_unit_or_type(numeric_method, alphabetic_method, io_range, exclusive, "unit", full_range)

    def check_type(numeric_method, alphabetic_method, io_range, exclusive, full_range = None):
        """check types of the numeric and alphabetic APIs"""
        check_unit_or_type(numeric_method, alphabetic_method, io_range, exclusive, "type", full_range)


    def check_fields(set_method, get_method, io_range, exclusive, full_range):
        """check fields of the numeric and alphabetic APIs

        Parameters
        ----------
        set_method : Callable
            setInput... method
        get_method : Callable
            getOutput... method
        io_range : range
            expected range for the test
        exclusive : bool
            is the API excluding initial API of not
        full_range : range
            full theoretical range if API is not restricted
        """

        for i in (full_range if full_range is not None else io_range):  #On va passer en revue tous les elements possibles.
            alphabetic_name = chr(i)
            numeric_name = str(i)
            if not exclusive:
                get_method(alphabetic_name)                             #On verifie qu'avec les lettres ca fonctionne toujours.
                set_method(alphabetic_name, "any")
            else:
                with pytest.raises(ValueError):
                    get_method(alphabetic_name)                         #Ou pas.
                with pytest.raises(ValueError):
                    set_method(alphabetic_name, "any")
            if i in io_range:
                get_method(numeric_name)                                #Si dans le range demande, on regarde que c'est aussi correct avec les chiffres.
                set_method(numeric_name, "any")
            else:                                                       #Et que ca ne marche pas sinon.
                with pytest.raises(ValueError):
                    get_method(numeric_name)
                with pytest.raises(ValueError):
                    set_method(numeric_name, "any")


    def check_values(set_method, get_method, o_range, i_range, exclusive, full_ranges):
        """check values of the numeric and alphabetic APIs

        Parameters
        ----------
        set_method : Callable
            setInput... method
        get_method : Callable
            getOutput... method
        o_range : range
            expected output range for the test
        i_range : range
            expected input range for the test
        exclusive : bool
            is the API excluding initial API of not
        full_range : (range, range)
            full theoretical range if API is not restricted
        """

        full_o_range = full_ranges[0] if full_ranges is not None else o_range
        full_i_range = full_ranges[1] if full_ranges is not None else i_range

        for full_x_range, x_range, xet_method, args in [
                (full_o_range, o_range, get_method, [None]),
                (full_i_range, i_range, set_method, [None, "Any"])]:        #cote get puis cote set

            for i in full_x_range:                                          #On va passer en revue tous les elements possibles.
                alphabetic_name = chr(i)
                numeric_name = str(i)
                args[0] = alphabetic_name
                if not exclusive:
                    xet_method(*args)                                       #On verifie qu'avec les lettres ca fonctionne toujours.
                else:
                    with pytest.raises(ValueError):                           #Ou pas
                        xet_method(*args)
                if i in x_range:
                    args[0] = numeric_name
                    xet_method(*args)                                       #Si dans le range demande, on regarde que c'est aussi correct avec les chiffres.
                else:                                                       #Et que ca ne marche pas sinon.
                    args[0] = numeric_name
                    with pytest.raises(ValueError):
                        xet_method(*args)


    # interface names are letters
    alphabetic = Alphabetic()

    # Non exclusive, non I/O dinstinction
    # creates an API with interface names containing letters and the associated integer
    nameMappingField={str(i): chr(i) for i in range(alphabetic.of_range.start, alphabetic.if_range.stop)}
    nameMappingValue={str(i): chr(i) for i in range(alphabetic.ov_range.start, alphabetic.iv_range.stop)}
    exclusive = False
    numeric = c3po.NameChanger(physics=alphabetic,
                               nameMappingValue=nameMappingValue,
                               nameMappingField=nameMappingField,
                               exclusive=exclusive)

    check_names(numeric.getOutputFieldsNames, alphabetic.getOutputFieldsNames, Alphabetic.of_range, exclusive, Alphabetic.of_range)
    check_names(numeric.getInputFieldsNames, alphabetic.getInputFieldsNames, Alphabetic.if_range, exclusive, Alphabetic.if_range)
    check_names(numeric.getOutputValuesNames, alphabetic.getOutputValuesNames, Alphabetic.ov_range, exclusive, Alphabetic.ov_range)
    check_names(numeric.getInputValuesNames, alphabetic.getInputValuesNames, Alphabetic.iv_range, exclusive, Alphabetic.iv_range)
    check_unit(numeric.getFieldUnit, alphabetic.getFieldUnit, Alphabetic.f_range, exclusive)
    check_unit(numeric.getValueUnit, alphabetic.getValueUnit, Alphabetic.v_range, exclusive)
    check_type(numeric.getFieldType, alphabetic.getFieldType, Alphabetic.f_range, exclusive)
    check_type(numeric.getValueType, alphabetic.getValueType, Alphabetic.v_range, exclusive)
    check_fields(numeric.updateOutputMEDDoubleField, numeric.getOutputMEDDoubleField, Alphabetic.of_range, exclusive, Alphabetic.of_range)
    check_fields(numeric.setInputMEDDoubleField, numeric.getInputMEDDoubleFieldTemplate, Alphabetic.if_range, exclusive, Alphabetic.if_range)
    check_fields(numeric.updateOutputMEDIntField, numeric.getOutputMEDIntField, Alphabetic.of_range, exclusive, Alphabetic.of_range)
    check_fields(numeric.setInputMEDIntField, numeric.getInputMEDIntFieldTemplate, Alphabetic.if_range, exclusive, Alphabetic.if_range)
    check_values(numeric.setInputDoubleValue, numeric.getOutputDoubleValue, Alphabetic.ov_range, Alphabetic.iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])
    check_values(numeric.setInputIntValue, numeric.getOutputIntValue, Alphabetic.ov_range, Alphabetic.iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])
    check_values(numeric.setInputStringValue, numeric.getOutputStringValue, Alphabetic.ov_range, Alphabetic.iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])

    # Exclusive, non I/O dinstinction
    # creates an API with interface names containing only integers, masking letters
    exclusive = True
    numeric = c3po.NameChanger(physics=alphabetic,
                               nameMappingValue=nameMappingValue,
                               nameMappingField=nameMappingField,
                               exclusive=exclusive)
    check_names(numeric.getOutputFieldsNames, alphabetic.getOutputFieldsNames, Alphabetic.of_range, exclusive, Alphabetic.of_range)
    check_names(numeric.getInputFieldsNames, alphabetic.getInputFieldsNames, Alphabetic.if_range, exclusive, Alphabetic.if_range)
    check_names(numeric.getOutputValuesNames, alphabetic.getOutputValuesNames, Alphabetic.ov_range, exclusive, Alphabetic.ov_range)
    check_names(numeric.getInputValuesNames, alphabetic.getInputValuesNames, Alphabetic.iv_range, exclusive, Alphabetic.iv_range)
    check_unit(numeric.getFieldUnit, alphabetic.getFieldUnit, Alphabetic.f_range, exclusive)
    check_unit(numeric.getValueUnit, alphabetic.getValueUnit, Alphabetic.v_range, exclusive)
    check_type(numeric.getFieldType, alphabetic.getFieldType, Alphabetic.f_range, exclusive)
    check_type(numeric.getValueType, alphabetic.getValueType, Alphabetic.v_range, exclusive)
    check_fields(numeric.updateOutputMEDDoubleField, numeric.getOutputMEDDoubleField, Alphabetic.of_range, exclusive, Alphabetic.of_range)
    check_fields(numeric.setInputMEDDoubleField, numeric.getInputMEDDoubleFieldTemplate, Alphabetic.if_range, exclusive, Alphabetic.if_range)
    check_fields(numeric.updateOutputMEDIntField, numeric.getOutputMEDIntField, Alphabetic.of_range, exclusive, Alphabetic.of_range)
    check_fields(numeric.setInputMEDIntField, numeric.getInputMEDIntFieldTemplate, Alphabetic.if_range, exclusive, Alphabetic.if_range)
    check_values(numeric.setInputDoubleValue, numeric.getOutputDoubleValue, Alphabetic.ov_range, Alphabetic.iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])
    check_values(numeric.setInputIntValue, numeric.getOutputIntValue, Alphabetic.ov_range, Alphabetic.iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])
    check_values(numeric.setInputStringValue, numeric.getOutputStringValue, Alphabetic.ov_range, Alphabetic.iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])

    # tests all combinations for name mapping different for input and output

    def test_case(exclusive: bool, of_range: range, if_range: range, ov_range: range, iv_range: range):
        """test one combinaison with overlapping or not names between input and outputs.

        Parameters
        ----------
        exclusive : bool
            exclusive API or not
        of_range : range
            output field range for name mapping
        if_range : range
            input field range for name mapping
        ov_range : range
            output value range for name mapping
        iv_range : range
            input value range for name mapping
        """
        # creates a numeric API from alphabetic API, exclusive or not.
        numeric = c3po.NameChanger(physics=alphabetic, exclusive=exclusive)
        # defines name mapping for field and values differently for input and outputs.
        numeric.updateNameMappingField(nameMappingField={str(i): chr(i) for i in of_range}, variableTypes=[0])
        numeric.updateNameMappingField(nameMappingField={str(i): chr(i) for i in if_range}, variableTypes=[1])
        numeric.updateNameMappingValue(nameMappingValue={str(i): chr(i) for i in ov_range}, variableTypes=[0])
        numeric.updateNameMappingValue(nameMappingValue={str(i): chr(i) for i in iv_range}, variableTypes=[1])
        # Do the same tests as for the previous cases.
        f_list = list(of_range) + list(if_range)
        v_list = list(ov_range) + list(iv_range)
        check_names(numeric.getOutputFieldsNames, alphabetic.getOutputFieldsNames, of_range, exclusive, Alphabetic.of_range)
        check_names(numeric.getInputFieldsNames, alphabetic.getInputFieldsNames, if_range, exclusive, Alphabetic.if_range)
        check_names(numeric.getOutputValuesNames, alphabetic.getOutputValuesNames, ov_range, exclusive, Alphabetic.ov_range)
        check_names(numeric.getInputValuesNames, alphabetic.getInputValuesNames, iv_range, exclusive, Alphabetic.iv_range)
        check_unit(numeric.getFieldUnit, alphabetic.getFieldUnit, f_list, exclusive, Alphabetic.f_range)
        check_unit(numeric.getValueUnit, alphabetic.getValueUnit, v_list, exclusive, Alphabetic.v_range)
        check_type(numeric.getFieldType, alphabetic.getFieldType, f_list, exclusive, Alphabetic.f_range)
        check_type(numeric.getValueType, alphabetic.getValueType, v_list, exclusive, Alphabetic.v_range)
        check_fields(numeric.updateOutputMEDDoubleField, numeric.getOutputMEDDoubleField, of_range, exclusive, Alphabetic.of_range)
        check_fields(numeric.setInputMEDDoubleField, numeric.getInputMEDDoubleFieldTemplate, if_range, exclusive, Alphabetic.if_range)
        check_fields(numeric.updateOutputMEDIntField, numeric.getOutputMEDIntField, of_range, exclusive, Alphabetic.of_range)
        check_fields(numeric.setInputMEDIntField, numeric.getInputMEDIntFieldTemplate, if_range, exclusive, Alphabetic.if_range)
        check_values(numeric.setInputDoubleValue, numeric.getOutputDoubleValue, ov_range, iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])
        check_values(numeric.setInputIntValue, numeric.getOutputIntValue, ov_range, iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])
        check_values(numeric.setInputStringValue, numeric.getOutputStringValue, ov_range, iv_range, exclusive, [Alphabetic.ov_range, Alphabetic.iv_range])

    # recouvrement complet api complete
    test_case(False, Alphabetic.of_range, Alphabetic.if_range, Alphabetic.ov_range, Alphabetic.iv_range)
    test_case(True, Alphabetic.of_range, Alphabetic.if_range, Alphabetic.ov_range, Alphabetic.iv_range)

    # pas de recouvrement
    test_case(False, Alphabetic.of_range, Alphabetic.ief_range, Alphabetic.ov_range, Alphabetic.iev_range)
    test_case(True, Alphabetic.of_range, Alphabetic.ief_range, Alphabetic.ov_range, Alphabetic.iev_range)

    # pas de recouvrement inverse
    test_case(False, Alphabetic.oef_range, Alphabetic.if_range, Alphabetic.oev_range, Alphabetic.iv_range)
    test_case(True, Alphabetic.oef_range, Alphabetic.if_range, Alphabetic.oev_range, Alphabetic.iv_range)

    # pas de recouvrement api partielle
    test_case(False, Alphabetic.oef_range, Alphabetic.ief_range, Alphabetic.oev_range, Alphabetic.iev_range)
    test_case(True, Alphabetic.oef_range, Alphabetic.ief_range, Alphabetic.oev_range, Alphabetic.iev_range)

    # recouvrement partiel api partielle
    test_case(False, Alphabetic.of_range, Alphabetic.iof_range, Alphabetic.ov_range, Alphabetic.iov_range)
    test_case(True, Alphabetic.of_range, Alphabetic.iof_range, Alphabetic.ov_range, Alphabetic.iov_range)

    # recouvrement partiel api partielle inverse
    test_case(False, Alphabetic.iof_range, Alphabetic.if_range, Alphabetic.iov_range, Alphabetic.iv_range)
    test_case(True, Alphabetic.iof_range, Alphabetic.if_range, Alphabetic.iov_range, Alphabetic.iv_range)

    # recouvrement complet api partielle
    test_case(False, Alphabetic.iof_range, Alphabetic.iof_range, Alphabetic.iov_range, Alphabetic.iov_range)
    test_case(True, Alphabetic.iof_range, Alphabetic.iof_range, Alphabetic.iov_range, Alphabetic.iov_range)


if __name__ == "__main__":
    test_name_changer()
