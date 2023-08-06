from parsers.src.serialize_functions import serialize, deserialize
from parsers.yaml.source import serialize_yaml, deserialize_yaml


class YamlParser:

    @staticmethod
    def dumps(obj) -> str:
        obj = serialize(obj)
        return serialize_yaml(obj)

    @staticmethod
    def dump(obj, file):
        file.write(YamlParser.dumps(obj))

    @staticmethod
    def loads(obj: str):
        obj = deserialize_yaml(obj)
        return deserialize(obj)

    @staticmethod
    def load(file):
        return YamlParser.loads(file.read())
