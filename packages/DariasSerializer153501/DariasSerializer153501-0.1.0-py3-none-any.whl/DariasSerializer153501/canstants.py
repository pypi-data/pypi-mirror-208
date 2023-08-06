
INT_REGULAR = r"[+-]?\d+"
FLOAT_REGULAR = r"(?:[+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)"
BOOL_REGULAR = r"((?:true)|(?:false))\b"
STR_REGULAR = r"\"(?:(?:\\\")|[^\"])*\""
NONE_REGULAR = r"\b(?:Null)\b"
COMPLEX_REGULAR = fr"{INT_REGULAR}{INT_REGULAR}j"

LIST_RECURSION = r"\[(?R)?(?:,(?R))*\]"
VALUE_RECURSION = r"\{(?:(?R):(?R))?(?:,(?R):(?R))*\}"

VALUE_REGULAR_EXPR = fr"\s*({LIST_RECURSION}|{VALUE_RECURSION}|{STR_REGULAR}|{FLOAT_REGULAR}|" \
                fr"{BOOL_REGULAR}|{INT_REGULAR}|{NONE_REGULAR}|{COMPLEX_REGULAR}\s*)"

BASE_TYPES = r"str|int|float|bool|NoneType|list|dict"
key = "key"
val = "value"
# именованные группы(для оращения по key и value)
ELEMENT_REGULAR = fr"\s*(\<(?P<{key}>{BASE_TYPES})\>(?P<{val}>([^<>]*)|(?R)+)\</(?:{BASE_TYPES})\>)\s*"

CODE_ATTRIBUTES = ("co_argcount",
        "co_posonlyargcount",
        "co_kwonlyargcount",
        "co_nlocals",
        "co_stacksize",
        "co_flags",
        "co_code",
        "co_consts",
        "co_names",
        "co_varnames",
        "co_filename",
        "co_name",
        #"co_qualname",
        "co_firstlineno",
        "co_lnotab",
        #"co_exceptiontable",
        "co_freevars",
        "co_cellvars")

DEFAULT_TYPES = ("int", "float", "complex", "str", "bool")

BASIC_COLLECTION = ("list", "tuple", "set", "frozenset", "bytearray", "bytes")
