import types
from Core.constants import TYPES, PACKER_STORAGE


class Deserialize:
    processed_class_obj = None

    def deserialize(self, obj):
        if isinstance(obj, TYPES):
            return obj
        elif isinstance(obj, list):
            return [self.deserialize(item) for item in obj]
        elif isinstance(obj, dict):
            if '__type__' in obj.keys():
                match obj['__type__']:
                    case 'bytes':
                        return self.deserialize_bytes(obj)
                    case 'iterator':
                        return self.deserialize_iterator(obj)
                    case 'function':
                        return self.deserialize_function(obj)
                    case 'code':
                        return self.deserialize_code(obj)
                    case 'cell':
                        return self.deserialize_cell(obj)
                    case 'module':
                        return self.deserialize_module(obj)
                    case 'class':
                        return self.deserialize_class(obj)
                    case 'object':
                        return self.deserialize_object(obj)
                    case 'tuple':
                        return tuple(self.deserialize(item) for item in obj[PACKER_STORAGE])
                    case 'set':
                        return set(self.deserialize(item) for item in obj[PACKER_STORAGE])
            else:
                return {key: self.deserialize(value) for key, value in obj.items()}
        else:
            return obj

    def deserialize_bytes(self, obj):
        return bytes.fromhex(obj[PACKER_STORAGE])

    def deserialize_iterator(self, obj):
        return iter(self.deserialize(item) for item in obj[PACKER_STORAGE])

    def deserialize_code(self, obj):
        temp = lambda x: x
        return temp.__code__.replace(**(self.deserialize(obj[PACKER_STORAGE])))

    def deserialize_cell(self, obj):
        return self.__make_cell_skeleton(self.deserialize(obj[PACKER_STORAGE]))

    def deserialize_module(self, obj):
        return __import__(obj[PACKER_STORAGE])

    def __is_func(self, obj):
        return isinstance(obj, types.MethodType) or isinstance(obj, types.FunctionType)

    def __make_cell_skeleton(self, value):
        x = value

        def closure():
            return x

        return closure.__closure__[0]

    def deserialize_function(self, obj):
        unpacked = self.deserialize(obj[PACKER_STORAGE])
        dictionary = unpacked.pop('dictionary')
        skeleton_func = types.FunctionType(**unpacked)

        if obj['__method__'] and self.processed_class_obj != None:
            skeleton_func = types.MethodType(skeleton_func, self.processed_class_obj)

        skeleton_func.__dict__.update(dictionary)
        skeleton_func.__globals__.update({skeleton_func.__name__: skeleton_func})
        return skeleton_func

    def deserialize_object(self, obj):
        stored = obj[PACKER_STORAGE]
        related_class = self.deserialize(stored['__class__'])
        new_obj = object.__new__(related_class)
        self.processed_class_obj = new_obj
        new_obj.__dict__ = {key: self.deserialize(value) for key, value in stored['attrs'].items()}
        self.processed_class_obj = None
        return new_obj

    def deserialize_class(self, obj):
        stored = obj[PACKER_STORAGE]
        bases = tuple(self.deserialize(base) for base in stored.pop('__bases__'))

        innards = {}
        for key, value in stored.items():
            if not self.__is_func(value) and not isinstance(value, dict):
                innards[key] = self.deserialize(value)

        new_class = type(stored['__name__'], bases, innards)

        for key, value in stored.items():
            if isinstance(value, dict) and '__type__' in value.keys() and value['__type__'] == 'function':
                func = self.deserialize(value)
                func.__globals__.update({new_class.__name__: new_class})

                if value['__method__']:
                    func = types.MethodType(func, new_class)

                setattr(new_class, key, func)

        return new_class
