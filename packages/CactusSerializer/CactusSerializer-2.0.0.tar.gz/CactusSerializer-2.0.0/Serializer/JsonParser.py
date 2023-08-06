import Serializer.JsonSerializer
import Serializer.JsonDeserializer


class JsonParser:

    @staticmethod
    def dump(obj, filename, indent=0):
        result = JsonParser.dumps(obj, indent)
        with open(filename, 'w') as file:
            file.write(result)

    @staticmethod
    def dumps(obj, indent=0) -> str:
        result = Serializer.JsonSerializer.serialize(obj, indent)
        return result

    @staticmethod
    def load(filename):
        with open(filename, 'r') as file:
            data = file.read()
        result = JsonParser.loads(data)
        return result

    @staticmethod
    def loads(data: str):
        result = Serializer.JsonDeserializer.deserialize(data)[0]
        return result
