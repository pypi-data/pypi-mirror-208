import inspect
import types
from source.constants import PRIMITIVES, IGNORE_TYPES, IGNORE_CODE, IGNORE_DUNDER_METHODS


class Serializer:
    class_object = None

    def is_iter(self, obj):
        return hasattr(obj, '__iter__') and hasattr(obj, '__next__')

    def is_func(self, obj):
        return isinstance(obj, types.MethodType) or isinstance(obj, types.FunctionType)

    def extract_class(self, obj):
        cls = getattr(inspect.getmodule(obj), obj.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0], None)
        if isinstance(cls, type):
            return cls

    def make_cell_skeleton(self, value):
        x = value
        def closure():
            return x
        return closure.__closure__[0]

    def serialize(self, obj):
        if isinstance(obj, PRIMITIVES):
            return obj
        elif isinstance(obj, bytes):
            return self.serialize_bytes(obj)
        elif isinstance(obj, (list, tuple, set, dict)):
            return self.serialize_collection(obj)
        elif self.is_iter(obj):
            return self.serialize_iterator(obj)
        elif self.is_func(obj):
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
            raise Exception('Unprocessed type')

    def serialize_bytes(self, obj):
        return {
            '__type__': 'bytes',
            '__packer_storage__': obj.hex()
        }

    def serialize_collection(self, obj):
        if isinstance(obj, dict):
            return {key: self.serialize(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.serialize(item) for item in obj]
        else:
            return {
                '__type__': type(obj).__name__,
                '__packer_storage__': [self.serialize(item) for item in obj]
            }

    def serialize_iterator(self, obj):
        return {
            '__type__': 'iterator',
            '__packer_storage__': [self.serialize(item) for item in obj]
        }

    def serialize_function(self, obj):
        cls = self.extract_class(obj)

        globs = {}
        for key, value in obj.__globals__.items():
            if key in obj.__code__.co_names and key != obj.__code__.co_name and value is not cls:
                globs[key] = self.serialize(value)

        closure = tuple()
        if obj.__closure__ is not None:
            closure = tuple(cell for cell in obj.__closure__ if cell.cell_contents is not cls)

        return {
            '__type__': 'function',
            '__packer_storage__': self.serialize(
                dict(
                    code=obj.__code__,
                    globals=globs,
                    name=obj.__name__,
                    argdefs=obj.__defaults__,
                    closure=closure,
                    dictionary=obj.__dict__
                )
            ),
            '__method__': inspect.ismethod(obj)
        }

    def serialize_code(self, obj):
        primary_code = [code for code in dir(obj) if code.startswith('co_')]
        return {
            '__type__': 'code',
            '__packer_storage__': {code: self.serialize(getattr(obj, code)) for code in primary_code if
                                   code not in IGNORE_CODE}
        }

    def serialize_cell(self, obj):
        return {
            '__type__': 'cell',
            '__packer_storage__': self.serialize(obj.cell_contents)
        }

    def serialize_module(self, obj):
        return {'__type__': 'module', '__packer_storage__': obj.__name__}

    def serialize_class(self, obj):
        stored = {'__name__': obj.__name__}
        stored['__bases__'] = [self.serialize(base) for base in obj.__bases__ if base != object]

        for key, value in inspect.getmembers(obj):
            if key not in IGNORE_DUNDER_METHODS and type(value) not in IGNORE_TYPES:
                stored[key] = self.serialize(value)

        return {
            '__type__': 'class',
            '__packer_storage__': stored
        }

    def serialize_object(self, obj):
        stored = {'__class__': self.serialize(obj.__class__), 'attrs': {}}

        for attr, value in inspect.getmembers(obj):
            if not attr.startswith('__') and not self.is_func(value):
                stored['attrs'][attr] = self.serialize(value)
        return {
            '__type__': 'object',
            '__packer_storage__': stored
        }

    def deserialize(self, obj):
        if isinstance(obj, PRIMITIVES):
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
                        return tuple(self.deserialize(item) for item in obj['__packer_storage__'])
                    case 'set':
                        return set(self.deserialize(item) for item in obj['__packer_storage__'])
            else:
                return {key: self.deserialize(value) for key, value in obj.items()}
        else:
            return obj

    def deserialize_bytes(self, obj):
        return bytes.fromhex(obj['__packer_storage__'])

    def deserialize_iterator(self, obj):
        return iter(self.deserialize(item) for item in obj['__packer_storage__'])

    def deserialize_function(self, obj):
        deserialized = self.deserialize(obj['__packer_storage__'])
        dictionary = deserialized.pop('dictionary')
        skeleton_func = types.FunctionType(**deserialized)

        if obj['__method__'] and self.class_object != None:
            skeleton_func = types.MethodType(skeleton_func, self.class_object)

        skeleton_func.__dict__.update(dictionary)
        skeleton_func.__globals__.update({skeleton_func.__name__: skeleton_func})
        return skeleton_func

    def deserialize_code(self, obj):
        temp = lambda x: x
        return temp.__code__.replace(**(self.deserialize(obj['__packer_storage__'])))


    def deserialize_cell(self, obj):
        return self.make_cell_skeleton(self.deserialize(obj['__packer_storage__']))

    def deserialize_module(self, obj):
        return __import__(obj['__packer_storage__'])

    def deserialize_class(self, obj):
        stored = obj['__packer_storage__']
        bases = tuple(self.deserialize(base) for base in stored.pop('__bases__'))

        innards = {}
        for key, value in stored.items():
            if not self.is_func(value) and not isinstance(value, dict):
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

    def deserialize_object(self, obj):
        stored = obj['__packer_storage__']
        related_class = self.deserialize(stored['__class__'])
        new_obj = object.__new__(related_class)
        self.class_object = new_obj
        new_obj.__dict__ = {key: self.deserialize(value) for key, value in stored['attrs'].items()}
        self.class_object = None
        return new_obj