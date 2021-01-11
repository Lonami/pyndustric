from .constants import *
from collections import Counter
from dataclasses import dataclass
import ast
import inspect
import sys
import textwrap


@dataclass
class Function:
    start: int
    argc: int


class CompilerError(ValueError):
    def __init__(self, code, node: ast.AST):
        if node is None:
            node = ast.Module(lineno=0, col_offset=0)  # dummy value

        super().__init__(f"[{code}/{node.lineno}:{node.col_offset}] {ERROR_DESCRIPTIONS[code]}")


if sys.version_info < (3, 8):

    class CompatTransformer(ast.NodeTransformer):
        def visit_Num(self, node):
            return ast.copy_location(ast.Constant(value=node.n), node)

        def visit_Str(self, node):
            return ast.copy_location(ast.Constant(value=node.s), node)

        def visit_Bytes(self, node):
            return ast.copy_location(ast.Constant(value=node.s), node)

        def visit_NameConstant(self, node):
            return ast.copy_location(ast.Constant(value=node.value), node)


else:

    class CompatTransformer(ast.NodeTransformer):
        pass


class Compiler(ast.NodeVisitor):
    def __init__(self):
        self._ins = [
            f"set {REG_STACK} 0",
        ]
        self._in_def = None
        self._functions = {}

    def compile(self, code):
        if inspect.isfunction(code):
            code = textwrap.dedent(inspect.getsource(code))
            # i.e. `tree.body_of_tree[def].body_of_function`
            body = ast.parse(code).body[0].body
            if (
                isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                # Skip doc-string
                body = body[1:]
        elif isinstance(code, str):
            body = ast.parse(code).body
        else:
            raise CompilerError(ERR_INVALID_SOURCE, None)

        for node in body:
            self.visit(node)

        return self.generate_masm()

    def visit(self, node):
        compat = CompatTransformer()
        compat_node = compat.visit(node)
        super().visit(compat_node)

    def visit_Import(self, node):
        raise CompilerError(ERR_UNSUPPORTED_IMPORT, node)

    def visit_ImportFrom(self, node):
        if node.module != "pyndustri" or len(node.names) != 1 or node.names[0].name != "*":
            raise CompilerError(ERR_UNSUPPORTED_IMPORT, node)

    def visit_Assign(self, node: ast.Assign):
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)

        self.insert_assign_ins(target.id, node.value)

        if len(node.targets) > 1:
            for additional_target in node.targets[1:]:
                self._ins.append(f"set {additional_target.id} {target.id}")

    def insert_assign_ins(self, variable: str, value: ast.AST):
        if isinstance(value, ast.BinOp):
            op = BIN_OPS.get(type(value.op))
            if op is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, value)

            left = self.as_value(value.left)
            right = self.as_value(value.right)
            self._ins.append(f"op {op} {variable} {left} {right}")

        elif isinstance(value, ast.Compare):
            if len(value.ops) != 1 or len(value.comparators) != 1:
                raise CompilerError(ERR_UNSUPPORTED_EXPR)

            cmp = BIN_CMP.get(type(value.ops[0]))
            if cmp is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, value)

            left = self.as_value(value.left)
            right = self.as_value(value.comparators[0])
            self._ins.append(f"op {cmp} {variable} {left} {right}")

        elif (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and value.func.value.id == "Sensor"
        ):
            if len(value.args) != 1:
                raise CompilerError(ERR_ARGC_MISMATCH, value)

            arg = value.args[0].id

            attr = RES_MAP.get(value.func.attr)
            if attr is None:
                raise CompilerError(ERR_UNSUPPORTED_SYSCALL, value)

            self._ins.append(f"sensor {variable} {arg} {attr}")

        elif isinstance(value, ast.Attribute):
            obj = value.value.id
            attr = value.attr

            mlog_attr = "@" + attr.replace("_", "-")
            self._ins.append(f"sensor {variable} {obj} {mlog_attr}")

        else:
            val = self.as_value(value)
            self._ins.append(f"set {variable} {val}")

    def visit_AugAssign(self, node: ast.Assign):
        target = node.target  # e.g., x in "x += 1"
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)

        op = BIN_OPS.get(type(node.op))
        if op is None:
            raise CompilerError(ERR_UNSUPPORTED_OP, node)

        right = self.as_value(node.value)
        self._ins.append(f"op {op} {target.id} {target.id} {right}")

    def visit_If(self, node):
        if isinstance(node.test, ast.Compare):
            if len(node.test.ops) != 1 or len(node.test.comparators) != 1:
                raise CompilerError(ERR_UNSUPPORTED_EXPR)

            cmp = BIN_CMP.get(type(node.test.ops[0]))
            if cmp is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, node)

            left = self.as_value(node.test.left)
            right = self.as_value(node.test.comparators[0])
            self._ins.append(f"jump {{}} {cmp} {left} {right}")
        else:
            test = self.as_value(node.test)
            self._ins.append(f"jump {{}} notEqual {test} 0")

        initial = len(self._ins) - 1

        for subnode in node.orelse:
            self.visit(subnode)
        self._ins.append(f"jump {{}} always")
        orelse = len(self._ins) - 1

        for subnode in node.body:
            self.visit(subnode)
        end = len(self._ins)

        self._ins[initial] = self._ins[initial].format(orelse + 1)
        self._ins[orelse] = self._ins[orelse].format(end)

    def visit_While(self, node):
        self._ins.append(f"jump {{}} always")
        initial = len(self._ins) - 1

        for subnode in node.body:
            self.visit(subnode)

        test = self.as_value(node.test)
        self._ins.append(f"jump {initial + 1} notEqual {test} 0")
        end = len(self._ins) - 1

        self._ins[initial] = self._ins[initial].format(end)

    def visit_For(self, node):
        target = node.target
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)

        call = node.iter
        if not isinstance(call, ast.Call):
            raise CompilerError(ERR_UNSUPPORTED_ITER, node)

        inject = []

        if (
            isinstance(call.func, ast.Attribute)
            and call.func.value.id == "Env"
            and call.func.attr == "links"
        ):
            it = REG_IT_FMT.format(call.lineno, call.col_offset)
            start, end, step = 0, "@links", 1
            inject.append(f"getlink {target.id} {it}")
        elif isinstance(call.func, ast.Name) and call.func.id == "range":
            it = target.id
            argv = call.args
            argc = len(argv)
            if argc == 1:
                start, end, step = 0, self.as_value(argv[0]), 1
            elif argc == 2:
                start, end, step = *map(self.as_value, argv), 1
            elif argc == 3:
                start, end, step = map(self.as_value, argv)
            else:
                raise CompilerError(ERR_BAD_ITER_ARGS, node)
        else:
            raise CompilerError(ERR_UNSUPPORTED_ITER, node)

        self._ins.append(f"set {it} {start}")

        self._ins.append(f"jump {{}} greaterThanEq {it} {end}")
        condition = len(self._ins) - 1

        self._ins.extend(inject)
        for subnode in node.body:
            self.visit(subnode)

        self._ins.append(f"op add {it} {it} {step}")
        self._ins.append(f"jump {condition} always")
        self._ins[condition] = self._ins[condition].format(len(self._ins))

    def visit_FunctionDef(self, node):
        # TODO forbid recursion (or implement it by storing and restoring everything from stack)
        # TODO local variable namespace per-function
        if self._in_def is not None:
            raise CompilerError(ERR_NESTED_DEF, node)

        if node.name in self._functions or node.name == "print":
            raise CompilerError(ERR_REDEF, node)

        self._in_def = node.name
        reg_ret = f"{REG_RET_COUNTER_PREFIX}{len(self._functions)}"

        args = node.args
        if any(
            (
                args.vararg,
                args.kwonlyargs,
                args.kw_defaults,
                args.kwarg,
                args.defaults,
            )
        ):
            raise CompilerError(ERR_INVALID_DEF, node)

        if sys.version_info >= (3, 8):
            if args.posonlyargs:
                raise CompilerError(ERR_INVALID_DEF, node)

        # TODO it's better to put functions at the end and not have to skip them as code, but jumps need fixing
        self._ins.append("jump {} always")

        prologue = len(self._ins)
        self._functions[node.name] = Function(start=prologue, argc=len(args.args))

        self._ins.append(f"read {reg_ret} cell1 {REG_STACK}")
        for arg in args.args:
            self._ins.append(f"op sub {REG_STACK} {REG_STACK} 1")
            self._ins.append(f"read {arg.arg} cell1 {REG_STACK}")

        for subnode in node.body:
            self.visit(subnode)

        epilogue = len(self._ins)
        # TODO better way to patch this (ins should be concrete types, not immutable strings)
        for i in range(prologue, epilogue):
            if "{epilogue}" in self._ins[i]:
                self._ins[i] = self._ins[i].format(epilogue=epilogue)

        # Add 1 to the return value to skip the jump that made the call.
        self._ins.append(f"op add @counter {reg_ret} 1")

        end = len(self._ins)
        self._ins[prologue - 1] = self._ins[prologue - 1].format(end)
        self._in_def = None

    def visit_Return(self, node):
        val = self.as_value(node.value)
        self._ins.append(f"set {REG_RET} {val}")
        self._ins.append("jump {epilogue} always")

    def visit_Expr(self, node):
        call = node.value
        if not isinstance(call, ast.Call):
            raise CompilerError(ERR_UNSUPPORTED_EXPR, node)

        # `print`, unlike the rest of syscalls, has no namespace
        if isinstance(call.func, ast.Name):
            if call.func.id == "print":
                return self.emit_print_syscall(call)
            else:
                return self.as_value(call)

        if not isinstance(call.func, ast.Attribute) or not isinstance(call.func.value, ast.Name):
            raise CompilerError(ERR_UNSUPPORTED_EXPR, node)

        ns = call.func.value.id
        if ns == "Screen":
            self.emit_screen_syscall(call)
        elif ns == "Control":
            self.emit_control_syscall(call)
        else:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

    def emit_print_syscall(self, node: ast.Call):
        if len(node.args) != 1:
            raise CompilerError(ERR_BAD_SYSCALL_ARGS)

        arg = node.args[0]
        if isinstance(arg, ast.JoinedStr):
            for value in arg.values:
                if isinstance(value, ast.FormattedValue):
                    if value.format_spec is not None:
                        raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

                    val = self.as_value(value.value)
                    self._ins.append(f"print {val}")
                elif isinstance(value, ast.Constant):
                    val = self.as_value(value)
                    self._ins.append(f"print {val}")
                else:
                    raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)
        else:
            val = self.as_value(arg)
            self._ins.append(f"print {val}")

        flush = True
        for kw in node.keywords:
            if kw.arg == "flush":
                if isinstance(kw.value, ast.Constant) and kw.value.value in (
                    False,
                    True,
                ):
                    flush = kw.value.value
                elif isinstance(kw.value, ast.Name):
                    flush = kw.value.id
                else:
                    raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

        if isinstance(flush, str):
            self._ins.append(f"printflush {flush}")
        elif flush:
            self._ins.append(f"printflush message1")

    def emit_screen_syscall(self, node: ast.Call):
        method = node.func.attr
        if method == "clear":
            if len(node.args) != 3:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            r, g, b = map(self.as_value, node.args)
            self._ins.append(f"draw clear {r} {g} {b}")

        elif method == "color":
            if len(node.args) == 3:
                r, g, b, a = *map(self.as_value, node.args), 255
            elif len(node.args) == 4:
                r, g, b, a = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self._ins.append(f"draw color {r} {g} {b} {a}")

        elif method == "stroke":
            if len(node.args) != 1:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            width = self.as_value(node.args[0])
            self._ins.append(f"draw stroke {width}")

        elif method == "line":
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x0, y0, x1, y1 = map(self.as_value, node.args)
            self._ins.append(f"draw line {x0} {y0} {x1} {y1}")

        elif method == "rect":
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y, width, height = map(self.as_value, node.args)
            self._ins.append(f"draw rect {x} {y} {width} {height}")

        elif method == "hollow_rect":
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y, width, height = map(self.as_value, node.args)
            self._ins.append(f"draw lineRect {x} {y} {width} {height}")

        elif method == "poly":
            if len(node.args) == 4:
                x, y, radius, sides, rotation = *map(self.as_value, node.args), 0
            elif len(node.args) == 5:
                x, y, radius, sides, rotation = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self._ins.append(f"draw poly {x} {y} {sides} {radius} {rotation}")

        elif method == "hollow_poly":
            if len(node.args) == 4:
                x, y, radius, sides, rotation = *map(self.as_value, node.args), 0
            elif len(node.args) == 5:
                x, y, radius, sides, rotation = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self._ins.append(f"draw linePoly {x} {y} {sides} {radius} {rotation}")

        elif method == "triangle":
            if len(node.args) != 6:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x0, y0, x1, y1, x2, y2 = map(self.as_value, node.args)
            self._ins.append(f"draw triangle {x0} {y0} {x1} {y1} {x2} {y2}")

        # elif method == 'image':
        #     pass

        elif method == "flush":
            if len(node.args) == 0:
                self._ins.append(f"drawflush display1")
            elif len(node.args) == 1:
                value = self.as_value(node.args[0])
                self._ins.append(f"drawflush {value}")
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

        else:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

    def emit_control_syscall(self, node: ast.Call):
        method = node.func.attr
        if method == "enabled":
            if len(node.args) != 2:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            link, enabled = map(self.as_value, node.args)
            self._ins.append(f"control enabled {link} {enabled}")
        elif method == "shoot":
            if len(node.args) == 3:
                link, x, y, enabled = *map(self.as_value, node.args), 1
            elif len(node.args) == 4:
                link, x, y, enabled = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self._ins.append(f"control shoot {link} {x} {y} {enabled}")
        elif method == "ceasefire":
            if len(node.args) != 1:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            link = self.as_value(node.args[0])
            self._ins.append(f"control shoot {link} 0 0 0")
        else:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

    def as_value(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return ("false", "true")[node.value]
            elif isinstance(node.value, (int, float)):
                return str(node.value)
            elif isinstance(node.value, str):
                return '"' + "".join(c for c in node.value if c >= " " and c != '"') + '"'
            else:
                raise CompilerError(ERR_COMPLEX_VALUE, node)
        elif isinstance(node, ast.Name):
            assert isinstance(node.ctx, ast.Load)
            return node.id
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.value.id == "Env":
                    return self.env_as_value(node.func)
                else:
                    raise CompilerError(ERR_COMPLEX_VALUE, node)

            fn = self._functions.get(node.func.id)
            if fn is None:
                raise CompilerError(ERR_NO_DEF, node)

            if len(node.args) != fn.argc:
                raise CompilerError(ERR_ARGC_MISMATCH, node)

            for arg in node.args:
                val = self.as_value(arg)
                self._ins.append(f"write {val} cell1 {REG_STACK}")
                self._ins.append(f"op add {REG_STACK} {REG_STACK} 1")

            # `REG_STACK` is not updated because it's immediately read by the function.
            # If it was, the `op add` followed by the `op sub` would be redundant.
            self._ins.append(f"write @counter cell1 {REG_STACK}")
            self._ins.append(f"jump {fn.start} always")
            return REG_RET
        else:
            raise CompilerError(ERR_COMPLEX_VALUE, node)

    def env_as_value(self, node):
        var = ENV_TO_VAR.get(node.attr)
        if var is None:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)
        return var

    def generate_masm(self):
        if len(self._ins) + 1 > MAX_INSTRUCTIONS:
            raise CompilerError(ERR_TOO_LONG, None)

        return "\n".join(self._ins) + "\nend\n"
