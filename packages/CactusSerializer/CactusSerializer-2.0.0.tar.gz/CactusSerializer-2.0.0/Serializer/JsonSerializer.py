import re
import inspect
import types
from Serializer.constants import *


def serialize(obj, indent, new_indent=0):
    if obj is None:
        return NONE
    elif obj is True:
        return TRUE
    elif obj is False:
        return FALSE
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, str):
        result = QUOTATION_MARK + obj + QUOTATION_MARK
        return result
    elif isinstance(obj, dict):
        return serialize_dict(obj, indent, new_indent)
    elif isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set) or isinstance(obj, frozenset):
        return serialize_list(obj, indent, new_indent)
    elif isinstance(obj, types.CodeType):
        return serialize_code(obj, indent, new_indent)
    elif inspect.isclass(obj):
        return serialize_class(obj, indent, new_indent)
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        return serialize_func(obj, indent, new_indent)
    elif isinstance(obj, staticmethod):
        return serialize_staticmethod(obj, indent, new_indent)
    elif isinstance(obj, classmethod):
        return serialize_classmethod(obj, indent, new_indent)
    elif isinstance(obj, property):
        return serialize_property(obj, indent, new_indent)
    elif inspect.isbuiltin(obj):
        return serialize_builtin(obj, indent, new_indent)
    elif isinstance(obj, types.GeneratorType):
        return serialize_iter(obj, indent, new_indent)
    elif inspect.ismodule(obj):
        return serialize_module(obj, indent, new_indent)
    elif hasattr(obj, '__iter__') and hasattr(obj, '__next__'):
        return serialize_iter(obj, indent, new_indent)
    else:
        try:
            return serialize_instance(obj, indent, new_indent)
        except TypeError:
            raise TypeError


def serialize_dict(obj, indent, new_indent):
    if len(obj) == 0:
        return '{}'
    else:
        result = '{\n'
        new_indent += indent
        for key in list(obj)[:len(obj)-1]:
            result += ' ' * new_indent + QUOTATION_MARK + serialize(key, indent, new_indent) + QUOTATION_MARK + ':' + \
                      serialize(obj[key], indent, new_indent) + '\n'
        result += ' ' * new_indent + QUOTATION_MARK + serialize(list(obj)[len(obj)-1], indent, new_indent) + \
                  QUOTATION_MARK + ':' + serialize(obj[list(obj)[len(obj)-1]], indent, new_indent) + '\n'
        result += ' ' * (new_indent - indent) + '}'
    return result


def serialize_list(obj, indent, new_indent):
    if len(obj) == 0:
        return '[]'
    else:
        result = '[\n'
        new_indent += indent
        for item in obj[:len(obj)-1]:
            result += ' ' * new_indent + serialize(item, indent, new_indent) + '\n'
        result += ' ' * new_indent + serialize(obj[len(obj)-1], indent, new_indent) + '\n'
        result += ' ' * (new_indent - indent) + ']'
    return result


def get_globals(obj):
    result = {}
    for key in obj.__globals__:
        if isinstance(obj.__globals__[key], types.ModuleType):
            result[key] = obj.__globals__[key].__name__
        elif key in obj.__code__.co_names and obj.__name__ != key:
            result[key] = obj.__globals__[key]
    return result


def serialize_func(obj, indent, new_indent):
    glob = get_globals(obj)
    closure = None
    if obj.__closure__ is not None:
        temp = list()
        for item in obj.__closure__:
            temp.append(item.cell_contents)
        closure = tuple(temp)
    func_dict = {
        "function_type": {
            "__globals__": glob,
            "__name__": obj.__name__,
            "__defaults__": obj.__defaults__,
            "__closure__": closure,
            "__code__": {
                "code_type": {
                    "co_argcount": obj.__code__.co_argcount,
                    "co_posonlyargcount": obj.__code__.co_posonlyargcount,
                    "co_kwonlyargcount": obj.__code__.co_kwonlyargcount,
                    "co_nlocals": obj.__code__.co_nlocals,
                    "co_stacksize": obj.__code__.co_stacksize,
                    "co_flags": obj.__code__.co_flags,
                    "co_code": list(obj.__code__.co_code),
                    "co_consts": obj.__code__.co_consts,
                    "co_names": obj.__code__.co_names,
                    "co_varnames": obj.__code__.co_varnames,
                    "co_filename": obj.__code__.co_filename,
                    "co_name": obj.__code__.co_name,
                    "co_firstlineno": obj.__code__.co_firstlineno,
                    "co_lnotab": list(obj.__code__.co_lnotab),
                    "co_freevars": obj.__code__.co_freevars,
                    "co_cellvars": obj.__code__.co_cellvars
                }
            }
        }
    }
    result = serialize_dict(func_dict, indent, new_indent)
    return result


def serialize_staticmethod(obj, indent, new_indent):
    staticmethod_dict = {"staticmethod_type": obj.__func__}
    result = serialize_dict(staticmethod_dict, indent, new_indent)
    return result


def serialize_classmethod(obj, indent, new_indent):
    classmethod_dict = {"classmethod_type": obj.__func__}
    result = serialize_dict(classmethod_dict, indent, new_indent)
    return result


def serialize_property(obj, indent, new_indent):
    property_dict = {"property_type": obj.fget}
    result = serialize_dict(property_dict, indent, new_indent)
    return result


def get_code_class(obj):
    if obj.__name__ != 'object':
        temp = dict(obj.__dict__)
        for key in list(temp)[:len(temp)-1]:
            if key in EXTRA_ATTRIBUTE_CLASS_CODE:
                if key in temp:
                    temp.pop(key)
                continue
            if list(temp)[len(temp)-1] in EXTRA_ATTRIBUTE_CLASS_CODE:
                temp.pop(list(temp)[len(temp)-1])
        result = temp
    else:
        result = {}
    return result


def serialize_class(obj, indent, new_indent):
    code = get_code_class(obj)
    class_dict = {
        "class_type": {
            "__name__": obj.__name__,
            "__bases__": obj.__bases__,
            "__code__": code
        }
    }
    result = serialize_dict(class_dict, indent, new_indent)
    return result


def serialize_code(obj, indent, new_indent):
    code_dict = {
        "type_code": {
            "co_argcount": obj.co_argcount,
            "co_posonlyargcount": obj.co_posonlyargcount,
            "co_kwonlyargcount": obj.co_kwonlyargcount,
            "co_nlocals": obj.co_nlocals,
            "co_stacksize": obj.co_stacksize,
            "co_flags": obj.co_flags,
            "co_code": list(obj.co_code),
            "co_consts": obj.co_consts,
            "co_names": obj.co_names,
            "co_varnames": obj.co_varnames,
            "co_filename": obj.co_filename,
            "co_name": obj.co_name,
            "co_firstlineno": obj.co_firstlineno,
            "co_lnotab": list(obj.co_lnotab),
            "co_freevars": obj.co_freevars,
            "co_cellvars": obj.co_cellvars
        }
    }
    result = serialize_dict(code_dict, indent, new_indent)
    return result


def serialize_builtin(obj, indent, new_indent):
    builtin_dict = {
        "builtin_type": {
            "__name__": obj.__name__,
            "__self__": re.search(r"\'(\w+)\'", str(obj.__self__)).group(1)
        }
    }
    result = serialize_dict(builtin_dict, indent, new_indent)
    return result


def serialize_module(obj, indent, new_indent):
    module_dict = {
        "module_type": {
            "__name__": obj.__name__
        }
    }
    result = serialize_dict(module_dict, indent, new_indent)
    return result


def serialize_iter(obj, indent, new_indent):
    iter_dict = {
        "iter_type": {
            "elements": list(obj)
        }
    }
    result = serialize_dict(iter_dict, indent, new_indent)
    return result


def serialize_instance(obj, indent, new_indent):
    data = {
        "instance_type": {
            "class": obj.__class__,
            "dict": obj.__dict__
        }
    }
    result = serialize_dict(data, indent, new_indent)
    return result
