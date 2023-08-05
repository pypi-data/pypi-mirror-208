import pytest

from relational_algebra import *


def test_leftsemijoin():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b", "c"])
    r2.add_attributes(["c", "d"])
    r1.add_rows(
        [
            ["a", "a", "q"],
            ["b", "b", "r"],
            ["c", "c", "s"],
            ["d", "d", "t"],
        ]
    )
    r2.add_rows(
        [
            ["r", "x"],
            ["t", "y"],
        ]
    )
    lsj = LeftSemiJoin(r1, r2)
    result = lsj.evaluate()
    rows = result.rows
    assert result.get_minimal_attribute_names(result.attributes) == ["a", "b", "c"]
    assert set(rows) == {
        ("b", "b", "r"),
        ("d", "d", "t"),
    }
