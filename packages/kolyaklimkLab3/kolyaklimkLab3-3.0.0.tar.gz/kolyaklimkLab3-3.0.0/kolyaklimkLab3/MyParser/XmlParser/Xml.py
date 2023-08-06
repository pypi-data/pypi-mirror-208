import regex
from kolyaklimkLab3.MySerializer import Serializer
from kolyaklimkLab3.MyParser import Parser, nonetype
from kolyaklimkLab3.MyParser.XmlParser import KEY_GROUP_NAME, VALUE_GROUP_NAME, XML_SCHEME_SOURCE, XML_ELEMENT_PATTERN, \
    FIRST_XML_ELEMENT_PATTERN


class Xml(Serializer):
    def dumps(self, obj) -> str:
        def create_xml_element(name: str, data: str, is_first=False):
            if is_first:
                return f"<{name} {XML_SCHEME_SOURCE}>{data}</{name}>"
            else:
                return f"<{name}>{data}</{name}>"

        def dumps_from_dict(string, is_first=False) -> str:
            if type(string) in (int, float, bool, nonetype):
                return create_xml_element(type(string).__name__, str(string), is_first)

            if type(string) is str:
                data = string.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;"). \
                    replace('"', "&quot;").replace("'", "&apos;")
                return create_xml_element(str.__name__, data, is_first)

            if type(string) is list:
                data = ''.join([dumps_from_dict(o) for o in string])
                return create_xml_element(list.__name__, data, is_first)

            if type(string) is dict:
                data = ''.join([f"{dumps_from_dict(item[0])}{dumps_from_dict(item[1])}" for item in string.items()])
                return create_xml_element(dict.__name__, data, is_first)
            else:
                raise ValueError

        obj = Parser.to_dict(obj)
        return dumps_from_dict(obj, True)

    def loads(self, obj: str):
        def loads_to_dict(string: str, is_first=False):
            string = string.strip()
            xml_element_pattern = FIRST_XML_ELEMENT_PATTERN if is_first else XML_ELEMENT_PATTERN

            match = regex.fullmatch(xml_element_pattern, string)

            if not match:
                raise ValueError

            key = match.group(KEY_GROUP_NAME)
            value = match.group(VALUE_GROUP_NAME)

            if key == int.__name__:
                return int(value)

            if key == float.__name__:
                return float(value)

            if key == bool.__name__:
                return value == str(True)

            if key == str.__name__:
                return value.replace("&amp;", '&').replace("&lt;", '<').replace("&gt;", '>'). \
                    replace("&quot;", '"').replace("&apos;", "'")

            if key == nonetype.__name__:
                return None

            if key == list.__name__:
                matches = regex.findall(XML_ELEMENT_PATTERN, value)
                return [loads_to_dict(match[0]) for match in matches]

            if key == dict.__name__:
                matches = regex.findall(XML_ELEMENT_PATTERN, value)
                return {loads_to_dict(matches[i][0]): loads_to_dict(matches[i + 1][0]) for i in
                        range(0, len(matches), 2)}
            else:
                raise ValueError

        obj = loads_to_dict(obj, True)
        return Parser.from_dict(obj)
