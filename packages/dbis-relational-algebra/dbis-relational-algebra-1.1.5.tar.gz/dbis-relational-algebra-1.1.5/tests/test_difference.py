import pytest

from relational_algebra import *


def test_minus():
    r1 = Relation("R1")
    r2 = Relation("R2")
    assert isinstance(r1 - r2, Difference)


def test_evaluate_raises_exception():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["c", "d"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["c", "d"], ["f", "g"]])
    d = r1 - r2
    with pytest.raises(ValueError):
        d.evaluate()


def test_equal():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["a", "b"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["a", "b"], ["d", "e"]])
    d = r1 - r2
    result = d.evaluate()
    rows = result.rows
    assert set(rows) == set()


def test_subset():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["a", "b"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["a", "b"], ["d", "e"], ["f", "g"]])
    d = r1 - r2
    result = d.evaluate()
    rows = result.rows
    assert set(rows) == set()


def test_superset():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["a", "b"])
    r1.add_rows([["a", "b"], ["d", "e"], ["f", "g"]])
    r2.add_rows([["a", "b"], ["d", "e"]])
    d = r1 - r2
    result = d.evaluate()
    rows = result.rows
    assert set(rows) == {("f", "g")}
