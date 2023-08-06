import inspect
import types

from Core.constants import CODE, COLLECTIONS, TYPES, IGNORE_DUNDER, TYPES_DOT, PACKER_STORAGE


class Serialize:
    class_object = None

    def __is_iter(self, obj):
        return hasattr(obj, '__iter__') and hasattr(obj, '__next__')

    def __is_func(self, obj):
        return isinstance(obj, types.MethodType) or isinstance(obj, types.FunctionType)

    def __extract_class(self, obj):
        cls = getattr(inspect.getmodule(obj), obj.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0], None)
        if isinstance(cls, type):
            return cls

    def __make_cell_skeleton(self, value):
        x = value

        def closure():
            return x
        return closure.__closure__[0]

    def serialize(self, obj):
        if isinstance(obj, TYPES):
            return obj
        elif isinstance(obj, bytes):
            return self.serialize_bytes(obj)
        elif isinstance(obj, COLLECTIONS):
            return self.serialize_collection(obj)
        elif self.__is_iter(obj):
            return self.serialize_iterator(obj)
        elif self.__is_func(obj):
            return self.serialize_function(obj)
        elif isinstance(obj, types.CodeType):
            return self.serialize_code(obj)
        elif isinstance(obj, types.CellType):
            return self.serialize_cell(obj)
        elif isinstance(obj, types.ModuleType):
            return self.serialize_module(obj)
        elif inspect.isclass(obj):
            return self.serialize_class(obj)
        elif isinstance(obj, object):
            return self.serialize_object(obj)
        else:
            raise Exception("unknown type")

    def serialize_collection(self, obj):
        if isinstance(obj, dict):
            return {key: self.serialize(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.serialize(item) for item in obj]
        else:
            return {
                '__type__': type(obj).__name__,
                PACKER_STORAGE: [self.serialize(item) for item in obj]
            }

    def serialize_function(self, obj):
        cls = self.__extract_class(obj)

        glob = {}
        for key, value in obj.__globals__.items():
            if key in obj.__code__.co_names and key != obj.__code__.co_name and value is not cls:
                glob[key] = self.serialize(value)

        closure = tuple()
        if obj.__closure__ is not None:
            closure = tuple(cell for cell in obj.__closure__ if cell.cell_contents is not cls)

        return {'__type__': 'function', PACKER_STORAGE: self.serialize(dict(
            code=obj.__code__,
            globals=glob,
            name=obj.__name__,
            argdefs=obj.__defaults__,
            closure=closure,
            dictionary=obj.__dict__)), '__method__': inspect.ismethod(obj)}

    def serialize_bytes(self, obj):
        return {'__type__': 'bytes',
                PACKER_STORAGE: obj.hex()}

    def serialize_iterator(self, obj):
        return {'__type__': 'iterator',
                PACKER_STORAGE: [self.serialize(item) for item in obj]}

    def serialize_code(self, obj):
        primary_code = [code for code in dir(obj) if code.startswith('co_')]
        return {'__type__': 'code',
                PACKER_STORAGE: {code: self.serialize(getattr(obj, code)) for code in primary_code
                                       if code not in CODE}}

    def serialize_cell(self, obj):
        return {'__type__': 'cell', PACKER_STORAGE: self.serialize(obj.cell_contents)}

    def serialize_module(self, obj):
        return {'__type__': 'module', PACKER_STORAGE: obj.__name__}

    def serialize_class(self, obj):
        stored = {'__name__': obj.__name__}
        stored['__bases__'] = [self.serialize(base) for base in obj.__bases__ if base != object]

        for key, value in inspect.getmembers(obj):
            if key not in IGNORE_DUNDER and type(value) not in TYPES_DOT:
                stored[key] = self.serialize(value)

        return {'__type__': 'class', PACKER_STORAGE: stored}

    def serialize_object(self, obj):
        stored = {'__class__': self.serialize(obj.__class__), 'attrs': {}}

        for attr, value in inspect.getmembers(obj):
            if not attr.startswith('__') and not self.__is_func(value):
                stored['attrs'][attr] = self.serialize(value)
        return {'__type__': 'object', PACKER_STORAGE: stored}
