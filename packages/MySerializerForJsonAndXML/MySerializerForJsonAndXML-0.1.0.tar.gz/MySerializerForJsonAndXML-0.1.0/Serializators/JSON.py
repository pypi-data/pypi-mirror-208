import regex
from functions_for_serializer import serialize
from functions_for_deserialize import deserialize


class JsonSerializer:
    from constants import INT_REG, STR_REG, BOOL_REG, NONE_REG, VALUE_REG, FLOAT_REG

    def dumps(self, obj):
        obj = serialize(obj)
        return self.check_value(obj)

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def check_value(self, value):
        if isinstance(value, str):
            return '"' + value.replace("\\", "\\\\").replace('"', "\"").replace("'", "\'") + '"'

        elif isinstance(value, (int, float, complex)):
            return str(value)

        elif isinstance(value, bool):
            return "true" if value else "false"

        elif isinstance(value, list):
            return "[" + ", ".join([self.check_value(val) for val in value]) + "]"

        if isinstance(value, dict):
            return "{" + ", ".join([f"{self.check_value(k)}: {self.check_value(v)}" for k, v in value.items()]) + "}"

    def find_element(self, string):
        string = string.strip()

        match = regex.fullmatch(self.INT_REG, string)
        if match:
            return int(match.group(0))

        match = regex.fullmatch(self.STR_REG, string)
        if match:
            res = match.group(0)
            res = res.replace("\\\\", "\\").replace(r"\"", '"').replace(r"\'", "'")
            return res[1:-1]

        match = regex.fullmatch(self.FLOAT_REG, string)
        if match:
            return float(match.group(0))

        match = regex.fullmatch(self.BOOL_REG, string)

        if match:
            return match.group(0) == "true"

        match = regex.fullmatch(self.NONE_REG, string)

        if match:
            return None

        if string.startswith("[") and string.endswith("]"):
            string = string[1:-1]
            matches = regex.findall(self.VALUE_REG, string)
            return [self.find_element(match[0]) for match in matches]

        if string.startswith("{") and string.endswith("}"):
            string = string[1:-1]
            matches = regex.findall(self.VALUE_REG, string)

            return {self.find_element(matches[i][0]): self.find_element(matches[i+1][0])
                    for i in range(0, len(matches), 2)}

    def loads(self, string):
        obj = self.find_element(string)
        return deserialize(obj)

    def load(self, file):
        return self.loads(file.read())
