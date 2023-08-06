import re
import regex
from Lab3.MySerializer import Serializer
from Lab3.MyParser.Parser import Parser
from Lab3.MyParser import nonetype
from Lab3.MyParser.JsonParser import TRUE_LITERAL, FALSE_LITERAL, NULL_LITERAL, INT_PATTERN, FLOAT_PATTERN, BOOL_PATTERN, \
    STRING_PATTERN, NULL_PATTERN, VALUE_PATTERN


class Json(Serializer):
    def dumps(self, obj) -> str:
        def dumps_from_dict(string) -> str:
            if type(string) is nonetype:
                return NULL_LITERAL

            if type(string) is bool:
                return TRUE_LITERAL if string else FALSE_LITERAL

            if type(string) is str:
                return '"' + string.replace('\\', "\\\\").replace('"', r"\"").replace("'", r"\'") + '"'

            if type(string) in (int, float):
                return str(string)

            if type(string) is list:
                return '[' + ", ".join([dumps_from_dict(item) for item in string]) + ']'

            if type(string) is dict:
                return '{' + ", ".join([f"{dumps_from_dict(item[0])}: "
                                        f"{dumps_from_dict(item[1])}" for item in string.items()]) + '}'
            else:
                raise ValueError

        obj = Parser.to_dict(obj)
        return dumps_from_dict(obj)

    def loads(self, obj: str):
        def loads_to_dict(string: str):
            string = string.strip()

            match = re.fullmatch(NULL_PATTERN, string)
            if match:
                return None

            match = re.fullmatch(BOOL_PATTERN, string)
            if match:
                return match.group(0) == TRUE_LITERAL

            match = re.fullmatch(INT_PATTERN, string)
            if match:
                return int(match.group(0))

            match = re.fullmatch(FLOAT_PATTERN, string)
            if match:
                return float(match.group(0))

            match = re.fullmatch(STRING_PATTERN, string)
            if match:
                ans = match.group(0)
                ans = ans.replace('\\\\', "\\").replace(r"\"", '"').replace(r"\'", "'")
                return ans[1:-1]

            if string[0] == '[' and string[-1] == ']':
                string = string[1:-1]
                matches = regex.findall(VALUE_PATTERN, string)
                return [loads_to_dict(match[0]) for match in matches]

            if string[0] == '{' and string[-1] == '}':
                string = string[1:-1]
                matches = regex.findall(VALUE_PATTERN, string)

                return {loads_to_dict(matches[i][0]): loads_to_dict(matches[i + 1][0]) for i in
                        range(0, len(matches), 2)}
            else:
                raise ValueError

        obj = loads_to_dict(obj)
        return Parser.from_dict(obj)
