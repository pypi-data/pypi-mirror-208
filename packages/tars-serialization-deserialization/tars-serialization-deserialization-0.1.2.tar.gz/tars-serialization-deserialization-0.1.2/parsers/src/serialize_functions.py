import re
import inspect
import parsers.src.constants as constants

from pydoc import locate
from types import CodeType, FunctionType


def create_serializer(obj):
    if isinstance(obj, (float, int, complex, bool, str, type(None))):
        return serialize_fincbs
    if isinstance(obj, (list, tuple, bytes)):
        return serialize_ltb
    if isinstance(obj, dict):
        return serialize_dict
    if inspect.isfunction(obj):
        return serialize_function
    if inspect.isclass(obj):
        return serialize_class
    if inspect.iscode(obj):
        return serialize_code
    if inspect.ismodule(obj):
        return serialize_module
    if inspect.ismethoddescriptor(obj) or inspect.isbuiltin(obj):
        return serialize_instance
    if inspect.isgetsetdescriptor(obj) or inspect.ismemberdescriptor(obj):
        return serialize_instance
    if isinstance(obj, type(type.__dict__)):  # mappingproxy type
        return serialize_instance

    return serialize_object


def serialize(obj):
    """
    :param obj: object to serialize
    :return: tuple of dicts of tuples..., that can be used to create JSON
    """
    serializer = create_serializer(obj)
    serialized = serializer(obj)
    serialized = tuple((k, serialized[k]) for k in serialized)

    return serialized


def serialize_fincbs(fincbs):
    """
    serialize ficbs to dict of type and value
    :param fincbs: float, int, none, complex, bool, str
    :return: dict with ["type"] and ["value"]
    """
    serialized_ficbs = dict()
    serialized_ficbs[constants.TYPE] = re.search(constants.REGEX_TYPE, str(type(fincbs))).group(1)
    serialized_ficbs[constants.VALUE] = fincbs

    return serialized_ficbs


def serialize_ltb(objects):
    """
    serialize objects to dict of type and value
    :param objects: list, tuple, bytes
    :return: dict with ["type"] and ["value"]
    """
    serialized_list = dict()
    serialized_list[constants.TYPE] = re.search(constants.REGEX_TYPE, str(type(objects))).group(1)
    serialized_list[constants.VALUE] = tuple([serialize(obj) for obj in objects])

    return serialized_list


def serialize_dict(dict_object):
    """
    serialize dict_object to dict of type and value
    :param dict_object: dict
    :return: dict with ["type"] and ["value"]
    """
    serialized_dict = dict()
    serialized_dict[constants.TYPE] = constants.DICT
    serialized_dict[constants.VALUE] = {}

    for i in dict_object:
        key = serialize(i)
        value = serialize(dict_object[i])
        serialized_dict[constants.VALUE][key] = value

    serialized_dict[constants.VALUE] = tuple((k, serialized_dict[constants.VALUE][k])
                                             for k in serialized_dict[constants.VALUE])

    return serialized_dict


def serialize_function(function_object):
    ans = dict()
    ans[constants.TYPE] = constants.FUNCTION
    ans[constants.VALUE] = {}
    members = inspect.getmembers(function_object)
    members = [i for i in members if i[0] in constants.FUNCTION_ATTRIBUTES]
    for i in members:
        key = serialize(i[0])
        if i[0] != constants.CLOSURE:
            value = serialize(i[1])
        else:
            value = serialize(None)

        ans[constants.VALUE][key] = value
        if i[0] == constants.CODE:
            key = serialize(constants.GLOBALS)
            ans[constants.VALUE][key] = {}
            names = i[1].__getattribute__("co_names")
            glob = function_object.__getattribute__(constants.GLOBALS)
            glob_dict = {}
            for name in names:
                if name == function_object.__name__:
                    glob_dict[name] = function_object.__name__
                elif name in glob and not inspect.ismodule(name) and name not in __builtins__:
                    glob_dict[name] = glob[name]
            ans[constants.VALUE][key] = serialize(glob_dict)

    ans[constants.VALUE] = tuple((k, ans[constants.VALUE][k]) for k in ans[constants.VALUE])
    return ans


def serialize_class(class_obj):
    ans = dict()
    ans[constants.TYPE] = constants.CLASS
    ans[constants.VALUE] = {}
    ans[constants.VALUE][serialize(constants.NAME_NAME)] = serialize(class_obj.__name__)
    members = []
    for i in inspect.getmembers(class_obj):
        if not (i[0] in constants.NOT_CLASS_ATTRIBUTES):
            members.append(i)

    for i in members:
        key = serialize(i[0])
        val = serialize(i[1])
        ans[constants.VALUE][key] = val
    ans[constants.VALUE] = tuple((k, ans[constants.VALUE][k]) for k in ans[constants.VALUE])

    return ans


def serialize_object(some_object):
    class_obj = type(some_object)
    ans = dict()
    ans[constants.TYPE] = constants.OBJECT
    ans[constants.VALUE] = {}
    ans[constants.VALUE][serialize(constants.OBJECT_NAME)] = serialize(class_obj)
    ans[constants.VALUE][serialize(constants.FIELDS_NAME)] = serialize(some_object.__dict__)
    ans[constants.VALUE] = tuple((k, ans[constants.VALUE][k]) for k in ans[constants.VALUE])

    return ans


def serialize_instance(instance_obj):
    ans = dict()
    ans[constants.TYPE] = re.search(constants.REGEX_TYPE, str(type(instance_obj))).group(1)

    ans[constants.VALUE] = {}
    members = inspect.getmembers(instance_obj)
    members = [i for i in members if not callable(i[1])]
    for i in members:
        key = serialize(i[0])
        val = serialize(i[1])
        ans[constants.VALUE][key] = val
    ans[constants.VALUE] = tuple((k, ans[constants.VALUE][k]) for k in ans[constants.VALUE])

    return ans


def serialize_code(instance_obj):
    if re.search(constants.REGEX_TYPE, str(type(instance_obj))) is None:
        return None

    ans = dict()
    ans[constants.TYPE] = re.search(constants.REGEX_TYPE, str(type(instance_obj))).group(1)

    ans[constants.VALUE] = {}
    members = inspect.getmembers(instance_obj)
    members = [i for i in members if not callable(i[1])]
    for i in members:
        key = serialize(i[0])
        val = serialize(i[1])
        ans[constants.VALUE][key] = val
    ans[constants.VALUE] = tuple((k, ans[constants.VALUE][k]) for k in ans[constants.VALUE])

    return ans


def serialize_module(module):
    ans = dict()
    ans[constants.TYPE] = constants.MODULE_NAME
    ans[constants.VALUE] = re.search(constants.REGEX_TYPE, str(module)).group(1)

    return ans


def create_deserializer(object_type):
    if object_type == constants.DICT:
        return deserialize_dict
    if object_type == constants.FUNCTION:
        return deserialize_function
    if object_type in [constants.LIST, constants.TUPLE, constants.BYTES]:
        return deserialize_ltb
    if object_type == constants.CLASS:
        return deserialize_class
    if object_type in [constants.FLOAT, constants.INT, constants.COMPLEX, constants.NONE_TYPE, constants.BOOL,
                       constants.STRING]:
        return deserialize_fincbs
    if object_type == constants.OBJECT:
        return deserialize_object
    if object_type == constants.MODULE_NAME:
        return deserialize_module


def deserialize(d):
    d = dict((a, b) for a, b in d)
    object_type = d[constants.TYPE]
    deserializer = create_deserializer(object_type)

    if deserializer is None:
        return

    return deserializer(object_type, d[constants.VALUE])


def deserialize_fincbs(object_type, fincbs=None):
    if object_type == constants.NONE_TYPE:
        return None

    if object_type == constants.BOOL and isinstance(fincbs, str):
        return fincbs == constants.TRUE

    return locate(object_type)(fincbs)


def deserialize_ltb(object_type, ltb):
    if object_type == constants.LIST:
        return [deserialize(i) for i in ltb]

    if object_type == constants.TUPLE:
        return tuple([deserialize(i) for i in ltb])

    if object_type == constants.BYTES:
        return bytes([deserialize(i) for i in ltb])


def deserialize_dict(object_type, dictionary):
    ans = {}
    for i in dictionary:
        val = deserialize(i[1])
        ans[deserialize(i[0])] = val

    return ans


def deserialize_function(object_type, foo):
    func = [0] * 4
    code = [0] * 16
    glob = {constants.BUILTINS: __builtins__}

    for i in foo:
        key = deserialize(i[0])

        if key == constants.GLOBALS:
            glob_dict = deserialize(i[1])
            for glob_key in glob_dict:
                glob[glob_key] = glob_dict[glob_key]

        elif key == constants.CODE:
            val = i[1][1][1]

            for arg in val:
                code_arg_key = deserialize(arg[0])
                if code_arg_key != constants.DOC and code_arg_key != 'co_linetable':
                    code_arg_val = deserialize(arg[1])
                    index = constants.CODE_OBJECT_ARGS.index(code_arg_key)
                    code[index] = code_arg_val

            code = CodeType(*code)
        else:
            index = constants.FUNCTION_ATTRIBUTES.index(key)
            func[index] = (deserialize(i[1]))

    func[0] = code
    func.insert(1, glob)

    ans = FunctionType(*func)
    if ans.__name__ in ans.__getattribute__(constants.GLOBALS):
        ans.__getattribute__(constants.GLOBALS)[ans.__name__] = ans

    return ans


def deserialize_object(object_type, obj):
    obj_dict = deserialize_dict(constants.DICT, obj)
    result = obj_dict[constants.OBJECT_NAME]()

    for key, value in obj_dict[constants.FIELDS_NAME].items():
        result.key = value

    return result


def deserialize_class(object_type, class_dict):
    some_dict = deserialize_dict(constants.DICT, class_dict)
    name = some_dict[constants.NAME_NAME]
    del some_dict[constants.NAME_NAME]

    return type(name, (object,), some_dict)


def deserialize_module(object_type, module_name):
    return __import__(module_name)
