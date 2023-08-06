from Serializators.Meta import MetaSerializer
from Serializators.JSON import JsonSerializer
from Serializators.XML import XMLSerializer
from Serializators.Shell import SerializerShell


class SerializerFactory:
    serializer_lib = {'json': JsonSerializer, 'xml': XMLSerializer}

    @classmethod
    def get_serializer(cls, related_type: str):
        return SerializerShell(cls.serializer_lib[related_type]())

    @classmethod
    def save_serializer(cls, related_type: str, serializer: MetaSerializer):
        cls.serializer_lib[related_type] = serializer
