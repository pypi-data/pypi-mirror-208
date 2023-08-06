import re
import inspect
import types
from DariasSerializer153501.canstants import CODE_ATTRIBUTES,BASIC_COLLECTION,DEFAULT_TYPES

def my_serializer(objet):


    serial = dict()
    obj_type = type(objet)

    def return_basic_type():
        return re.search(r"\'(\w+)\'", str(obj_type))[1]#не берем скобки, берем слово

    if isinstance(objet,(str, int, bool, float, complex)):
        serial["type"] = return_basic_type()
        serial["value"] = objet

    elif (isinstance(objet,(tuple, list, set, frozenset, bytes, bytearray))):
        serial["type"] = return_basic_type()
        serial["value"] = [my_serializer(serialised_objet) for serialised_objet in objet]

    elif isinstance(objet, dict):
        serial["type"] = return_basic_type()
        serial["value"] = [my_serializer([key,val]) for (key,val) in objet.items()]

    elif inspect.isfunction(objet):
        serial["type"] = "function"
        serial["value"] = serialize_function(objet)

    elif inspect.iscode(objet):
        serial["type"] = "code"
        arguments = dict()
        for key,val in inspect.getmembers(objet):
            if key in CODE_ATTRIBUTES : arguments[key]=my_serializer(val)
        serial["value"] = arguments
    elif isinstance(objet, types.CellType):
        serial["type"] = "cell"
        serial["value"] = my_serializer(objet.cell_contents)

    elif inspect.isclass(objet):
        serial["type"] = "class"
        serial["value"] = serialize_class(objet)

    elif not objet:
        serial["type"] = "NoneType"
        serial["value"] = "Null"

    else:
        serial["type"] = "object"
        serial["value"] = serialize_object(objet)

    return serial

def serialize_function(function, clas = None):
    if not inspect.isfunction(function):
        return

    serialize_value_function = dict()

    serialize_value_function["__name__"] = function.__name__
    serialize_value_function["__globals__"] = return_globals(function, clas)
    serialize_value_function["__closure__"] = my_serializer(function.__closure__) if function.__closure__ else my_serializer(tuple())

    arguments = dict()

    for key,val in inspect.getmembers(function.__code__):
        if key in CODE_ATTRIBUTES : arguments[key]=my_serializer(val)

    serialize_value_function["__code__"] = arguments

    return serialize_value_function


def return_globals(function, cls=None):
    globs = dict()

    for glob_variable in function.__code__.co_names:
        if (glob_variable in function.__globals__):
            if (isinstance(function.__globals__[glob_variable], types.ModuleType)):
                globs["module " + glob_variable] = my_serializer(function.__globals__[glob_variable].__name__)

            elif (inspect.isclass(function.__globals__[glob_variable])):
                if (cls and function.__globals__[glob_variable] != cls) or (not cls):
                    globs[glob_variable] = my_serializer(function.__globals__[glob_variable])


            elif (glob_variable != function.__code__.co_name):
                globs[glob_variable] = my_serializer(function.__globals__[glob_variable])

            # на случай рекурсии
            else:
                globs[glob_variable] = my_serializer(function.__name__)

    return globs




def serialize_class(objet):
    serial = dict()

    serial["__name__"] = my_serializer(objet.__name__)

    for mem in objet.__dict__:
        member = [mem, objet.__dict__[mem]]#пара ключ значение

        if (member[0] in ("__name__", "__base__",
                          "__basicsize__", "__dictoffset__", "__class__") or
                type(member[1]) in (
                        types.WrapperDescriptorType,
                        types.MethodDescriptorType,
                        types.BuiltinFunctionType,
                        types.GetSetDescriptorType,
                        types.MappingProxyType
                )):
            continue
        if isinstance(objet.__dict__[member[0]], staticmethod):
            serial[member[0]] = {"type" : "staticmethod",
                              "value" : {"type" : "function",
                                         "value": serialize_function(member[1].__func__, objet)}}
        elif (isinstance(objet.__dict__[member[0]], classmethod)):
            serial[member[0]] = {"type" : "classmethod",
                              "value" : {"type" : "function",
                                         "value": serialize_function(member[1].__func__, objet)}}
        elif (inspect.ismethod(member[1])):
            serial[member[0]] = serialize_function(member[1].__func__, objet)

        elif inspect.isfunction(member[1]):
            serial[member[0]] = {"type" : "function", "value": serialize_function(member[1], objet)}

        else:
            serial[member[0]] = my_serializer(member[1])

    serial["__bases__"] ={"type" : "tuple", "value" :
                            [my_serializer(base) for base in objet.__bases__ if base != object]}
    return serial


def serialize_object(objet):#для чего это пример
    serial = dict()
    serial["__class__"] = my_serializer(objet.__class__)
    members = dict()
    for key, val in inspect.getmembers(objet):
        if key.startswith("__") or inspect.isfunction(val) or inspect.ismethod(val):
            continue
        members[key]=my_serializer(val)

    serial["__members__"]=members
    return serial




def my_deserializer(objet : dict):
    print(objet, type(objet))
    if objet["type"] in DEFAULT_TYPES:
        return return_type(objet["type"], objet["value"])

    elif objet["type"] in BASIC_COLLECTION:
        return return_collection(objet["type"], objet["value"])

    elif objet["type"] =="dict":
        return dict(return_collection("list", objet["value"]))

    elif objet["type"] =="function":
        return deserialize_function(objet["value"])

    elif objet["type"] == "code":
        code = objet["value"]
        return types.CodeType(my_deserializer(code["co_argcount"]),
                              my_deserializer(code["co_posonlyargcount"]),
                              my_deserializer(code["co_kwonlyargcount"]),
                              my_deserializer(code["co_nlocals"]),
                              my_deserializer(code["co_stacksize"]),
                              my_deserializer(code["co_flags"]),
                              my_deserializer(code["co_code"]),
                              my_deserializer(code["co_consts"]),
                              my_deserializer(code["co_names"]),
                              my_deserializer(code["co_varnames"]),
                              my_deserializer(code["co_filename"]),
                              my_deserializer(code["co_name"]),
                              #my_deserializer(code["co_qualname"]),
                              my_deserializer(code["co_firstlineno"]),
                              my_deserializer(code["co_lnotab"]),
                              #my_deserializer(code["co_exeptiontable"]),
                              my_deserializer(code["co_freevars"]),
                              my_deserializer(code["co_cellvars"]))

    elif objet["type"] =="cell":
        return types.CellType(my_deserializer(objet["value"]))

    elif objet["type"] =="class":
        return deserialize_class(objet["value"])

    elif objet["type"] =="staticmethod":
        return staticmethod(my_deserializer(objet["value"]))

    elif objet["type"] =="classmethod":
        return classmethod(my_deserializer(objet["value"]))

    elif objet["type"] =="object":
        return deserialize_object(objet["value"])



def return_type(_type, objet):
    if (_type == "int"):
        return int(objet)
    elif (_type == "float"):
        return float(objet)
    elif (_type == "complex"):
        return complex(objet)
    elif (_type == "str"):
        return str(objet)
    elif (_type == "bool"):
        return bool(objet)

def return_collection(_type, objet):
    if _type == "list":
        return list(my_deserializer(o) for o in objet)
    elif _type == "tuple":
        return tuple(my_deserializer(o) for o in objet)
    elif _type == "set":
        return set(my_deserializer(o) for o in objet)
    elif _type == "frozenset":
        return frozenset(my_deserializer(o) for o in objet)
    elif _type == "bytearray":
        return bytearray(my_deserializer(o) for o in objet)
    elif _type == "bytes":
        return bytes(my_deserializer(o) for o in objet)

def deserialize_function(objet):
    code = objet["__code__"]
    globs = objet["__globals__"]
    closures = objet["__closure__"]
    res_globs = dict()

    for key in objet["__globals__"]:
        if ("module" in key):
            res_globs[globs[key]["value"]] = __import__(globs[key]["value"])

        elif (globs[key] != objet["__name__"]):
            res_globs[key] = my_deserializer(globs[key])

    closure = tuple(my_deserializer(closures))

    codeType = types.CodeType(my_deserializer(code["co_argcount"]),
                              my_deserializer(code["co_posonlyargcount"]),
                              my_deserializer(code["co_kwonlyargcount"]),
                              my_deserializer(code["co_nlocals"]),
                              my_deserializer(code["co_stacksize"]),
                              my_deserializer(code["co_flags"]),
                              my_deserializer(code["co_code"]),
                              my_deserializer(code["co_consts"]),
                              my_deserializer(code["co_names"]),
                              my_deserializer(code["co_varnames"]),
                              my_deserializer(code["co_filename"]),
                              my_deserializer(code["co_name"]),
                              # my_deserializer(code["co_qualname"]),
                              my_deserializer(code["co_firstlineno"]),
                              my_deserializer(code["co_lnotab"]),
                              # my_deserializer(code["co_exeptiontable"]),
                              my_deserializer(code["co_freevars"]),
                              my_deserializer(code["co_cellvars"]))

    funcRes = types.FunctionType(code=codeType, globals=res_globs, closure=closure)
    funcRes.__globals__.update({funcRes.__name__: funcRes})

    return funcRes

def deserialize_class(objet):

    bases = my_deserializer(objet["__bases__"])
    members = dict()

    for member, value in objet.items():
        members[member] = my_deserializer(value)

    clas = type(my_deserializer(objet["__name__"]), bases, members)

    # чтоб не было бесконечной рекурсии метода и класса
    for k, member in members.items():
        if (inspect.isfunction(member)):
            member.__globals__.update({clas.__name__: clas})
        elif isinstance(member, (staticmethod, classmethod)):
            member.__func__.__globals__.update({clas.__name__: clas})
    return clas


def deserialize_object(obj):
    clas = my_deserializer(obj["__class__"])
    members = dict()

    for k, v in obj["__members__"].items():
        members[k] = my_deserializer(v)

    res = object.__new__(clas)
    res.__dict__ = members

    return res








