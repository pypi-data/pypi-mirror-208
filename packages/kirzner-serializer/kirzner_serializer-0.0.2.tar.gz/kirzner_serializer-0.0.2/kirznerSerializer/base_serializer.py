import inspect
from abc import ABC, abstractmethod

from kirznerSerializer.constants import (FUNCTION_ATTRIBUTES,
                                         STATIC_METHOD_TYPE,
                                         CLASS_METHOD_TYPE,
                                         CODE_ATTRIBUTES,
                                         BoolException,
                                         FUNCTION_TYPE,
                                         NullException,
                                         DEFAULTS_KEY,
                                         FALSE_VALUE,
                                         GLOBALS_KEY,
                                         MODULE_TYPE,
                                         CLOSURE_KEY,
                                         TRUE_VALUE,
                                         NULL_VALUE,
                                         CODE_TYPE,
                                         CELL_TYPE,
                                         BASES_KEY,
                                         CODE_KEY,
                                         NAME_KEY,
                                         DICT_KEY)


class BaseSerializer(ABC):
    @classmethod
    def dump(cls, obj, filepath: str):
        string = cls.dumps(obj)
        with open(filepath, 'w') as file:
            file.write(string)

    @classmethod
    @abstractmethod
    def dumps(cls, obj):
        pass

    @classmethod
    def load(cls, filepath: str):
        with open(filepath, 'r') as file:
            return cls.loads(file.read())

    @classmethod
    @abstractmethod
    def loads(cls, s: str):
        pass

    @classmethod
    def is_iterator(cls, obj):
        return hasattr(obj, '__iter__') and hasattr(obj, '__next__') and callable(obj.__iter__)

    @classmethod
    def serialize_code(cls, obj: CODE_TYPE):
        source = {}
        for (key, value) in inspect.getmembers(obj):
            if key in CODE_ATTRIBUTES:
                source[key] = value
        source_json = cls.dumps(source)

        return source_json

    @classmethod
    def serialize_routine(cls, obj, is_inner_function):
        source = {}
        global_vars = cls.get_global_vars(obj, is_inner_function)

        for key, value in inspect.getmembers(obj):
            if key in FUNCTION_ATTRIBUTES:
                source[key] = value

        source[GLOBALS_KEY] = global_vars

        return cls.dumps(source)

    @classmethod
    def get_global_vars(cls, function, is_inner_function):
        name = function.__name__
        global_vars = {}

        for global_var_name in function.__code__.co_names:
            if global_var_name in function.__globals__:
                if isinstance(function.__globals__[global_var_name], MODULE_TYPE):
                    global_vars[global_var_name] = function.__globals__[global_var_name]

                elif inspect.isclass(function.__globals__[global_var_name]):
                    global_var_class = function.__globals__[global_var_name]
                    is_in_class_dict = function == global_var_class.__dict__[name].__func__

                    if is_inner_function and name in global_var_class.__dict__ and is_in_class_dict:
                        global_vars[global_var_name] = global_var_class.__name__
                    else:
                        global_vars[global_var_name] = global_var_class

                elif global_var_name == function.__code__.co_name:
                    global_vars[global_var_name] = function.__name__

                else:
                    global_vars[global_var_name] = function.__globals__[global_var_name]

        return global_vars

    @classmethod
    def deserialize_bool(cls, value: str):
        if value == TRUE_VALUE:
            return True

        if value == FALSE_VALUE:
            return False

        raise BoolException()

    @classmethod
    def deserialize_none_type(cls, value: str):
        if value == NULL_VALUE:
            return None

        raise NullException()

    @classmethod
    def deserialize_code(cls, value):
        source = cls.loads(value)
        attributes = []
        for attribute in CODE_ATTRIBUTES:
            attributes.append(source[attribute])

        return CODE_TYPE(*attributes)

    @classmethod
    def deserialize_cell(cls, value):
        cell_value = cls.loads(value)
        cell = CELL_TYPE()
        cell.cell_contents = cell_value

        return cell

    @classmethod
    def deserialize_function(cls, value):
        source = cls.loads(value)
        for key in source[GLOBALS_KEY]:
            if key in source[CODE_KEY].co_name and key in globals():
                source[GLOBALS_KEY][key] = globals()[key]

        function = FUNCTION_TYPE(source[CODE_KEY], source[GLOBALS_KEY], source[NAME_KEY],
                                 source[DEFAULTS_KEY], source[CLOSURE_KEY])

        if function.__name__ in source[GLOBALS_KEY]:
            function.__globals__.update({function.__name__: function})

        return function

    @classmethod
    def deserialize_type(cls, value):
        source = cls.loads(value)
        name = source[NAME_KEY]
        bases = source[BASES_KEY]
        dictionary = source[DICT_KEY]
        result = type(name, bases, dictionary)

        for attribute in result.__dict__.values():
            if inspect.isroutine(attribute):

                if type(attribute) in (STATIC_METHOD_TYPE, CLASS_METHOD_TYPE):
                    function_globals = attribute.__func__.__globals__
                else:
                    function_globals = attribute.__globals__

                for variable in function_globals.keys():
                    if variable == result.__name__:
                        function_globals[variable] = result

        return result
