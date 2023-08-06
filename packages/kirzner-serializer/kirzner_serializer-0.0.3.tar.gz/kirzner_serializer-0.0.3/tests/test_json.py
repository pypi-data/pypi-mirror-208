import unittest

from kirznerSerializer.json_serializer import JsonSerializer

from kirznerSerializer.constants import (InvalidJsonException,
                                         BoolException)

from tests.test_constants import (SPECIAL_STRING_VARIABLE, FILE_FOR_SPECIAL_STRING_JSON, EXPECTED_SPECIAL_STRING_JSON,
                                  QUOTES_STRING_VARIABLE, FILE_FOR_QUOTES_STRING_JSON, EXPECTED_QUOTES_STRING_JSON,
                                  NESTED_LIST_VARIABLE, FILE_FOR_NESTED_LIST_JSON, EXPECTED_NESTED_LIST_JSON,
                                  DICTIONARY_VARIABLE, FILE_FOR_DICTIONARY_JSON, EXPECTED_DICTIONARY_JSON,
                                  STRING_VARIABLE, FILE_FOR_STRING_JSON, EXPECTED_STRING_JSON,
                                  FLOAT_VARIABLE, FILE_FOR_FLOAT_JSON, EXPECTED_FLOAT_JSON,
                                  TUPLE_VARIABLE, FILE_FOR_TUPLE_JSON, EXPECTED_TUPLE_JSON,
                                  BYTES_VARIABLE, FILE_FOR_BYTES_JSON, EXPECTED_BYTES_JSON,
                                  BOOL_VARIABLE, FILE_FOR_BOOL_JSON, EXPECTED_BOOL_JSON,
                                  NONE_VARIABLE, FILE_FOR_NONE_JSON, EXPECTED_NONE_JSON,
                                  LIST_VARIABLE, FILE_FOR_LIST_JSON, EXPECTED_LIST_JSON,
                                  INT_VARIABLE, FILE_FOR_INT_JSON, EXPECTED_INT_JSON,
                                  SET_VARIABLE, FILE_FOR_SET_JSON, EXPECTED_SET_JSON,
                                  GENERATOR_WITH_SUB_GENERATOR_VARIABLE,
                                  CLASS_WITH_MULTY_LEVEL_INHERITANCE,
                                  FUNCTION_WITH_GLOBALS_REFERENCE,
                                  CLASS_WITH_MULTIPLE_INHERITANCE,
                                  CLASS_WITH_STATIC_METHOD,
                                  INVALID_SERIALIZED_VALUE,
                                  CLASS_WITH_CLASS_METHOD,
                                  CLASS_WITH_INHERITANCE,
                                  DECORATOR_VARIABLE,
                                  GENERATOR_VARIABLE,
                                  RECURSIVE_VARIABLE,
                                  FUNCTION_VARIABLE,
                                  INVALID_BOOL_JSON,
                                  BUILT_IN_FUNCTION,
                                  MODULE_VARIABLE,
                                  LAMBDA_VARIABLE,
                                  FALSE_BOOL_JSON,
                                  CLASS_REFERENCE,
                                  CLASS_WITH_MRO,
                                  CODE_VARIABLE)


class JSONTests(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(JSONPrimitivesTestCase))
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(JSONCollectionsTestCase))
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(JSONFunctionsTestCase))
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(JSONClassesTestCase))
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(JSONAdditionalTestCase))


class JSONPrimitivesTestCase(unittest.TestCase):
    def test_int_serialization(self):
        JsonSerializer.dump(INT_VARIABLE, FILE_FOR_INT_JSON)
        with open(FILE_FOR_INT_JSON, 'r') as file:
            self.assertEqual(EXPECTED_INT_JSON, file.read())

    def test_int_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_INT_JSON)
        self.assertEqual(INT_VARIABLE, actual)

    def test_float_serialization(self):
        JsonSerializer.dump(FLOAT_VARIABLE, FILE_FOR_FLOAT_JSON)
        with open(FILE_FOR_FLOAT_JSON, 'r') as file:
            self.assertEqual(EXPECTED_FLOAT_JSON, file.read())

    def test_float_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_FLOAT_JSON)
        self.assertEqual(FLOAT_VARIABLE, actual)

    def test_string_serialization(self):
        JsonSerializer.dump(STRING_VARIABLE, FILE_FOR_STRING_JSON)
        with open(FILE_FOR_STRING_JSON, 'r') as file:
            self.assertEqual(EXPECTED_STRING_JSON, file.read())

    def test_string_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_STRING_JSON)
        self.assertEqual(STRING_VARIABLE, actual)

    def test_string_with_special_symbols_serialization(self):
        JsonSerializer.dump(SPECIAL_STRING_VARIABLE, FILE_FOR_SPECIAL_STRING_JSON)
        with open(FILE_FOR_SPECIAL_STRING_JSON, 'r') as file:
            self.assertEqual(EXPECTED_SPECIAL_STRING_JSON, file.read())

    def test_string_with_special_symbols_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_SPECIAL_STRING_JSON)
        self.assertEqual(SPECIAL_STRING_VARIABLE, actual)

    def test_string_with_double_quotes_serialization(self):
        JsonSerializer.dump(QUOTES_STRING_VARIABLE, FILE_FOR_QUOTES_STRING_JSON)
        with open(FILE_FOR_QUOTES_STRING_JSON, 'r') as file:
            self.assertEqual(EXPECTED_QUOTES_STRING_JSON, file.read())

    def test_string_with_double_quotes_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_QUOTES_STRING_JSON)
        self.assertEqual(QUOTES_STRING_VARIABLE, actual)

    def test_bool_serialization(self):
        JsonSerializer.dump(BOOL_VARIABLE, FILE_FOR_BOOL_JSON)
        with open(FILE_FOR_BOOL_JSON, 'r') as file:
            self.assertEqual(EXPECTED_BOOL_JSON, file.read())

    def test_bool_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_BOOL_JSON)
        self.assertEqual(BOOL_VARIABLE, actual)

    def test_another_bool_deserialization(self):
        actual = JsonSerializer.loads(FALSE_BOOL_JSON)
        self.assertFalse(actual)

    def test_invalid_bool_deserialization(self):
        self.assertRaises(BoolException, JsonSerializer.loads, INVALID_BOOL_JSON)

    def test_none_type_serialization(self):
        JsonSerializer.dump(NONE_VARIABLE, FILE_FOR_NONE_JSON)
        with open(FILE_FOR_NONE_JSON, 'r') as file:
            self.assertEqual(EXPECTED_NONE_JSON, file.read())

    def test_none_type_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_NONE_JSON)
        self.assertEqual(NONE_VARIABLE, actual)


class JSONCollectionsTestCase(unittest.TestCase):
    def test_list_serialization(self):
        JsonSerializer.dump(LIST_VARIABLE, FILE_FOR_LIST_JSON)
        with open(FILE_FOR_LIST_JSON, 'r') as file:
            self.assertEqual(EXPECTED_LIST_JSON, file.read())

    def test_list_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_LIST_JSON)
        self.assertEqual(LIST_VARIABLE, actual)

    def test_nested_list_serialization(self):
        JsonSerializer.dump(NESTED_LIST_VARIABLE, FILE_FOR_NESTED_LIST_JSON)
        with open(FILE_FOR_NESTED_LIST_JSON, 'r') as file:
            self.assertEqual(EXPECTED_NESTED_LIST_JSON, file.read())

    def test_nested_list_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_NESTED_LIST_JSON)
        self.assertEqual(NESTED_LIST_VARIABLE, actual)

    def test_tuple_serialization(self):
        JsonSerializer.dump(TUPLE_VARIABLE, FILE_FOR_TUPLE_JSON)
        with open(FILE_FOR_TUPLE_JSON, 'r') as file:
            self.assertEqual(EXPECTED_TUPLE_JSON, file.read())

    def test_tuple_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_TUPLE_JSON)
        self.assertEqual(TUPLE_VARIABLE, actual)

    def test_bytes_serialization(self):
        JsonSerializer.dump(BYTES_VARIABLE, FILE_FOR_BYTES_JSON)
        with open(FILE_FOR_BYTES_JSON, 'r') as file:
            self.assertEqual(EXPECTED_BYTES_JSON, file.read())

    def test_bytes_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_BYTES_JSON)
        self.assertEqual(BYTES_VARIABLE, actual)

    def test_set_serialization(self):
        JsonSerializer.dump(SET_VARIABLE, FILE_FOR_SET_JSON)
        with open(FILE_FOR_SET_JSON, 'r') as file:
            self.assertEqual(EXPECTED_SET_JSON, file.read())

    def test_set_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_SET_JSON)
        self.assertEqual(SET_VARIABLE, actual)

    def test_dictionary_serialization(self):
        print(JsonSerializer.dump(DICTIONARY_VARIABLE, FILE_FOR_DICTIONARY_JSON))
        with open(FILE_FOR_DICTIONARY_JSON, 'r') as file:
            self.assertEqual(EXPECTED_DICTIONARY_JSON, file.read())

    def test_dictionary_deserialization(self):
        actual = JsonSerializer.load(FILE_FOR_DICTIONARY_JSON)
        self.assertEqual(DICTIONARY_VARIABLE, actual)


class JSONFunctionsTestCase(unittest.TestCase):
    def test_function(self):
        json = JsonSerializer.dumps(FUNCTION_VARIABLE)
        obj = JsonSerializer.loads(json)
        self.assertEqual(FUNCTION_VARIABLE(), obj())

    def test_built_in_function(self):
        json = JsonSerializer.dumps(BUILT_IN_FUNCTION)
        obj = JsonSerializer.loads(json)
        self.assertEqual(BUILT_IN_FUNCTION, obj)

    def test_lambda(self):
        json = JsonSerializer.dumps(LAMBDA_VARIABLE)
        obj = JsonSerializer.loads(json)
        self.assertEqual(LAMBDA_VARIABLE(STRING_VARIABLE), obj(STRING_VARIABLE))

    def test_wrapper(self):
        json = JsonSerializer.dumps(DECORATOR_VARIABLE)
        obj = JsonSerializer.loads(json)
        self.assertEqual(DECORATOR_VARIABLE(), obj())

    def test_generator(self):
        json = JsonSerializer.dumps(GENERATOR_VARIABLE)
        obj = JsonSerializer.loads(json)
        self.assertEqual([*GENERATOR_VARIABLE()], [*obj()])

    def test_generator_with_sub_generator(self):
        json = JsonSerializer.dumps(GENERATOR_WITH_SUB_GENERATOR_VARIABLE)
        obj = JsonSerializer.loads(json)
        self.assertEqual([*GENERATOR_WITH_SUB_GENERATOR_VARIABLE()], [*obj()])

    def test_recursive(self):
        json = JsonSerializer.dumps(RECURSIVE_VARIABLE)
        obj = JsonSerializer.loads(json)
        self.assertEqual(RECURSIVE_VARIABLE(10), obj(10))

    def test_function_with_globals(self):
        json = JsonSerializer.dumps(FUNCTION_WITH_GLOBALS_REFERENCE)
        obj = JsonSerializer.loads(json)
        self.assertEqual(FUNCTION_WITH_GLOBALS_REFERENCE(0), obj(0))


class JSONClassesTestCase(unittest.TestCase):
    def test_object(self):
        expected_object = CLASS_REFERENCE()
        json = JsonSerializer.dumps(expected_object)
        obj = JsonSerializer.loads(json)
        self.assertEqual(expected_object.hi(), obj.hi())

    def test_class_with_inheritance(self):
        expected_object = CLASS_WITH_INHERITANCE()
        json = JsonSerializer.dumps(CLASS_WITH_INHERITANCE)
        print(json)
        obj = JsonSerializer.loads(json)()
        self.assertEqual(expected_object.hi(), obj.hi())

    def test_with_multy_level_inheritance(self):
        expected_object = CLASS_WITH_MULTY_LEVEL_INHERITANCE()
        json = JsonSerializer.dumps(CLASS_WITH_MULTY_LEVEL_INHERITANCE)
        obj = JsonSerializer.loads(json)()
        self.assertEqual(expected_object.hi(), obj.hi())

    def test_with_multiple_inheritance(self):
        expected_object = CLASS_WITH_MULTIPLE_INHERITANCE()
        json = JsonSerializer.dumps(CLASS_WITH_MULTIPLE_INHERITANCE)
        obj = JsonSerializer.loads(json)()
        self.assertEqual(expected_object.hi(), obj.hi())
        self.assertEqual(expected_object.goodbye(), obj.goodbye())

    def test_with_MRO(self):
        expected_object = CLASS_WITH_MRO()
        json = JsonSerializer.dumps(CLASS_WITH_MRO)
        obj = JsonSerializer.loads(json)()
        self.assertEqual(expected_object.hi(), obj.hi())

    def test_with_static_method(self):
        json = JsonSerializer.dumps(CLASS_WITH_STATIC_METHOD)
        obj = JsonSerializer.loads(json)
        self.assertEqual(CLASS_WITH_STATIC_METHOD.best_programming_language(), obj.best_programming_language())

    def test_with_class_method(self):
        json = JsonSerializer.dumps(CLASS_WITH_CLASS_METHOD)
        obj = JsonSerializer.loads(json)
        self.assertEqual(CLASS_WITH_CLASS_METHOD.class_method(), obj.class_method())


class JSONAdditionalTestCase(unittest.TestCase):
    def test_invalid_json(self):
        self.assertRaises(InvalidJsonException, JsonSerializer.loads, INVALID_SERIALIZED_VALUE)

    def test_module(self):
        json = JsonSerializer.dumps(MODULE_VARIABLE)
        obj = JsonSerializer.loads(json)
        self.assertEqual(obj, MODULE_VARIABLE)
        self.assertEqual(0, obj.sin(0))

    def test_code(self):
        json = JsonSerializer.dumps(CODE_VARIABLE)
        obj = JsonSerializer.loads(json)
        self.assertEqual(CODE_VARIABLE, obj)

    def test_map(self):
        json = JsonSerializer.dumps(map(lambda x: x + 1, [1, 2, 3]))
        obj = JsonSerializer.loads(json)
        self.assertEqual(list(map(lambda x: x + 1, [1, 2, 3])), list(obj))

    def test_filter(self):
        json = JsonSerializer.dumps(filter(lambda x: x > 2, [1, 2, 3]))
        obj = JsonSerializer.loads(json)
        self.assertEqual(list(filter(lambda x: x > 2, [1, 2, 3])), list(obj))

    def test_iter(self):
        json = JsonSerializer.dumps(iter('string'))
        obj = JsonSerializer.loads(json)
        self.assertEqual(next(iter('string')), next(obj))


if __name__ == '__main__':
    unittest.TextTestRunner().run(JSONTests())
