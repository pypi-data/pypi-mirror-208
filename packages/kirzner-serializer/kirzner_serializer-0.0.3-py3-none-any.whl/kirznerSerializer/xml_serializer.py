import inspect
import types

import regex

from kirznerSerializer.base_serializer import BaseSerializer
from kirznerSerializer.constants import (CLASS_OR_STATIC_METHOD_TYPE,
                                         BUILD_IN_FUNCTION_NAME,
                                         FIRST_TYPE_GROUP_NAME,
                                         UnknownTypeException,
                                         LAST_TYPE_GROUP_NAME,
                                         LIST_TUPLE_BYTES_SET,
                                         GENERATOR_TYPE_NAME,
                                         InvalidXmlException,
                                         STATIC_METHOD_TYPE,
                                         FUNCTION_TYPE_NAME,
                                         CLASS_METHOD_TYPE,
                                         VALUE_GROUP_NAME,
                                         MODULE_TYPE_NAME,
                                         COMMON_XML_REG,
                                         CODE_TYPE_NAME,
                                         CELL_TYPE_NAME,
                                         PROPERTY_TYPE,
                                         UNIQUE_TYPES,
                                         DELETER_KEY,
                                         MODULE_KEY,
                                         NULL_VALUE,
                                         SOURCE_KEY,
                                         GETTER_KEY,
                                         SETTER_KEY,
                                         FILTER_KEY,
                                         CELL_TYPE,
                                         BASES_KEY,
                                         CLASS_KEY,
                                         DICT_KEY,
                                         NAME_KEY,
                                         ITER_KEY,
                                         MAP_KEY,
                                         NUM)


class XmlSerializer(BaseSerializer):

    @classmethod
    def dumps(cls, obj):
        return cls.__to_xml(obj)

    @classmethod
    def loads(cls, s: str):
        return cls.__from_xml(s)

    @classmethod
    def __to_xml(cls, obj, is_inner_function=False, serialize_value=True):
        type_name = type(obj).__name__
        xml_string = f'<{type_name}>'

        if isinstance(obj, type(None)):
            xml_string += NULL_VALUE

        elif isinstance(obj, str):
            xml_string += f'"{cls.__escape_string(obj)}"'

        elif isinstance(obj, bool):
            xml_string += f'{str(obj).lower()}'

        elif isinstance(obj, NUM):
            xml_string += f'{obj}'

        elif isinstance(obj, LIST_TUPLE_BYTES_SET):
            if serialize_value:
                xml_string += ''.join([f'{cls.__to_xml(item)}' for item in obj])
            else:
                xml_string += ''.join(item for item in obj)

        elif isinstance(obj, dict):
            if serialize_value:
                xml_string += ''.join([f'{cls.__to_xml(key)}{cls.__to_xml(value)}' for (key, value) in obj.items()])
            else:
                xml_string += ''.join([f'{cls.__to_xml(key)}{value}' for (key, value) in obj.items()])

        elif inspect.ismodule(obj):
            xml_string += f'{obj.__name__}'

        elif inspect.iscode(obj):
            xml_string += cls.serialize_code(obj)

        elif isinstance(obj, CELL_TYPE):
            xml_string += cls.__to_xml(obj.cell_contents)

        elif type(obj) in CLASS_OR_STATIC_METHOD_TYPE:
            xml_string += cls.__to_xml(obj.__func__, is_inner_function=is_inner_function)

        elif type(obj) is PROPERTY_TYPE:
            type_name = property.__name__
            xml_string = f'<{type_name}>'
            xml_string += cls.__to_xml({GETTER_KEY: obj.fget, SETTER_KEY: obj.fset, DELETER_KEY: obj.fdel})

        elif cls.is_iterator(obj):
            if not isinstance(obj, (map, filter, types.GeneratorType)):
                type_name = ITER_KEY
                xml_string = f'<{type_name}>'

            data = list(map(cls.__to_xml, obj))
            xml_string += cls.__to_xml(data, serialize_value=False)

        elif inspect.isbuiltin(obj):
            xml_string += cls.__to_xml({MODULE_KEY: obj.__module__, NAME_KEY: obj.__name__})

        elif inspect.isroutine(obj):
            xml_string += cls.serialize_routine(obj, is_inner_function)

        elif inspect.isclass(obj):
            xml_string += cls.__serialize_class(obj)

        elif isinstance(obj, object):
            source = {CLASS_KEY: cls.__to_xml(obj.__class__),
                      SOURCE_KEY: cls.__to_xml(cls.__get_dict(obj), serialize_value=False)}
            xml_string += cls.__to_xml(source, serialize_value=False)

        else:
            raise UnknownTypeException(type(obj).__name__)

        xml_string += f'</{type_name}>'

        return xml_string

    @classmethod
    def __escape_string(cls, s: str):
        s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        s = s.replace('"', '&quot;').replace("'", '&apos;')
        return s

    @classmethod
    def __serialize_class(cls, obj):
        bases = tuple(base for base in obj.__bases__ if base != object)
        source = {NAME_KEY: cls.__to_xml(obj.__name__),
                  BASES_KEY: cls.__to_xml(bases),
                  DICT_KEY: cls.__to_xml(cls.__get_dict(obj), serialize_value=False)}

        return cls.__to_xml(source, serialize_value=False)

    @classmethod
    def __get_dict(cls, obj):
        result = {}

        for key, value in obj.__dict__.items():
            if type(value) not in UNIQUE_TYPES:
                if inspect.isroutine(value):
                    result[key] = cls.__to_xml(value, is_inner_function=True)
                else:
                    result[key] = cls.__to_xml(value)

        return result

    @classmethod
    def __from_xml(cls, s: str):
        xml_pattern_reg = COMMON_XML_REG
        match = regex.fullmatch(xml_pattern_reg, s)

        if not match:
            raise InvalidXmlException()
        else:
            open_tag = match.group(FIRST_TYPE_GROUP_NAME)
            value = match.group(VALUE_GROUP_NAME)
            close_tag = match.group(LAST_TYPE_GROUP_NAME)

            if open_tag != close_tag:
                raise InvalidXmlException()
            else:
                if open_tag == type(None).__name__:
                    return cls.deserialize_none_type(value)

                elif open_tag == str.__name__:
                    return cls.__unescape_string(value[1: (len(value) - 1)])

                elif open_tag == bool.__name__:
                    return cls.deserialize_bool(value)

                elif open_tag == int.__name__:
                    return int(value)

                elif open_tag == float.__name__:
                    return float(value)

                elif open_tag == list.__name__:
                    matches = regex.findall(COMMON_XML_REG, value)
                    return [cls.__from_xml(match[0]) for match in matches]

                elif open_tag == tuple.__name__:
                    matches = regex.findall(COMMON_XML_REG, value)
                    return tuple([cls.__from_xml(match[0]) for match in matches])

                elif open_tag == set.__name__:
                    matches = regex.findall(COMMON_XML_REG, value)
                    return set([cls.__from_xml(match[0]) for match in matches])

                elif open_tag == bytes.__name__:
                    matches = regex.findall(COMMON_XML_REG, value)
                    return bytes([cls.__from_xml(match[0]) for match in matches])

                elif open_tag == dict.__name__:
                    matches = regex.findall(COMMON_XML_REG, value)
                    return {cls.__from_xml(matches[i][0]): cls.__from_xml(matches[i + 1][0]) for i in
                            range(0, len(matches), 2)}

                elif open_tag == MODULE_TYPE_NAME:
                    return __import__(value)

                elif open_tag == CODE_TYPE_NAME:
                    return cls.deserialize_code(value)

                elif open_tag == CELL_TYPE_NAME:
                    return cls.deserialize_cell(value)

                elif open_tag == MAP_KEY:
                    source = cls.__from_xml(value)
                    return map(lambda x: x, source)

                elif open_tag == FILTER_KEY:
                    source = cls.__from_xml(value)
                    return filter(lambda x: x, source)

                elif open_tag == GENERATOR_TYPE_NAME:
                    source = cls.__from_xml(value)
                    return iter(value for value in source)

                elif open_tag == ITER_KEY:
                    source = cls.__from_xml(value)
                    return iter(source)

                elif open_tag == property.__name__:
                    source = cls.__from_xml(value)
                    return property(source[GETTER_KEY], source[SETTER_KEY], source[DELETER_KEY])

                elif open_tag == STATIC_METHOD_TYPE.__name__:
                    return staticmethod(cls.__from_xml(value))

                elif open_tag == CLASS_METHOD_TYPE.__name__:
                    return classmethod(cls.__from_xml(value))

                elif open_tag == BUILD_IN_FUNCTION_NAME:
                    source = cls.__from_xml(value)
                    module = __import__(source[MODULE_KEY])
                    return getattr(module, source[NAME_KEY])

                elif open_tag == FUNCTION_TYPE_NAME:
                    return cls.deserialize_function(value)

                elif open_tag == type.__name__:
                    return cls.deserialize_type(value)

                else:
                    value = cls.__from_xml(value)
                    obj = object.__new__(value[CLASS_KEY])
                    obj.__dict__ = value[SOURCE_KEY]
                    return obj

    @classmethod
    def __unescape_string(cls, s: str):
        s = s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        s = s.replace('&quot;', '"').replace('&apos;', "'")
        return s
