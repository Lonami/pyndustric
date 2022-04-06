import ast

ERR_COMPLEX_ASSIGN = "E002"
ERR_COMPLEX_VALUE = "E003"
ERR_UNSUPPORTED_OP = "E004"
ERR_UNSUPPORTED_ITER = "E005"
ERR_BAD_ITER_ARGS = "E006"
ERR_UNSUPPORTED_IMPORT = "E007"
ERR_UNSUPPORTED_EXPR = "E008"
ERR_UNSUPPORTED_SYSCALL = "E009"
ERR_BAD_SYSCALL_ARGS = "E010"
ERR_NESTED_DEF = "E011"
ERR_INVALID_DEF = "E012"
ERR_REDEF = "E013"
ERR_NO_DEF = "E014"
ERR_ARGC_MISMATCH = "E015"
ERR_TOO_LONG = "E016"
ERR_INVALID_SOURCE = "E017"
ERR_BAD_TUPLE_ASSIGN = "E018"

ERROR_DESCRIPTIONS = {
    ERR_COMPLEX_ASSIGN: "cannot perform complex assignment",
    ERR_COMPLEX_VALUE: "cannot evaluate complex value",
    ERR_UNSUPPORTED_OP: "unsupported operation",
    ERR_UNSUPPORTED_ITER: "unsupported iteration",
    ERR_BAD_ITER_ARGS: "invalid iteration arguments",
    ERR_UNSUPPORTED_IMPORT: "unsupported import",
    ERR_UNSUPPORTED_EXPR: "unsupported standalone expression",
    ERR_UNSUPPORTED_SYSCALL: "unsupported system call",
    ERR_BAD_SYSCALL_ARGS: "invalid syscall arguments",
    ERR_NESTED_DEF: "nested function definitions are not allowed",
    ERR_INVALID_DEF: "invalid function definition",
    ERR_REDEF: "cannot define the same function name twice",
    ERR_NO_DEF: "function has not been defined",
    ERR_ARGC_MISMATCH: "different number of arguments used in function call from function definition",
    ERR_TOO_LONG: "the program is too long to fit in a logic processor",
    ERR_INVALID_SOURCE: "the provided source type to compile is not supported",
    ERR_BAD_TUPLE_ASSIGN: "can only assign to a tuple if the right-hand side is a tuple of the same length",
}

BIN_CMP = {
    ast.Eq: "equal",
    ast.NotEq: "notEqual",
    ast.And: "and",
    ast.Or: "or",
    ast.Lt: "lessThan",
    ast.LtE: "lessThanEq",
    ast.Gt: "greaterThan",
    ast.GtE: "greaterThanEq",
}

NEGATED_BIN_CMP = {
    "equal": "notEqual",
    "notEqual": "equal",
    "lessThan": "greaterThanEq",
    "greaterThanEq": "lessThan",
    "greaterThan": "lessThanEq",
    "lessThanEq": "greaterThan",
    "and": "nand",
    "or": "nor",
}

BIN_OPS = {
    ast.Add: "add",
    ast.Sub: "sub",
    ast.Mult: "mul",
    ast.Div: "div",
    ast.FloorDiv: "idiv",
    ast.Mod: "mod",
    ast.Pow: "pow",
    ast.LShift: "shl",
    ast.RShift: "shr",
    ast.BitOr: "or",
    ast.BitAnd: "and",
    ast.BitXor: "xor",
}

BUILTIN_DEFS = {
    "flip": 1,
    "max": 2,
    "min": 2,
    "xor": 2,
    "atan2": 2,
    "dst": 2,
    "noise": 2,
    "abs": 1,
    "log": 1,
    "log10": 1,
    "sin": 1,
    "cos": 1,
    "tan": 1,
    "floor": 1,
    "ceil": 1,
    "sqrt": 1,
    "rand": 1,
}

RADAR_ORDERS = {"min": "1", "True": "1", "1": "1", "max": "0", "False": "0", "0": "0"}

# Map Pythonic environment and resource names with non-standard resources (camelCase, not kebab-case).
ENV_MAP = {
    "this": "@this",
    "x": "@thisx",
    "y": "@thisy",
    "counter": "@counter",
    "link_count": "@links",
    "time": "@time",
    "width": "@mapw",
    "height": "@maph",
}

RES_MAP = {
    # Resource-related
    "items": "@totalItems",
    "first_item": "@firstItem",
    "liquids": "@totalLiquids",
    "power": "@totalPower",
    "max_items": "@itemCapacity",
    "max_liquids": "@liquidCapacity",
    "max_power": "@powerCapacity",
    "power_stored": "@powerNetStored",
    "power_capacity": "@powerNetCapacity",
    "power_in": "@powerNetIn",
    "power_out": "@powerNetOut",
    "ammo": "@ammo",
    "max_ammo": "@ammoCapacity",
    "health": "@health",
    "max_health": "@maxHealth",
    "heat": "@heat",
    "efficiency": "@efficiency",
    "progress": "@progress",
    "timescale": "@timescale",
    "rotation": "@rotation",
    "x": "@x",
    "y": "@y",
    "shoot_x": "@shootX",
    "shoot_y": "@shootY",
    "size": "@size",
    "dead": "@dead",
    "range": "@range",
    "shooting": "@shooting",
    "boosting": "@boosting",
    "mine_x": "@mineX",
    "mine_y": "@mineY",
    "mining": "@mining",
    "team": "@team",
    "type": "@type",
    "flag": "@flag",
    "controlled": "@controlled",
    "controller": "@controller",
    "commanded": "@commanded",
    "name": "@name",
    "payload": "@payloadCount",
    "payload_type": "@payloadType",
}

REG_STACK = "__pyc_sp"
REG_RET = "__pyc_ret"
REG_RET_COUNTER_PREFIX = "__pyc_rc_"
REG_IT_FMT = "__pyc_it_{}_{}"
REG_TMP_FMT = "__pyc_tmp_{}"

# https://github.com/Anuken/Mindustry/blob/ab19e6f/core/src/mindustry/logic/LExecutor.java#L28
MAX_INSTRUCTIONS = 1000
