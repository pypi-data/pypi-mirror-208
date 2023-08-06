from parsers.src.serialize_functions import serialize_fincbs
from parsers.src.serialize_functions import serialize_ltb
from parsers.src.serialize_functions import serialize_dict
from parsers.src.serialize_functions import serialize
from parsers.src.serialize_functions import deserialize

from parsers.json.json_parser import JsonParser
from parsers.yaml.yaml_parser import YamlParser
from parsers.toml.toml_parser import TomlParser
import tests.test_functions as test_functions


def test_fincbs_types():
    f = 0.5
    i = 5
    n = None
    c = complex(1, 2)
    b = True
    s = "ABOBA"

    assert (str(serialize_fincbs(f)) == "{'type': 'float', 'value': 0.5}")
    assert (str(serialize_fincbs(i)) == "{'type': 'int', 'value': 5}")
    assert (str(serialize_fincbs(n)) == "{'type': 'NoneType', 'value': None}")
    assert (str(serialize_fincbs(c)) == "{'type': 'complex', 'value': (1+2j)}")
    assert (str(serialize_fincbs(b)) == "{'type': 'bool', 'value': True}")
    assert (str(serialize_fincbs(s)) == "{'type': 'str', 'value': 'ABOBA'}")


def test_ltb_types():
    list1 = []
    list2 = ["a", 4, -4]
    list3 = [["4q", 78], True]

    tuple1 = ()
    tuple2 = ("a", 4, -4)
    tuple3 = (("4q", 78), True)
    bytes1 = b'bytes'

    assert (str(serialize_ltb(list1)) == "{'type': 'list', 'value': ()}")
    assert (str(serialize_ltb(
        list2)) == "{'type': 'list', 'value': ((('type', 'str'), ('value', 'a')), "
                   "(('type', 'int'), ('value', 4)), (('type', 'int'), ('value', -4)))}")
    assert (str(serialize_ltb(
        list3)) == "{'type': 'list', 'value': ((('type', 'list'), ('value', "
                   "((('type', 'str'), ('value', '4q')), (('type', 'int'), ('value', 78))))),"
                   " (('type', 'bool'), ('value', True)))}")

    assert (str(serialize_ltb(tuple1)) == "{'type': 'tuple', 'value': ()}")
    assert (str(serialize_ltb(
        tuple2)) == "{'type': 'tuple', 'value': ((('type', 'str'), ('value', 'a')), "
                    "(('type', 'int'), ('value', 4)), (('type', 'int'), ('value', -4)))}")
    assert (str(serialize_ltb(
        tuple3)) == "{'type': 'tuple', 'value': ((('type', 'tuple'), "
                    "('value', ((('type', 'str'), ('value', '4q')), (('type', 'int'), "
                    "('value', 78))))), (('type', 'bool'), ('value', True)))}")
    assert (str(serialize_ltb(
        bytes1)) == "{'type': 'bytes', 'value': ((('type', 'int'), ('value', 98)), "
                    "(('type', 'int'), ('value', 121)), (('type', 'int'), ('value', 116)),"
                    " (('type', 'int'), ('value', 101)), (('type', 'int'), ('value', 115)))}")


def test_dict():
    dict1 = dict()
    dict2 = {4: 7, 5: 3, 2: 1}
    dict3 = {("aaa", "bbb"): ["biba"], 32: "ABOBA"}
    dict4 = {1: dict1.copy(), 2: dict2.copy(), 3: dict3.copy()}
    dict5 = {"aa": 5}

    assert (str(serialize_dict(dict1)) == "{'type': 'dict', 'value': ()}")
    assert (str(serialize_dict(
        dict2)) == "{'type': 'dict', 'value': (((('type', 'int'), "
                   "('value', 4)), (('type', 'int'), ('value', 7))), "
                   "((('type', 'int'), ('value', 5)), (('type', 'int'), ('value', 3))),"
                   " ((('type', 'int'), ('value', 2)), (('type', 'int'), ('value', 1))))}")
    assert (str(serialize_dict(
        dict3)) == "{'type': 'dict', 'value': (((('type', 'tuple'), "
                   "('value', ((('type', 'str'), ('value', 'aaa')), (('type', 'str'), ('value', 'bbb'))))),"
                   " (('type', 'list'), ('value', ((('type', 'str'), ('value', 'biba')),)))), ((('type', 'int'),"
                   " ('value', 32)), (('type', 'str'), ('value', 'ABOBA'))))}")
    assert (str(serialize_dict(
        dict4)) == "{'type': 'dict', 'value': (((('type', 'int'), ('value', 1)), (('type', 'dict'), "
                   "('value', ()))), ((('type', 'int'), ('value', 2)), (('type', 'dict'), ('value', (((('type', 'int'),"
                   " ('value', 4)), (('type', 'int'), ('value', 7))), ((('type', 'int'), ('value', 5)), "
                   "(('type', 'int'), ('value', 3))), ((('type', 'int'), ('value', 2)), (('type', 'int'), "
                   "('value', 1))))))), ((('type', 'int'), ('value', 3)), (('type', 'dict'), ('value', "
                   "(((('type', 'tuple'), ('value', ((('type', 'str'), ('value', 'aaa')), (('type', 'str'), "
                   "('value', 'bbb'))))), (('type', 'list'), ('value', ((('type', 'str'), ('value', 'biba')),)))), "
                   "((('type', 'int'), ('value', 32)), (('type', 'str'), ('value', 'ABOBA'))))))))}")

    assert (dict1 == deserialize(serialize(dict1)))
    assert (dict2 == deserialize(serialize(dict2)))
    assert (dict3 == deserialize(serialize(dict3)))
    assert (dict4 == deserialize(serialize(dict4)))
    assert (dict5 == deserialize(serialize(dict5)))


def test_foo():
    test_functions.foo_test(deserialize, serialize)
    test_functions.foo_test(JsonParser.loads, JsonParser.dumps)
    test_functions.foo_test(YamlParser.loads, YamlParser.dumps)
    test_functions.foo_test(TomlParser.loads, TomlParser.dumps)


def test_class():
    test_functions.class_test(deserialize, serialize)
    test_functions.class_test(JsonParser.loads, JsonParser.dumps)
    test_functions.class_test(YamlParser.loads, YamlParser.dumps)
    test_functions.class_test(TomlParser.loads, TomlParser.dumps)


def test_object():
    test_functions.object_test(deserialize, serialize)
    test_functions.object_test(JsonParser.loads, JsonParser.dumps)
    test_functions.object_test(YamlParser.loads, YamlParser.dumps)
    test_functions.object_test(TomlParser.loads, TomlParser.dumps)


def test_complicated():
    test_functions.complicated_test(deserialize, serialize)
    test_functions.complicated_test(JsonParser.loads, JsonParser.dumps)
    test_functions.complicated_test(YamlParser.loads, YamlParser.dumps)
    test_functions.complicated_test(TomlParser.loads, TomlParser.dumps)


def test_lambda():
    test_functions.lambda_test(deserialize, serialize)
    test_functions.lambda_test(JsonParser.loads, JsonParser.dumps)
    test_functions.lambda_test(YamlParser.loads, YamlParser.dumps)
    test_functions.lambda_test(TomlParser.loads, TomlParser.dumps)


def test_butoma():
    test_functions.butoma_test(deserialize, serialize)
    test_functions.butoma_test(JsonParser.loads, JsonParser.dumps)
    test_functions.butoma_test(YamlParser.loads, YamlParser.dumps)
    test_functions.butoma_test(TomlParser.loads, TomlParser.dumps)


def test_test_test():
    with open("serialized_test.txt", "w") as f:
        JsonParser.dump([15, complex(-3, 4)], f)
