CODE_ATTRIBUTE = (
    'co_argcount',
    'co_code',
    'co_cellvars',
    'co_consts',
    'co_filename',
    'co_firstlineno',
    'co_flags',
    'co_lnotab',
    'co_freevars',
    'co_posonlyargcount',
    'co_kwonlyargcount',
    'co_name',
    'co_qualname',
    'co_names',
    'co_nlocals',
    'co_stacksize',
    'co_varnames'
)

CODE_NAME_ATTRIBUTE = 'co_names'

FUNCTION_ATTRIBUTE = ('__doc__', '__name__', '__code__', '__qualname__', '__defaults__', '__kwdefaults__',
    '__globals__', '__builtins__', '__annotations__', '__module__', '__closure__')

FUNCTION_CREATE_ATTRIBUTE = (
    '__doc__',
    '__name__',
    '__code__',
    '__qualname__',
    '__defaults__',
    '__kwdefaults__',
    '__globals__',
    '__builtins__',
    '__annotations__',
    '__module__',
    '__closure__'
)

CLASS_ATTRIBUTE = (
    '__doc__',
    '__name__',
    '__qualname__',
    '__module__'
    '__class__',
    '__getattribute__',
    '__new__',
    '__setattr'
)

CODE_FIELD = '__code__'
GLOBAL_FIELD = '__globals__'
NAME_FIELD = '__name__'

OBJECT_TYPE_REGEX = "\'([\w\W]+)\'"

TYPE_FIELD = 'TYPE'
VALUE_FIELD = 'VALUE'

PRIMITIVE_TYPES = ['int', 'float', 'complex', 'bool', 'str', 'NoneType']

COLLECTIONS = ['list', 'tuple', 'bytes', 'set']

CLASS = 'class'
OBJECT = 'object'
DICT = 'dict'
FUNC = 'function'
CODE = 'code'
MODULE = 'module'
BASE = 'base'
DATA = 'data'

DOC_ATTRIBUTE = '__doc__'
