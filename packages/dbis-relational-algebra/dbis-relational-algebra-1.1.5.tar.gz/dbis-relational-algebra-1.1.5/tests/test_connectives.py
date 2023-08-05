import pytest

from relational_algebra import *


def test_not():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "a"], ["d", "e", "f"]])
    formula = Equals(f"{r.name}.a", f"{r.name}.c")
    not_formula = Not(formula)
    rows = list(r.rows)
    result = formula.selection(r)
    not_result = not_formula.selection(r)
    # disjunct
    assert set(result.rows) | set(not_result.rows) == set(rows)
    # conjunct
    assert set(result.rows) & set(not_result.rows) == set()


def test_and():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "a"], ["d", "e", "f"], ["b", "b", "b"]])
    formula1 = Equals(f"{r.name}.a", f"{r.name}.c")
    formula2 = Equals(f"{r.name}.a", f"{r.name}.b")
    and_formula = And(formula1, formula2)
    result = and_formula.selection(r)
    # and_formula true for exactly one row
    assert len(result.rows) == 1


def test_or():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "a"], ["d", "e", "f"], ["b", "b", "b"]])
    formula1 = Equals(f"{r.name}.a", f"{r.name}.c")
    formula2 = Equals(f"{r.name}.a", f"{r.name}.b")
    or_formula = Or(formula1, formula2)
    result = or_formula.selection(r)
    # or_formula true for exactly two rows
    assert len(result.rows) == 2
