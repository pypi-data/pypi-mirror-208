from Serializer.JsonParser import *
from Serializer.XmlParser import *
from Serializer.constants import JSON, XML


class SerializerFactory:

    @staticmethod
    def create_serializer(type_of_serializer):
        if type_of_serializer == JSON:
            return JsonParser
        elif type_of_serializer == XML:
            return XmlParser
        else:
            raise ValueError
