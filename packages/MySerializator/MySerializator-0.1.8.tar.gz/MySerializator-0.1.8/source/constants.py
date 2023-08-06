import types

PRIMITIVES = (int, float, str, bool, types.NoneType)

IGNORE_CODE = (
    "co_lines"
    "co_lnotab"
    "co_positions"
    "co_exceptiontable"
    "co_firstlineno"
)


IGNORE_TYPES = (
    types.WrapperDescriptorType,
    types.MethodDescriptorType,
    types.BuiltinFunctionType,
    types.MappingProxyType,
    types.GetSetDescriptorType,
)


IGNORE_DUNDER_METHODS = (
    "__weakrefoffset__",
    "__objclass__",
    "__mro__",
    "__doc__",
    "__base__",
    "__basicsize__",
    "__qualname__",
    "__text_signature__",
    "__itemsize__",
    "__flags__",
    "__class__",
    "__dictoffset__",
    "__name__",
)



