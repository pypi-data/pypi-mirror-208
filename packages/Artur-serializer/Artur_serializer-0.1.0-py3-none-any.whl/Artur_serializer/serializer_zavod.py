from Artur_serializer.xml_serializer import xml_serializer
from Artur_serializer.json_serializer import json_serializer


class zavod:

    @staticmethod
    def create_zavod(f_mat: str):
        f_mat = f_mat.lower()

        if f_mat == "json":
            return json_serializer()
        elif f_mat == "xml":
            return xml_serializer()
        else:
            raise ValueError
