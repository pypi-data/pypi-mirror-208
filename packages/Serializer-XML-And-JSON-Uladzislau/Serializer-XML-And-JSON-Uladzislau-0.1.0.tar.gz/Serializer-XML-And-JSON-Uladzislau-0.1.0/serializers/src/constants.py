import types

JSON_DATA_TYPE = '.json'

XML_DATA_TYPE = '.xml'

TOML_DATA_TYPE = '.toml'

YAML_DATA_TYPE = '.yaml'

PRIMITIVE_TYPES = (int, str, bool, float, type(None))

UNKNOWN_TYPE_ERROR = 'Unknown type of serialization!'

SAME_TYPE_ERROR = 'Same type of objects!'

UNSUPPORTED_TYPE_ERROR = 'Unsupported data type: %s (%s)'

ITERATOR_TYPE = 'iterator'
BYTES_TYPE = 'bytes'
CODE_TYPE = 'code'
OBJ_TYPE = 'object'
MODULE_TYPE = 'module'
CELL_TYPE = 'cell'
FUNCTION_TYPE = 'function'
CLASS_TYPE = 'type'
SET_TYPE = 'set'
DICT_TYPE = 'dict'
TUPLE_TYPE = 'tuple'


UNSERIALIZABLE_DUNDER = (
    "__mro__",
    "__base__",
    "__basicsize__",
    "__class__",
    "__dictoffset__",
    "__name__",
    "__qualname__",
    "__text_signature__",
    "__itemsize__",
    "__flags__",
    "__weakrefoffset__",
    "__objclass__",
    "__doc__"
)

UNSERIALIZABLE_CODE_TYPES = (
    "co_positions",
    "co_lines",
    "co_exceptiontable",
    "co_lnotab",
)

UNSERIALIZABLE_TYPES = (
    types.WrapperDescriptorType,
    types.MethodDescriptorType,
    types.BuiltinFunctionType,
    types.MappingProxyType,
    types.GetSetDescriptorType,
)
