import types

COLLECTIONS = (list, tuple, set, dict)
TYPES = (str, int, float, bool, types.NoneType)
PACKER_STORAGE = '__packer_storage__'

CODE = ("co_positions", "co_lines", "co_exceptiontable", "co_lnotab")

TYPES_DOT = (types.WrapperDescriptorType, types.MethodDescriptorType, types.BuiltinMethodType,
                   types.GetSetDescriptorType, types.MappingProxyType)


IGNORE_DUNDER = ("__mro__", "__doc__", "__base__", "__basicsize__", "__class__", "__dictoffset__", "__name__",
                 "__qualname__", "__text_signature__", "__itemsize__", "__flags__", "__weakrefoffset__", "__objclass__",)


CREATOR_JSON = "json"
CREATOR_XML = "xml"
