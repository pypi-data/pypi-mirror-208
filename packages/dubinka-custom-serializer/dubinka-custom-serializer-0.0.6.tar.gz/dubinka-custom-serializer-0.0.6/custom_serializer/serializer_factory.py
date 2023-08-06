from typing import Literal

from .serializers import json_serializer, xml_serializer


class SerializerFactory:
    @staticmethod
    def serializer(serializer_type: Literal['xml', 'json']):
        if serializer_type == 'xml':
            return xml_serializer
        elif serializer_type == 'json':
            return json_serializer
        else:
            raise Exception("Unknown serializer type")
