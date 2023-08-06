
from DariasSerializer153501.my_serializer import my_deserializer, my_serializer
import regex


class serialiser_XML:
    BASE_TYPES = r"str|int|float|bool|NoneType|list|dict"
    key = "key"
    val = "value"
    # именованные группы(для оращения по key и value)
    ELEMENT_REGULAR = fr"\s*(\<(?P<{key}>{BASE_TYPES})\>(?P<{val}>([^<>]*)|(?R)+)\</(?:{BASE_TYPES})\>)\s*"
    def dumps(self, objet):
        print(objet)
        return self.convert_to_str(my_serializer(objet))

    def dump(self, objet, file):
        file.write(self.dumps(objet))

    def loads(self, string):
        # print (string)
        return my_deserializer(self.convert_to_expression(string))

    def load(self, file):
        return self.loads(file.read())

    def convert_to_str(self, obj):
        if isinstance(obj, (int, float, bool, complex)):
            return self._create_element(type(obj).__name__, str(obj))

        if isinstance(obj, str):
            return self._create_element("str", self._from_normal_symbol(obj))

        if isinstance(obj, list):
            value = "".join([self.convert_to_str(v) for v in obj])
            return self._create_element("list", value)

        if isinstance(obj, dict):
            value = "".join([f"{self.convert_to_str(k)}\
                                {self.convert_to_str(v)}" \
                             for k, v in obj.items()])
            return self._create_element("dict", value)

        if not obj:
            return self._create_element("NoneType", "None")

    def _create_element(self, name, value):
        return f"<{name}>{value}</{name}>"

    def _from_normal_symbol(self, string):
        return string.replace("&", "&amp;").replace("<", "&lt;"). \
                replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

    def _from_reverse_symbol(self, string):
        return string.replace("&amp;", "&").replace("&lt;", "<"). \
            replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")

    def convert_to_expression(self, string):
        print(string)
        string = str(string)
        string = string.strip()

        copia = regex.fullmatch(self.ELEMENT_REGULAR, string)

        if not copia:
            return

        key = copia.group("key")
        value = copia.group("value")

        if key == "int":
            return int(value)

        if key == "float":
            return float(value)

        if key == "str":
            return self._from_reverse_symbol(value)

        if key == "bool":
            return value == "True"

        if key == "complex":
            return complex(value)

        if key == "NoneType":
            return None

        if key == "list":
            all_sovpad = regex.findall(self.ELEMENT_REGULAR, value)
            return [self.convert_to_expression(a[0]) for a in all_sovpad]

        if key == "dict":
            all_sovpad = regex.findall(self.ELEMENT_REGULAR, value)
            return {self.convert_to_expression(all_sovpad[i][0]):
                        self.convert_to_expression(all_sovpad[i + 1][0]) \
                    for i in range(0, len(all_sovpad), 2)}