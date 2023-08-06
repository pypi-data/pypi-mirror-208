import base64
import builtins
import inspect
import math

from .constants import PRIMITIVE_TYPES, UNSERIALIZABLE_DUNDER, \
    UNSERIALIZABLE_TYPES, UNSERIALIZABLE_CODE_TYPES, \
    ITERATOR_TYPE, CODE_TYPE, CELL_TYPE, MODULE_TYPE, FUNCTION_TYPE, \
    BYTES_TYPE, CLASS_TYPE, OBJ_TYPE, TUPLE_TYPE, SET_TYPE
from .supportive import get_fathers_class_for_method

from types import ModuleType, CellType, FunctionType, \
    MethodType, CodeType


class Converter:
    @classmethod
    def convert(cls, obj):
        if isinstance(obj, PRIMITIVE_TYPES):
            return obj
        if isinstance(obj, ModuleType):
            return cls._encode_module(obj)
        if isinstance(obj, CellType):
            return cls._encode_cell(obj)
        if isinstance(obj, bytes):
            return cls._encode_bytes(obj)
        if isinstance(obj, list):
            return type(obj)((cls.convert(item) for item in obj))
        if isinstance(obj, (tuple, set)):
            return cls._encode_collection(obj)
        if isinstance(obj, dict):
            return {key: cls.convert(value) for key, value in obj.items()}
        if isinstance(obj, (FunctionType, MethodType)):
            return cls._encode_function(obj)
        if isinstance(obj, type):
            return cls._encode_class(obj)
        if cls.is_iterable(obj):
            return cls._encode_iterator(obj)
        if isinstance(obj, CodeType):
            return cls._encode_code(obj)
        if isinstance(obj, object):
            return cls._encode_object(obj)

    @classmethod
    def deconvert(cls, obj):
        if isinstance(obj, PRIMITIVE_TYPES):
            return obj
        if isinstance(obj, list):
            return type(obj)((cls.deconvert(item) for item in obj))
        if isinstance(obj, dict):
            type_to_decode = cls._get_type(obj)

            if type_to_decode is None:
                return {key: cls.deconvert(value) for key, value in obj.items()}
            if type_to_decode == BYTES_TYPE:
                return cls._decode_bytes(obj)
            if type_to_decode == FUNCTION_TYPE:
                return cls._decode_function(obj)
            if type_to_decode == CELL_TYPE:
                return cls._decode_cell(obj)
            if type_to_decode == CLASS_TYPE:
                return cls._decode_class(obj)
            if type_to_decode == ITERATOR_TYPE:
                return cls._decode_iterator(obj)
            if type_to_decode == CODE_TYPE:
                return cls._decode_code(obj)
            if type_to_decode == MODULE_TYPE:
                return cls._decode_module(obj)
            if type_to_decode in (TUPLE_TYPE, SET_TYPE):
                return cls._decode_collection(obj)
            if type_to_decode == OBJ_TYPE:
                return cls._decode_object(obj)
        return obj

    @classmethod
    def _decode_collection(cls, obj):
        data = cls._get_data(obj)
        collection = getattr(builtins, cls._get_type(obj).lower())
        return collection((cls.deconvert(item) for item in data))

    @classmethod
    def _decode_module(cls, obj):
        return __import__(cls._get_data(obj))

    @classmethod
    def _decode_iterator(cls, obj):
        data = cls._get_data(obj)
        return iter(cls.deconvert(value) for value in data)

    @classmethod
    def _decode_code(cls, obj):
        data = cls._get_data(obj)

        def func():
            pass

        code_dict = cls.deconvert(data)
        return func.__code__.replace(**code_dict)


    @classmethod
    def _decode_object(cls, obj):
        data = cls._get_data(obj)
        obj_class = cls.deconvert(data['__class__'])

        decoded_obj = object.__new__(obj_class)
        decoded_obj.__dict__ = {
            key: cls.deconvert(value) for key, value in data['attrs'].items()
        }

        return decoded_obj

    @classmethod
    def _decode_class(cls, obj):
        data = cls._get_data(obj)

        class_bases = tuple(cls.deconvert(base) for base in data.pop('__bases__'))

        class_dict = {
            attr: cls.deconvert(value)
            for attr, value in data.items()
            if not (isinstance(value, dict) and cls._get_type(value) == FUNCTION_TYPE)
        }

        decoded_class = type(data['__name__'], class_bases, class_dict)

        for key, value in data.items():
            if isinstance(value, dict) and cls._get_type(value) == FUNCTION_TYPE:
                try:
                    function = cls.deconvert(value)
                except ValueError:
                    closure = cls._get_data(value)['closure']
                    cls._get_data(closure).append(cls._make_cell(decoded_class))
                    function = cls.deconvert(value)
                function.__globals__.update({decoded_class.__name__: decoded_class})

                if value.get('is_method'):
                    function = MethodType(function, decoded_class)

                setattr(decoded_class, key, function)
        return decoded_class

    @classmethod
    def _decode_cell(cls, obj):
        return cls._make_cell(cls.deconvert(cls._get_data(obj)))

    @classmethod
    def _decode_function(cls, obj):
        encoded_function = cls.deconvert(cls._get_data(obj))

        func_dict = encoded_function.pop('func_dict')

        new_func = FunctionType(**encoded_function)
        new_func.__dict__.update(func_dict)
        new_func.__globals__.update({new_func.__name__: new_func})
        return new_func

    @classmethod
    def _decode_bytes(cls, obj):
        return base64.b64decode(cls._get_data(obj).encode("ascii"))

    @classmethod
    def _encode_cell(cls, obj):
        data = cls.convert(obj.cell_contents)
        return cls._create_dict(data, CELL_TYPE)

    @classmethod
    def _encode_code(cls, obj):
        attrs = [attr for attr in dir(obj) if attr.startswith('co')]

        code_dict = {
            attr: cls.convert(getattr(obj, attr))
            for attr in attrs
            if attr not in UNSERIALIZABLE_CODE_TYPES
        }

        return cls._create_dict(code_dict, CODE_TYPE)

    @classmethod
    def _encode_iterator(cls, obj):
        data = list(map(cls.convert, obj))
        return cls._create_dict(data, ITERATOR_TYPE)

    @classmethod
    def _encode_class(cls, obj):
        data = {
            attr: cls.convert(getattr(obj, attr))
            for attr, value in inspect.getmembers(obj)
            if attr not in UNSERIALIZABLE_DUNDER
            and type(value) not in UNSERIALIZABLE_TYPES
        }

        data["__bases__"] = [
            cls.convert(base) for base in obj.__bases__ if base != object
        ]

        data["__name__"] = obj.__name__

        return cls._create_dict(data, CLASS_TYPE)

    @classmethod
    def _encode_object(cls, obj):
        data = {
            '__class__': cls.convert(obj.__class__),
            'attrs': {
                attr: cls.convert(value)
                for attr, value in inspect.getmembers(obj)
                if not attr.startswith('__')
                and not isinstance(value, FunctionType)
                and not isinstance(value, MethodType)
            }
        }
        return cls._create_dict(data, OBJ_TYPE)


    @classmethod
    def _encode_function(cls, obj):
        func_code = obj.__code__
        func_name = obj.__name__
        func_defaults = obj.__defaults__
        func_dict = obj.__dict__
        func_class = get_fathers_class_for_method(obj)
        func_closure = (
            tuple(cell for cell in obj.__closure__ if cell.cell_contents is not func_class)
            if obj.__closure__ is not None
            else tuple()
        )
        func_globs = {
            key: cls.convert(value)
            for key, value in obj.__globals__.items()
            if key in obj.__code__.co_names
            and value is not func_class
            and key != obj.__code__.co_name
        }

        encoded_func = cls.convert(
            dict(
                code=func_code,
                name=func_name,
                argdefs=func_defaults,
                closure=func_closure,
                func_dict=func_dict,
                globals=func_globs,
            )
        )
        return cls._create_dict(encoded_func, FUNCTION_TYPE, is_method=isinstance(obj, MethodType))

    @classmethod
    def _encode_collection(cls, obj):
        data = [cls.convert(item) for item in obj]
        return cls._create_dict(data, type(obj).__name__.lower())

    @classmethod
    def _encode_bytes(cls, obj: bytes):
        data = base64.b64encode(obj).decode("ascii")
        return cls._create_dict(data, BYTES_TYPE)

    @classmethod
    def _encode_module(cls, obj):
        return cls._create_dict(obj.__name__, MODULE_TYPE)

    @staticmethod
    def is_iterable(obj):
        return hasattr(obj, '__iter__') \
            and hasattr(obj, '__next__') \
            and callable(obj.__iter__)

    @staticmethod
    def _get_type(obj):
        if isinstance(obj, dict):
            return obj.get('__type')

    @staticmethod
    def _make_cell(value):
        return (lambda: value).__closure__[0]

    @staticmethod
    def _get_data(obj):
        if isinstance(obj, dict):
            return obj.get('data')

    @staticmethod
    def _create_dict(data, _type, **additional):
        return dict(__type=_type, data=data, **additional)
