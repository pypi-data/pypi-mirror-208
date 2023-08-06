import Serializer.XmlSerializer
import Serializer.XmlDeserializer


class XmlParser:

    @staticmethod
    def dump(obj, filename, indent=0):
        result = XmlParser.dumps(obj, indent)
        with open(filename, 'w') as file:
            file.write(result, 'w')

    @staticmethod
    def dumps(obj, indent=0) -> str:
        result = Serializer.XmlSerializer.serialize(obj, indent)
        return result

    @staticmethod
    def load(filename):
        with open(filename, 'r') as file:
            data = file.read(filename)
        result = Serializer.XmlDeserializer.deserialize(data)
        return result

    @staticmethod
    def loads(data: str):
        result = Serializer.XmlDeserializer.deserialize(data)[0]
        return result
