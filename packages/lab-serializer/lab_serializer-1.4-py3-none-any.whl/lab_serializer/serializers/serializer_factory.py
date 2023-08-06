from lab_serializer.serializers.serializer_shell import SerializerShell
from lab_serializer.serializers.json_serializer import Json
from lab_serializer.serializers.xml_serializer import Xml
from .serializer_meta import MetaSerializer

class SerializerFactory:

    serializer_lib={
        'json':Json,
        'xml':Xml
    }


    @classmethod
    def get_serializer(cls,related_type:str):
        return SerializerShell(cls.serializer_lib[related_type]())
    

    @classmethod
    def save_serializer(cls,related_type:str,serializer:MetaSerializer):
        cls.serializer_lib[related_type]=serializer

