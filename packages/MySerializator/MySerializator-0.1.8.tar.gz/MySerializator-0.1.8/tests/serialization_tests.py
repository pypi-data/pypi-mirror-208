import pytest

from serializers.json.json_serializer import JsonSerializer
from serializers.xml.xml_serializer import XmlSerializer


# tests of primitives


def test_primitive_int_json():
    value = 7656789876789
    serializer = JsonSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_primitive_str_json():
    value = "my first string test"
    serializer = JsonSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_primitive_none_json():
    value = None
    serializer = JsonSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_primitive_int_XmlSerializer():
    value = 999345151544311
    serializer = XmlSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_primitive_str_xml():
    value = "my second test"
    serializer = XmlSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_primitive_none_xml():
    value = None
    serializer = XmlSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


# empty tests for collections

def test_empty_tuple_json():
    value = ()
    serializer = JsonSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_empty_dict_json():
    value = {}
    serializer = JsonSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_empty_list_xml():
    value = []
    serializer = XmlSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_empty_set_xml():
    value = set()
    serializer = XmlSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


# tests collections

def test_simple_list_json():
    value = [111, 'qwerty', '=', False, 10.5]
    serializer = JsonSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_simple_dict_json():
    value = {'key1': 'value1', 11: None, 12.6: None}
    serializer = JsonSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_simple_tuple_xml():
    value = (11, 45, 21.5, True, 'tuple')
    serializer = XmlSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


def test_simple_dict_xml():
    value = {'key1': 'value1', 2: True, '???': None}
    serializer = XmlSerializer()
    packed = serializer.dumps(value)
    assert value == serializer.loads(packed)


# testing functions
def no_arg_func():
    return 'hello'


def test_no_arg_func_json():
    serializer = JsonSerializer()
    packed = serializer.dumps(no_arg_func)
    assert no_arg_func() == serializer.loads(packed)()

