import builtins
import inspect
import types
from types import LambdaType, CodeType, FunctionType, ModuleType

from serializers.constants import PRIMITIVE_TYPES


def get_global(func, cls):
    globs = {}

    for var in func.__code__.co_names:
        if var in func.__globals__:
            if isinstance(func.__globals__[var], ModuleType):
                globs[var] = func.__globals__[var].__name__

            elif inspect.isclass(func.__globals__[var]):
                if cls and func.__globals__[var] != cls:
                    globs[var] = func.__globals__[var]

            elif var != func.__code__.co_name:
                globs[var] = func.__globals__[var]

            else:
                globs[var] = func.__name__

    return globs


def to_string_func(obj, cls=None):
    res = {'__type__': 'function'}

    if inspect.ismethod(obj):
        obj = obj.__func__

    obj.__name__ = obj.__name__.replace('>', '')
    res['__name__'] = obj.__name__.replace('<', '')

    globs = get_global(obj, cls)
    res['__globals__'] = to_string_iter(globs)

    arg = {}

    for key, value in inspect.getmembers(obj.__code__):
        if key.startswith('co_'):
            if key == 'co_lines':
                continue

            if isinstance(value, bytes):
                value = list(value)

            if getattr(value, '__iter__', None) is not None and not isinstance(value, str):
                list_ = []

                for val in value:
                    if val is not None:
                        list_.append(to_string_objects(val))

                    else:
                        list_.append(None)

                arg[key] = list_

                continue

            arg[key] = value

    res['__args__'] = arg

    return res


def to_string_iter(obj):
    if isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
        iter = []

        for value in obj:
            iter.append(to_string_objects(value))

        if isinstance(obj, tuple):
            return tuple(iter)

        if isinstance(obj, set):
            return set(iter)

        return iter

    elif isinstance(obj, dict):
        dict_ = {}

        for key, value in obj.items():
            dict_[key] = to_string_objects(value)

        return dict_


def to_string_class(obj):
    res = {'__type__': 'class', '__name__': obj.__name__}

    for attr in inspect.getmembers(obj):
        if attr[0] not in (
            '__mro__',
            '__base__',
            '__basicsize__',
            '__class__',
            '__dictoffset__',
            '__name__',
            '__qualname__',
            '__text_signature__',
            '__itemsize__',
            '__flags__',
            '__weakrefoffset__',
            '__objclass__',
        ) and type(attr[1]) not in (
                types.WrapperDescriptorType,
                types.MethodDescriptorType,
                types.BuiltinFunctionType,
                types.MappingProxyType,
                types.GetSetDescriptorType
        ):
            attr_value = getattr(obj, attr[0])

            if inspect.isfunction(attr_value) or inspect.ismethod(attr_value) or isinstance(attr_value, LambdaType):
                res[attr[0]] = to_string_func(attr_value, obj)

            else:
                res[attr[0]] = to_string_objects(attr_value)

    res['__bases__'] = [to_string_class(base) for base in obj.__bases__ if base != object]

    return res


def to_string_object(obj):
    res = {'__type__': 'object', '__class__': to_string_class(obj.__class__), 'attr': {}}

    for key, value in inspect.getmembers(obj):
        if not key.startswith('__') and not inspect.isfunction(value) or inspect.ismethod(value) or isinstance(value, LambdaType):
            res['attr'][key] = to_string_objects(value)

    return res


def to_string_objects(obj):
    if isinstance(obj, (int, float, complex, bool, str)):
        return obj

    elif isinstance(obj, (list, tuple, set, dict)):
        return obj

    elif inspect.isfunction(obj) or inspect.ismethod(obj) or isinstance(obj, LambdaType):
        return to_string_func(obj)

    elif inspect.isclass(obj):
        return to_string_class(obj)

    elif inspect.iscode(obj):
        return to_string_func(FunctionType(obj, {}))

    elif getattr(obj, "__iter__", None) is not None:
        return to_string_iter(obj)

    else:
        return to_string_object(obj)


def from_string_objects(obj):

    if obj is None:
        return 'None'
    elif isinstance(obj, (int, float, complex, bool, str)):
        return obj

    elif isinstance(obj, dict):
        if 'function' in obj.values():
            return from_string_func(obj)

        elif 'object' in obj.values():
            return from_string_object(obj)

        elif 'class' in obj.values():
            return from_string_class(obj)

        else:
            return from_string_iter(obj)

    elif getattr(obj, "__iter__", None) is not None:
        return from_string_iter(obj)

    else:
        raise Exception('Unknown type')


def from_string_func(obj):
    arg = obj['__arg__']
    globs = obj['__globals__']

    globs['__builtins__'] = builtins

    for key in obj['__globals__']:
        if key in arg['co_names']:
            try:
                globs[key] = __import__(obj['__globals__'][key])
            except:
                if globs[key] != obj['__name__']:
                    globs[key] = to_string_objects(obj['__globals__'][key])

    code_arg = CodeType(arg['co_argcount'],
                        arg['co_code'],
                        arg['co_cellvars'],
                        arg['co_consts'],
                        arg['co_filename'],
                        arg['co_firstlineno'],
                        arg['co_flags'],
                        arg['co_lnotab'],
                        arg['co_freevars'],
                        arg['co_posonlyargcount'],
                        arg['co_kwonlyargcount'],
                        arg['co_name'],
                        arg['co_qualname'],
                        arg['co_names'],
                        arg['co_nlocals'],
                        arg['co_stacksize'],
                        arg['co_varnames']
                        )

    func_res = FunctionType(code_arg, globs)

    func_res.__globals__.update({func_res.__name__: func_res})

    return func_res


def from_string_iter(obj):
    if isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
        iter = []

        for value in obj:
            iter.append(from_string_objects(value))

        if isinstance(obj, tuple):
            return tuple(iter)

        if isinstance(obj, set):
            return set(iter)

        return iter

    elif isinstance(obj, dict):
        dict_ = {}

        for key, value in obj.items():
            dict_[key] = from_string_objects(value)

        return dict_


def from_string_class(obj):
    bases = tuple(from_string_class(base) for base in obj['__bases__'])
    methods = {}

    for attr, value in obj.items():
        methods[attr] = from_string_objects(value)

    res = type(obj['__name__'], bases, methods)

    for key, value in methods.items():
        if inspect.isfunction(value):
            value.__globals__.update({res.__name__: res})

    return res


def from_string_object(obj):
    cls = from_string_objects(obj['__class__'])
    attr = {}

    for key, value in obj['attr'].items():
        attr[key] = from_string_objects(value)

    res = object.__new__(cls)
    res.__dict__ = attr

    return res

def to_dict(obj):
    if isinstance(obj, type(None)):

        return {
            "None": "None"
        }

    elif isinstance(obj, (int, float, complex, bool, str)):

        return {
            str(type(obj)): obj
        }

    elif isinstance(obj, (list, tuple, set)):
        res = []

        for i in obj:
            res.append(to_dict(i))

        return {
            str(type(obj)): res
        }

    elif isinstance(obj, dict):
        res = {}

        for key, value in obj.items():
            res[key] = to_dict(value)

        return res

    else:
        raise Exception('Unknown type')


def from_dict(obj):
    if type(obj) is dict:
        if len(obj.keys()) == 1:
            key, value = list(obj.items())[0]

            if key == "None":
                return None

            elif isinstance(value, (int, float, complex, bool, str)):
                return value

            elif isinstance(value, list):
                res = []

                for i in value:
                    res.append(from_dict(i))

                if key == "<class 'tuple'>":
                    res = tuple(res)

                elif key == "<class 'set'>":
                    res = set(res)

                return res

        res = {}

        for key, value in obj.items():
            res[key] = from_dict(value)

        return res

    else:
        raise Exception('Object type must be dict')
