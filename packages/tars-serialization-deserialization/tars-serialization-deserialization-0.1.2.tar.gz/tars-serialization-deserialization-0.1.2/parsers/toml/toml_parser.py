from parsers.src.serialize_functions import serialize, deserialize
from parsers.toml.source import serialize_toml, deserialize_toml


class TomlParser:

    @staticmethod
    def dumps(obj) -> str:
        obj = serialize(obj)
        return f"tuple = {serialize_toml(obj)}"

    @staticmethod
    def dump(obj, file):
        file.write(TomlParser.dumps(obj))

    @staticmethod
    def loads(obj: str):
        obj = obj.split('=', 1)[1]

        obj = deserialize_toml(obj.replace("\\n", "\n").strip())
        return deserialize(obj)

    @staticmethod
    def load(file):
        return TomlParser.loads(file.read())
