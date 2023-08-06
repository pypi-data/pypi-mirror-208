import inspect
import re
import types

from kirznerSerializer.base_serializer import BaseSerializer
from kirznerSerializer.constants import (CLASS_OR_STATIC_METHOD_TYPE,
                                         BUILD_IN_FUNCTION_NAME,
                                         InvalidJsonException,
                                         UnknownTypeException,
                                         CLOSE_SQUARE_BRACKET,
                                         OPEN_SQUARE_BRACKET,
                                         GENERATOR_TYPE_NAME,
                                         MAP_FILER_GENERATOR,
                                         FUNCTION_TYPE_NAME,
                                         STATIC_METHOD_TYPE,
                                         CLASS_METHOD_TYPE,
                                         LIST_TUPLE_BYTES,
                                         MODULE_TYPE_NAME,
                                         COMMON_JSON_REG,
                                         CODE_TYPE_NAME,
                                         CELL_TYPE_NAME,
                                         PROPERTY_TYPE,
                                         UNIQUE_TYPES,
                                         CLOSE_BRACE,
                                         DELETER_KEY,
                                         OPEN_BRACE,
                                         FILTER_KEY,
                                         NULL_VALUE,
                                         GETTER_KEY,
                                         SETTER_KEY,
                                         MODULE_KEY,
                                         SOURCE_KEY,
                                         CELL_TYPE,
                                         CLASS_KEY,
                                         VALUE_KEY,
                                         BASES_KEY,
                                         TYPE_KEY,
                                         NAME_KEY,
                                         DICT_KEY,
                                         ITER_KEY,
                                         MAP_KEY,
                                         COLON,
                                         COMMA,
                                         NUM)


class JsonSerializer(BaseSerializer):

    @classmethod
    def dumps(cls, obj) -> str:
        return cls.__to_json(obj)

    @classmethod
    def loads(cls, s: str):
        return cls.__from_json(s)

    @classmethod
    def __to_json(cls, obj, comma=False, is_inner_function=False, serialize_value=True):
        json_string = f'{{{TYPE_KEY}"{type(obj).__name__}",{VALUE_KEY}'

        if isinstance(obj, type(None)):
            json_string += NULL_VALUE

        elif isinstance(obj, str):
            json_string += f'"{cls.__escape_string(obj)}"'

        elif isinstance(obj, bool):
            json_string += f'{str(obj).lower()}'

        elif isinstance(obj, NUM):
            json_string += f'{obj}'

        elif isinstance(obj, LIST_TUPLE_BYTES):
            json_string += cls.__serialize_list(obj, serialize_value=serialize_value)

        elif isinstance(obj, set):
            json_string += cls.__serialize_set(obj, serialize_value=serialize_value)

        elif isinstance(obj, dict):
            json_string += cls.__serialize_dict(obj, serialize_value=serialize_value)

        elif inspect.ismodule(obj):
            json_string += f'{obj.__name__}'

        elif inspect.iscode(obj):
            json_string += cls.serialize_code(obj)

        elif isinstance(obj, CELL_TYPE):
            json_string += cls.__to_json(obj.cell_contents)

        elif type(obj) in CLASS_OR_STATIC_METHOD_TYPE:
            json_string += cls.__to_json(obj.__func__, is_inner_function=is_inner_function)

        elif type(obj) is PROPERTY_TYPE:
            json_string = f'{{{TYPE_KEY}"{property.__name__}",{VALUE_KEY}'
            json_string += cls.__to_json({GETTER_KEY: obj.fget, SETTER_KEY: obj.fset, DELETER_KEY: obj.fdel})

        elif inspect.isbuiltin(obj):
            json_string += cls.__to_json({MODULE_KEY: obj.__module__, NAME_KEY: obj.__name__})

        elif inspect.isroutine(obj):
            json_string += cls.serialize_routine(obj, is_inner_function)

        elif cls.is_iterator(obj):
            if not isinstance(obj, MAP_FILER_GENERATOR):
                json_string = f'{{{TYPE_KEY}"{ITER_KEY}",{VALUE_KEY}'
            a = list(obj)
            json_string += cls.__to_json(a)

        elif inspect.isclass(obj):
            json_string += cls.__serialize_class(obj)

        elif isinstance(obj, object):
            source = {CLASS_KEY: cls.__to_json(obj.__class__), SOURCE_KEY: cls.__get_dict(obj)}
            json_string += cls.__to_json(source, serialize_value=False)

        else:
            raise UnknownTypeException(type(obj).__name__)

        json_string += CLOSE_BRACE

        print(json_string)

        if comma:
            json_string += COMMA

        return json_string

    @classmethod
    def __escape_string(cls, s: str):
        s = s.replace('\\', '\\\\').replace('"', '\\"')
        return s

    @classmethod
    def __serialize_list(cls, obj: list | tuple | bytes, serialize_value=True):
        json_string = OPEN_SQUARE_BRACKET
        for i, item in enumerate(obj):
            if serialize_value:
                json_string += cls.__to_json(item, comma=i != len(obj) - 1)
            else:
                json_string += item
        json_string += CLOSE_SQUARE_BRACKET

        return json_string

    @classmethod
    def __serialize_set(cls, obj: set, serialize_value=True):
        json_string = OPEN_BRACE
        for i, item in enumerate(obj):
            if serialize_value:
                json_string += cls.__to_json(item, comma=i != len(obj) - 1)
            else:
                json_string += item
        json_string += CLOSE_BRACE

        return json_string

    @classmethod
    def __serialize_dict(cls, obj: dict, serialize_value=True) -> str:
        json_string = OPEN_BRACE
        for index, (key, value) in enumerate(obj.items()):
            json_string += f'{cls.__to_json(key)}{COLON} '

            if serialize_value:
                json_string += cls.__to_json(value, comma=False)
            else:
                json_string += value

            if index != len(obj) - 1:
                json_string += COMMA

        json_string += CLOSE_BRACE

        return json_string

    @classmethod
    def __serialize_class(cls, obj):
        bases = tuple(base for base in obj.__bases__ if base != object)
        source = {NAME_KEY: cls.__to_json(obj.__name__),
                  BASES_KEY: cls.__to_json(bases),
                  DICT_KEY: cls.__get_dict(obj)}

        return cls.__to_json(source, serialize_value=False)

    @classmethod
    def __get_dict(cls, obj):
        result = {}

        for key, value in obj.__dict__.items():
            if type(value) not in UNIQUE_TYPES:
                if inspect.isroutine(value):
                    result[key] = cls.__to_json(value, is_inner_function=True)
                else:
                    result[key] = cls.__to_json(value)

        return cls.__to_json(result, serialize_value=False)

    @classmethod
    def __from_json(cls, s: str):
        json_pattern_reg = COMMON_JSON_REG
        match = re.fullmatch(json_pattern_reg, s, re.MULTILINE)

        if not match:
            print(s)
            raise InvalidJsonException()
        else:
            type_name = match.group(1)
            value = match.group(2)

            if type_name == type(None).__name__:
                return cls.deserialize_none_type(value)

            elif type_name == str.__name__:
                return cls.__unescape_string(value[1: (len(value) - 1)])

            elif type_name == bool.__name__:
                return cls.deserialize_bool(value)

            elif type_name == int.__name__:
                return int(value)

            elif type_name == float.__name__:
                return float(value)

            elif type_name == list.__name__:
                return cls.__deserialize_list_items(value)

            elif type_name == tuple.__name__:
                return tuple(cls.__deserialize_list_items(value))

            elif type_name == bytes.__name__:
                bytes_value = cls.__deserialize_list_items(value[1: len(value) - 1])
                return bytes(bytes_value)

            elif type_name == set.__name__:
                string = value[1: len(value) - 1]
                return set(cls.__deserialize_list_items(string))

            elif type_name == dict.__name__:
                string = value[1: len(value) - 1]
                return cls.__deserialize_dict_items(string)

            elif type_name == MODULE_TYPE_NAME:
                return __import__(value)

            elif type_name == CODE_TYPE_NAME:
                return cls.deserialize_code(value)

            elif type_name == CELL_TYPE_NAME:
                return cls.deserialize_cell(value)

            elif type_name == MAP_KEY:
                source = cls.__from_json(value)
                return map(lambda x: x, source)

            elif type_name == FILTER_KEY:
                source = cls.__from_json(value)
                return filter(lambda x: x, source)

            elif type_name == GENERATOR_TYPE_NAME:
                source = cls.__from_json(value)
                return iter(value for value in source)

            elif type_name == property.__name__:
                source = cls.__from_json(value)
                return property(source[GETTER_KEY], source[SETTER_KEY], source[DELETER_KEY])

            elif type_name == STATIC_METHOD_TYPE.__name__:
                return staticmethod(cls.__from_json(value))

            elif type_name == CLASS_METHOD_TYPE.__name__:
                return classmethod(cls.__from_json(value))

            elif type_name == BUILD_IN_FUNCTION_NAME:
                source = cls.__from_json(value)
                module = __import__(source[MODULE_KEY])
                return getattr(module, source[NAME_KEY])

            elif type_name == FUNCTION_TYPE_NAME:
                return cls.deserialize_function(value)

            elif type_name == ITER_KEY:
                source = cls.__from_json(value)
                return iter(source)

            elif type_name == type.__name__:
                return cls.deserialize_type(value)

            else:
                value = cls.__from_json(value)
                obj = object.__new__(value[CLASS_KEY])
                obj.__dict__ = value[SOURCE_KEY]
                return obj

    @classmethod
    def __unescape_string(cls, value: str):
        result = value.replace('\\\\', '\\').replace('\\"', '\"')
        return result

    @classmethod
    def __deserialize_list_items(cls, s: str) -> list:
        start_brackets = 0
        start_index = 0
        end_brackets = 0
        result = []

        for i in range(len(s)):
            if s[i] == OPEN_BRACE:
                if start_index == 0:
                    start_index = i
                start_brackets += 1

            elif s[i] == CLOSE_BRACE:
                end_brackets += 1
                if start_brackets == end_brackets:
                    result.append(cls.__from_json(s[start_index: i + 1]))
                    start_index = 0
                    start_brackets = 0
                    end_brackets = 0

        return result

    @classmethod
    def __deserialize_dict_items(cls, s: str) -> dict:
        start_brackets = 0
        start_index = 0
        end_brackets = 0
        key = 0
        key_exists = False
        result = dict()

        for i, char in enumerate(s):
            if char == OPEN_BRACE:
                if start_index == 0:
                    start_index = i
                start_brackets += 1

            elif char == CLOSE_BRACE:
                end_brackets += 1
                if i == len(s) - 1:
                    value = cls.__from_json(s[start_index: i + 1])
                    result[key] = value
                    return result

            elif char == COLON:
                if start_brackets == end_brackets:
                    key = cls.__from_json(s[start_index: i])
                    start_brackets = 0
                    end_brackets = 0
                    start_index = 0
                    key_exists = True

            elif char == COMMA:
                if start_brackets == end_brackets and start_brackets != 0 and key_exists:
                    value = cls.__from_json(s[start_index: i])
                    result[key] = value
                    start_brackets = 0
                    end_brackets = 0
                    start_index = 0
                    key_exists = False

        return result
