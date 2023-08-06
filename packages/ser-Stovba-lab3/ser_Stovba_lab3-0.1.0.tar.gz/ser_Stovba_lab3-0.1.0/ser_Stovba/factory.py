from ser_Stovba.json_serializer import json_ser
from ser_Stovba.xml_serializer import xml_ser


class ser_factory:
    @staticmethod
    def create_ser(format:str):
        format = format.lower()

        if format == "json":
            return json_ser()
        elif format == "xml":
            return xml_ser()
        else:
            raise ValueError("No such format")