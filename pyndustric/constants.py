import ast

ERR_MULTI_ASSIGN = 'E001'
ERR_COMPLEX_ASSIGN = 'E002'
ERR_COMPLEX_VALUE = 'E003'
ERR_UNSUPPORTED_OP = 'E004'
ERR_UNSUPPORTED_ITER = 'E005'
ERR_BAD_ITER_ARGS = 'E006'
ERR_UNSUPPORTED_IMPORT = 'E007'
ERR_UNSUPPORTED_EXPR = 'E008'
ERR_UNSUPPORTED_SYSCALL = 'E009'
ERR_BAD_SYSCALL_ARGS = 'E010'
ERR_NESTED_DEF = 'E011'
ERR_INVALID_DEF = 'E012'
ERR_REDEF = 'E013'
ERR_NO_DEF = 'E014'
ERR_ARGC_MISMATCH = 'E015'
ERR_TOO_LONG = 'E016'

ERROR_DESCRIPTIONS = {
    ERR_MULTI_ASSIGN: 'can only assign to 1 target',
    ERR_COMPLEX_ASSIGN: 'cannot perform complex assignment',
    ERR_COMPLEX_VALUE: 'cannot evaluate complex value',
    ERR_UNSUPPORTED_OP: 'unsupported operation',
    ERR_UNSUPPORTED_ITER: 'unsupported iteration',
    ERR_BAD_ITER_ARGS: 'invalid iteration arguments',
    ERR_UNSUPPORTED_IMPORT: 'unsupported import',
    ERR_UNSUPPORTED_EXPR: 'unsupported standalone expression',
    ERR_UNSUPPORTED_SYSCALL: 'unsupported system call',
    ERR_BAD_SYSCALL_ARGS: 'invalid syscall arguments',
    ERR_NESTED_DEF: 'nested function definitions are not allowed',
    ERR_INVALID_DEF: 'invalid function definition',
    ERR_REDEF: 'cannot define the same function name twice',
    ERR_NO_DEF: 'function has not been defined',
    ERR_ARGC_MISMATCH: 'different number of arguments used in function call from function definition',
    ERR_TOO_LONG: 'the program is too long to fit in a logic processor',
}

BIN_CMP = {
    ast.Eq: 'equal',
    ast.NotEq: 'notEqual',
    ast.And: 'land',
    ast.Lt: 'lessThan',
    ast.LtE: 'lessThanEq',
    ast.Gt: 'greaterThan',
    ast.GtE: 'greaterThanEq',
}

BIN_OPS = {
    ast.Add: 'add',
    ast.Sub: 'sub',
    ast.Mult: 'mul',
    ast.Div: 'div',
    ast.FloorDiv: 'idiv',
    ast.Mod: 'mod',
    ast.Pow: 'pow',
    ast.LShift: 'shl',
    ast.RShift: 'shr',
    ast.BitOr: 'or',
    ast.BitAnd: 'and',
    ast.BitXor: 'xor',
    **BIN_CMP,
}

ENV_TO_VAR = {
    'this': '@this',
    'x': '@thisx',
    'y': '@thisy',
    'counter': '@counter',
    'link_count': '@links',
    'time': '@time',
    'width': '@mapw',
    'height': '@maph',
}

REG_STACK = '__pyc_sp'
REG_RET = '__pyc_ret'
REG_RET_COUNTER_PREFIX = '__pyc_rc_'
REG_IT_FMT = '__pyc_it_{}_{}'

# https://github.com/Anuken/Mindustry/blob/ab19e6f/core/src/mindustry/logic/LExecutor.java#L28
MAX_INSTRUCTIONS = 1000
