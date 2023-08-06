from types import NoneType

from object_serializer.pre_serializer import PreSerializer

from .built_in_serializers import BaseSerializer


class SerializerProxy(BaseSerializer):
    """
    This class is aimed at unifying python objects
    coming to serialization. It uses 'pre_serializer' tool
    for such purposes and contains serializer field which is
    instance of specific serializer that implements BaseSerializer.
    """

    serializer: BaseSerializer
    pre_serializer = PreSerializer()

    def __init__(self, serializer: BaseSerializer):
        self.serializer = serializer

    def load(self, file) -> object:
        return self.pre_serializer.decode(self.serializer.load(file))

    def loads(self, str_to_load_from: str) -> object:
        return self.pre_serializer.decode(self.serializer.loads(str_to_load_from))

    def dump(self, obj_to_serialize, file) -> NoneType:
        self.serializer.dump(
            self.pre_serializer.encode(obj_to_serialize),
            file=file,
        )

    def dumps(self, obj_to_serialize) -> str:
        return self.serializer.dumps(self.pre_serializer.encode(obj_to_serialize))
