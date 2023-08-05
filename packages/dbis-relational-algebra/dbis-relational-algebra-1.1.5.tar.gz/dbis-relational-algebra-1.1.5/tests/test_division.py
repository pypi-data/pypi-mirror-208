import pytest

from relational_algebra import *


def test_division_symbol():
    r1 = Relation("R1")
    r2 = Relation("R2")
    assert isinstance(r1 / r2, Division)


def test_division():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b", "c", "d"])
    r2.add_attributes(["c", "d"])
    r1.add_rows(
        [
            ["a", "a", "a", "a"],
            ["a", "a", "b", "d"],
            ["a", "b", "e", "f"],
            ["z", "z", "y", "x"],
            ["z", "z", "b", "d"],
            ["z", "z", "e", "f"],
            ["o", "o", "o", "o"],
        ]
    )
    r2.add_rows(
        [
            ["b", "d"],
            ["e", "f"],
        ]
    )
    d = r1 / r2
    result = d.evaluate()
    rows = result.rows
    assert result.get_minimal_attribute_names(result.attributes) == ["a", "b"]
    assert set(rows) == {
        ("z", "z"),
    }
