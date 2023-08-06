import unittest

from kirznerSerializer.xml_serializer import XmlSerializer

from kirznerSerializer.constants import (InvalidXmlException,
                                         BoolException)

from tests.test_constants import (SPECIAL_STRING_VARIABLE, FILE_FOR_SPECIAL_STRING_XML, EXPECTED_SPECIAL_STRING_XML,
                                  QUOTES_STRING_VARIABLE, FILE_FOR_QUOTES_STRING_XML, EXPECTED_QUOTES_STRING_XML,
                                  NESTED_LIST_VARIABLE, FILE_FOR_NESTED_LIST_XML, EXPECTED_NESTED_LIST_XML,
                                  DICTIONARY_VARIABLE, FILE_FOR_DICTIONARY_XML, EXPECTED_DICTIONARY_XML,
                                  STRING_VARIABLE, FILE_FOR_STRING_XML, EXPECTED_STRING_XML,
                                  FLOAT_VARIABLE, FILE_FOR_FLOAT_XML, EXPECTED_FLOAT_XML,
                                  TUPLE_VARIABLE, FILE_FOR_TUPLE_XML, EXPECTED_TUPLE_XML,
                                  BYTES_VARIABLE, FILE_FOR_BYTES_XML, EXPECTED_BYTES_XML,
                                  BOOL_VARIABLE, FILE_FOR_BOOL_XML, EXPECTED_BOOL_XML,
                                  NONE_VARIABLE, FILE_FOR_NONE_XML, EXPECTED_NONE_XML,
                                  LIST_VARIABLE, FILE_FOR_LIST_XML, EXPECTED_LIST_XML,
                                  INT_VARIABLE, FILE_FOR_INT_XML, EXPECTED_INT_XML,
                                  SET_VARIABLE, FILE_FOR_SET_XML, EXPECTED_SET_XML,
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
                                  BUILT_IN_FUNCTION,
                                  INVALID_BOOL_XML,
                                  MODULE_VARIABLE,
                                  LAMBDA_VARIABLE,
                                  CLASS_REFERENCE,
                                  FALSE_BOOL_XML,
                                  CLASS_WITH_MRO,
                                  CODE_VARIABLE)


class XMLTests(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(XMLPrimitivesTestCase))
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(XMLCollectionsTestCase))
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(XMLFunctionsTestCase))
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(XMLClassesTestCase))
        self.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(XMLAdditionalTestCase))


class XMLPrimitivesTestCase(unittest.TestCase):
    def test_int_serialization(self):
        XmlSerializer.dump(INT_VARIABLE, FILE_FOR_INT_XML)
        with open(FILE_FOR_INT_XML, 'r') as file:
            self.assertEqual(EXPECTED_INT_XML, file.read())

    def test_int_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_INT_XML)
        self.assertEqual(INT_VARIABLE, actual)

    def test_float_serialization(self):
        XmlSerializer.dump(FLOAT_VARIABLE, FILE_FOR_FLOAT_XML)
        with open(FILE_FOR_FLOAT_XML, 'r') as file:
            self.assertEqual(EXPECTED_FLOAT_XML, file.read())

    def test_float_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_FLOAT_XML)
        self.assertEqual(FLOAT_VARIABLE, actual)

    def test_string_serialization(self):
        XmlSerializer.dump(STRING_VARIABLE, FILE_FOR_STRING_XML)
        with open(FILE_FOR_STRING_XML, 'r') as file:
            self.assertEqual(EXPECTED_STRING_XML, file.read())

    def test_string_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_STRING_XML)
        self.assertEqual(STRING_VARIABLE, actual)

    def test_string_with_special_symbols_serialization(self):
        XmlSerializer.dump(SPECIAL_STRING_VARIABLE, FILE_FOR_SPECIAL_STRING_XML)
        with open(FILE_FOR_SPECIAL_STRING_XML, 'r') as file:
            self.assertEqual(EXPECTED_SPECIAL_STRING_XML, file.read())

    def test_string_with_special_symbols_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_SPECIAL_STRING_XML)
        self.assertEqual(SPECIAL_STRING_VARIABLE, actual)

    def test_string_with_double_quotes_serialization(self):
        XmlSerializer.dump(QUOTES_STRING_VARIABLE, FILE_FOR_QUOTES_STRING_XML)
        with open(FILE_FOR_QUOTES_STRING_XML, 'r') as file:
            self.assertEqual(EXPECTED_QUOTES_STRING_XML, file.read())

    def test_string_with_double_quotes_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_QUOTES_STRING_XML)
        self.assertEqual(QUOTES_STRING_VARIABLE, actual)

    def test_bool_serialization(self):
        XmlSerializer.dump(BOOL_VARIABLE, FILE_FOR_BOOL_XML)
        with open(FILE_FOR_BOOL_XML, 'r') as file:
            self.assertEqual(EXPECTED_BOOL_XML, file.read())

    def test_bool_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_BOOL_XML)
        self.assertEqual(BOOL_VARIABLE, actual)

    def test_another_bool_deserialization(self):
        actual = XmlSerializer.loads(FALSE_BOOL_XML)
        self.assertFalse(actual)

    def test_invalid_bool_deserialization(self):
        self.assertRaises(BoolException, XmlSerializer.loads, INVALID_BOOL_XML)

    def test_none_type_serialization(self):
        XmlSerializer.dump(NONE_VARIABLE, FILE_FOR_NONE_XML)
        with open(FILE_FOR_NONE_XML, 'r') as file:
            self.assertEqual(EXPECTED_NONE_XML, file.read())

    def test_none_type_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_NONE_XML)
        self.assertEqual(NONE_VARIABLE, actual)


class XMLCollectionsTestCase(unittest.TestCase):
    def test_list_serialization(self):
        XmlSerializer.dump(LIST_VARIABLE, FILE_FOR_LIST_XML)
        with open(FILE_FOR_LIST_XML, 'r') as file:
            self.assertEqual(EXPECTED_LIST_XML, file.read())

    def test_list_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_LIST_XML)
        self.assertEqual(LIST_VARIABLE, actual)

    def test_nested_list_serialization(self):
        XmlSerializer.dump(NESTED_LIST_VARIABLE, FILE_FOR_NESTED_LIST_XML)
        with open(FILE_FOR_NESTED_LIST_XML, 'r') as file:
            self.assertEqual(EXPECTED_NESTED_LIST_XML, file.read())

    def test_nested_list_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_NESTED_LIST_XML)
        self.assertEqual(NESTED_LIST_VARIABLE, actual)

    def test_tuple_serialization(self):
        XmlSerializer.dump(TUPLE_VARIABLE, FILE_FOR_TUPLE_XML)
        with open(FILE_FOR_TUPLE_XML, 'r') as file:
            self.assertEqual(EXPECTED_TUPLE_XML, file.read())

    def test_tuple_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_TUPLE_XML)
        self.assertEqual(TUPLE_VARIABLE, actual)

    def test_bytes_serialization(self):
        XmlSerializer.dump(BYTES_VARIABLE, FILE_FOR_BYTES_XML)
        with open(FILE_FOR_BYTES_XML, 'r') as file:
            self.assertEqual(EXPECTED_BYTES_XML, file.read())

    def test_bytes_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_BYTES_XML)
        self.assertEqual(BYTES_VARIABLE, actual)

    def test_set_serialization(self):
        XmlSerializer.dump(SET_VARIABLE, FILE_FOR_SET_XML)
        with open(FILE_FOR_SET_XML, 'r') as file:
            self.assertEqual(EXPECTED_SET_XML, file.read())

    def test_set_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_SET_XML)
        self.assertEqual(SET_VARIABLE, actual)

    def test_dictionary_serialization(self):
        XmlSerializer.dump(DICTIONARY_VARIABLE, FILE_FOR_DICTIONARY_XML)
        with open(FILE_FOR_DICTIONARY_XML, 'r') as file:
            self.assertEqual(EXPECTED_DICTIONARY_XML, file.read())

    def test_dictionary_deserialization(self):
        actual = XmlSerializer.load(FILE_FOR_DICTIONARY_XML)
        self.assertEqual(DICTIONARY_VARIABLE, actual)


class XMLFunctionsTestCase(unittest.TestCase):
    def test_function(self):
        xml = XmlSerializer.dumps(FUNCTION_VARIABLE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(FUNCTION_VARIABLE(), obj())

    def test_built_in_function(self):
        xml = XmlSerializer.dumps(BUILT_IN_FUNCTION)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(BUILT_IN_FUNCTION, obj)

    def test_lambda(self):
        xml = XmlSerializer.dumps(LAMBDA_VARIABLE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(LAMBDA_VARIABLE(STRING_VARIABLE), obj(STRING_VARIABLE))

    def test_wrapper(self):
        xml = XmlSerializer.dumps(DECORATOR_VARIABLE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(DECORATOR_VARIABLE(), obj())

    def test_generator(self):
        xml = XmlSerializer.dumps(GENERATOR_VARIABLE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual([*GENERATOR_VARIABLE()], [*obj()])

    def test_generator_with_sub_generator(self):
        xml = XmlSerializer.dumps(GENERATOR_WITH_SUB_GENERATOR_VARIABLE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual([*GENERATOR_WITH_SUB_GENERATOR_VARIABLE()], [*obj()])

    def test_recursive(self):
        xml = XmlSerializer.dumps(RECURSIVE_VARIABLE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(RECURSIVE_VARIABLE(10), obj(10))

    def test_function_with_globals(self):
        xml = XmlSerializer.dumps(FUNCTION_WITH_GLOBALS_REFERENCE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(FUNCTION_WITH_GLOBALS_REFERENCE(0), obj(0))


class XMLClassesTestCase(unittest.TestCase):
    def test_object(self):
        expected_object = CLASS_REFERENCE()
        xml = XmlSerializer.dumps(expected_object)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(expected_object.hi(), obj.hi())

    def test_class_with_inheritance(self):
        expected_object = CLASS_WITH_INHERITANCE()
        xml = XmlSerializer.dumps(CLASS_WITH_INHERITANCE)
        obj = XmlSerializer.loads(xml)()
        self.assertEqual(expected_object.hi(), obj.hi())

    def test_with_multy_level_inheritance(self):
        expected_object = CLASS_WITH_MULTY_LEVEL_INHERITANCE()
        xml = XmlSerializer.dumps(CLASS_WITH_MULTY_LEVEL_INHERITANCE)
        obj = XmlSerializer.loads(xml)()
        self.assertEqual(expected_object.hi(), obj.hi())

    def test_with_multiple_inheritance(self):
        expected_object = CLASS_WITH_MULTIPLE_INHERITANCE()
        xml = XmlSerializer.dumps(CLASS_WITH_MULTIPLE_INHERITANCE)
        obj = XmlSerializer.loads(xml)()
        self.assertEqual(expected_object.hi(), obj.hi())
        self.assertEqual(expected_object.goodbye(), obj.goodbye())

    def test_with_MRO(self):
        expected_object = CLASS_WITH_MRO()
        xml = XmlSerializer.dumps(CLASS_WITH_MRO)
        obj = XmlSerializer.loads(xml)()
        self.assertEqual(expected_object.hi(), obj.hi())

    def test_with_static_method(self):
        xml = XmlSerializer.dumps(CLASS_WITH_STATIC_METHOD)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(CLASS_WITH_STATIC_METHOD.best_programming_language(), obj.best_programming_language())

    def test_with_class_method(self):
        xml = XmlSerializer.dumps(CLASS_WITH_CLASS_METHOD)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(CLASS_WITH_CLASS_METHOD.class_method(), obj.class_method())


class XMLAdditionalTestCase(unittest.TestCase):
    def test_invalid_XML(self):
        self.assertRaises(InvalidXmlException, XmlSerializer.loads, INVALID_SERIALIZED_VALUE)

    def test_module(self):
        xml = XmlSerializer.dumps(MODULE_VARIABLE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(obj, MODULE_VARIABLE)
        self.assertEqual(0, obj.sin(0))

    def test_code(self):
        xml = XmlSerializer.dumps(CODE_VARIABLE)
        obj = XmlSerializer.loads(xml)
        self.assertEqual(CODE_VARIABLE, obj)

    def test_map(self):
        json = XmlSerializer.dumps(map(lambda x: x + 1, [1, 2, 3]))
        obj = XmlSerializer.loads(json)
        self.assertEqual(list(map(lambda x: x + 1, [1, 2, 3])), list(obj))

    def test_filter(self):
        json = XmlSerializer.dumps(filter(lambda x: x > 2, [1, 2, 3]))
        obj = XmlSerializer.loads(json)
        self.assertEqual(list(filter(lambda x: x > 2, [1, 2, 3])), list(obj))

    def test_iter(self):
        json = XmlSerializer.dumps(iter('string'))
        obj = XmlSerializer.loads(json)
        self.assertEqual(next(iter('string')), next(obj))


if __name__ == '__main__':
    unittest.TextTestRunner().run(XMLTests())
