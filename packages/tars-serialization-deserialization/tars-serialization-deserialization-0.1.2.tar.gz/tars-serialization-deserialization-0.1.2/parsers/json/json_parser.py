from parsers.src.serialize_functions import serialize, deserialize
from parsers.json.source import serialize_json, deserialize_json


class JsonParser:

    @staticmethod
    def dumps(obj) -> str:
        obj = serialize(obj)
        return serialize_json(obj).replace("\n", "\\n")

    @staticmethod
    def dump(obj, file):
        file.write(JsonParser.dumps(obj))

    @staticmethod
    def loads(obj: str):
        obj = deserialize_json(obj.replace("\\n", "\n"))
        return deserialize(obj)

    @staticmethod
    def load(file):
        return JsonParser.loads(file.read())
