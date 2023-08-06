from DariasSerializer153501.serializer_xml import serialiser_XML
from DariasSerializer153501.serializer_json import serialiser_JSON


class Fabric:

    @staticmethod
    def create_serializer(format_name: str):
        format_name = format_name.lower()

        if (format_name == "json"):
            return serialiser_JSON()
        elif (format_name == "xml"):
            return serialiser_XML()
        else:
            raise ValueError
