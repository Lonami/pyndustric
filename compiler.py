import ast # standard python module for generating and using an abstract syntax tree (ast) representing python code

from dataclasses import dataclass # standard python module for simple classes used just to store data in attributes
from .constants import *          # definitions of various constants mapping Python entitites to mlog equivalents


@dataclass
class Function:
    """This stores information about a user-defined function that is callable within a compilable program."""
    start: int   #  Line number for the start of the function within the compiled program
    argc: int    #  Count of number of arguments the function takes


class CompilerError(ValueError):
    def __init__(self, code, node: ast.AST):
        super().__init__(f'[{code}/{node.lineno}:{node.col_offset}] {ERROR_DESCRIPTIONS[code]}')


class Compiler(ast.NodeVisitor):
    """ast.NodeVisitor is a superclass with methods that enable straightforward visitation of the various nodes
    in an AST syntax tree, calling corresponding methods for the different types of nodes as they're visited, where
    parent nodes typically opt to initiate visits for their children.  This subclass overwrites the defauly visit
    methods with ones that generate compiled mlog code as the various parts of the tree are visited."""
    def __init__(self):
        self._ins = [
            f'set {REG_STACK} 0',
        ] # This will end up being a list of instructions that will compose the compiled code.
          # We begin by initializing the stack
        #TODO I'm not sure we really want/need a stack by default -- probly better to do everything with dummy variables
        self._in_def = None   # will be set to a True-ish value while visiting user-defined function definitions
        self._functions = {}  # will map user defined function names to Function objects containing info about functions

    def compile(self, code):
        """This is the main function for the compiler taking in a chunk of Python code (specified either as a
        string, *** a function whose source code file can be found via python's inspect module, or *** a Path
        indicating a source code file to compile.  This visits various nodes in the syntax tree of that code,
        amassing a list of mlog instructions that will perform the equivalent of that code in mindustry.
        This list is then concatenated into a single string, and returned."""
        # TODO enable this to handle function and Path inputs, not just strings
        self.visit(ast.parse(code))  # visit the root node of the syntax tree, which will then visit branches and leaves
        return self.generate_masm()  # concatenate our amassed list of instructions into a single string to return
        # TODO print the resulting mlog instructions to console, so user can read or copy/paste
        # TODO place a copy of the resulting mlog string in the clipboard, so it can be pasted to Mindustry

    def visit(self, node):
        """This will call some specific flavor of visit method, depending upon what type of node this is, typically
        one of the ones defined below."""
        super().visit(node)

    def visit_Import(self, node):
        """This will be called for any* import statement in the given code (*aside from ones buried in parts of the
        syntax tree that end up not being visited, typically due to other errors -- a similar qualifier would apply
        to other specific visit methods, but will not be spelled out again)."""
        # TODO remember what files are imported, and that we may need to look there for source code for helper functions
        #      so that we can compile that into the mlog program too
        # TODO at worst this should probably be a warning rather than an error
        raise CompilerError(ERR_UNSUPPORTED_IMPORT, node)

    def visit_ImportFrom(self, node):
        """This will be called for any* statement of the form "from {module} import {names}.
           Currently, this allows only for importing everything from the pyndustri.pyi interface module."""
        # TODO again if we want to allow code to import other functions and end up compiling them, we'll probably
        #      need to allow these imports and track where to go to find the relevant function code to compile
        if node.module != 'pyndustri' or len(node.names) != 1 or node.names[0].name != '*':
            raise CompilerError(ERR_UNSUPPORTED_IMPORT, node)

    def visit_Assign(self, node: ast.Assign):
        """This will be called for any* statement of the form "{targets} = {values}"
        """
        if len(node.targets) != 1:
            raise CompilerError(ERR_MULTI_ASSIGN, node)
            # TODO some multi-assignment may as well be allowed, e.g., x,y = 30,50 should be fine, as should x=y=0
            # *** how do those two cases show up in an AST?

        target = node.targets[0]
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)
            # TODO Make sure this is the right error to raise?  Won't this often be triggered e.g., by things like
            #      "12 = x"? where the left-hand-side isn't a name?  This isn't "complex" assignment, just not the
            #      right sort of target to assign values to!

        value = node.value  # The value on the right-hand-side of the =
        # TODO: This should probably be consolidated together with other instances where expressions may be encountered
        if isinstance(value, ast.BinOp):  # if expression is a binary operation, e.g., a+b
            op = BIN_OPS.get(type(value.op)) # look up equivalent op in dict of mlog binary ops, or None if not there
            if op is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, node)

            left = self.as_value(value.left)
            right = self.as_value(value.right)
            self._ins.append(f'op {op} {target.id} {left} {right}') # e.g. "x=y+z" compiles to "op add x y z"
            #TODO if this is to be generalized to handle expressions wherever they might occur, this will need to
            #     be changed, e.g., to allow replacing target.id with an intermediate dummy variable

        elif isinstance(value, ast.Compare):  # if expression is a binary comparison, e.g., a<b
            if len(value.ops) != 1 or len(value.comparators) != 1:
                raise CompilerError(ERR_UNSUPPORTED_EXPR)
            #TODO not sure what exactly is being ruled out here? things like a<b<c?  Could be good to support those.

            cmp = BIN_CMP.get(type(value.ops[0])) # look up the mlog equivalent of this python comparison, or None
            if cmp is None:
                raise CompilerError(ERR_UNSUPPORTED_OP, value)

            left = self.as_value(value.left)
            right = self.as_value(value.comparators[0])
            self._ins.append(f'op {cmp} {target.id} {left} {right}') # e.g. "x = y<z" compiles to "op lessThan x y z"

            #TODO again needs to be generalized to handle expressions in other contexts
            #TODO there's no reason to keep this separate from the preceding case, given how closely parallel they are

        elif isinstance(value, ast.Call) \
                and isinstance(value.func, ast.Attribute) \
                and value.func.value.id == 'Sensor':  # if this node is of the form Sensor.attr( args )
            if len(value.args) != 1:
                raise CompilerError(ERR_ARGC_MISMATCH, node)

            arg = value.args[0].id

            attr = RES_MAP.get(value.func.attr)
            if attr is None:
                raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

            self._ins.append(f'sensor {target.id} {arg} {attr}') # "x=Sensor.copper(vault1)"->"sensor x vault1 @copper"

            # TODO offer "x = vault1.copper" as an alternative (or perhaps outright replacement) for this
            # TODO again this would need to be generalized to handle expressions found in other contexts

        # TODO this is where we'd handle any other object-attribute based calls, like Unit.approach() or salvo1.shoot()

        else:  # for anything else of the form "x = value"
            val = self.as_value(value)  # as_value() tries to coerce value to be some val that mlog can assign to x
            self._ins.append(f'set {target.id} {val}')  # and compile this to "set x val"

            #TODO need to rethink the division of labor between as_value and a generalized expression handler

    def visit_AugAssign(self, node: ast.Assign):  # This handles "augmenting assignments" like "x += 1"
        """This will be called for any* augmenting assignment statement, like "x += 1"  """
        target = node.target
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)
            # TODO again this isn't the right error.  The problem with 12 += 1 isn't that it's *complex*, it's that 12 isn't the right sort of thing to increment!

        op = BIN_OPS.get(type(node.op))
        if op is None:
            raise CompilerError(ERR_UNSUPPORTED_OP, node)

        right = self.as_value(node.value)
        self._ins.append(f'op {op} {target.id} {target.id} {right}')
        # TODO this closely parallels treatment of x = x + 1, and of x = y < 1, so likely should be merged with them
        # TODO this needs to allow for complex expressions on the right-hand side

    def visit_If(self, node):
        """This will be called for any* if statement, like "if test: body" potentially with else clause too."""
        if isinstance(node.test, ast.Compare):  #mlog lets us incorporate a binary comparison into a jump statement
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
        # TODO when there is no else clause, should negate the test to reduce jumps by one
        # TODO if we want to support OR, one place to do so will probably be here (another would be non-if expressions)

    def visit_While(self, node):
        """This will be called for any* while loop."""
        self._ins.append(f'jump {{}} always')
        initial = len(self._ins) - 1

        for subnode in node.body:
            self.visit(subnode)

        test = self.as_value(node.test)
        self._ins.append(f'jump {initial + 1} notEqual {test} 0')
        end = len(self._ins) - 1
        self._ins[initial] = self._ins[initial].format(end)
        # TODO in cases where the test is a comparison, that can be combined with the jump for efficiency as it is for if
        # TODO reconsider situating the test after the body of the loop; in the case where the test is initially false,
        #      it'd have been faster to have the (negated) test at the beginning (much like an if with no else);
        #      in other cases this ends up being a wash.  In the case where the test is atomic or a simple comparison,
        #      it'd be most efficient to duplicate the 1-line test at top and bottom, since a conditional jump takes no
        #      more instructions than an unconditional one does, and this would take one less cycle when the test is
        #      initially false.
        # TODO it may make sense to simply replace "while test: body" with something like "if not test: jump_to('end');
        #      label('beginning'); body; if test jump_to('beginning'); label('end')" thereby reducing this to other
        #      problems we're independently committed to solving.

    def visit_For(self, node):
        """This will be called for any* for loop, though not many will be supported because mlog doesn't offer much
           in the way of iterators or iterable lists.  The two iterables that are supported are range(start, stop, step)
           and Links (which iterates through various linked blocks)."""
        # TODO  It would be fairly natural to construe Unit.bind_next as an iterator, and to articulate code that
        #       cycles through units with the idiom "for Unit in UnitType( flare ):" so it might make sense to offer
        #       this as another pre-canned for-loop option.  Of course there are other ways of writing this, but
        #       the same is true of iterating over links

        target = node.target
        if not isinstance(target, ast.Name):
            raise CompilerError(ERR_COMPLEX_ASSIGN, node)
            # TODO: again the problem isn't that "for 12 in range(5):" is *complex*, it's that 12 isn't the right sort of thing to assign values to

        call = node.iter
        if not isinstance(call, ast.Call):
            raise CompilerError(ERR_UNSUPPORTED_ITER, node)

        inject = []

        if isinstance(call.func, ast.Attribute) \
                and call.func.value.id == 'Env' and call.func.attr == 'links':
            it = REG_IT_FMT.format(call.lineno, call.col_offset)
            start, end, step = 0, '@links', 1
            inject.append(f'getlink {target.id} {it}')
        elif isinstance(call.func, ast.Name) and call.func.id == 'range':
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

        self._ins.append(f'set {it} {start}')

        self._ins.append(f'jump {{}} greaterThanEq {it} {end}')
        # TODO  if the step in range(start,stop,step) is negative, the relevant test is lessThanEq
        condition = len(self._ins) - 1

        self._ins.extend(inject)
        for subnode in node.body:
            self.visit(subnode)

        self._ins.append(f'op add {it} {it} {step}')
        self._ins.append(f'jump {condition} always')
        self._ins[condition] = self._ins[condition].format(len(self._ins))

    def visit_FunctionDef(self, node):
        """This will be called for any* function definition of the form def fname( args ): body """

        # TODO forbid recursion (or implement it by storing and restoring everything from stack)
        #      Telos: There's no need to actively forbid recursion, though it may be good to warn about dangers of it.
        #             So long as there is no stack to overflow, recursion can work perfectly fine as a form of infinite
        #             loop, or the recursion can be escaped with an end() command, a jump_to( label ) command, or simply
        #             by entering into some other infinite loop and never return-ing. The key point is just to warn that
        #             recursive calls will overwrite the value of the return pointer (if we follow my suggestion of
        #             implementing that in a dummy variable to forego needing a stack) and thereby lose track of
        #             whatever it was that called the function in the first place.  If you instead push return addresses
        #             onto a stack, and wait to pop them at return-time, then recursion will still be fine, and will
        #             even return all the way back to the first caller, with the only caveat being that all variables
        #             are global, effectively including function arguments, so you have to be a bit cautious how
        #             you write the code.
        # TODO local variable namespace per-function
        #      Telos:  I doubt that mindustry's processor-speed is fast enough to really make this worthwhile.
        #              I'd recommend instead just documenting that mlog uses a single global namespace, and that
        #              each call to a function overwrites the prior global values of its arguments.

        if self._in_def is not None:
            raise CompilerError(ERR_NESTED_DEF, node)
        # TODO there's no reason we *couldn't* allow nested function defns, though it may be more tricky than it's worth
        #      At first blush, I think these actually *probably* would work as is, if you remove this test banning them.
        #      The main uses of nested function definitions involve namespaces which probably aren't worth bothering with.
        #      Another use is to assign a function name to a different function definition, depending upon which
        #      def(s) end up being executed. The best way to implement that would probably be to assign a variable for
        #      each function name that points to the line number for whatever the current definition of that function
        #      is, and rather than compiling def simply to jump past the body of the function, each time a def is
        #      encountered, it should first change that function's name to point to this def's body, rather than
        #      whatever other def of the same-named function it might previously have pointed to.  I.e., this would treat
        #      function names as Python does, just as variables that point to an object that happens to be callable.
        #      In some ways, this would be better than your unPythonic assumption that each function name can have only
        #      one def in a program, though it would cost an instruction-cycle each time a def is "exectuted" which is
        #      a pretty minor cost.  (Regardless, we probably should make an unPythonic assumption that a given
        #      function-name will always accept the same arguments, though I suppose if we keep pushing positional args
        #      on the stack to pass them, then we needn't even assume that!)

        if node.name in self._functions or node.name == 'print':
            raise CompilerError(ERR_REDEF, node)

        self._in_def = node.name
        reg_ret = f'{REG_RET_COUNTER_PREFIX}{len(self._functions)}'

        args = node.args
        if any((
                args.posonlyargs,
                args.vararg,
                args.kwonlyargs,
                args.kw_defaults,
                args.kwarg,
                args.defaults,
        )):
            raise CompilerError(ERR_INVALID_DEF, node)

        # TODO  many of the above could/should be supported

        # TODO it's better to put functions at the end and not have to skip them as code, but jumps need fixing
        self._ins.append('jump {} always')

        prologue = len(self._ins)  # line number where the function definition begins
        self._functions[node.name] = Function(start=prologue, argc=len(args.args))

        self._ins.append(f'read {reg_ret} cell1 {REG_STACK}')
        for arg in args.args:
            self._ins.append(f'op sub {REG_STACK} {REG_STACK} 1')
            self._ins.append(f'read {arg.arg} cell1 {REG_STACK}')

        # TODO argument passing would be more efficient if function-calling simply stored the arguments into the relevant
        #      variables directly, rather than slowly piping them through a memory block, and this would also obviate
        #      the need for an associated memory block.  (This would *not* however allow for recursion to retain
        #      different namespaces for different levels, but to allow that we'd also need to store old values for the
        #      namespace in the stack too, which would be really taxing for slow mindustry processors!)

        for subnode in node.body:
            self.visit(subnode)

        epilogue = len(self._ins)
        # TODO better way to patch this (ins should be concrete types, not immutable strings)
        #      Telos:  I've caught myself having this sort of thought many times over the years, but these strings are
        #              so short that creating new ones with heavily optimized methods like format just is better/faster
        #              than any sort of mutable data-type we'd be likely to come up with!
        #              However, in this particular case, I think we should consider making each function name be an
        #              mlog variable that points to the beginning of that function's body, so that "calling" the function
        #              later is just a matter of "passing" variables, setting a return pointer, and then setting the
        #              @counter to jump to the line number stored in that function's name.  But I think you'll still
        #              be stuck going back to make one substitution later depending upon where exactly you end up
        #              deciding to stick the function body.  Do you really need to iterate through *all* the lines
        #              between prologue and epilogue?  You could make each Return jump straight back
        #              to the caller, rather than detouring through the epilogue, and then the only remaining thing
        #              you'd need to substitute for after the fact is the {} in the prologue.

        for i in range(prologue, epilogue):
            if '{epilogue}' in self._ins[i]:
                self._ins[i] = self._ins[i].format(epilogue=epilogue)

        # Add 1 to the return value to skip the jump that made the call.
        self._ins.append(f'op add @counter {reg_ret} 1')

        end = len(self._ins)
        self._ins[prologue - 1] = self._ins[prologue - 1].format(end)
        self._in_def = None

    def visit_Return(self, node):
        """This will be called for any instance of Return, typically from within a function definition."""
        val = self.as_value(node.value)
        self._ins.append(f'set {REG_RET} {val}')
        self._ins.append('jump {epilogue} always')
        # TODO  better to pass back the return value in a dummy variable, rather than requiring a stack
        # TODO  maybe raise an error if not self._in_def  (can't return except when within a function definition)
        #       what we have currently will end up leaving the {epilogue} in the compiled program
        #       Or does AST itself enforce that Return must be within the scope of a Def?

    def visit_Expr(self, node):
        """This will be called for any* instance of an Expr, *** whatever exactly that is???."""
        # TODO  figure out what all counts as an Expr, and figure out how to combine this with a general ability
        #       to process complex expressions
        call = node.value
        if not isinstance(call, ast.Call):
            raise CompilerError(ERR_UNSUPPORTED_EXPR, node)

        # `print`, unlike the rest of syscalls, has no namespace
        if isinstance(call.func, ast.Name):
            if call.func.id == 'print':
                return self.emit_print_syscall(call)
            else:
                return self.as_value(call)

        if not isinstance(call.func, ast.Attribute) or not isinstance(call.func.value, ast.Name):
            raise CompilerError(ERR_UNSUPPORTED_EXPR, node)

        ns = call.func.value.id
        if ns == 'Screen':
            self.emit_screen_syscall(call)
        elif ns == 'Control':
            self.emit_control_syscall(call)
        else:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

        # TODO  This may be the place to handle other (pseudo-)function calls, like dst(), abs(),
        #       end(), label(), and jump_to()

    def emit_print_syscall(self, node: ast.Call):
        """This will be called by visit_Expr when it encounters a print(...) command."""
        if len(node.args) != 1:
            raise CompilerError(ERR_BAD_SYSCALL_ARGS)

        arg = node.args[0]
        if isinstance(arg, ast.JoinedStr):
            for value in arg.values:
                if isinstance(value, ast.FormattedValue):
                    if value.format_spec is not None:
                        raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

                    val = self.as_value(value.value)
                    self._ins.append(f'print {val}')
                elif isinstance(value, ast.Constant):
                    val = self.as_value(value)
                    self._ins.append(f'print {val}')
                else:
                    raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)
        else:
            val = self.as_value(arg)
            self._ins.append(f'print {val}')

        flush = True
        for kw in node.keywords:
            if kw.arg == 'flush':
                if isinstance(kw.value, ast.Constant) and kw.value.value in (False, True):
                    flush = kw.value.value
                elif isinstance(kw.value, ast.Name):
                    flush = kw.value.id
                else:
                    raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

        if isinstance(flush, str):
            self._ins.append(f'printflush {flush}')
        elif flush:
            self._ins.append(f'printflush message1')

    def emit_screen_syscall(self, node: ast.Call):
        """This will be called by visit_Expr when it encounters a Screen.attr(...) command."""
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

    def emit_control_syscall(self, node: ast.Call):
        """This will be called by visit_Expr when it encounters a Control(...) command."""

        # TODO may want to reimplement much of this in a more object-oriented fashion, e.g., ripple1.shoot(...)
        #      rather than Control.shoot( ripple1, ... )

        method = node.func.attr
        if method == 'enabled':
            if len(node.args) != 2:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            link, enabled = map(self.as_value, node.args)
            self._ins.append(f'control enabled {link} {enabled}')
        elif method == 'shoot':
            if len(node.args) == 3:
                link, x, y, enabled = *map(self.as_value, node.args), 1
            elif len(node.args) == 4:
                link, x, y, enabled = map(self.as_value, node.args)
            else:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            self._ins.append(f'control shoot {link} {x} {y} {enabled}')
        elif method == 'ceasefire':
            if len(node.args) != 1:
                raise CompilerError(ERR_BAD_SYSCALL_ARGS, node)

            link = self.as_value(node.args[0])
            self._ins.append(f'control shoot {link} 0 0 0')
        else:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)

    def as_value(self, node):
        """This will be called by various visit methods when they encounter something to treat as an atomic expression,
           e.g. for the y and 3 in x=y+3.  This coerces the given node to a string that can appear in mlog code."""

        # TODO figure out balance of labor between this and other things in evaluating complex expressions

        if isinstance(node, ast.Constant):  # constants include True, 1.5, and "yarn"
            if isinstance(node.value, bool):
                return ('false', 'true')[node.value]
            elif isinstance(node.value, (int, float)):
                return str(node.value)
            elif isinstance(node.value, str):
                return '"' + ''.join(c for c in node.value if c >= ' ' and c != '"') + '"' #scrub quotes and control characters from string
            else:
                raise CompilerError(ERR_COMPLEX_VALUE, node)

        elif isinstance(node, ast.Name):
            assert isinstance(node.ctx, ast.Load)
            # TODO should this raise a CompilerError like most other errors do?
            return node.id
            # TODO figure out what this does???

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.value.id == 'Env':
                    return self.env_as_value(node.func)
                else:
                    raise CompilerError(ERR_COMPLEX_VALUE, node)
            # TODO  It looks like this is the place to handle object attributes like vault1.copper and Unit.x

            fn = self._functions.get(node.func.id)
            if fn is None:
                raise CompilerError(ERR_NO_DEF, node)

            if len(node.args) != fn.argc:
                raise CompilerError(ERR_ARGC_MISMATCH, node)

            for arg in node.args:
                val = self.as_value(arg)
                self._ins.append(f'write {val} cell1 {REG_STACK}')
                self._ins.append(f'op add {REG_STACK} {REG_STACK} 1')
            # TODO  probably better to set the values straight into the relevant variables, rather than slowly piping through stack

            # `REG_STACK` is not updated because it's immediately read by the function.
            # If it was, the `op add` followed by the `op sub` would be redundant.
            self._ins.append(f'write @counter cell1 {REG_STACK}')
            self._ins.append(f'jump {fn.start} always')
            return REG_RET
            # TODO  probably better to pass the returned value via a dummy variable rather than piping through stack

        else:
            raise CompilerError(ERR_COMPLEX_VALUE, node)
            # TODO This may be where we want code that handles complex expressions, like 1+2*3

    def env_as_value(self, node):
        """This is used to process expressions like Env.width, which compile to mlog globals like @mapw """
        var = ENV_TO_VAR.get(node.attr)
        if var is None:
            raise CompilerError(ERR_UNSUPPORTED_SYSCALL, node)
        return var

    def generate_masm(self):
        """This will be called after the full list self._ins of mlog instructions is generated, concatenating
           them together into a single string of mlog assembly (masm) code."""
        if len(self._ins) + 1 > MAX_INSTRUCTIONS:
            raise CompilerError(ERR_TOO_LONG, ast.Module(lineno=0, col_offset=0))

        return '\n'.join(self._ins) + '\nend\n'
        #TODO it's not at all clear that you really want an explicit 'end' here!  My understanding is that
        #   'end' wipes all variables, whereas simply reaching the end with no explicit 'end' command instead
        #   loops back to the beginning, retaining the values of variables.  The choice of these should be left up
        #   to users, not forced by Pyndustric.  end() should probably instead be included as an explicit command
        #   that users might opt to include when they want to restart with variable wipe.
