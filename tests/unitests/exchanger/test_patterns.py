# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest

import c3po


class ToTestPatterns(c3po.ExchangeMethod):
    def __init__(self):
        self._pattern = []

    def setPattern(self, lenFieldsToGet, lenFieldsToSet, lenValuesToGet, lenValuesToSet):
        self._pattern.append((lenFieldsToGet, lenFieldsToSet, lenValuesToGet, lenValuesToSet))

    def getPatterns(self):
        return self._pattern


def test_patterns():
    directMatchingPattern = ToTestPatterns()
    directMatchingPattern.setPattern(1, 1, 0, 0)
    directMatchingPattern.setPattern(0, 0, 1, 1)

    newLists = c3po.LocalExchanger._divideInputsAccordingToPatterns(directMatchingPattern, ["fieldToGet1", "fieldToGet2"], ["fieldToSet1", "fieldToSet2"],
                                                                    ["valueToGet1", "valueToGet2", "valueToGet3"], ["valueToSet1", "valueToSet2", "valueToSet3"])
    assert newLists == [[["fieldToGet1"], ["fieldToSet1"], [], []],
                        [["fieldToGet2"], ["fieldToSet2"], [], []],
                        [[], [], ["valueToGet1"], ["valueToSet1"]],
                        [[], [], ["valueToGet2"], ["valueToSet2"]],
                        [[], [], ["valueToGet3"], ["valueToSet3"]]]

    with pytest.raises(Exception) as excinfo:
        newLists = c3po.LocalExchanger._divideInputsAccordingToPatterns(directMatchingPattern, ["fieldToGet1", "fieldToGet2"], ["fieldToSet1"],
                                                                        ["valueToGet1", "valueToGet2", "valueToGet3"], ["valueToSet1", "valueToSet2", "valueToSet3"])
    print(excinfo.value)

    complicatedPattern = ToTestPatterns()
    complicatedPattern.setPattern(1, 1, -1, 0)
    complicatedPattern.setPattern(1, 0, 0, 1)

    newLists = c3po.LocalExchanger._divideInputsAccordingToPatterns(complicatedPattern, ["fieldToGet1", "fieldToGet2", "fieldToGet3"], ["fieldToSet1", "fieldToSet2"],
                                                                    ["valueToGet1", "valueToGet2", "valueToGet3"], ["valueToSet1"])
    assert newLists == [[["fieldToGet1"], ["fieldToSet1"], ["valueToGet1", "valueToGet2", "valueToGet3"], []],
                        [["fieldToGet2"], ["fieldToSet2"], ["valueToGet1", "valueToGet2", "valueToGet3"], []],
                        [["fieldToGet3"], [], [], ["valueToSet1"]]]

    impossiblePattern = ToTestPatterns()
    impossiblePattern.setPattern(1, 1, -1, 0)
    impossiblePattern.setPattern(1, 0, 1, 1)

    with pytest.raises(Exception) as excinfo:
        newLists = c3po.LocalExchanger._divideInputsAccordingToPatterns(impossiblePattern, ["fieldToGet1", "fieldToGet2", "fieldToGet3"], ["fieldToSet1", "fieldToSet2"],
                                                                        ["valueToGet1", "valueToGet2", "valueToGet3"], ["valueToSet1"])
    print(excinfo.value)

    noPatter = ToTestPatterns()
    noPatter.setPattern(-1, -1, -1, -1)

    newLists = c3po.LocalExchanger._divideInputsAccordingToPatterns(noPatter, ["fieldToGet1", "fieldToGet2"], ["fieldToSet1", "fieldToSet2"],
                                                                    ["valueToGet1", "valueToGet2"], ["valueToSet1"])
    assert newLists == [[["fieldToGet1", "fieldToGet2"], ["fieldToSet1", "fieldToSet2"], ["valueToGet1", "valueToGet2"], ["valueToSet1"]]]

    def justAFunction(fieldsToGet, fieldsToSet, valuesToGet):
        return fieldsToGet, valuesToGet

    newLists = c3po.LocalExchanger._divideInputsAccordingToPatterns(justAFunction, ["fieldToGet1", "fieldToGet2"], ["fieldToSet1", "fieldToSet2"],
                                                                    ["valueToGet1", "valueToGet2"], ["valueToSet1"])
    assert newLists == [[["fieldToGet1", "fieldToGet2"], ["fieldToSet1", "fieldToSet2"], ["valueToGet1", "valueToGet2"], ["valueToSet1"]]]


if __name__ == "__main__":
    test_patterns()
