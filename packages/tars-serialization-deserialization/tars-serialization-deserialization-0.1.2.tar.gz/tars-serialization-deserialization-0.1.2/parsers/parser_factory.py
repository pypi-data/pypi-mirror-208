from parsers.json.json_parser import JsonParser
from parsers.yaml.yaml_parser import YamlParser
from parsers.toml.toml_parser import TomlParser


class ParserFactory:
    @staticmethod
    def create_parser(name: str):
        """
        :param name: desirable serializer: json, yaml, toml
        :return: serializer
        """

        name = name.lower()
        if name == "json":
            return JsonParser

        if name == "yaml":
            return YamlParser

        if name == "toml":
            return TomlParser

        raise ValueError(f"Format {name} is not supported")
