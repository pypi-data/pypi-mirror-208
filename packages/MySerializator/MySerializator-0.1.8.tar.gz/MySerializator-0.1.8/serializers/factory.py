from serializers.json.json_serializer import JsonSerializer
from serializers.xml.xml_serializer import XmlSerializer
from source.meta_serializer import MetaSerializer
from source.serializer_shell import SerializerShell


class Factory:
    serializer_types = {'json': JsonSerializer, 'xml': XmlSerializer}

    @classmethod
    def create_serializer(cls, related_type: str):
        return SerializerShell(cls.serializer_types[related_type]())

    @classmethod
    def save_serializer(cls, related_type: str, serializer: MetaSerializer):
        cls.serializer_types[related_type] = serializer
