from .constants import JSON_DATA_TYPE, TOML_DATA_TYPE, \
    YAML_DATA_TYPE, UNKNOWN_TYPE_ERROR, XML_DATA_TYPE
from .json_serializer import JsonSerializer
from .xml_serializer import XmlSerializer


class Factory:
    @staticmethod
    def create_serializer(data_format):
        if data_format == JSON_DATA_TYPE:
            return JsonSerializer()

        elif data_format == XML_DATA_TYPE:
            return XmlSerializer()

        else:
            raise Exception(UNKNOWN_TYPE_ERROR)
