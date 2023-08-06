import inspect
import re
import types


from ser_Stovba.constants import BASE_TYPES, SIMILAR_COLLECTIONS, CODE_PROPERTIES, BASE_COLLECTIONS, CLASS_PROPERTIES, TYPESES, \
    METHODS


def serialize(obj):
    if isinstance(obj, tuple(BASE_TYPES.values())):
        return serialize_single_var(obj)
    elif isinstance(obj, types.NoneType):
        return serialize_none_type()
    elif isinstance(obj, tuple(SIMILAR_COLLECTIONS.values())):
        return serialize_collections(obj)
    elif isinstance(obj, dict):
        return serialize_dict(obj)
    elif inspect.isfunction(obj):
        return serialize_function(obj)
    elif inspect.iscode(obj):
        return serialize_code(obj)
    elif isinstance(obj, types.CellType):
        return serialize_cell(obj)
    elif inspect.isclass(obj):
        return serialize_class(obj)
    else:
        return serialize_object(obj)


def get_obj_type(obj):
    obj_type = str(type(obj))
    return obj_type[8:-2]


def serialize_single_var(obj):
    data = {"type": get_obj_type(obj), "value": obj}
    return data


def serialize_collections(obj):
    data = {"type": get_obj_type(obj), "value": list(map(serialize,obj))}
    return data


def serialize_none_type():
    data = {"type": "NoneType", "value": "none"}
    return data


def serialize_dict(obj):
    data = {"type": get_obj_type(obj), "value": [[serialize(key), serialize(value)] for (key, value) in obj.items()]}
    return data


def serialize_function(obj):
    data = {"type": "function", "value": get_function_values(obj)}
    return data


def get_function_values(obj, cls=None):
    value = dict()

    value["__name__"] = obj.__name__
    value["__globals__"] = get_globals(obj, cls)

    value["__closure__"] = serialize(obj.__closure__)

    arguments = {key: serialize(value) for key, value in inspect.getmembers(obj.__code__)
                 if key in CODE_PROPERTIES}

    value["__code__"] = arguments

    return value


def get_globals(obj, cls=None):
    globs = dict()

    for global_variable in obj.__code__.co_names:

        if global_variable in obj.__globals__:

            if isinstance(obj.__globals__[global_variable], types.ModuleType):
                globs[" ".join(["module", global_variable])] = serialize(
                    obj.__globals__[global_variable].__name__)

            elif inspect.isclass(obj.__globals__[global_variable]):

                if cls and obj.__globals__[global_variable] != cls or not cls:
                    globs[global_variable] = serialize(obj.__globals__[global_variable])

            elif global_variable != obj.__code__.co_name:
                globs[global_variable] = serialize(obj.__globals__[global_variable])

            else:
                globs[global_variable] = serialize(obj.__name__)

    return globs


def serialize_code(obj):
    value = {key: serialize(value) for key, value in inspect.getmembers(obj)
                    if key in CODE_PROPERTIES}
    data = {"type": "code", "value": value}
    return data


def serialize_cell(obj):
    data = {"type": "cell", "value": serialize(obj.cell_contents)}
    return data


def serialize_class(obj):
    data = {"type": "class", "value": get_class_values(obj)}
    return data


def get_class_values(obj):
    data = dict()
    data["__name__"] = serialize(obj.__name__)

    for key, value in obj.__dict__.items():

        if key in CLASS_PROPERTIES or type(value) in TYPESES:
            continue

        if isinstance(obj.__dict__[key], staticmethod):
            data[key] = dict()
            data[key]["type"] = "staticmethod"
            data[key]["value"] = {"type": "function", "value": get_function_values(value.__func__, obj)}

        elif isinstance(obj.__dict__[key], classmethod):
            data[key] = dict()
            data[key]["type"] = "classmethod"
            data[key]["value"] = {"type": "function", "value": get_function_values(value.__func__, obj)}

        elif inspect.ismethod(value):
            data[key] = get_function_values(value.__func__, obj)



        elif inspect.isfunction(value):
            data[key] = dict()
            data[key]["type"] = "function"
            data[key]["value"] = get_function_values(value, obj)

        else:
            data[key] = serialize(value)

    data["__bases__"] = dict()
    data["__bases__"]["type"] = "tuple"
    data["__bases__"]["value"] = [serialize(base) for base in obj.__bases__ if base != object]

    return data


def serialize_property(obj):
    val = dict()

    val["fget"] = serialize(obj.fget)
    val["fset"] = serialize(obj.fset)
    val["fdel"] = serialize(obj.fdel)

    return val


def serialize_object(obj):
    if isinstance(obj, property):
        data = {"type": "property", "value": serialize_property(obj)}
    else:
        data = {"type": "object", "value": get_object_values(obj)}

    return data


def get_object_values(obj):
    value = dict()

    value["__class__"] = serialize(obj.__class__)

    value["__members__"] = {key: serialize(value) for key, value in inspect.getmembers(obj)
                            if not (key.startswith("__") or inspect.isfunction(value) or inspect.ismethod(value))}

    return value


def deserialize(obj):

    if obj["type"] in BASE_TYPES:
        return deserialize_base_type(obj)

    elif obj["type"] in BASE_COLLECTIONS:
        return deserialize_base_collections(obj)

    elif obj["type"] == "code":
        return deserialize_code(obj["value"])

    elif obj["type"] == "function":
        return deserialize_function(obj["value"])

    elif obj["type"] == "cell":
        return deserialize_cell(obj)

    elif obj["type"] == "class":
        return deserialize_class(obj["value"])

    elif obj["type"] in METHODS:
        return METHODS[obj["type"]](deserialize(obj["value"]))

    elif obj["type"] == "object":
        return deserialize_object(obj["value"])


def deserialize_base_type(obj):
    return BASE_TYPES[obj["type"]](obj["value"])


def deserialize_base_collections(obj):
    if obj["type"] == "list":
        return list(map(deserialize, obj["value"]))
    elif obj["type"] == "tuple":
        return tuple(map(deserialize, obj["value"]))
    elif obj["type"] == "set":
        return set(map(deserialize, obj["value"]))
    elif obj["type"] == "frozenset":
        return frozenset(map(deserialize, obj["value"]))
    elif obj["type"] == "bytes":
        return bytes(map(deserialize, obj["value"]))
    elif obj["type"] == "bytearray":
        return bytearray(map(deserialize, obj["value"]))
    elif obj["type"] == "dict":
        data = {deserialize(item[0]): deserialize(item[1]) for item in obj["value"]}
        return data


def deserialize_code(code):
    return types.CodeType(*(deserialize(code[prop]) for prop in CODE_PROPERTIES))


def deserialize_function(func):
    code = func["__code__"]
    globs = func["__globals__"]
    func_closure = func["__closure__"]

    des_globals = deserialize_globals(globs, func)

    cl = deserialize(func_closure)
    if cl:
        closure = tuple(cl)
    else:
        closure = tuple()
    codeType = deserialize_code(code)

    des_globals["__builtins__"] = __import__("builtins")
    des_function = types.FunctionType(code=codeType, globals=des_globals, closure=closure)
    des_function.__globals__.update({des_function.__name__: des_function})

    return des_function


def deserialize_globals(globs, func):
    des_globals = dict()

    for glob in globs:
        if "module" in glob:
            des_globals[globs[glob]["value"]] = __import__(globs[glob]["value"])

        elif globs[glob] != func["__name__"]:
            des_globals[glob] = deserialize(globs[glob])

    return des_globals


def deserialize_cell(obj):
    return types.CellType(deserialize(obj["value"]))


def deserialize_class(obj):
    bases = deserialize(obj["__bases__"])

    members = {member: deserialize(value) for member, value in obj.items()}

    cls = type(deserialize(obj["__name__"]), bases, members)

    for k, member in members.items():
        if inspect.isfunction(member):
            member.__globals__.update({cls.__name__: cls})
        elif isinstance(member, (staticmethod, classmethod)):
            member.__func__.__globals__.update({cls.__name__: cls})

    return cls


def deserialize_object(obj):
    cls = deserialize(obj["__class__"])

    des = object.__new__(cls)
    des.__dict__ = {key: deserialize(value) for key, value in obj["__members__"].items()}

    return des
