"""Tests for handling mathematica's binary object representation.

This is primarily useful for dealing with compressed fields.
"""


from pyecl.models import ConstellationFieldParser


def testDecompressInteger():
    """Compress[4] -> 1:eJxTTMoPymRhYGAAAAtUAbI="""
    assert (
        ConstellationFieldParser().decompress_field(b"1:eJxTTMoPymRhYGAAAAtUAbI=")
        == "4"
    )


def testDecompressLargeInteger():
    """Compress[90348590834890590349058038945] -> "1:eJxTTMoP8pRlYGCwNDA2sTC1NLAAUpYGpiAukLIwMLawNDEFAJVXB6k=" """
    assert (
        ConstellationFieldParser().decompress_field(
            b"1:eJxTTMoP8pRlYGCwNDA2sTC1NLAAUpYGpiAukLIwMLawNDEFAJVXB6k="
        )
        == "90348590834890590349058038945"
    )


def testDecompressSimpleFloat():
    """Compress[4.0] -> "1:eJxTTMoPKmIAAwEHABKtAgc=" """
    assert (
        ConstellationFieldParser().decompress_field(b"1:eJxTTMoPKmIAAwEHABKtAgc=")
        == "4.0"
    )


def testDecompressComplexFloat():
    """Compress[3.432643] -> "1:eJxTTMoPKlLeX9fBW8btAAAgJgRt" """
    assert (
        ConstellationFieldParser().decompress_field(b"1:eJxTTMoPKlLeX9fBW8btAAAgJgRt")
        == "3.432643"
    )


def testDecompressString():
    """Compress["Hi There!"] -> "1:eJxTTMoPCuZkYGDwyFQIyUgtSlUEACgoBIs=" """
    assert (
        ConstellationFieldParser().decompress_field(
            b"1:eJxTTMoPCuZkYGDwyFQIyUgtSlUEACgoBIs="
        )
        == "Hi There!"
    )


def testDecompressSymbol():
    """Compress[Login] -> "1:eJxTTMoPKmZlYGDwyU/PzAMAGegDtg==" """
    assert (
        ConstellationFieldParser().decompress_field(
            b"1:eJxTTMoPKmZlYGDwyU/PzAMAGegDtg=="
        )
        == "Login"
    )


def testDecompressEmptyList():
    """Compress[{}] -> "1:eJxTTMoPSmMAgmIWIOGTWVwCACIoA74=" """
    assert (
        ConstellationFieldParser().decompress_field(
            b"1:eJxTTMoPSmMAgmIWIOGTWVwCACIoA74="
        )
        == "List[]"
    )


def testDecompressListOfNumbers():
    """Compress[{1, 2}] -> "1:eJxTTMoPSmNiYGAoZgESPpnFJZmMQEYmSAgATfoElQ==" """
    assert (
        ConstellationFieldParser().decompress_field(
            b"1:eJxTTMoPSmNiYGAoZgESPpnFJZmMQEYmSAgATfoElQ=="
        )
        == "List[1, 2]"
    )


def testDecompressLargeMatrix():
    """Large matricies of real numbers get compresed into a special format, which we test here"""
    parsed_field = ConstellationFieldParser().parse_variable_unit_field(
        b"1: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"
    )

    # The result should look like:
    # {{0.min,-87.529Lsus},{0.016667min,-96.7016Lsus},<<357>>,{5.98333min,1742.05Lsus},{6.min,1009.1Lsus}}

    assert len(parsed_field) == 361
    assert parsed_field[0][0].value == 0.0
    assert parsed_field[0][0].unit == "Minutes"
    assert parsed_field[0][1].value == -87.528984
    assert parsed_field[0][1].unit == "IndependentUnit[Lsus]"
    assert parsed_field[-1][0].value == 6.0
    assert parsed_field[-1][0].unit == "Minutes"
    assert parsed_field[-1][1].value == 1009.098328
    assert parsed_field[-1][1].unit == "IndependentUnit[Lsus]"
