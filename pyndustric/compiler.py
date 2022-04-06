from .constants import *
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Union
import ast
import inspect
import sys
import textwrap


class _Instruction:
    """
    Represents a mlog instruction.
    """

    def __init__(self, ins: str):
        self._ins = ins

    def __str__(self):
        return self._ins


class _Label(_Instruction):
    """
    Represents a no-op instruction used to label certain destinations for mlog jumps.
    """

    def __init__(self):
        super().__init__("")
        self._lineno = None

    def __str__(self):
        if self._lineno is None:
            raise InternalCompilerError(
                "lineno should be set. some instruction likely referenced this unstored label", None
            )

        return str(self._lineno)


class _Jump(_Instruction):
    """
    Represents a jump instruction towards a specific label.
    """

    def __init__(self, label: _Label, condition: str):
        super().__init__(f"jump {{}} {condition}")
        self._label = label

    def __str__(self):
        return super().__str__().format(self._label)


@dataclass
class Function:
    """
    Stores information about a user-defined functions which are callable within a compilable program.
    """

    start: _Label  # label pointing to the function's prologue
    argc: int  # count of number of arguments the function takes


class CompilerError(ValueError):
    def __init__(self, code, node: ast.AST):
        if node is None:
            node = ast.Module(lineno=0, col_offset=0)  # dummy value

        super().__init__(f"[{code}/{node.lineno}:{node.col_offset}] {ERROR_DESCRIPTIONS[code]}")


class InternalCompilerError(CompilerError):
    def __init__(self, code, node: ast.AST):
        if node is None:
            node = ast.Module(lineno=0, col_offset=0)  # dummy value

        ValueError.__init__(self, f"[ICE/{node.lineno}:{node.col_offset}] {code}")


class CompatTransformer(ast.NodeTransformer):
    if sys.version_info < (3, 9):

        def visit_Index(self, node):
            return self.visit(node.value)

    if sys.version_info < (3, 8):

        def visit_Num(self, node):
            return ast.copy_location(ast.Constant(value=node.n), node)

        def visit_Str(self, node):
            return ast.copy_location(ast.Constant(value=node.s), node)

        def visit_Bytes(self, node):
            return ast.copy_location(ast.Constant(value=node.s), node)

        def visit_NameConstant(self, node):
            return ast.copy_location(ast.Constant(value=node.value), node)


def _parse_code(code: str):
    return CompatTransformer().visit(ast.parse(code))


def _name_as_resource(name: str, mapping: dict):
    # It might already be a resource (e.g. when needing a resource and getting Env.res).
    if name.startswith("@"):
        return name

    # String literal name, perform no replacement.
    if name.startswith('"'):
        return "@" + name.strip('"')

    # Some names are not kebab-case, try resolve those from the RES_MAP first.
    resource = mapping.get(name)

    # For any other name, assume it's kebab-case.
    if not resource:
        resource = "@" + name.replace("_", "-")

    return resource


def _name_as_env(name: str):
    return _name_as_resource(name, ENV_MAP)


def _name_as_res(name: str):
    return _name_as_resource(name, RES_MAP)


class Compiler(ast.NodeVisitor):
    def __init__(self):
        self._ins = [_Instruction(f"set {REG_STACK} 0")]
        self._in_def = None  # current function name
        self._epilogue = None  # current function's epilogue label
        self._functions = {}
        self._tmp_var_counter = 0

    def ins_append(self, ins):
        if not isinstance(ins, _Instruction):
            ins = _Instruction(ins)
        self._ins.append(ins)

    def _tmp_var_name(self):
        self._tmp_var_counter += 1
        return REG_TMP_FMT.format(self._tmp_var_counter)

    def compile(self, code: Union[str, Callable, Path]):
        if inspect.isfunction(code):
            code = textwrap.dedent(inspect.getsource(code))
            # i.e. `tree.body_of_tree[def].body_of_function`
            body = _parse_code(code).body[0].body
            if (
                isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                # Skip doc-string
                body = body[1:]
        elif isinstance(code, str):
            body = _parse_code(code).body
        elif isinstance(code, Path):
            with code.open("r", encoding="utf-8") as fd:
                body = _parse_code(fd.read()).body
        else:
            raise CompilerError(ERR_INVALID_SOURCE, None)

        for node in body:
            self.visit(node)

        return self.generate_masm()

    def visit_Import(self, node):
        raise CompilerError(ERR_UNSUPPORTED_IMPORT, node)

    def visit_ImportFrom(self, node):
        if node.module != "pyndustri" or len(node.names) != 1 or node.names[0].name != "*":
            raise CompilerError(ERR_UNSUPPORTED_IMPORT, node)

    def visit_Assign(self, node: ast.Assign):
        target = node.targets[0]
        if isinstance(target, ast.Name):
            # a = b
            output = self.as_value(node.value, target.id)
            if output != target.id:
                self.ins_append(f"set {target.id} {output}")

            if len(node.targets) > 1:
                for additional_target in node.targets[1:]:
                    self.ins_append(f"set {additional_target.id} {target.id}")
        elif isinstance(target, ast.Subscript):
            # Mem.cell[idx] = val
            if not isinstance(target.value, ast.Attribute) or target.value.value.id != "Mem":
                raise CompilerError(ERR_COMPLEX_ASSIGN, node)

            cell = target.value.attr
            idx = self.as_value(target.slice)
            val = self.as_value(node.value)

            self.ins_append(f"write {val} {cell} {idx}")
        elif isinstance(target, ast.Tuple) and len(node.targets) == 1:
            # a, b = c, d
            if not isinstance(node.value, ast.Tuple) or len(target.elts) != len(node.value.elts):
                raise CompilerError(ERR_BAD_TUPLE_ASSIGN, node)

            for left, right in zip(target.elts, node.value.elts):
                left = left.id
                output = self.as_value(right, left)
                if output != left:
                    self.ins_append(f"set {left} {output}")
        else:
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)

    def visit_AugAssign(self, node: ast.Assign):
        target = node.target  # e.g., x in "x += 1"
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)

        op = BIN_OPS.get(type(node.op))
        if op is None:
            raise CompilerError(ERR_UNSUPPORTED_OP, node)

        right = self.as_value(node.value)
        self.ins_append(f"op {op} {target.id} {target.id} {right}")

    def conditional_jump(self, destination_label, test, jump_if_test=True):
        if isinstance(test, ast.Compare):
            if len(test.ops) != 1 or len(test.comparators) != 1:
                raise CompilerError(ERR_UNSUPPORTED_EXPR, test)

            cmp = BIN_CMP.get(type(test.ops[0]))
            left = self.as_value(test.left)
            right = self.as_value(test.comparators[0])

        elif isinstance(test, ast.BoolOp):
            cmp = BIN_CMP.get(type(test.op))
            left, right = self.as_value(test.values[0]), self.as_value(test.values[1])

        else:
            left, cmp, right = self.as_value(test), "notEqual", 0

        if not jump_if_test:
            cmp = NEGATED_BIN_CMP.get(cmp)
        if cmp is None:
            raise CompilerError(ERR_UNSUPPORTED_OP, test)

        if cmp == "and":
            failed_label = _Label()
            self.ins_append(_Jump(failed_label, f"equal {left} 0"))
            self.ins_append(_Jump(destination_label, f"notEqual {right} 0"))
            self.ins_append(failed_label)
        elif cmp == "or":
            self.ins_append(_Jump(destination_label, f"notEqual {left} 0"))
            self.ins_append(_Jump(destination_label, f"notEqual {right} 0"))
        elif cmp == "nand":
            self.ins_append(_Jump(destination_label, f"equal {left} 0"))
            self.ins_append(_Jump(destination_label, f"equal {right} 0"))
        elif cmp == "nor":
            failed_label = _Label()
            self.ins_append(_Jump(failed_label, f"notEqual {left} 0"))
            self.ins_append(_Jump(destination_label, f"equal {right} 0"))
            self.ins_append(failed_label)
        else:
            self.ins_append(_Jump(destination_label, f"{cmp} {left} {right}"))

    def radar_instruction(self, variable, obj, value):
        if obj == "Unit":
            radar = "uradar"
            obj = "@unit"
        else:
            radar = "radar"

        criteria = [arg.id for arg in value.args]
        if len(criteria) > 3:
            raise CompilerError(ERR_ARGC_MISMATCH, value)

        while len(criteria) < 3:
            criteria.append("any")

        criteria = " ".join(criteria)
        key = "distance"
        order = "min"
        for k in value.keywords:
            if k.arg == "key":
                key = self.as_value(k.value)
            elif k.arg == "order":
                order = RADAR_ORDERS[self.as_value(k.value)]
            else:
                raise CompilerError(ERR_UNSUPPORTED_EXPR, value)

        try:
            order = RADAR_ORDERS[order]
        except KeyError:
            raise CompilerError(ERR_UNSUPPORTED_EXPR, value)

        self.ins_append(f"{radar} {criteria} {key} {obj} {order} {variable}")
        return variable

    def visit_If(self, node):
        endif_label = _Label()
        if_false_label = _Label() if node.orelse else endif_label
        self.conditional_jump(if_false_label, node.test, jump_if_test=False)
        for subnode in node.body:
            self.visit(subnode)
        if node.orelse:
            self.ins_append(_Jump(endif_label, "always"))
            self.ins_append(if_false_label)
            for subnode in node.orelse:
                self.visit(subnode)
        self.ins_append(endif_label)

    def visit_While(self, node):
        """This will be called for any* while loop."""
        body_label = _Label()
        end_label = _Label()
        self.conditional_jump(end_label, node.test, jump_if_test=False)
        self.ins_append(body_label)
        for subnode in node.body:
            self.visit(subnode)
        self.conditional_jump(body_label, node.test, jump_if_test=True)
        self.ins_append(end_label)

    def visit_For(self, node):
        target = node.target
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)

        call = node.iter
        if not isinstance(call, ast.Call):
            raise CompilerError(ERR_UNSUPPORTED_ITER, node)

        inject = []
        backwards = False

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
                backwards = isinstance(argv[2], ast.UnaryOp) and isinstance(argv[2].op, ast.USub)
            else:
                raise CompilerError(ERR_BAD_ITER_ARGS, node)
        else:
            raise CompilerError(ERR_UNSUPPORTED_ITER, node)

        self.ins_append(f"set {it} {start}")

        end_label = _Label()
        condition = _Label()
        self.ins_append(condition)
        if backwards:
            self.ins_append(_Jump(end_label, f"lessThanEq {it} {end}"))
        else:
            self.ins_append(_Jump(end_label, f"greaterThanEq {it} {end}"))

        self._ins.extend(inject)
        for subnode in node.body:
            self.visit(subnode)

        self.ins_append(f"op add {it} {it} {step}")
        self.ins_append(_Jump(condition, "always"))
        self.ins_append(end_label)

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
        end = _Label()
        self.ins_append(_Jump(end, "always"))

        prologue = _Label()
        self.ins_append(prologue)
        self._functions[node.name] = Function(start=prologue, argc=len(args.args))

        self.ins_append(f"read {reg_ret} cell1 {REG_STACK}")
        for arg in args.args:
            self.ins_append(f"op sub {REG_STACK} {REG_STACK} 1")
            self.ins_append(f"read {arg.arg} cell1 {REG_STACK}")

        # This relies on the fact that there are no nested definitions.
        # Set the epilogue now so that `visit_Return` can use this label.
        self._epilogue = _Label()

        for subnode in node.body:
            self.visit(subnode)

        self.ins_append(self._epilogue)

        # Add 1 to the return value to skip the jump that made the call.
        self.ins_append(f"op add @counter {reg_ret} 1")
        self.ins_append(end)
        self._in_def = None
        self._epilogue = None

    def visit_Return(self, node):
        if not self._epilogue:
            raise InternalCompilerError("return encountered with epilogue being unset", node)

        val = self.as_value(node.value)
        self.ins_append(f"set {REG_RET} {val}")
        self.ins_append(_Jump(self._epilogue, "always"))

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
        elif ns == "Unit":
            self.emit_unit_syscall(call)
        # Try to emit certain special calls if the method name is recognised, no matter the object.
        elif self.emit_control_syscall(call):
            pass
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
                    self.ins_append(f"print {val}")
                elif isinstance(value, ast.Constant):
                    val = self.as_value(value)
                    self.ins_append(f"print {val}")
                else:
                    raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)
        else:
            val = self.as_value(arg)
            self.ins_append(f"print {val}")

        flush = True
        for kw in node.keywords:
            if kw.arg == "flush":
                if isinstance(kw.value, ast.Constant) and kw.value.value in (False, True):
                    flush = kw.value.value
                elif isinstance(kw.value, ast.Name):
                    flush = kw.value.id
                else:
                    raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

        if isinstance(flush, str):
            self.ins_append(f"printflush {flush}")
        elif flush:
            self.ins_append(f"printflush message1")

    def emit_screen_syscall(self, node: ast.Call):
        method = node.func.attr
        if method == "clear":
            if len(node.args) != 3:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            r, g, b = map(self.as_value, node.args)
            self.ins_append(f"draw clear {r} {g} {b}")

        elif method == "color":
            if len(node.args) == 3:
                r, g, b, a = *map(self.as_value, node.args), 255
            elif len(node.args) == 4:
                r, g, b, a = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append(f"draw color {r} {g} {b} {a}")

        elif method == "stroke":
            if len(node.args) != 1:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            width = self.as_value(node.args[0])
            self.ins_append(f"draw stroke {width}")

        elif method == "line":
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x0, y0, x1, y1 = map(self.as_value, node.args)
            self.ins_append(f"draw line {x0} {y0} {x1} {y1}")

        elif method == "rect":
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y, width, height = map(self.as_value, node.args)
            self.ins_append(f"draw rect {x} {y} {width} {height}")

        elif method == "hollow_rect":
            if len(node.args) != 4:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y, width, height = map(self.as_value, node.args)
            self.ins_append(f"draw lineRect {x} {y} {width} {height}")

        elif method == "poly":
            if len(node.args) == 4:
                x, y, radius, sides, rotation = *map(self.as_value, node.args), 0
            elif len(node.args) == 5:
                x, y, radius, sides, rotation = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append(f"draw poly {x} {y} {sides} {radius} {rotation}")

        elif method == "hollow_poly":
            if len(node.args) == 4:
                x, y, radius, sides, rotation = *map(self.as_value, node.args), 0
            elif len(node.args) == 5:
                x, y, radius, sides, rotation = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append(f"draw linePoly {x} {y} {sides} {radius} {rotation}")

        elif method == "triangle":
            if len(node.args) != 6:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x0, y0, x1, y1, x2, y2 = map(self.as_value, node.args)
            self.ins_append(f"draw triangle {x0} {y0} {x1} {y1} {x2} {y2}")

        # elif method == 'image':
        #     pass

        elif method == "flush":
            if len(node.args) == 0:
                self.ins_append(f"drawflush display1")
            elif len(node.args) == 1:
                value = self.as_value(node.args[0])
                self.ins_append(f"drawflush {value}")
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

        else:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

    def emit_unit_syscall(self, node: ast.Call):
        method = node.func.attr
        if method == "bind":
            if len(node.args) != 1:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            if not isinstance(node.args[0], ast.Constant):
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            unit = node.args[0].value

            if not isinstance(unit, str):
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append(f"ubind @{unit}")

        elif method == "idle":
            if len(node.args) != 0:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append("ucontrol idle 0 0 0 0 0")

        elif method == "stop":
            if len(node.args) != 0:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append("ucontrol stop 0 0 0 0 0")

        elif method == "move":
            if len(node.args) != 2:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y = map(self.as_value, node.args)
            self.ins_append(f"ucontrol move {x} {y} 0 0 0")

        elif method == "approach":
            if len(node.args) != 3:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y, r = map(self.as_value, node.args)
            self.ins_append(f"ucontrol approach {x} {y} {r} 0 0")

        elif method == "boost":
            if len(node.args) != 1:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            enable = self.as_value(node.args[0])
            self.ins_append(f"ucontrol boost {enable} 0 0 0 0")

        elif method == "pathfind":
            if len(node.args) != 0:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append("ucontrol pathfind 0 0 0 0 0")

        elif method == "shoot":
            if len(node.args) != 2:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            # Not sure how targetp (unit shoot) works... so that's not implemented.
            x, y = map(self.as_value, node.args)
            self.ins_append(f"ucontrol target {x} {y} 1 0 0")

        elif method == "ceasefire":
            if len(node.args) != 0:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append("ucontrol target 0 0 0 0 0")

        elif method == "fetch":
            if len(node.args) not in (2, 3):
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            # WIP
            self.ins_append("ucontrol itemTake from item amount 0 0")

        elif method == "store":
            if len(node.args) not in (1, 2):
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            # WIP
            self.ins_append("ucontrol itemDrop to amount 0 0 0")

        elif method == "lift":
            if len(node.args) != 0:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append("ucontrol payTake takeUnits 0 0 0 0")

        elif method == "carry":
            if len(node.args) != 0:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append("ucontrol payTake takeUnits 0 0 0 0")

        elif method == "drop":
            if len(node.args) != 0:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append("ucontrol payDrop 0 0 0 0 0")

        elif method == "mine":
            if len(node.args) != 2:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            x, y = map(self.as_value, node.args)
            self.ins_append(f"ucontrol mine {x} {y} 0 0 0")

        else:
            # build and getBlock have virtually no documentation, so not implemented yet as I can't figure them out.
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

    def emit_control_syscall(self, node: ast.Call):
        link = node.func.value.id
        method = node.func.attr
        if method == "enabled":
            if len(node.args) != 1:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            enabled = self.as_value(node.args[0])
            self.ins_append(f"control enabled {link} {enabled}")
        elif method == "shoot":
            if len(node.args) == 2:
                x, y, enabled = *map(self.as_value, node.args), 1
            elif len(node.args) == 3:
                x, y, enabled = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append(f"control shoot {link} {x} {y} {enabled}")
        elif method == "ceasefire":
            if len(node.args) != 0:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self.ins_append(f"control shoot {link} 0 0 0")
        else:
            return False

        return True

    def as_value(self, node, output: str = None):
        """
        Returns the string representing either a value (like a number) or a variable.

        If a temporary variable needs to be created, it will be called `output`.
        If `output` is not set, it will be a random name.
        """
        if output is None:
            output = self._tmp_var_name()

        if isinstance(node, ast.Constant):
            # true, 1.23, "string", 4j
            if isinstance(node.value, bool):
                return ("false", "true")[node.value]
            elif isinstance(node.value, (int, float)):
                return str(node.value)
            elif isinstance(node.value, str):
                return '"' + "".join(c for c in node.value if c >= " " and c != '"') + '"'
            else:
                raise CompilerError(ERR_COMPLEX_VALUE, node)

        elif isinstance(node, ast.Name):
            # foo, bar
            return node.id

        elif isinstance(node, ast.Attribute):
            # Env.copper
            # container1.copper
            obj = node.value.id

            # No need to sense the resource if we just want to grab it from Env.
            if obj == "Env":
                return _name_as_env(node.attr)

            # Unit is special-cased.
            if obj == "Unit":
                # ...and the Unit's flag doubly-so.
                obj = "@unit"

            attr = _name_as_res(node.attr)

            self.ins_append(f"sensor {output} {obj} {attr}")
            return output

        elif isinstance(node, ast.Subscript):
            # Memory is a special case because it's read, not sensed.
            # Accessing the attribute itself (e.g. "Mem.cell") shouldn't be a sensor either.
            if isinstance(node.value, ast.Attribute) and node.value.value.id == "Mem":
                cell = node.value.attr
                val = self.as_value(node.slice)
                self.ins_append(f"read {output} {cell} {val}")
                return output

            # container1[dynamic_res]
            # 'some_object'['some_resource']
            obj = self.as_value(node.value).strip('"')
            if isinstance(node.slice, ast.Name):
                # Dynamic resource (pretend the input is a variable and not a resource).
                # If the user does not want this, they should use `obj.attr` instead.
                attr = node.slice.id
            else:
                attr = _name_as_res(self.as_value(node.slice))

            self.ins_append(f"sensor {output} {obj} {attr}")
            return output

        if isinstance(node, ast.UnaryOp):
            # -1
            op = type(node.op)
            # Optimize constants by evaluating them directly.
            if isinstance(node.operand, ast.Constant):
                const = node.operand.value
                if op == ast.Invert:
                    value = ~const
                elif op == ast.Not:
                    value = not const
                elif op == ast.UAdd:
                    value = +const
                elif op == ast.USub:
                    value = -const
                else:
                    raise CompilerError(ERR_UNSUPPORTED_OP, node)

                return self.as_value(ast.Constant(value=value))
            else:
                operand = self.as_value(node.operand)
                # No map here because Mindustry lacks some of these as unary (emulated as binary).
                if op == ast.Invert:
                    self.ins_append(f"op flip {output} {operand}")
                elif op == ast.Not:
                    self.ins_append(f"op equal {output} 0 {operand}")
                elif op == ast.UAdd:
                    self.ins_append(f"op add {output} 0 {operand}")
                elif op == ast.USub:
                    self.ins_append(f"op sub {output} 0 {operand}")
                else:
                    raise CompilerError(ERR_UNSUPPORTED_OP, node)

                return output

        if isinstance(node, ast.BinOp):
            # 1 + 2
            op = BIN_OPS.get(type(node.op))
            if op is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, node)

            left = self.as_value(node.left)
            right = self.as_value(node.right)
            self.ins_append(f"op {op} {output} {left} {right}")
            return output

        elif isinstance(node, ast.Compare):
            # 1 < 2
            if len(node.ops) != 1 or len(node.comparators) != 1:
                raise CompilerError(ERR_UNSUPPORTED_EXPR)

            cmp = BIN_CMP.get(type(node.ops[0]))
            if cmp is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, node)

            left = self.as_value(node.left)
            right = self.as_value(node.comparators[0])
            self.ins_append(f"op {cmp} {output} {left} {right}")
            return output

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            # foo()
            function = node.func.id
            if function in BUILTIN_DEFS:
                argc = BUILTIN_DEFS[function]
                if len(node.args) != argc:
                    raise CompilerError(ERR_ARGC_MISMATCH, node)

                operands = " ".join(self.as_value(arg) for arg in node.args)
                self.ins_append(f"op {function} {output} {operands}")
                return output

            else:
                fn = self._functions.get(node.func.id)
                if fn is None:
                    raise CompilerError(ERR_NO_DEF, node)

                if len(node.args) != fn.argc:
                    raise CompilerError(ERR_ARGC_MISMATCH, node)

                for arg in node.args:
                    val = self.as_value(arg)
                    self.ins_append(f"write {val} cell1 {REG_STACK}")
                    self.ins_append(f"op add {REG_STACK} {REG_STACK} 1")

                self.ins_append(f"write @counter cell1 {REG_STACK}")
                self.ins_append(_Jump(fn.start, "always"))
                # Expressions may be very complex elsewhere, make sure `REG_RET` is not overwritten.
                self.ins_append(f"set {output} {REG_RET}")
                return output

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # building.radar(), Unit.radar()
            obj = node.func.value.id
            method = node.func.attr
            if method == "radar":
                return self.radar_instruction(output, obj, node)

            # The next functions are only available on units.
            if obj != "Unit":
                raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

            if method == "within":
                if len(node.args) != 3:
                    raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

                x, y, r = map(self.as_value, node.args)
                self.ins_append(f"ucontrol within {x} {y} {r} {output} 0")
                return output
            else:
                raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

        raise CompilerError(ERR_UNSUPPORTED_EXPR, node)

    def generate_masm(self):
        # Fill labels' line numbers
        lineno = 0
        for ins in self._ins:
            if isinstance(ins, _Label):
                ins._lineno = lineno
            else:
                lineno += 1

        if lineno > MAX_INSTRUCTIONS:
            raise CompilerError(ERR_TOO_LONG, ast.Module(lineno=0, col_offset=0))

        # Final output is all instructions ignoring labels
        return "\n".join(str(i) for i in self._ins if not isinstance(i, _Label)) + "\nend\n"
