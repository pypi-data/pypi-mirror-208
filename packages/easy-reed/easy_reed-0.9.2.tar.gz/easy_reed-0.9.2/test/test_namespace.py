# Standard Library Imports
import os

# Third party imports
import pytest

# Application level imports
from namespace import NameSpace


def test_add_entry_1_field():
    test = NameSpace("pytest")

    test.add_entry("test", str, "default")
    assert hasattr(test, "entries")
    assert hasattr(test, "name")
    assert test.name == "pytest"
    assert test.get_name() == "pytest"
    assert isinstance(test.entries, list)
    assert len(test.entries) == 1
    assert isinstance(test.entries[0], tuple)
    assert test.entries[0] == ("TEST", str, "default")

def test_add_entry_bad_field_name_type():
    test = NameSpace("pytest")

    with pytest.raises(TypeError) as e:
        test.add_entry(str, str, "default")

    assert "field_name: <class 'str'>" in str(e)

def test_add_entry_empty_field_name():
    test = NameSpace("pytest")

    with pytest.raises(ValueError) as e:
        test.add_entry("", str, "default")

    assert "field_name:  |" in str(e)

def test_add_entry_string_for_typ():
    test = NameSpace("pytest")

    with pytest.raises(TypeError) as e:
        test.add_entry("name", "fail", "default")

    assert "typ: fail" in str(e)

def test_add_entry_wrong_default_type():
    test = NameSpace("pytest")

    with pytest.raises(TypeError) as e:
        test.add_entry("name", str, 0)

    assert "Instead, a <class 'int'> was passed." in str(e)

def test_add_multiple_entries():
    test = NameSpace("pytest")

    test.add_entry("test1", str, "testing")
    test.add_entry("test2", int, 0)
    test.add_entry("test3", list, ['hello'])

    assert test.has_field("test1")
    assert test.has_field("test2")
    assert test.has_field("test3")

    assert ("TEST1", str, "testing") in test
    assert ("TEST2", int, 0) in test
    assert ("TEST3", list, ['hello']) in test

def test_add_duplicate_entry():
    test = NameSpace("pytest")

    test.add_entry("test", str, "testing")

    assert test.has_field("test")
    assert ("TEST", str, "testing") in test

    with pytest.raises(ValueError) as e:
        test.add_entry("test", str, "testing")

    assert "config field test already exists" in str(e)

    with pytest.raises(ValueError) as e2:
        test.add_entry("test", int, 0)

    assert "config field test already exists" in str(e2)