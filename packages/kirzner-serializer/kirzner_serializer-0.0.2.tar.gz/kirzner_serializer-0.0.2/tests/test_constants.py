import math

INVALID_SERIALIZED_VALUE = 'tests string'

INT_VARIABLE = 9
FILE_FOR_INT_JSON = 'test_int.json'
FILE_FOR_INT_XML = 'test_int.xml'
EXPECTED_INT_JSON = '{"type": "int","value": 9}'
EXPECTED_INT_XML = '<int>9</int>'

FLOAT_VARIABLE = 9.9
FILE_FOR_FLOAT_JSON = 'test_float.json'
EXPECTED_FLOAT_JSON = '{"type": "float","value": 9.9}'
FILE_FOR_FLOAT_XML = 'test_float.xml'
EXPECTED_FLOAT_XML = '<float>9.9</float>'

STRING_VARIABLE = 'abc'
FILE_FOR_STRING_JSON = 'test_string.json'
EXPECTED_STRING_JSON = '{"type": "str","value": "abc"}'
FILE_FOR_STRING_XML = 'test_string.xml'
EXPECTED_STRING_XML = '<str>"abc"</str>'

SPECIAL_STRING_VARIABLE = 'abc\\'
FILE_FOR_SPECIAL_STRING_JSON = 'test_special_string.json'
EXPECTED_SPECIAL_STRING_JSON = '{"type": "str","value": "abc\\\\"}'
FILE_FOR_SPECIAL_STRING_XML = 'test_special_string.xml'
EXPECTED_SPECIAL_STRING_XML = '<str>"abc\\"</str>'

QUOTES_STRING_VARIABLE = 'abc"'
FILE_FOR_QUOTES_STRING_JSON = 'test_quotes_string.json'
EXPECTED_QUOTES_STRING_JSON = '{"type": "str","value": "abc\\""}'
FILE_FOR_QUOTES_STRING_XML = 'test_quotes_string.xml'
EXPECTED_QUOTES_STRING_XML = '<str>"abc&quot;"</str>'

BOOL_VARIABLE = True
FILE_FOR_BOOL_JSON = 'test_bool.json'
EXPECTED_BOOL_JSON = '{"type": "bool","value": true}'
FILE_FOR_BOOL_XML = 'test_bool.xml'
EXPECTED_BOOL_XML = '<bool>true</bool>'

FALSE_BOOL_JSON = '{"type": "bool","value": false}'
FALSE_BOOL_XML = '<bool>false</bool>'

INVALID_BOOL_JSON = '{"type": "bool","value": tests}'
INVALID_BOOL_XML = '<bool>tests</bool>'

NONE_VARIABLE = None
FILE_FOR_NONE_JSON = 'test_none.json'
EXPECTED_NONE_JSON = '{"type": "NoneType","value": null}'
FILE_FOR_NONE_XML = 'test_none.xml'
EXPECTED_NONE_XML = '<NoneType>null</NoneType>'

LIST_VARIABLE = [1, 2, 3]
FILE_FOR_LIST_JSON = 'test_list.json'
EXPECTED_LIST_JSON = '{"type": "list","value": [{"type": "int","value": 1},{"type": "int","value": 2},{"type": "int",' \
                     '"value": 3}]}'
FILE_FOR_LIST_XML = 'test_list.xml'
EXPECTED_LIST_XML = '<list><int>1</int><int>2</int><int>3</int></list>'

NESTED_LIST_VARIABLE = [[1], 2, 3]
FILE_FOR_NESTED_LIST_JSON = 'test_nested_list.json'
EXPECTED_NESTED_LIST_JSON = '{"type": "list","value": [{"type": "list","value": [{"type": "int","value": 1}]},' \
                            '{"type": "int","value": 2},{"type": "int","value": 3}]}'
FILE_FOR_NESTED_LIST_XML = 'test_nested_list.xml'
EXPECTED_NESTED_LIST_XML = '<list><list><int>1</int></list><int>2</int><int>3</int></list>'

TUPLE_VARIABLE = (1, 2, 3)
FILE_FOR_TUPLE_JSON = 'test_tuple.json'
EXPECTED_TUPLE_JSON = '{"type": "tuple","value": [{"type": "int","value": 1},{"type": "int","value": 2},{"type": ' \
                      '"int","value": 3}]}'
FILE_FOR_TUPLE_XML = 'test_tuple.xml'
EXPECTED_TUPLE_XML = '<tuple><int>1</int><int>2</int><int>3</int></tuple>'

BYTES_VARIABLE = bytes([1, 2, 3])
FILE_FOR_BYTES_JSON = 'test_bytes.json'
EXPECTED_BYTES_JSON = '{"type": "bytes","value": [{"type": "int","value": 1},{"type": "int","value": 2},{"type": ' \
                      '"int","value": 3}]}'
FILE_FOR_BYTES_XML = 'test_bytes.xml'
EXPECTED_BYTES_XML = '<bytes><int>1</int><int>2</int><int>3</int></bytes>'

SET_VARIABLE = {1, 2, 3}
FILE_FOR_SET_JSON = 'test_set.json'
EXPECTED_SET_JSON = '{"type": "set","value": {{"type": "int","value": 1},{"type": "int","value": 2},{"type": "int",' \
                    '"value": 3}}}'
FILE_FOR_SET_XML = 'test_set.xml'
EXPECTED_SET_XML = '<set><int>1</int><int>2</int><int>3</int></set>'

DICTIONARY_VARIABLE = {1: 'a', 2: 'b', 3: 'c'}
FILE_FOR_DICTIONARY_JSON = 'test_dictionary.json'
EXPECTED_DICTIONARY_JSON = '{"type": "dict","value": {{"type": "int","value": 1}: {"type": "str","value": "a"},' \
                           '{"type": "int","value": 2}: {"type": "str","value": "b"},{"type": "int","value": 3}: {' \
                           '"type": "str","value": "c"}}}'
FILE_FOR_DICTIONARY_XML = 'test_dictionary.xml'
EXPECTED_DICTIONARY_XML = '<dict><int>1</int><str>"a"</str><int>2</int><str>"b"</str><int>3</int><str>"c"</str></dict>'

MODULE_VARIABLE = math


def test_function_1():
    pass


def test_function_2():
    return 9


CODE_VARIABLE = test_function_1.__code__

FUNCTION_VARIABLE = test_function_2

BUILT_IN_FUNCTION = len

LAMBDA_VARIABLE = lambda string: string.upper()[::-1]


def decorator(function):
    def inner():
        return function()

    return inner


def function_to_be_used():
    return 5


DECORATOR_VARIABLE = decorator(function_to_be_used)


def generator():
    for i in range(3):
        yield i


def generator_with_sub_generator():
    for i in range(9):
        yield i
    yield from generator()


GENERATOR_VARIABLE = generator

GENERATOR_WITH_SUB_GENERATOR_VARIABLE = generator_with_sub_generator


def fibonacci(n: int):
    if n <= 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


RECURSIVE_VARIABLE = fibonacci


def function_with_globals(n):
    return math.sin(n)


FUNCTION_WITH_GLOBALS_REFERENCE = function_with_globals


class A:
    def hi(self):
        return 'hi'


class B(A):
    pass


class C(B):
    pass


class D:
    def goodbye(self):
        return 'goodbye'


class E(A, D):
    pass


class F(A):
    def hi(self):
        return 'hi in F!'


class G:
    @staticmethod
    def best_programming_language():
        return 'PYTHON'


class H:
    num = 10

    @classmethod
    def class_method(cls):
        return cls.num


CLASS_REFERENCE = A
CLASS_WITH_INHERITANCE = B
CLASS_WITH_MULTY_LEVEL_INHERITANCE = C
CLASS_WITH_MULTIPLE_INHERITANCE = E
CLASS_WITH_MRO = F
CLASS_WITH_STATIC_METHOD = G
CLASS_WITH_CLASS_METHOD = H
