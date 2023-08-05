import pytest

from relational_algebra import *


def test_times():
    r1 = Relation("R1")
    r2 = Relation("R2")
    assert isinstance(r1 * r2, CrossProduct)


def test_disjunct():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["c", "d"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["c", "d"], ["f", "g"]])
    cp = r1 * r2
    result = cp.evaluate()
    rows = result.rows
    assert set(rows) == {
        ("a", "b", "c", "d"),
        ("a", "b", "f", "g"),
        ("d", "e", "c", "d"),
        ("d", "e", "f", "g"),
    }


def test_intersect():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["c", "d"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["c", "d"], ["f", "g"]])
    cp = r1 * r2
    result = cp.evaluate()
    rows = result.rows
    assert set(rows) == {
        ("a", "b", "c", "d"),
        ("a", "b", "f", "g"),
        ("d", "e", "c", "d"),
        ("d", "e", "f", "g"),
    }
