import types

BASE_TYPE = (
    int,
    float,
    str,
    bool,
    types.NoneType
)

UNSERIALIZED_ATTRIBUTES = [
    "__mro__", "__base__", "__basicsize__",
    "__class__", "__dictoffset__", "__name__",
    "__qualname__", "__text_signature__", "__itemsize__",
    "__flags__", "__weakrefoffset__", "__objclass__", "__doc__"
]

UNSERIALIZED_TYPES = [
    types.WrapperDescriptorType, types.MethodDescriptorType,
    types.BuiltinFunctionType, types.MappingProxyType,
    types.GetSetDescriptorType
]
