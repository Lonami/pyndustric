import functools
import inspect
import pathlib
import pyndustric
import pytest
import re
import sys
import tempfile


def as_masm(source):
    # Dedent expected mlog source by removing all leading whitespace
    return "set __pyc_sp 0\n" + re.sub(r"^\s+", "", source.strip(), flags=re.MULTILINE) + "\nend\n"


def masm_test(source_func):
    """
    Marks the function as a "masm test".

    The body of the wrapped function will be compiled, and this masm output will be compared
    against the function's docstring, which should contain the *expected* masm output.
    """
    dbg_name = f"{source_func.__name__}:{inspect.currentframe().f_back.f_lineno}"

    @functools.wraps(source_func)
    def wrapped():
        assert source_func.__doc__ is not None, "bad `masm_test` usage; def should have docstring"
        expected = as_masm(source_func.__doc__)
        masm = pyndustric.Compiler().compile(source_func)
        assert masm == expected, f"bad masm for {dbg_name}\n{masm}"

    return wrapped


def expect_err(err, source):
    """
    Expect the error to be raised, and fail if it's not.
    """
    with pytest.raises(pyndustric.CompilerError, match=err):
        pyndustric.Compiler().compile(source)


def test_all_err_have_desc_and_tests():
    error_names = [name for name in dir(pyndustric) if name.startswith("ERR_")]
    error_values = {getattr(pyndustric, name) for name in error_names}

    assert len(error_values) == len(error_names), "some error constants have duplicate values"
    assert len(error_values) == len(pyndustric.ERROR_DESCRIPTIONS), "not all errors are documented"

    with open(__file__, encoding="utf-8") as fd:
        source = fd.read()

    for name in error_names:
        assert name in source, "error is missing a test"


def test_err_complex_assign():
    expect_err(pyndustric.ERR_COMPLEX_ASSIGN, "a, b = c = 1, 2")
    expect_err(pyndustric.ERR_COMPLEX_ASSIGN, "a.b = 1")


def test_err_complex_value():
    expect_err(pyndustric.ERR_COMPLEX_VALUE, "a = 1 + 2j")


def test_err_unsupported_op():
    expect_err(pyndustric.ERR_UNSUPPORTED_OP, "a = m0 @ m1")
    expect_err(pyndustric.ERR_UNSUPPORTED_OP, "a @= m")


def test_err_unsupported_iter():
    expect_err(pyndustric.ERR_UNSUPPORTED_ITER, "for x in [1, 2]: pass")


def test_err_bad_iter_args():
    expect_err(pyndustric.ERR_BAD_ITER_ARGS, "for x in range(): pass")
    expect_err(pyndustric.ERR_BAD_ITER_ARGS, "for x in range(1, 2, 3, 4): pass")


def test_err_unsupported_import():
    expect_err(pyndustric.ERR_UNSUPPORTED_IMPORT, "from math import log")
    expect_err(pyndustric.ERR_UNSUPPORTED_IMPORT, "import pyndustri")


def test_err_unsupported_expr():
    expect_err(pyndustric.ERR_UNSUPPORTED_EXPR, "1 + (2 + 3)")


def test_err_unsupported_syscall():
    expect_err(pyndustric.ERR_UNSUPPORTED_SYSCALL, "Missing.method()")
    expect_err(pyndustric.ERR_UNSUPPORTED_SYSCALL, "Screen.missing()")
    expect_err(pyndustric.ERR_UNSUPPORTED_SYSCALL, "unit.unknown_control()")


def test_err_bad_syscall_args():
    expect_err(pyndustric.ERR_BAD_SYSCALL_ARGS, "Screen.clear(1)")
    expect_err(pyndustric.ERR_BAD_SYSCALL_ARGS, "Screen.clear(1, 2, 3, 4)")


def test_err_nested_def():
    expect_err(pyndustric.ERR_NESTED_DEF, "def foo():\n  def bar():\n    pass")


def test_err_invalid_def():
    expect_err(pyndustric.ERR_INVALID_DEF, "def foo(a=None): pass")
    expect_err(pyndustric.ERR_INVALID_DEF, "def foo(*, a): pass")

    if sys.version_info >= (3, 8):
        expect_err(pyndustric.ERR_INVALID_DEF, "def foo(a, /, b): pass")


def test_err_redef():
    expect_err(pyndustric.ERR_REDEF, "def foo(): pass\ndef foo(): pass")
    expect_err(pyndustric.ERR_REDEF, "def print(): pass")


def test_err_no_def():
    expect_err(pyndustric.ERR_NO_DEF, "x = foo()")


def test_err_argc_mismatch():
    expect_err(pyndustric.ERR_ARGC_MISMATCH, "def foo(n): pass\nx = foo()")
    expect_err(pyndustric.ERR_ARGC_MISMATCH, "def foo(n): pass\nx = foo(1, 2)")
    expect_err(pyndustric.ERR_ARGC_MISMATCH, "u = Unit.radar(enemy, flying, ally, any)")


def test_err_too_long():
    expect_err(pyndustric.ERR_TOO_LONG, "x = 1\n" * (1 + pyndustric.MAX_INSTRUCTIONS))


def test_err_bad_tuple():
    expect_err(pyndustric.ERR_UNSUPPORTED_EXPR, "x = 1, 2")
    expect_err(pyndustric.ERR_BAD_TUPLE_ASSIGN, "x, y = 1")
    expect_err(pyndustric.ERR_BAD_TUPLE_ASSIGN, "x, y = foo()")
    expect_err(pyndustric.ERR_BAD_TUPLE_ASSIGN, "x, y = a, b, c")


def test_no_compile_method():
    class Foo:
        def bar(self):
            pass

    foo = Foo()

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_INVALID_SOURCE):
        pyndustric.Compiler().compile(foo.bar)


def test_compile_string():
    masm = pyndustric.Compiler().compile(
        """\
from pyndustri import *
x = 1
    """
    )


def test_compile_path():
    expected = as_masm(
        """\
        set x 1
        """
    )

    with tempfile.TemporaryDirectory() as folder:
        file = pathlib.Path(folder) / "test_compile_path.py"
        with file.open("w") as fd:
            fd.write("x = 1\n")

        masm = pyndustric.Compiler().compile(file)
        assert masm == expected


def test_compile_function():
    def source():
        """Skip me!"""
        x = 1

    def source2():
        x = 1

    expected = as_masm(
        """\
        set x 1
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected

    masm = pyndustric.Compiler().compile(source2)
    assert masm == expected


@masm_test
def test_assignments():
    """
    set x -1
    op add y x 2
    op equal z x y
    op equal a 0 z
    """
    x = -1
    y = x + 2
    z = x == y
    a = not z


@masm_test
def test_multi_assignment():
    """
    set x 0
    set y x
    set z x
    set a 1
    set b 2
    """
    x = y = z = 0
    a, b = 1, 2


@masm_test
def test_types():
    """
    set x true
    set y 1
    set z 0.1
    set a "string"
    """
    x = True
    y = 1
    z = 0.1
    a = "string"


@masm_test
def test_builtin_defs():
    """
    op abs a 1
    op min lo 1 2
    """
    a = abs(1)
    lo = min(1, 2)


@masm_test
def test_complex_assign():
    """
    op mul __pyc_tmp_1 2 x
    op add a __pyc_tmp_1 1
    op mul __pyc_tmp_6 x x
    op mul __pyc_tmp_9 y y
    op add __pyc_tmp_5 __pyc_tmp_6 __pyc_tmp_9
    op sqrt d __pyc_tmp_5
    """
    a = 2 * x + 1
    d = sqrt(x * x + y * y)


@masm_test
def test_aug_assignments():
    """
    set x 1
    op add x x 1
    """
    x = 1
    x += 1


@masm_test
def test_complex_aug_assig():
    """
    set x 1
    op add __pyc_tmp_2 1 2
    op mul __pyc_tmp_1 __pyc_tmp_2 3
    op add x x __pyc_tmp_1
    """
    x = 1
    x += (1 + 2) * 3


@masm_test
def test_if():
    """
    set x 1
    jump 4 equal x 0
    set y 1
    set z 1
    """
    x = 1
    if x:
        y = 1
    z = 1


@masm_test
def test_complex_if():
    """
    set x 1
    jump 4 greaterThanEq x 10
    set y 1
    """
    x = 1
    if x < 10:
        y = 1


@masm_test
def test_if_else():
    """
    set x 1
    jump 5 equal x 0
    set y 1
    jump 6 always
    set y 0
    set z 1
    """
    x = 1
    if x:
        y = 1
    else:
        y = 0
    z = 1


@masm_test
def test_if_elif_else():
    """
    set x 1
    jump 5 notEqual x 0
    set y 1
    jump 9 always
    jump 8 notEqual x 1
    set y 2
    jump 9 always
    set y 3
    """
    x = 1
    if x == 0:
        y = 1
    elif x == 1:
        y = 2
    else:
        y = 3


@masm_test
def test_while():
    """
    set x 10
    jump 5 equal x 0
    op sub x x 1
    jump 3 notEqual x 0
    set z 1
    """
    x = 10
    while x:
        x = x - 1
    z = 1


@masm_test
def test_for_end():
    """
    set x 0
    jump 6 greaterThanEq x 10
    op add y x x
    op add x x 1
    jump 2 always
    set z 1
    """
    for x in range(10):
        y = x + x
    z = 1


@masm_test
def test_for_start_end():
    """
    set x 5
    jump 6 greaterThanEq x 10
    op add y x x
    op add x x 1
    jump 2 always
    """
    for x in range(5, 10):
        y = x + x


@masm_test
def test_for_start_end_step():
    """
    set x 0
    jump 6 greaterThanEq x 10
    op add y x x
    op add x x 3
    jump 2 always
    """
    for x in range(0, 10, 3):
        y = x + x


@masm_test
def test_for_negative():
    """
    set x 10
    jump 6 lessThanEq x 0
    op add y x x
    op add x x -1
    jump 2 always
    """
    for x in range(10, 0, -1):
        y = x + x


@masm_test
def test_def():
    # TODO cells can't store strings, test that no fn args are
    """
    jump 12 always
    read __pyc_rc_0 cell1 __pyc_sp
    op sub __pyc_sp __pyc_sp 1
    read n cell1 __pyc_sp
    jump 9 greaterThanEq n 10
    set __pyc_ret true
    jump 11 always
    jump 11 always
    set __pyc_ret false
    jump 11 always
    op add @counter __pyc_rc_0 1
    write 5 cell1 __pyc_sp
    op add __pyc_sp __pyc_sp 1
    write @counter cell1 __pyc_sp
    jump 2 always
    set a __pyc_ret
    write 15 cell1 __pyc_sp
    op add __pyc_sp __pyc_sp 1
    write @counter cell1 __pyc_sp
    jump 2 always
    set b __pyc_ret
    print "5 small? "
    print a
    print ", 15 small? "
    print b
    printflush message1
    """

    def small(n):
        if n < 10:
            return True
        else:
            return False

    a = small(5)
    b = small(15)
    print(f"5 small? {a}, 15 small? {b}")


@masm_test
def test_multi_call():
    """
    jump 8 always
    read __pyc_rc_0 cell1 __pyc_sp
    op sub __pyc_sp __pyc_sp 1
    read i cell1 __pyc_sp
    set __pyc_ret i
    jump 7 always
    op add @counter __pyc_rc_0 1
    write 1 cell1 __pyc_sp
    op add __pyc_sp __pyc_sp 1
    write @counter cell1 __pyc_sp
    jump 2 always
    set __pyc_tmp_2 __pyc_ret
    write 2 cell1 __pyc_sp
    op add __pyc_sp __pyc_sp 1
    write @counter cell1 __pyc_sp
    jump 2 always
    set __pyc_tmp_4 __pyc_ret
    op add x __pyc_tmp_2 __pyc_tmp_4
    """

    def f(i):
        return i

    x = f(1) + f(2)


@masm_test
def test_complex_call():
    """
    jump 8 always
    read __pyc_rc_0 cell1 __pyc_sp
    op sub __pyc_sp __pyc_sp 1
    read i cell1 __pyc_sp
    set __pyc_ret i
    jump 7 always
    op add @counter __pyc_rc_0 1
    op add __pyc_tmp_5 2 3
    write __pyc_tmp_5 cell1 __pyc_sp
    op add __pyc_sp __pyc_sp 1
    write @counter cell1 __pyc_sp
    jump 2 always
    set __pyc_tmp_4 __pyc_ret
    op mul __pyc_tmp_2 1 __pyc_tmp_4
    op add x __pyc_tmp_2 4
    """

    def f(i):
        return i

    x = 1 * f(2 + 3) + 4


@masm_test
def test_def_sideeffects():
    # TODO detect this unnecessary use of __pyc_tmp_3 and optimize it away
    """
    jump 6 always
    read __pyc_rc_0 cell1 __pyc_sp
    print "bar"
    printflush message1
    op add @counter __pyc_rc_0 1
    write @counter cell1 __pyc_sp
    jump 2 always
    set __pyc_tmp_2 __pyc_ret
    """

    def foo():
        print("bar")

    foo()


@masm_test
def test_def_call_as_call_arg():
    # TODO detect this unnecessary use of __pyc_tmp_3 and optimize it away
    """
    jump 9 always
    read __pyc_rc_0 cell1 __pyc_sp
    op sub __pyc_sp __pyc_sp 1
    read n cell1 __pyc_sp
    op pow n n 2
    set __pyc_ret n
    jump 8 always
    op add @counter __pyc_rc_0 1
    write 2 cell1 __pyc_sp
    op add __pyc_sp __pyc_sp 1
    write @counter cell1 __pyc_sp
    jump 2 always
    set __pyc_tmp_3 __pyc_ret
    write __pyc_tmp_3 cell1 __pyc_sp
    op add __pyc_sp __pyc_sp 1
    write @counter cell1 __pyc_sp
    jump 2 always
    set r __pyc_ret
    """

    def square(n):
        n **= 2
        return n

    r = square(square(2))


@masm_test
def test_print():
    """
    set x 1
    set y 2
    print "showing variables:"
    printflush message1
    print "x = "
    print x
    print ", y = "
    print y
    printflush message1
    """
    x = 1
    y = 2
    print("showing variables:")
    print(f"x = {x}, y = ", flush=False)
    print(y, flush=message1)


@masm_test
def test_env():
    """
    set cop @copper
    set this @this
    set x @thisx
    set y @thisy
    set pc @counter
    set links @links
    set time @time
    set width @mapw
    set height @maph
    set __pyc_it_28_16 0
    jump 15 greaterThanEq __pyc_it_28_16 @links
    getlink link __pyc_it_28_16
    op add __pyc_it_28_16 __pyc_it_28_16 1
    jump 11 always
    """
    cop = Env.copper
    this = Env.this
    x = Env.x
    y = Env.y
    pc = Env.counter
    links = Env.link_count
    time = Env.time
    width = Env.width
    height = Env.height
    for link in Env.links():
        pass


@masm_test
def test_sensor():
    """
    sensor pf container1 @phase-fabric
    """
    pf = container1.phase_fabric


@masm_test
def test_sensor_subscript():
    """
    set dyn @copper
    sensor co container2 dyn
    sensor ab a_b @lead
    sensor cd container3 @c_d
    sensor ef e_f @g_h
    """
    dyn = Env.copper
    co = container2[dyn]
    ab = "a_b"[Env.lead]
    cd = container3["c_d"]
    ef = "e_f"["g_h"]


@masm_test
def test_sensor_special_names():
    """
    sensor __pyc_tmp_1 duo1 @health
    sensor __pyc_tmp_2 duo1 @maxHealth
    op div health __pyc_tmp_1 __pyc_tmp_2
    """
    health = duo1.health / duo1.max_health


@masm_test
def test_radar():
    """
    uradar enemy flying any distance @unit 0 u1
    radar ally any any health ripple1 1 u2
    """
    u1 = Unit.radar(enemy, flying, order=max, key=distance)
    u2 = ripple1.radar(ally, key=health)


@masm_test
def test_draw():
    """
    draw clear 255 0 0
    draw color 0 255 255 255
    draw stroke 2
    draw line 0 0 80 80
    draw rect 0 0 20 20
    draw lineRect 0 0 40 40
    draw poly 60 60 3 10 0
    draw linePoly 60 60 5 20 0
    draw triangle 70 80 80 80 80 70
    drawflush display1
    """
    Screen.clear(255, 0, 0)
    Screen.color(0, 255, 255)
    Screen.stroke(2)
    Screen.line(0, 0, 80, 80)
    Screen.rect(0, 0, 20, 20)
    Screen.hollow_rect(0, 0, 40, 40)
    Screen.poly(60, 60, 10, 3)
    Screen.hollow_poly(60, 60, 20, 5)
    Screen.triangle(70, 80, 80, 80, 80, 70)
    Screen.flush()


@masm_test
def test_control():
    """
    control enabled reactor false
    control shoot duo1 10 20 1
    control shoot scatter1 0 0 0
    """
    reactor.enabled(False)
    duo1.shoot(10, 20)
    scatter1.ceasefire()


@masm_test
def test_memory():
    """
    set dst 2
    read value cell1 1
    write value cell1 dst
    """
    dst = 2
    value = cell1.read(1)
    cell1.write(dst, value)

    # If the read result is written to nowhere, it's a no-op, so not emitted.
    cell1.read(0)
