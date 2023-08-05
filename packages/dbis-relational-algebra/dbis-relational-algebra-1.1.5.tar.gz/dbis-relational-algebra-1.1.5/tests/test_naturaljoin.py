import pytest

from relational_algebra import *


def test_disjoint_attributes():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["c", "d"])
    r1.add_rows([["a", "b"], ["d", "e"]])
    r2.add_rows([["c", "d"], ["f", "g"]])
    n = NaturalJoin(r1, r2)
    cp = r1 * r2
    n_relation = n.evaluate()
    cp_relation = cp.evaluate()
    assert n_relation.get_minimal_attribute_names(
        n_relation.attributes
    ) == cp_relation.get_minimal_attribute_names(cp_relation.attributes)
    assert n_relation.rows == cp_relation.rows


def test_union_compatible_attributes():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["b", "a"])
    r1.add_rows([["a", "b"], ["d", "e"], ["f", "g"]])
    r2.add_rows([["d", "c"], ["g", "f"], ["i", "h"]])
    n = NaturalJoin(r1, r2)
    n_relation = n.evaluate()
    assert n_relation.get_minimal_attribute_names(n_relation.attributes) == ["a", "b"]
    assert set(n_relation.rows) == {("f", "g")}


def test_overlapping_attributes():
    r1 = Relation("R1")
    r2 = Relation("R2")
    r1.add_attributes(["a", "b"])
    r2.add_attributes(["b", "c"])
    r1.add_rows([["a", "b"], ["d", "e"], ["f", "g"]])
    r2.add_rows([["c", "d"], ["g", "f"], ["i", "h"], ["g", "i"]])
    n = NaturalJoin(r1, r2)
    n_relation = n.evaluate()
    assert n_relation.get_minimal_attribute_names(n_relation.attributes) == [
        "a",
        "b",
        "c",
    ]
    assert set(n_relation.rows) == {("f", "g", "f"), ("f", "g", "i")}
