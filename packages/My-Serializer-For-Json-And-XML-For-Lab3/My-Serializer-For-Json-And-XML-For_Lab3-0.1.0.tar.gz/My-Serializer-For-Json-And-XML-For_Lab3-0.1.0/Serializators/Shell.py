from Core.functions_for_serializer import Serialize
from Core.functions_for_deserialize import Deserialize
from Serializators.Meta import MetaSerializer


class SerializerShell(MetaSerializer):

    def __init__(self, serializer: MetaSerializer):
        self.serialize = Serialize()
        self.deserialize = Deserialize()
        self.serializer = serializer

    def dump(self, obj, file):
        self.serializer.dump(self.serialize.serialize(obj), file)

    def dumps(self, obj):
        return self.serializer.dumps(self.serialize.serialize(obj))

    def load(self, file):
        return self.deserialize.deserialize(self.serializer.load(file))

    def loads(self, string):
        return self.deserialize.deserialize(self.serializer.loads(string))
    