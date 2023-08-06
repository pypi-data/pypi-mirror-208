from types import NoneType as nonetype, \
    CodeType as codetype, \
    ModuleType as moduletype, \
    FunctionType as functype, \
    BuiltinFunctionType as bldinfunctype, \
    CellType as celltype, \
    MappingProxyType as mapproxytype, \
    WrapperDescriptorType as wrapdesctype , \
    MethodDescriptorType as metdesctype, \
    GetSetDescriptorType as getsetdesctype


class Cls:
    @staticmethod
    def sf():
        pass

    @classmethod
    def cf(cls):
        pass


smethodtype = type(Cls.__dict__["sf"])
cmethodtype = type(Cls.__dict__["cf"])


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
    codetype.co_firstlineno,
    codetype.co_lnotab,
    codetype.co_freevars,
    codetype.co_cellvars]
]

UNIQUE_TYPES = [
    mapproxytype,
    wrapdesctype,
    metdesctype,
    getsetdesctype,
    bldinfunctype
]
