from source.serializer import Serializer
from source.meta_serializer import MetaSerializer


class SerializerShell(MetaSerializer):

    def __init__(self, serializer_: MetaSerializer):
        self.serialiser = Serializer()
        self.serializer = serializer_

    def dump(self, obj, file):
        self.serializer.dump(self.serialiser.serialize(obj), file)

    def dumps(self, obj):
        return self.serializer.dumps(self.serialiser.serialize(obj))

    def load(self, file):
        return self.serialiser.deserialize(self.serializer.load(file))

    def loads(self, string):
        return self.serialiser.deserialize(self.serializer.loads(string))
