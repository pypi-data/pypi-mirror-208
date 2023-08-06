"""Tests for handling variable units.
"""

from pyecl.models import VariableUnitValue


def testParseSingleVariableUnit():
    """220 nm"""
    mm_expression = 'Quantity[220, "Nanometers"]'
    expected_output = VariableUnitValue(220, "Nanometers")
    result = VariableUnitValue.parse_mathematica_expression(mm_expression)
    assert result == expected_output


def testParseDoubleVariableUnit():
    """{220 nm, 25. C}"""
    mm_expression = 'QuantityArray[StructuredArray`StructuredData[{2},{{220, 25.}, {"Nanometers", "DegreesCelsius"}, {{1}}}]]'
    expected_output = [
        VariableUnitValue(220, "Nanometers"),
        VariableUnitValue(25.0, "DegreesCelsius"),
    ]
    result = VariableUnitValue.parse_mathematica_expression(mm_expression)
    assert len(result) == len(expected_output)
    for x, y in zip(result, expected_output):
        assert x == y


def testParseDoubleDoubleVariableUnit():
    """{{220 nm, 25. C}, {221 nm, 25. C}}"""
    mm_expression = 'QuantityArray[StructuredArray`StructuredData[{2, 2}, {{{220, 25.}, {221, 25.}}, {"Nanometers", "DegreesCelsius"}, {{1}, {2}}}]]'
    expected_output = [
        [
            VariableUnitValue(220, "Nanometers"),
            VariableUnitValue(25.0, "DegreesCelsius"),
        ],
        [
            VariableUnitValue(221, "Nanometers"),
            VariableUnitValue(25.0, "DegreesCelsius"),
        ],
    ]
    result = VariableUnitValue.parse_mathematica_expression(mm_expression)
    assert len(result) == len(expected_output)
    for x, y in zip(result, expected_output):
        assert x == y


def testParseNestedStructuredArrayVariableUnit():
    """{{220 nm, 25. C}}"""
    mm_expression = "StructuredArray[QuantityArray, List[1, 2], StructuredArray`StructuredData[QuantityArray, List[List[220, 25.0]], List[Nanometers, DegreesCelsius], List[List[1], List[2]]]]"
    expected_output = [
        [
            VariableUnitValue(220, "Nanometers"),
            VariableUnitValue(25.0, "DegreesCelsius"),
        ]
    ]
    result = VariableUnitValue.parse_mathematica_expression(mm_expression)
    assert len(result) == len(expected_output)
    for x, y in zip(result, expected_output):
        assert x == y
