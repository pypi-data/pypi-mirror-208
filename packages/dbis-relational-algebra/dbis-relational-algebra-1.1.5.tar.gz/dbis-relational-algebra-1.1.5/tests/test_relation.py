import pytest

from relational_algebra import *


def test_duplicates():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "c"], ["a", "b", "c"]])
    rows = r.rows
    assert len(rows) == 1
    assert set(rows) == {("a", "b", "c")}
