import pytest

from relational_algebra import *


def test_key_not_found():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "c"], ["d", "e", "f"]])
    rename = Rename(r, {"d": "a"})
    with pytest.raises(KeyError):
        rename.evaluate()


def test_duplicate_key():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "c"], ["d", "e", "f"]])
    rename = Rename(r, {"a": "d", "R.a": "d"})
    with pytest.raises(KeyError):
        rename.evaluate()


def test_duplicate_value_relation():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "c"], ["d", "e", "f"]])
    rename = Rename(r, {"a": "b"})
    with pytest.raises(ValueError):
        rename.evaluate()


def test_duplicate_value_mapping():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "c"], ["d", "e", "f"]])
    rename = Rename(r, {"a": "b", "c": "b"})
    with pytest.raises(ValueError):
        rename.evaluate()


def test_rename_relation():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "c"], ["d", "e", "f"]])
    rename = Rename(r, "E")
    result = rename.evaluate()
    name = result.name
    assert name == "E"
    assert r.rows == result.rows


def test_rename():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "c"], ["d", "e", "f"]])
    rename = Rename(r, {"a": "d"})
    result = rename.evaluate()
    attributes = result.attributes
    assert result.get_minimal_attribute_names(attributes) == ["d", "b", "c"]
    assert r.rows == result.rows


def test_rename_with_relation_name():
    r = Relation("R")
    r.add_attributes(["a", "b", "c"])
    r.add_rows([["a", "b", "c"], ["d", "e", "f"]])
    rename = Rename(r, {"R.a": "d"})
    result = rename.evaluate()
    attributes = result.attributes
    assert result.get_minimal_attribute_names(attributes) == ["d", "b", "c"]
    assert r.rows == result.rows
