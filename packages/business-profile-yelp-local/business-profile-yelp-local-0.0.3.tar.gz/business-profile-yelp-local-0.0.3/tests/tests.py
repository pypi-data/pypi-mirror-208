import pytest
from yelp import get_data

def test_get_data1():
    response = get_data('restaurant', 'Ann Arbor')
    assert type (response) is list

def test_get_data2():
    response = get_data('bar', 'San Francisco')
    assert type (response) is list