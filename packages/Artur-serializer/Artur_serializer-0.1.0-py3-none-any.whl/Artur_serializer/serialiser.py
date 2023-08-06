import inspect
import re
import types


from Artur_serializer.constants import BASE_TYPES, SIMILAR_COLLECTIONS, CODE_PROPERTIES, BASE_COLLECTIONS, CLASS_PROPERTIES, TYPESES, \
    METHODS


def serialize(obj):
    # Serialising of base types
    if isinstance(obj, tuple(BASE_TYPES.values())):
        return serialize_base_types(obj)

    # Serializing none-type
    elif isinstance(obj, types.NoneType):
        return serialize_none_type()

    # Serializing list, tuple, frozenset, set, bytes, bytearray
    elif isinstance(obj, tuple(SIMILAR_COLLECTIONS.values())):
        return serialize_similar_collections(obj)

    # Serializing dict
    elif isinstance(obj, dict):
        return serialize_dict(obj)

    # Serializing functions
    elif inspect.isfunction(obj):
        return serialize_function(obj)

    # Serializing code
    elif inspect.iscode(obj):
        return serialize_code(obj)

    elif isinstance(obj, types.CellType):
        return serialize_cell(obj)

    elif inspect.isclass(obj):
        return serialize_class(obj)

    else:
        return serialize_object(obj)


def get_obj_type(obj):
    return re.search(r"\'(\w+)\'", str(type(obj)))[1]


def serialize_base_types(obj):
    srz = dict()

    srz["type"] = get_obj_type(obj)
    srz["value"] = obj
    return srz


def serialize_similar_collections(obj):
    srz = dict()

    srz["type"] = get_obj_type(obj)
    srz["value"] = [serialize(item) for item in obj]
    return srz


def serialize_none_type():
    srz = dict()

    srz["type"] = "NoneType"
    srz["value"] = "definitely none"
    return srz


def serialize_dict(obj):
    srz = dict()

    srz["type"] = get_obj_type(obj)
    srz["value"] = [[serialize(key), serialize(value)] for (key, value) in obj.items()]
    return srz


def serialize_function(obj):
    srz = dict()
    srz["type"] = "function"

    srz["value"] = full_function_serialize(obj)

    return srz


def full_function_serialize(obj, cls=None):
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
    srz = dict()

    srz["type"] = "code"
    srz["value"] = {key: serialize(value) for key, value in inspect.getmembers(obj)
                    if key in CODE_PROPERTIES}
    return srz


def serialize_cell(obj):
    srz = dict()

    srz["type"] = "cell"
    srz["value"] = serialize(obj.cell_contents)

    return srz


def serialize_class(obj):
    srz = dict()

    srz["type"] = "class"
    srz["value"] = full_class_serialize(obj)

    return srz


def full_class_serialize(obj):
    srz = dict()
    srz["__name__"] = serialize(obj.__name__)

    for key, value in obj.__dict__.items():

        if key in CLASS_PROPERTIES or type(value) in TYPESES:
            continue

        if isinstance(obj.__dict__[key], staticmethod):
            srz[key] = dict()
            srz[key]["type"] = "staticmethod"
            srz[key]["value"] = {"type": "function", "value": full_function_serialize(value.__func__, obj)}

        elif isinstance(obj.__dict__[key], classmethod):
            srz[key] = dict()
            srz[key]["type"] = "classmethod"
            srz[key]["value"] = {"type": "function", "value": full_function_serialize(value.__func__, obj)}

        elif inspect.ismethod(value):
            srz[key] = full_function_serialize(value.__func__, obj)



        elif inspect.isfunction(value):
            srz[key] = dict()
            srz[key]["type"] = "function"
            srz[key]["value"] = full_function_serialize(value, obj)

        else:
            srz[key] = serialize(value)

    srz["__bases__"] = dict()
    srz["__bases__"]["type"] = "tuple"
    srz["__bases__"]["value"] = [serialize(base) for base in obj.__bases__ if base != object]

    return srz


def serialize_property(obj):
    val = dict()

    val["fget"] = serialize(obj.fget)
    val["fset"] = serialize(obj.fset)
    val["fdel"] = serialize(obj.fdel)

    return val



def serialize_object(obj):
    srz = dict()

    if isinstance(obj, property):
        srz["type"] = "property"
        srz["vavlue"] = serialize_property(obj)
    else:
        srz["type"] = "object"
        srz["value"] = full_object_serialization(obj)

    return srz


def full_object_serialization(obj):
    value = dict()

    value["__class__"] = serialize(obj.__class__)

    value["__members__"] = {key: serialize(value) for key, value in inspect.getmembers(obj)
                            if not (key.startswith("__") or inspect.isfunction(value) or inspect.ismethod(value))}

    return value


def deserialize(obj):

    if obj["type"] in extract_keys(str(BASE_TYPES.keys())):
        return deserialize_base_type(obj)

    elif obj["type"] in str(BASE_COLLECTIONS.keys()):
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
    # Getting type of collection
    collection_type = obj["type"]

    if collection_type in SIMILAR_COLLECTIONS.keys():
        # type cast to certain collection from deserialized objects
        return SIMILAR_COLLECTIONS[collection_type](deserialize(item) for item in obj["value"])

    # tbh deserializes dictionary. Probably BASE_COLLECTION could be replaced by dict but fig s nim
    elif collection_type in BASE_COLLECTIONS.keys():
        return BASE_COLLECTIONS[collection_type]({deserialize(item[0]): deserialize(item[1]) for item in obj["value"]})


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
        if (inspect.isfunction(member)):
            member.__globals__.update({cls.__name__: cls})
        elif isinstance(member, (staticmethod, classmethod)):
            member.__func__.__globals__.update({cls.__name__: cls})

    return cls


def deserialize_object(obj):
    cls = deserialize(obj["__class__"])

    des = object.__new__(cls)
    des.__dict__ = {key: deserialize(value) for key, value in obj["__members__"].items()}

    return des

# when i did obj["type"] in str(BASE_TYPES.keys()) it returned true
# when obj["type"] is "dict", cause str(BASE_TYPES.keys()) is dict_keys(['str', 'int', 'bool', 'float', 'complex'])
# this function extracts ['str', 'int', 'bool', 'float', 'complex'] from str(BASE_TYPES.keys())
def extract_keys(string):
    return re.search(r"\[.*\]", string).group()
def MiniMain():
    a = serialize({1: 2, 3: 4, (5, 6, 7): 6})


MiniMain()
