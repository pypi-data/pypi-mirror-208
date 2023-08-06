import sys
from constants import CREATOR_XML, CREATOR_JSON
from Serializators.JSON import JsonSerializer
from Serializators.XML import XMLSerializer

sys.path.append("/home/PycharmProjects/python_labs/lab_3")


class Creator:

    @staticmethod
    def create_serializer(format_name: str):
        format_name = format_name.lower()

        if format_name == CREATOR_JSON:
            return JsonSerializer()
        elif format_name == CREATOR_XML:
            return XMLSerializer()
        else:
            raise ValueError
