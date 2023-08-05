import pytest

from relational_algebra import *


def test_thetajoin_attributes():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["b", "c"])
    t = ThetaJoin(r1, r2, Equals("R1.b", "R2.b"))
    result = t.evaluate()
    assert result.get_attribute_names(result.attributes) == [
        "R1.a",
        "R1.b",
        "R2.b",
        "R2.c",
    ]


def test_thetajoin_rows():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["b", "c"])
    r1.add_rows([["a", "b"], ["d", "e"], ["f", "g"]])
    r2.add_rows([["c", "d"], ["g", "f"], ["i", "h"], ["g", "i"]])
    t = ThetaJoin(r1, r2, Or(Equals("R1.b", "R2.b"), Equals("R1.a", "R2.c")))
    result = t.evaluate()
    assert set(result.rows) == {
        ("d", "e", "c", "d"),
        ("f", "g", "g", "f"),
        ("f", "g", "g", "i"),
    }


def test_thetajoin_numerical():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b", "c"])
    r2.add_attributes(["b", "c", "e"])
    r1.add_rows([[1, 1, 1], [1, 2, 1], [3, 1, 2], [3, 2, 2], [5, 1, 3], [5, 2, 3]])
    r2.add_rows([[1, 1, 1], [2, 1, 1], [1, 2, 1], [2, 2, 1], [1, 1, 2]])
    # (R1.a = R2.b) AND ((R1.c < R2.e) OR (R1.c > R2.e))
    formula = And(
        GreaterEquals("R1.b", "R2.b"),
        Or(LessThan("R1.c", "R2.e"), Equals("R1.a", "R2.c")),
    )
    t = ThetaJoin(r1, r2, formula)
    result = t.evaluate()
    assert result.get_attribute_names(result.attributes) == [
        "R1.a",
        "R1.b",
        "R1.c",
        "R2.b",
        "R2.c",
        "R2.e",
    ]
    assert set(result.rows) == {
        (1, 1, 1, 1, 1, 1),
        (1, 1, 1, 1, 1, 2),
        (1, 2, 1, 1, 1, 1),
        (1, 2, 1, 1, 1, 2),
        (1, 2, 1, 2, 1, 1),
    }


# Theta Join produces the same result as a cross product followed by a selection
def test_crossproduct_selection():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b", "c"])
    r2.add_attributes(["b", "c", "e"])
    r1.add_rows([[1, 1, 1], [1, 2, 1], [3, 1, 2], [3, 2, 2], [5, 1, 3], [5, 2, 3]])
    r2.add_rows([[1, 1, 1], [2, 1, 1], [1, 2, 1], [2, 2, 1], [1, 1, 2]])
    # (R1.a = R2.b) AND ((R1.c < R2.e) OR (R1.c > R2.e))
    formula = And(
        GreaterEquals("R1.b", "R2.b"),
        Or(LessThan("R1.c", "R2.e"), Equals("R1.a", "R2.c")),
    )
    t = ThetaJoin(r1, r2, formula)
    other = Selection(r1 * r2, formula)
    result = t.evaluate()
    other_result = other.evaluate()
    assert result.get_attribute_names(
        result.attributes
    ) == other_result.get_attribute_names(other_result.attributes)
    assert set(result.rows) == set(other_result.rows)
