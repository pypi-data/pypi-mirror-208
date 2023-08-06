import regex

from functions_for_deserialize import deserialize
from functions_for_serializer import serialize


def _change_symbol(string, reverse=False):
    if reverse:
        return string.replace("&amp;", "&").replace("&lt;", "<").\
            replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")

    else:
        return string.replace("&", "&amp;").replace("<", "&lt;").\
            replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def _create_element(name, value):
    return f"<{name}>{value}</{name}>"


class XMLSerializer:
    from constants import ELEMENT_REG

    def dumps(self, obj):
        obj = serialize(obj)
        return self.check_value(obj)

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def check_value(self, obj):
        if isinstance(obj, (int, float, bool, complex)):
            return _create_element(type(obj).__name__, str(obj))

        if isinstance(obj, str):
            value = _change_symbol(obj)
            return _create_element("str", value)

        if isinstance(obj, list):
            value = "".join([self.check_value(v) for v in obj])
            return _create_element("list", value)

        if isinstance(obj, dict):
            value = "".join([f"{self.check_value(k)}{self.check_value(v)}" for k, v in obj.items()])
            return _create_element("dict", value)

        if not obj:
            return _create_element("NoneType", "None")

    def loads(self, string):
        obj = self.find_element(string)
        return deserialize(obj)

    def load(self, file):
        return self.loads(file.read())

    def find_element(self, string):
        string = str(string)
        string = string.strip()

        match = regex.fullmatch(self.ELEMENT_REG, string)

        if not match:
            return

        key = match.group("key")
        value = match.group("value")

        if key == "int":
            return int(value)

        if key == "float":
            return float(value)

        if key == "str":
            return _change_symbol(value, True)

        if key == "bool":
            return value == "True"

        if key == "complex":
            return complex(value)

        if key == "NoneType":
            return None

        if key == "dict":
            matches = regex.findall(self.ELEMENT_REG, value)
            return {self.find_element(matches[i][0]): self.find_element(matches[i + 1][0])
                    for i in range(0, len(matches), 2)}
