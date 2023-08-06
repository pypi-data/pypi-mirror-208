import inspect
import types

from .utils import (
    PRIMITIVES,
    TYPE,
    UNSERIALIZABLE_CODE_TYPES,
    UNSERIALIZABLE_DUNDER,
    UNSERIALIZABLE_TYPES,
    PropertyType,
    get_class_by_method,
    is_iterable,
)


class PreSerializer:
    """
    This tool is aimed at fetching data from
    built-in and custom python objects for
    further serializing them by serializers.
    """

    def _wrap_in_dict(self, data, _type: TYPE, **additional_props):
        return dict(__type=_type, data=data, **additional_props)

    def _get_type(self, encoded):
        if isinstance(encoded, dict):
            return encoded.get("__type")

    def _get_data(self, encoded):
        if isinstance(encoded, dict):
            return encoded.get("data")

    def _get_properties(self, encoded):
        if isinstance(encoded, dict):
            return encoded.get("properties")

    def _create_cell_object(self, value):
        return (lambda: value).__closure__[0]

    def encode(self, obj):
        if isinstance(obj, PRIMITIVES):  # default data structures
            return obj
        if isinstance(obj, bytes):
            return self._encode_bytes(obj)

        if isinstance(obj, list):  # collection
            return type(obj)((self.encode(item) for item in obj))

        if isinstance(obj, (tuple, set)):
            return self._encode_collection(obj)

        if isinstance(obj, dict):
            return {key: self.encode(value) for key, value in obj.items()}

        if isinstance(obj, types.CellType):
            return self._encode_cell(obj)

        if isinstance(obj, PropertyType):
            return self._encode_property(obj)

        if isinstance(obj, (types.FunctionType, types.MethodType)):  # functions
            return self._encode_function(obj)

        if isinstance(obj, type):  # class
            return self._encode_class(obj)

        if isinstance(obj, types.CodeType):  # code object
            return self._encode_code(obj)

        if isinstance(obj, types.GeneratorType):
            return self._encode_generator(obj)

        if isinstance(obj, map):
            return self._encode_map(obj)

        if isinstance(obj, filter):
            return self._encode_filter(obj)

        if is_iterable(obj):  # no analog in inspect
            return self._encode_iterator(obj)

        if isinstance(obj, types.ModuleType):
            return self._encode_module(obj)

        if isinstance(obj, object):  # instances
            return self._encode_object(obj)

    def decode(self, obj) -> any:
        if isinstance(obj, PRIMITIVES):
            return obj

        if isinstance(obj, list):
            return type(obj)((self.decode(item) for item in obj))

        if isinstance(obj, dict):
            type_to_decode = self._get_type(obj)

            if type_to_decode is None:
                return {key: self.decode(value) for key, value in obj.items()}

            if type_to_decode == TYPE.BYTES:
                return self._decode_bytes(obj)

            if type_to_decode == TYPE.PROPERTY:
                return self._decode_property(obj)

            if type_to_decode == TYPE.FUNCTION:
                return self._decode_function(obj)

            if type_to_decode == TYPE.CELL:
                return self._decode_cell(obj)

            if type_to_decode == TYPE.CLASS:
                return self._decode_class(obj)

            if type_to_decode == TYPE.GENERATOR:
                return self._decode_generator(obj)

            if type_to_decode == TYPE.FILTER:
                return self._decode_filter(obj)

            if type_to_decode == TYPE.MAP:
                return self._decode_map(obj)

            if type_to_decode == TYPE.FILTER:
                return self._decode_filter(obj)

            if type_to_decode == TYPE.ITERATOR:
                return self._decode_iterator(obj)

            if type_to_decode == TYPE.CODE:
                return self._decode_code(obj)

            if type_to_decode == TYPE.OBJECT:
                return self._decode_object(obj)

            if type_to_decode == TYPE.MODULE:
                return self._decode_module(obj)

            if type_to_decode in (TYPE.TUPLE, TYPE.SET):
                return self._decode_collection(obj)

        return obj

    def _encode_generator(self, obj):
        data = list(map(self.encode, obj))
        return self._wrap_in_dict(
            data=data,
            _type=TYPE.GENERATOR,
        )

    def _decode_generator(self, obj):
        data = self._get_data(obj)
        print(data)
        return iter(self.decode(value) for value in data)

    def _encode_bytes(self, bytes_obj: bytes):
        data = bytes_obj.hex()
        return self._wrap_in_dict(data, TYPE.BYTES)

    def _decode_bytes(self, encoded: str):
        return bytes.fromhex(self._get_data(encoded))

    def _encode_module(self, obj):
        return self._wrap_in_dict(obj.__name__, TYPE.MODULE)

    def _decode_module(self, encoded):
        return __import__(self._get_data(encoded))

    def _encode_collection(self, obj):
        data = [self.encode(item) for item in obj]
        return self._wrap_in_dict(data, type(obj).__name__.lower())

    def _decode_collection(self, obj):
        data = self._get_data(obj)

        collection = tuple if self._get_type(obj) == "tuple" else set
        return collection(map(self.decode, data))

    def _encode_code(self, code):
        attrs = [attr for attr in dir(code) if attr.startswith("co")]
        code_dict = {attr: self.encode(getattr(code, attr)) for attr in attrs if attr not in UNSERIALIZABLE_CODE_TYPES}
        return self._wrap_in_dict(data=code_dict, _type=TYPE.CODE)

    def _decode_code(self, obj):
        data = self._get_data(obj)
        # creating temp func for further replacing
        temp_func = lambda b: b

        code_dict = self.decode(data)
        return temp_func.__code__.replace(**code_dict)  # returns updated co

    def _encode_function(self, func):
        func_code = func.__code__
        func_name = func.__name__
        func_defaults = func.__defaults__
        func_dict = func.__dict__
        func_class = get_class_by_method(func)
        func_closure = (
            tuple(cell for cell in func.__closure__ if cell.cell_contents is not func_class)
            if func.__closure__ is not None
            else tuple()
        )

        func_globs = {
            key: self.encode(value)
            for (key, value) in func.__globals__.items()
            if (key in func.__code__.co_names and value is not func_class and key != func.__code__.co_name)
        }

        encoded_function = self.encode(
            dict(
                code=func_code,
                name=func_name,
                argdefs=func_defaults,
                closure=func_closure,
                fdict=func_dict,
                globals=func_globs,
            )
        )

        return self._wrap_in_dict(
            data=encoded_function,
            _type=TYPE.FUNCTION,
            is_method=isinstance(func, types.MethodType),
        )

    def _decode_function(self, encoded):
        encoded_function = self.decode(self._get_data(encoded))

        func_dict = encoded_function.pop("fdict")

        new_func = types.FunctionType(**encoded_function)
        new_func.__dict__.update(func_dict)
        new_func.__globals__.update({new_func.__name__: new_func})
        return new_func

    def _encode_cell(self, obj):
        data = self.encode(obj=obj.cell_contents)  # raw values
        return self._wrap_in_dict(
            data=data,
            _type=TYPE.CELL,
        )

    def _encode_property(self, obj: PropertyType):
        data = {
            "fget": self.encode(obj.fget),
            "fset": self.encode(obj.fset),
            "fdel": self.encode(obj.fdel),
            "fdoc": self.encode(obj.__doc__),
        }

        return self._wrap_in_dict(data=data, _type=TYPE.PROPERTY)

    def _decode_property(self, obj):
        data = self._get_data(obj)

        fget = self.decode(data["fget"])
        fset = self.decode(data["fset"])
        fdel = self.decode(data["fdel"])
        fdoc = self.decode(data["fdoc"])

        return property(
            fget=fget,
            fset=fset,
            fdel=fdel,
            doc=fdoc,
        )

    def _decode_cell(self, obj):
        return self._create_cell_object(value=self.decode(self._get_data(obj)))

    def _encode_class(self, obj):
        data = {
            attr: self.encode(getattr(obj, attr))
            for attr, value in inspect.getmembers(obj)
            if (attr not in UNSERIALIZABLE_DUNDER and type(value) not in UNSERIALIZABLE_TYPES)
        }

        data["__bases__"] = [self.encode(base) for base in obj.__bases__ if base != object]

        data["__name__"] = obj.__name__

        # properties encoding
        properties: list[dict] = []
        for key in obj.__dict__:
            if isinstance(obj.__dict__[key], PropertyType):
                properties.append(self._encode_property(obj.__dict__[key]))

        return self._wrap_in_dict(
            data=data,
            _type=TYPE.CLASS,
            properties=properties,
        )

    def _decode_class(self, obj):
        data = self._get_data(obj)

        class_bases = tuple(self.decode(base) for base in data.pop("__bases__"))
        class_dict = {
            attr: self.decode(value)
            for (attr, value) in data.items()
            if not (isinstance(value, dict) and self._get_type(value) == TYPE.FUNCTION)
        }

        result = type(data["__name__"], class_bases, class_dict)

        for key, value in data.items():
            if isinstance(value, dict) and self._get_type(value) == TYPE.FUNCTION:
                try:
                    func = self.decode(value)
                except ValueError:
                    closure = self._get_data(value)["closure"]
                    self._get_data(closure).append(self._create_cell_object(result))
                    func = self.decode(value)

                func.__globals__.update({result.__name__: result})

                if value.get("is_method"):
                    func = types.MethodType(func, result)

                setattr(result, key, func)

        # decoding properties
        properties = self._get_properties(obj)
        for dct in properties:
            prop = self._decode_property(dct)
            setattr(result, prop.fget.__name__, prop)

        return result

    def _encode_iterator(self, obj):
        data = list(map(self.encode, obj))
        return self._wrap_in_dict(
            data=data,
            _type=TYPE.ITERATOR,
        )

    def _decode_iterator(self, obj):
        data = self._get_data(obj)
        return iter(list(self.decode(value) for value in data))

    def _encode_object(self, obj):
        data = {
            "__class__": self.encode(obj.__class__),
            "attrs": {
                attr: self.encode(value)
                for (attr, value) in inspect.getmembers(obj)
                if (
                    not attr.startswith("__")
                    and not isinstance(value, types.FunctionType)
                    and not isinstance(value, types.MethodType)
                )
            },
        }

        return self._wrap_in_dict(
            data=data,
            _type=TYPE.OBJECT,
        )

    def _decode_object(self, obj):
        data = self._get_data(obj)
        obj_class = self.decode(data["__class__"])

        result = object.__new__(obj_class)
        result.__dict__ = {key: self.decode(value) for key, value in data["attrs"].items()}

        return result

    def _encode_map(self, obj):
        data = list(map(self.encode, obj))
        return self._wrap_in_dict(
            data=data,
            _type=TYPE.MAP,
        )

    def _decode_map(self, obj):
        data = self._get_data(obj)
        return map(lambda x: x, list(self.decode(value) for value in data))

    def _encode_filter(self, obj):
        data = list(map(self.encode, obj))
        return self._wrap_in_dict(
            data=data,
            _type=TYPE.FILTER,
        )

    def _decode_filter(self, obj):
        data = self._get_data(obj)
        return filter(lambda x: x, list(self.decode(value) for value in data))