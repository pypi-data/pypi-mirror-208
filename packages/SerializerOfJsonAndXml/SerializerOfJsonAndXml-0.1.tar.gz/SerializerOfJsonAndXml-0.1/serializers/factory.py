from serializers.json.json_serializer import JsonSerializer
from serializers.xml.xml_serializer import XmlSerializer
from enum import Enum


class SerializerType(Enum):
    JSON = "json"
    XML = "xml"


class Factory:
    @staticmethod
    def create_serializer(file_type):
        if file_type == "json":
            return JsonSerializer
        elif file_type == "xml":
            return XmlSerializer
        else:
            return Exception("Unknown type of serialization")

