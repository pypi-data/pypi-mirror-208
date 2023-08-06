from types import \
    NoneType as nonetype, \
    ModuleType as moduletype, \
    CodeType as codetype, \
    FunctionType as functype, \
    BuiltinFunctionType as bldinfunctype, \
    CellType as celltype, \
    MappingProxyType as mapproxytype, \
    WrapperDescriptorType as wrapdesctype, \
    MethodDescriptorType as metdesctype, \
    GetSetDescriptorType as getsetdesctype

CODE_PROPS = [prop.__name__ for prop in [
    codetype.co_argcount,
    codetype.co_posonlyargcount,
    codetype.co_kwonlyargcount,
    codetype.co_nlocals,
    codetype.co_stacksize,
    codetype.co_flags,
    codetype.co_code,
    codetype.co_consts,
    codetype.co_names,
    codetype.co_varnames,
    codetype.co_filename,
    codetype.co_name,
    #codetype.co_qualname,
    codetype.co_firstlineno,
    codetype.co_lnotab,
    #codetype.co_exceptiontable,
    codetype.co_freevars,
    codetype.co_cellvars
]]

UNIQUE_TYPES = [
    mapproxytype,
    wrapdesctype,
    metdesctype,
    getsetdesctype,
    bldinfunctype
]

TYPE_KW = "type"
SOURCE_KW = "source"
CODE_KW = "__code__"
GLOBALS_KW = functype.__globals__.__name__
NAME_KW = "__name__"
DEFAULTS_KW = "__defaults__"
CLOSURE_KW = functype.__closure__.__name__
BASES_KW = "__bases__"
DICT_KW = "__dict__"
CLASS_KW = "__class__"
OBJECT_KW = "object"


class static_class:
    @staticmethod
    def sm():
        pass

    @classmethod
    def cm(cls):
        pass


smethodtype = type(static_class.__dict__["sm"])
cmethodtype = type(static_class.__dict__["cm"])
