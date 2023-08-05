import pytest

from relational_algebra import *


def test_or():
    r1 = Relation("R1")
    r2 = Relation("R2")
    assert isinstance(r1 | r2, Union)


def test_evaluate_raises_exception():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["b", "c"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["c", "d"], ["f", "g"]])
    u = r1 | r2
    with pytest.raises(ValueError):
        u.evaluate()


def test_equal():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["a", "b"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["a", "b"], ["d", "e"]])
    u = r1 | r2
    result = u.evaluate()
    rows = result.rows
    assert set(rows) == {("a", "b"), ("d", "e")}


def test_subset():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["a", "b"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["a", "b"], ["d", "e"], ["f", "g"]])
    u = r1 | r2
    result = u.evaluate()
    rows = result.rows
    assert set(rows) == {("a", "b"), ("d", "e"), ("f", "g")}


def test_superset():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["a", "b"])
    r1.add_rows([["a", "b"], ["d", "e"], ["f", "g"]])
    r2.add_rows([["a", "b"], ["d", "e"]])
    u = r1 | r2
    result = u.evaluate()
    rows = result.rows
    assert set(rows) == {("a", "b"), ("d", "e"), ("f", "g")}
