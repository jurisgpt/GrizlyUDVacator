from collections import OrderedDict

import pytest
from hypothesis import given, strategies as st

from grizlyudvacator.utils.sorted_dict import sorted_dict


def test_empty_dict():
    """Test empty dictionary input."""
    assert sorted_dict({}) == OrderedDict()


def test_single_item():
    """Test dictionary with a single item."""
    result = sorted_dict({"a": 42})
    assert isinstance(result, OrderedDict)
    assert len(result) == 1
    assert result["a"] == 42


def test_ties():
    """Test dictionary with equal values."""
    result = sorted_dict({"a": 1, "b": 1, "c": 1})
    assert isinstance(result, OrderedDict)
    assert len(result) == 3
    assert all(value == 1 for value in result.values())


def test_negative_values():
    """Test dictionary with negative values."""
    result = sorted_dict({"a": -1, "b": -3, "c": 0})
    assert list(result.items()) == [("b", -3), ("a", -1), ("c", 0)]


def test_large_values():
    """Test dictionary with large values."""
    result = sorted_dict({"a": 10**6, "b": 10**9, "c": 10**3})
    assert list(result.items()) == [("c", 10**3), ("a", 10**6), ("b", 10**9)]


@given(
    st.dictionaries(
        keys=st.text(min_size=1),  # Ensure keys are not empty
        values=st.integers(),
        min_size=0,  # Allow empty dictionaries
        max_size=100,  # Limit size for performance
    )
)
def test_sorted_dict_properties(input_dict):
    """
    Property-based tests for sorted_dict function.

    Tests multiple properties:
    1. Values are sorted correctly
    2. All original keys are preserved
    3. Output is an OrderedDict
    4. Handles empty dictionaries
    """
    result = sorted_dict(input_dict)

    # Property 1: Values are sorted correctly
    assert list(result.values()) == sorted(input_dict.values())
    assert isinstance(result, OrderedDict)

    # Check keys and values are preserved
    assert set(result.keys()) == set(input_dict.keys())
    assert all(result[key] == input_dict[key] for key in result)

    # Check values are sorted
    values = list(result.values())
    assert values == sorted(values)
