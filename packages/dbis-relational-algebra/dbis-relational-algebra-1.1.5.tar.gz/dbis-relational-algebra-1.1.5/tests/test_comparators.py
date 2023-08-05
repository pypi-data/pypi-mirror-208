import pytest

from relational_algebra import *

##########
# Equals #
##########


def test_equals_evaluation_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "a"], ["d", "e", "f"]])
    formula = Equals("d", "e")
    with pytest.raises(ValueError):
        formula.selection(r)


def test_equals_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "a"], ["d", "e", "f"]])
    with pytest.raises(ValueError):
        formula = Equals(1, 1)
        formula.selection(r)


def test_equals_one_column():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "a"], ["d", "e", "f"]])
    formula = Equals("f", "c")
    # true for only one row
    result = formula.selection(r)
    assert len(result.rows) == 1


def test_equals_two_columns():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "a"], ["d", "e", "f"]])
    formula = Equals("a", "c")
    # true for only one row
    result = formula.selection(r)
    assert len(result.rows) == 1


def test_equals_with_relation_name():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "a"], ["d", "e", "f"]])
    formula = Equals(f"{r.name}.a", "c")
    # true for only one row
    result = formula.selection(r)
    assert len(result.rows) == 1


#################
# GreaterEquals #
#################


def test_greaterequals_evaluation_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5]])
    formula = GreaterEquals("f", 5)
    with pytest.raises(ValueError):
        formula.selection(r)


def test_greaterequals_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5]])
    with pytest.raises(ValueError):
        formula = GreaterEquals(4, 5)
        formula.selection(r)


def test_greaterequals_one_column():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5], [3, 4, 2]])
    rows = list(r.rows)
    formula = GreaterEquals(f"{r.name}.c", 2)
    # formula true for exactly two rows
    result = formula.selection(r)
    assert len(result.rows) == 2


def test_greaterequals_two_columns():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5], [3, 4, 2]])
    rows = list(r.rows)
    formula = GreaterEquals(f"{r.name}.c", f"{r.name}.a")
    # formula true for exactly two rows
    result = formula.selection(r)
    assert len(result.rows) == 2


###############
# GreaterThan #
###############


def test_greaterthan_evaluation_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5]])
    formula = GreaterThan("f", 5)
    with pytest.raises(ValueError):
        formula.selection(r)


def test_greaterthan_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5]])
    with pytest.raises(ValueError):
        formula = GreaterThan(4, 5)
        formula.selection(r)


def test_greaterthan_one_column():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5], [3, 4, 2]])
    rows = list(r.rows)
    formula = GreaterThan(f"{r.name}.c", 2)
    # true for only one row
    result = formula.selection(r)
    assert len(result.rows) == 1


def test_greaterthan_two_columns():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5], [3, 4, 2]])
    rows = list(r.rows)
    formula = GreaterThan(f"{r.name}.c", f"{r.name}.a")
    # true for only one row
    result = formula.selection(r)
    assert len(result.rows) == 1


##############
# LessEquals #
##############


def test_lessequals_evaluation_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5]])
    formula = LessEquals("f", 5)
    with pytest.raises(ValueError):
        formula.selection(r)


def test_lessequals_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5]])
    with pytest.raises(ValueError):
        formula = LessEquals(4, 5)
        formula.selection(r)


def test_lessequals_one_column():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5], [3, 4, 2]])
    rows = list(r.rows)
    formula = LessEquals(f"{r.name}.c", 2)
    # formula true for exactly two rows
    result = formula.selection(r)
    assert len(result.rows) == 2


def test_lessequals_two_columns():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5], [3, 4, 2]])
    rows = list(r.rows)
    formula = LessEquals(f"{r.name}.c", f"{r.name}.a")
    # formula true for exactly two rows
    result = formula.selection(r)
    assert len(result.rows) == 2


##############
# LessThan #
##############


def test_lessthan_evaluation_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5]])
    formula = LessThan("f", 5)
    with pytest.raises(ValueError):
        formula.selection(r)


def test_lessthan_raises_exception():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5]])
    with pytest.raises(ValueError):
        formula = LessThan(4, 5)
        formula.selection(r)


def test_lessthan_one_column():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5], [3, 4, 2]])
    rows = list(r.rows)
    formula = LessThan(f"{r.name}.c", 2)
    # true for only one row
    result = formula.selection(r)
    assert len(result.rows) == 1


def test_lessthan_two_columns():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([[1, 2, 1], [3, 4, 5], [3, 4, 2]])
    rows = list(r.rows)
    formula = LessThan(f"{r.name}.c", f"{r.name}.a")
    # true for only one row
    result = formula.selection(r)
    assert len(result.rows) == 1
