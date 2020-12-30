import ast
import sys
import time

__version__ = '0.1'
DEBUG = False

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

class CompilerError(ValueError):
    def __init__(self, code, node: ast.AST):
        super().__init__(f'[{code}/{node.lineno}:{node.col_offset}] {ERROR_DESCRIPTIONS[code]}')

class Compiler(ast.NodeVisitor):
    def __init__(self):
        self._ins = []

    def compile(self, code):
        self.visit(ast.parse(code))
        return self.generate_masm()

    def visit(self, node):
        if DEBUG:
            print(ast.dump(node), '\n')
        super().visit(node)

    def visit_Import(self, node):
        raise CompilerError(ERR_UNSUPPORTED_IMPORT, node)

    def visit_ImportFrom(self, node):
        if node.module != 'pyndustri' or len(node.names) != 1 or node.names[0].name != '*':
            raise CompilerError(ERR_UNSUPPORTED_IMPORT, node)

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) != 1:
            raise CompilerError(ERR_MULTI_ASSIGN, node)

        target = node.targets[0]
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)

        value = node.value
        if isinstance(value, ast.BinOp):
            op = BIN_OPS.get(type(value.op))
            if op is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, node)

            left = self.as_value(value.left)
            right = self.as_value(value.right)
            self._ins.append(f'op {op} {target.id} {left} {right}')
        else:
            val = self.as_value(value)
            self._ins.append(f'set {target.id} {val}')

    def visit_If(self, node):
        if isinstance(node.test, ast.Compare):
            if len(node.test.ops) != 1 or len(node.test.comparators) != 1:
                raise CompilerError(ERR_UNSUPPORTED_EXPR)

            cmp = BIN_CMP.get(type(node.test.ops[0]))
            if cmp is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, node)

            left = self.as_value(node.test.left)
            right = self.as_value(node.test.comparators[0])
            self._ins.append(f'jump {{}} {cmp} {left} {right}')
        else:
            test = self.as_value(node.test)
            self._ins.append(f'jump {{}} notEqual {test} 0')

        initial = len(self._ins) - 1

        for subnode in node.orelse:
            self.visit(subnode)
        self._ins.append(f'jump {{}} always')
        orelse = len(self._ins) - 1

        for subnode in node.body:
            self.visit(subnode)
        end = len(self._ins)

        self._ins[initial] = self._ins[initial].format(orelse + 1)
        self._ins[orelse] = self._ins[orelse].format(end)

    def visit_While(self, node):
        self._ins.append(f'jump {{}} always')
        initial = len(self._ins) - 1

        for subnode in node.body:
            self.visit(subnode)

        test = self.as_value(node.test)
        self._ins.append(f'jump {initial + 1} notEqual {test} 0')
        end = len(self._ins) - 1

        self._ins[initial] = self._ins[initial].format(end)

    def visit_For(self, node):
        target = node.target
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)

        if not isinstance(node.iter, ast.Call) or node.iter.func.id != 'range':
            raise CompilerError(ERR_UNSUPPORTED_ITER, node)

        argv = node.iter.args
        argc = len(argv)
        if argc == 1:
            start, end, step = 0, self.as_value(argv[0]), 1
        elif argc == 2:
            start, end, step = *map(self.as_value, argv), 1
        elif argc == 3:
            start, end, step = map(self.as_value, argv)
        else:
            raise CompilerError(ERR_BAD_ITER_ARGS, node)

        self._ins.append(f'set {target.id} {start}')

        self._ins.append(f'jump {{}} greaterThanEq {target.id} {end}')
        condition = len(self._ins) - 1

        for subnode in node.body:
            self.visit(subnode)

        self._ins.append(f'op add {target.id} {target.id} {step}')
        self._ins.append(f'jump {condition} always')
        self._ins[condition] = self._ins[condition].format(len(self._ins))

    def visit_Expr(self, node):
        if (not isinstance(node.value, ast.Call)
                or not isinstance(node.value.func, ast.Attribute)
                or not isinstance(node.value.func.value, ast.Name)):
            raise CompilerError(ERR_UNSUPPORTED_EXPR, node)

        ns = node.value.func.value.id
        if ns == 'Screen':
            self.emit_screen_syscall(node.value)
        else:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

    def emit_screen_syscall(self, node: ast.Call):
        method = node.func.attr
        if method == 'clear':
            if len(node.args) != 3:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            r, g, b = map(self.as_value, node.args)
            self._ins.append(f'draw clear {r} {g} {b}')

        elif method == 'color':
            if len(node.args) == 3:
                r, g, b, a = *map(self.as_value, node.args), 255
            elif len(node.args) == 4:
                r, g, b, a = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self._ins.append(f'draw color {r} {g} {b} {a}')

        elif method == 'stroke':
            if len(node.args) != 1:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            width = self.as_value(node.args[0])
            self._ins.append(f'draw stroke {width}')

        elif method == 'line':
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x0, y0, x1, y1 = map(self.as_value, node.args)
            self._ins.append(f'draw line {x0} {y0} {x1} {y1}')

        elif method == 'rect':
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y, width, height = map(self.as_value, node.args)
            self._ins.append(f'draw rect {x} {y} {width} {height}')

        elif method == 'hollow_rect':
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y, width, height = map(self.as_value, node.args)
            self._ins.append(f'draw lineRect {x} {y} {width} {height}')

        elif method == 'poly':
            if len(node.args) == 4:
                x, y, radius, sides, rotation = *map(self.as_value, node.args), 0
            elif len(node.args) == 5:
                x, y, radius, sides, rotation = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self._ins.append(f'draw poly {x} {y} {sides} {radius} {rotation}')

        elif method == 'hollow_poly':
            if len(node.args) == 4:
                x, y, radius, sides, rotation = *map(self.as_value, node.args), 0
            elif len(node.args) == 5:
                x, y, radius, sides, rotation = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self._ins.append(f'draw linePoly {x} {y} {sides} {radius} {rotation}')

        elif method == 'triangle':
            if len(node.args) != 6:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x0, y0, x1, y1, x2, y2 = map(self.as_value, node.args)
            self._ins.append(f'draw triangle {x0} {y0} {x1} {y1} {x2} {y2}')

        # elif method == 'image':
        #     pass

        elif method == 'flush':
            if len(node.args) == 0:
                self._ins.append(f'drawflush display1')
            elif len(node.args) == 1:
                value = self.as_value(node.args[0])
                self._ins.append(f'drawflush {value}')
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

        else:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

    def as_value(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            assert isinstance(node.ctx, ast.Load)
            return node.id
        else:
            raise CompilerError(ERR_COMPLEX_VALUE, node)

    def generate_masm(self):
        return '\n'.join(self._ins) + '\nend\n'

def main():
    for file in sys.argv[1:]:
        print(f'# reading {file}...', file=sys.stderr)
        if file == '-':
            source = sys.stdin.read()
        else:
            with open(file, encoding='utf-8') as fd:
                source = fd.read()

        print(f'# compiling {file}...', file=sys.stderr)
        start = time.time()
        masm = Compiler().compile(source)
        took = time.time() - start
        print(masm)
        print(f'# compiled {file} with pyndustric {__version__} in {took:.2f}s', file=sys.stderr)

if __name__ == '__main__':
    main()
