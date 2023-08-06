import ctypes
import types
import sys

from Serializer.constants import *


def deserialize(string, index=0):
    if string[index:index+4] == NONE:
        index += 4
        return None, index
    elif string[index:index+4] == TRUE:
        index += 4
        return True, index
    elif string[index:index+5] == FALSE:
        index += 5
        return False, index
    elif string[index].isdigit() or string[index] == MINUS:
        result, index = deserialize_number(string, index)
        return result, index
    elif string[index] == QUOTATION_MARK:
        result, index = deserialize_string(string, index + 1)
        return result, index
    elif string[index] == '[':
        result, index = deserialize_list(string, index)
        return result, index
    elif string[index] == '{':
        result, index = deserialize_dict(string, index)
        return result, index
    else:
        raise TypeError


def deserialize_string(string, index):
    end = index
    while string[end] != QUOTATION_MARK:
        end += 1
    return string[index:end], end + 1


def deserialize_number(string, index):
    end = index
    while end != len(string) and (string[end].isdigit() or string[end] == '.' or string[end] == MINUS):
        end += 1
    try:
        result = int(string[index:end])
    except ValueError:
        try:
            result = float(string[index:end])
        except ValueError:
            raise ValueError
    return result, end


def deserialize_list(string, index):
    result = []
    index += 1
    while string[index] != ']':
        if string[index] in EXTRA_CHARACTERS_LIST:
            index += 1
        else:
            obj, index = deserialize(string, index)
            result.append(obj)
    return tuple(result), index + 1


def deserialize_dict(string, index):
    result = {}
    key = True
    now_key = None
    index += 1
    while string[index] != '}':
        if string[index] in EXTRA_CHARACTERS_DICT:
            index += 1
        elif string[index] == QUOTATION_MARK and key:
            now_key, index = deserialize_key(string, index)
            result[now_key] = None
            key = False
        else:
            now_value, index = deserialize(string, index)
            result[now_key] = now_value
            key = True
    if 'function_type' in result:
        result = deserialize_func(result)
    elif 'staticmethod_type' in result:
        result = staticmethod(result['staticmethod_type'])
    elif 'classmethod_type' in result:
        result = classmethod(result['classmethod_type'])
    elif 'property_type' in result:
        result = property(result['property_type'])
    elif 'class_type' in result:
        result = deserialize_class(result)
    elif 'type_code' in result:
        result = deserialize_code(result)
    elif 'iter_type' in result:
        result = deserialize_iter(result)
    elif 'builtin_type' in result:
        result = deserialize_builtin(result)
    elif 'module_type' in result:
        result = deserialize_module(result)
    elif 'instance_type' in result:
        result = deserialize_instance(result)
    return result, index + 1


def deserialize_key(string, index):
    end = index + 1
    while string[end] != ':':
        end += 1
    key = deserialize(string[index + 1:end - 1], 0)
    return key[0], end


def _create_cell(value):
    pycell_new = ctypes.pythonapi.PyCell_New
    pycell_new.argtypes = (ctypes.py_object,)
    pycell_new.restype = ctypes.py_object
    return pycell_new(value)


def _create_closure(values):
    return tuple(_create_cell(val) for val in values)


def get_code(obj):
    result = (obj['co_argcount'],
              obj['co_posonlyargcount'],
              obj['co_kwonlyargcount'],
              obj['co_nlocals'],
              obj['co_stacksize'],
              obj['co_flags'],
              bytes(obj['co_code']),
              tuple(obj['co_consts']),
              tuple(obj['co_names']),
              tuple(obj['co_varnames']),
              obj['co_filename'],
              obj['co_name'],
              obj['co_firstlineno'],
              bytes(obj['co_lnotab']),
              tuple(obj['co_freevars']),
              tuple(obj['co_cellvars']))
    return result


def deserialize_func(obj):
    temp_closure = None
    if obj['function_type']['__closure__'] is not None:
        temp_closure = _create_closure(obj['function_type']['__closure__'])
    temp_code = get_code(obj['function_type']['__code__']['code_type'])
    result = types.FunctionType(types.CodeType(*temp_code), obj['function_type']['__globals__'],
                                obj['function_type']['__name__'], obj['function_type']['__defaults__'],
                                temp_closure)
    for key in obj['function_type']['__globals__']:
        try:
            result.__globals__[key] = __import__(obj['function_type']['__globals__'][key])
        except:
            pass
    result.__globals__.update({result.__name__: result})
    result.__globals__["__builtins__"] = __import__("builtins")
    return result


def deserialize_class(obj):
    if obj['class_type']['__name__'] == 'object':
        return object
    else:
        result = type(obj['class_type']['__name__'], tuple(obj['class_type']['__bases__']),
                      obj['class_type']['__code__'])
        return result


def deserialize_code(obj):
    return types.CodeType(*get_code(obj['type_code']))


def deserialize_iter(obj):
    return iter(obj['iter_type']['elements'])


def deserialize_builtin(obj):
    module = sys.modules[obj['builtin_type']['__self__']]
    func = getattr(module, obj['builtin_type']['__name__'])
    return func


def deserialize_module(obj):
    module = sys.modules[obj['module_type']['__name__']]
    return module


def deserialize_instance(obj):
    def __init__(self):
        pass

    cls = obj['instance_type']['class']
    temp = cls.__init__
    cls.__init__ = __init__
    result = obj['instance_type']['class']()
    result.__dict__ = obj['instance_type']['dict']
    result.__init__ = temp
    result.__class__.__init__ = temp
    return result
