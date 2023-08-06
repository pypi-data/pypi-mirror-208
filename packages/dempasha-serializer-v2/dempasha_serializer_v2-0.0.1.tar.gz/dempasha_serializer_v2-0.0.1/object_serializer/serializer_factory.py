from object_serializer.built_in_serializers import (BaseSerializer,
                                                    JSONSerializer,
                                                    XMLSerializer)
from object_serializer.serializer_proxy import SerializerProxy


class SerializerFactory:
    """
    Note that you can extend or update default set of formats for this
    serializer. To do that your serializer must implement BaseSerializer
    and be compatible with 'pre_serializer' tool which is aimed at fetching
    new data from object's metadata.
    """

    serializers_mapping = {
        "JSON": JSONSerializer,
        "XML": XMLSerializer,
    }

    @classmethod
    def add_serializer(cls, serialization_type: str, serializer: BaseSerializer):
        cls.serializers_mapping[serialization_type.upper()] = serializer

    @classmethod
    def create_serializer(cls, serialization_type: str) -> BaseSerializer:
        """
        'SerializerProxy' is returned by this function. It is aimed at
        using both pre_serializer tool and serializer to encode data and
        to make fit it to particular data format.
        """
        serializer = cls.serializers_mapping.get(serialization_type.upper())
        if serializer is None:
            raise cls.ImproperlyConfiguredError(cls.IMPROPERLY_CONFIGURED_MESSAGE)
        return SerializerProxy(serializer=serializer())

    IMPROPERLY_CONFIGURED_MESSAGE = (
        "This serialization type is not available" " since there is no serializer for this type"
    )

    class ImproperlyConfiguredError(Exception):
        pass
