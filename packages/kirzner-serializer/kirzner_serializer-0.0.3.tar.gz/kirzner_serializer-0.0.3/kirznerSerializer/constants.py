import types
from types import (CodeType,
                   CellType,
                   ModuleType,
                   FunctionType,
                   MappingProxyType,
                   BuiltinMethodType,
                   MethodDescriptorType,
                   GetSetDescriptorType,
                   WrapperDescriptorType)

TYPE_KEY = '"type": '
VALUE_KEY = '"value": '

JSON_FORMAT = 'json'
XML_FORMAT = 'xml'

COMMA = ','
COLON = ':'
OPEN_BRACE = '{'
CLOSE_BRACE = '}'
OPEN_SQUARE_BRACKET = '['
CLOSE_SQUARE_BRACKET = ']'

NUM = (int, float)
LIST_TUPLE_BYTES = (list, tuple, bytes)
LIST_TUPLE_BYTES_SET = (list, tuple, bytes, set)

COMMON_JSON_REG = r'{\"type\": \"(\w+)\",\"value\": ([\s\S]+)}'

FIRST_TYPE_GROUP_NAME = 'open_type'
VALUE_GROUP_NAME = 'value'
LAST_TYPE_GROUP_NAME = 'close_type'

COMMON_XML_REG = fr'(\<(?P<{FIRST_TYPE_GROUP_NAME}>\w+)\>(?P<{VALUE_GROUP_NAME}>([^<>]*)|(?R)+)\</(?:(?P<' + \
                 fr'{LAST_TYPE_GROUP_NAME}>\w+))\>)'

NULL_VALUE = 'null'
TRUE_VALUE = 'true'
FALSE_VALUE = 'false'

BOOL_ERROR = 'Invalid bool value!'
NULL_ERROR = 'Invalid null value!'
JSON_ERROR = 'Invalid json value!'
XMl_ERROR = 'Invalid xml value!'
UNKNOWN_TYPE_ERROR = 'Type cannot be serialized: '


class BoolException(BaseException):
    message = BOOL_ERROR

    def __init__(self, *args):
        super().__init__(self.message, *args)


class NullException(BaseException):
    message = NULL_ERROR

    def __init__(self, *args):
        super().__init__(self.message, *args)


class InvalidJsonException(BaseException):
    message = JSON_ERROR

    def __init__(self, *args):
        super().__init__(self.message, *args)


class InvalidXmlException(BaseException):
    message = XMl_ERROR

    def __init__(self, *args):
        super().__init__(self.message, *args)


class UnknownTypeException(BaseException):
    message = UNKNOWN_TYPE_ERROR

    def __init__(self, type_name: str, *args):
        super().__init__(self.message + type_name, *args)


NAME_KEY = '__name__'
CODE_KEY = '__code__'
DICT_KEY = '__dict__'
CLASS_KEY = '__class__'
BASES_KEY = '__bases__'
MODULE_KEY = '__module__'
GLOBALS_KEY = '__globals__'
CLOSURE_KEY = '__closure__'
DEFAULTS_KEY = '__defaults__'


SOURCE_KEY = 'source'

GETTER_KEY = 'getter'
SETTER_KEY = 'setter'
DELETER_KEY = 'deleter'

MAP_KEY = 'map'
ITER_KEY = 'iter'
FILTER_KEY: str = 'filter'
GENERATOR_TYPE_NAME = 'generator'

MAP_FILER_GENERATOR = (map, filter, types.GeneratorType)

FUNCTION_ATTRIBUTES = (CODE_KEY, GLOBALS_KEY, NAME_KEY, DEFAULTS_KEY, CLOSURE_KEY)

CODE_ATTRIBUTES = [CodeType.co_argcount.__name__,
                   CodeType.co_posonlyargcount.__name__,
                   CodeType.co_kwonlyargcount.__name__,
                   CodeType.co_nlocals.__name__,
                   CodeType.co_stacksize.__name__,
                   CodeType.co_flags.__name__,
                   CodeType.co_code.__name__,
                   CodeType.co_consts.__name__,
                   CodeType.co_names.__name__,
                   CodeType.co_varnames.__name__,
                   CodeType.co_filename.__name__,
                   CodeType.co_name.__name__,
                   CodeType.co_firstlineno.__name__,
                   CodeType.co_lnotab.__name__,
                   CodeType.co_freevars.__name__,
                   CodeType.co_cellvars.__name__]

CELL_TYPE = CellType
CODE_TYPE = CodeType
MODULE_TYPE = ModuleType
FUNCTION_TYPE = FunctionType

UNIQUE_TYPES = (MappingProxyType, WrapperDescriptorType, MethodDescriptorType, GetSetDescriptorType, BuiltinMethodType)

CODE_TYPE_NAME = CODE_TYPE.__name__
CELL_TYPE_NAME = CELL_TYPE.__name__
MODULE_TYPE_NAME = MODULE_TYPE.__name__
FUNCTION_TYPE_NAME = FUNCTION_TYPE.__name__
BUILD_IN_FUNCTION_NAME = 'builtin_function_or_method'

PROPERTY_TYPE = property
CLASS_METHOD_TYPE = classmethod
STATIC_METHOD_TYPE = staticmethod

CLASS_OR_STATIC_METHOD_TYPE = (CLASS_METHOD_TYPE, STATIC_METHOD_TYPE)
