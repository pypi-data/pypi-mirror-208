from serializers.json import serialize_json, deserialize_json
from serializers.parser import Parser


class Json(Parser):

    def dump(self, obj, file: str):
        with open(file, 'w+') as f:
            f.write(self.dumps(obj))

    def dumps(self, obj):
        obj_ = self.serializer.serialize(obj)
        return serialize_json(obj_)

    def load(self, file):
        with open(file, 'r') as f:
            return self.loads(f.read())

    def loads(self, string):
        return self.serializer.deserialize(deserialize_json(string))
