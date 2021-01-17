import pathlib
import pyndustric
import pytest
import sys
import tempfile
import textwrap


def as_masm(source):
    return "set __pyc_sp 0\n" + textwrap.dedent(source).strip() + "\nend\n"


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
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_COMPLEX_ASSIGN):
        pyndustric.Compiler().compile("a, b = c = 1, 2")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_COMPLEX_ASSIGN):
        pyndustric.Compiler().compile("a.b = 1")


def test_err_complex_value():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_COMPLEX_VALUE):
        pyndustric.Compiler().compile("a = 1 + 2j")


def test_err_unsupported_op():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_OP):
        pyndustric.Compiler().compile("a = m0 @ m1")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_OP):
        pyndustric.Compiler().compile("a @= m")


def test_err_unsupported_iter():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_ITER):
        pyndustric.Compiler().compile("for x in [1, 2]: pass")


def test_err_bad_iter_args():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_ITER_ARGS):
        pyndustric.Compiler().compile("for x in range(): pass")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_ITER_ARGS):
        pyndustric.Compiler().compile("for x in range(1, 2, 3, 4): pass")


def test_err_unsupported_import():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_IMPORT):
        pyndustric.Compiler().compile("from math import log")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_IMPORT):
        pyndustric.Compiler().compile("import pyndustri")


def test_err_unsupported_expr():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_EXPR):
        pyndustric.Compiler().compile("1 + (2 + 3)")


def test_err_unsupported_syscall():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_SYSCALL):
        pyndustric.Compiler().compile("Missing.method()")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_SYSCALL):
        pyndustric.Compiler().compile("Screen.missing()")


def test_err_bad_syscall_args():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_SYSCALL_ARGS):
        pyndustric.Compiler().compile("Screen.clear(1)")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_SYSCALL_ARGS):
        pyndustric.Compiler().compile("Screen.clear(1, 2, 3, 4)")


def test_err_nested_def():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_NESTED_DEF):
        pyndustric.Compiler().compile("def foo():\n  def bar():\n    pass")


def test_err_invalid_def():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_INVALID_DEF):
        pyndustric.Compiler().compile("def foo(a=None): pass")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_INVALID_DEF):
        pyndustric.Compiler().compile("def foo(*, a): pass")

    if sys.version_info >= (3, 8):
        with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_INVALID_DEF):
            pyndustric.Compiler().compile("def foo(a, /, b): pass")


def test_err_redef():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_REDEF):
        pyndustric.Compiler().compile("def foo(): pass\ndef foo(): pass")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_REDEF):
        pyndustric.Compiler().compile("def print(): pass")


def test_err_no_def():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_NO_DEF):
        pyndustric.Compiler().compile("x = foo()")


def test_err_argc_mismatch():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_ARGC_MISMATCH):
        pyndustric.Compiler().compile("def foo(n): pass\nx = foo()")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_ARGC_MISMATCH):
        pyndustric.Compiler().compile("def foo(n): pass\nx = foo(1, 2)")


def test_err_too_long():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_TOO_LONG):
        pyndustric.Compiler().compile("x = 1\n" * (1 + pyndustric.MAX_INSTRUCTIONS))


def test_err_bad_tuple():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_EXPR):
        pyndustric.Compiler().compile("x = 1, 2")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_TUPLE_ASSIGN):
        pyndustric.Compiler().compile("x, y = 1")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_TUPLE_ASSIGN):
        pyndustric.Compiler().compile("x, y = foo()")

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_TUPLE_ASSIGN):
        pyndustric.Compiler().compile("x, y = a, b, c")


def test_no_compile_method():
    class Foo:
        def bar(self):
            pass

    foo = Foo()

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_INVALID_SOURCE):
        pyndustric.Compiler().compile(foo.bar)


def test_compile_string():
    masm = pyndustric.Compiler().compile("x = 1")


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


def test_assignments():
    source = textwrap.dedent(
        """\
        x = 1
        y = x + 2
        z = x == y
        """
    )

    expected = as_masm(
        """\
        set x 1
        op add y x 2
        op equal z x y
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_multi_assignment():
    def source():
        x = y = z = 0
        a, b = 1, 2

    expected = as_masm(
        """\
        set x 0
        set y x
        set z x
        set a 1
        set b 2
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_types():
    source = textwrap.dedent(
        """\
        x = True
        y = 1
        z = 0.1
        a = "string"
        """
    )

    expected = as_masm(
        """\
        set x true
        set y 1
        set z 0.1
        set a "string"
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_builtin_defs():
    def source():
        a = abs(1)
        lo = min(1, 2)

    expected = as_masm(
        """\
        op abs a 1
        op min lo 1 2
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_complex_assign():
    def source():
        a = 2 * x + 1
        d = sqrt(x * x + y * y)

    expected = as_masm(
        """\
        op mul __pyc_tmp_1 2 x
        op add a __pyc_tmp_1 1
        op mul __pyc_tmp_6 x x
        op mul __pyc_tmp_9 y y
        op add __pyc_tmp_5 __pyc_tmp_6 __pyc_tmp_9
        op sqrt d __pyc_tmp_5
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_aug_assignments():
    source = textwrap.dedent(
        """\
        x = 1
        x += 1
        """
    )

    expected = as_masm(
        """\
        set x 1
        op add x x 1
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_complex_aug_assig():
    source = textwrap.dedent(
        """\
        x = 1
        x += (1 + 2) * 3
        """
    )

    expected = as_masm(
        """\
        set x 1
        op add __pyc_tmp_2 1 2
        op mul __pyc_tmp_1 __pyc_tmp_2 3
        op add x x __pyc_tmp_1
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_if():
    source = textwrap.dedent(
        """\
        x = 1
        if x:
            y = 1
        z = 1
        """
    )

    # TODO negate initial jmp condition with no else
    expected = as_masm(
        """\
        set x 1
        jump 4 equal x 0
        set y 1
        set z 1
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_complex_if():
    source = textwrap.dedent(
        """\
        x = 1
        if x < 10:
            y = 1
        """
    )

    expected = as_masm(
        """\
        set x 1
        jump 4 greaterThanEq x 10
        set y 1
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_if_else():
    source = textwrap.dedent(
        """\
        x = 1
        if x:
            y = 1
        else:
            y = 0
        z = 1
        """
    )

    expected = as_masm(
        """\
        set x 1
        jump 5 equal x 0
        set y 1
        jump 6 always
        set y 0
        set z 1
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_if_elif_else():
    source = textwrap.dedent(
        """\
        x = 1
        if x == 0:
            y = 1
        elif x == 1:
            y = 2
        else:
            y = 3
        """
    )

    expected = as_masm(
        """\
        set x 1
        jump 5 notEqual x 0
        set y 1
        jump 9 always
        jump 8 notEqual x 1
        set y 2
        jump 9 always
        set y 3
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_while():
    source = textwrap.dedent(
        """\
        x = 10
        while x:
            x = x - 1
        z = 1
        """
    )

    expected = as_masm(
        """\
        set x 10
        jump 5 equal x 0
        op sub x x 1
        jump 3 notEqual x 0
        set z 1
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_for():
    source = textwrap.dedent(
        """\
        for x in range(10):
            y = x + x
        z = 1
        """
    )

    expected = as_masm(
        """\
        set x 0
        jump 6 greaterThanEq x 10
        op add y x x
        op add x x 1
        jump 2 always
        set z 1
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected

    source = textwrap.dedent(
        """\
        for x in range(5, 10):
            y = x + x
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert "set x 5" in masm

    source = textwrap.dedent(
        """\
        for x in range(0, 10, 3):
            y = x + x
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert "op add x x 3" in masm


def test_def():
    # TODO cells can't store strings, test that no fn args are
    # TODO standalone calls are not supported
    source = textwrap.dedent(
        """\
        def small(n):
            if n < 10:
                return True
            else:
                return False

        a = small(5)
        b = small(15)
        print(f'5 small? {a}, 15 small? {b}')
        """
    )

    expected = as_masm(
        """\
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
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_multi_call():
    def source():
        def f(i):
            return i

        x = f(1) + f(2)

    expected = as_masm(
        """\
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
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_complex_call():
    def source():
        def f(i):
            return i

        x = 1 * f(2 + 3) + 4

    expected = as_masm(
        """\
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
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_def_sideeffects():
    source = textwrap.dedent(
        """\
        def foo():
            print('bar')

        foo()
        """
    )

    # TODO detect this unnecessary use of __pyc_tmp_3 and optimize it away
    expected = as_masm(
        """\
        jump 6 always
        read __pyc_rc_0 cell1 __pyc_sp
        print "bar"
        printflush message1
        op add @counter __pyc_rc_0 1
        write @counter cell1 __pyc_sp
        jump 2 always
        set __pyc_tmp_2 __pyc_ret
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_def_call_as_call_arg():
    source = textwrap.dedent(
        """\
        def square(n):
            n **= 2
            return n

        r = square(square(2))
        """
    )

    # TODO detect this unnecessary use of __pyc_tmp_3 and optimize it away
    expected = as_masm(
        """\
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
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_print():
    source = textwrap.dedent(
        """\
        x = 1
        y = 2
        print("showing variables:")
        print(f"x = {x}, y = ", flush=False)
        print(y, flush=message1)
        """
    )

    expected = as_masm(
        """\
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
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_env():
    source = textwrap.dedent(
        """\
        this = Env.this()
        x = Env.x()
        y = Env.y()
        pc = Env.counter()
        links = Env.link_count()
        time = Env.time()
        width = Env.width()
        height = Env.height()

        for link in Env.links():
            pass
        """
    )

    expected = as_masm(
        """\
        set this @this
        set x @thisx
        set y @thisy
        set pc @counter
        set links @links
        set time @time
        set width @mapw
        set height @maph
        set __pyc_it_10_12 0
        jump 14 greaterThanEq __pyc_it_10_12 @links
        getlink link __pyc_it_10_12
        op add __pyc_it_10_12 __pyc_it_10_12 1
        jump 10 always
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_sensor():
    source = textwrap.dedent(
        """\
        pf = Sensor.phase_fabric(container1)
        """
    )

    expected = as_masm(
        """\
        sensor pf container1 @phase-fabric
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_object_attribute():
    def source(container1):
        pf = container1.phase_fabric

    expected = as_masm(
        """\
        sensor pf container1 @phase-fabric
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_radar():
    def source(ripple1):
        u1 = Unit.radar(enemy, flying, order=max, key=distance)
        u2 = ripple1.radar(ally, key=health)

    expected = as_masm(
        """\
        uradar enemy flying any distance @unit 0 u1
        radar ally any any health ripple1 1 u2
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_radar_too_many():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_ARGC_MISMATCH):
        pyndustric.Compiler().compile("u = Unit.radar(enemy, flying, ally, any)")


def test_draw():
    source = textwrap.dedent(
        """\
        from pyndustri import *

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
        """
    )

    expected = as_masm(
        """\
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
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_control():
    source = textwrap.dedent(
        """\
        Control.enabled(reactor, False)
        Control.shoot(duo1, 10, 20)
        Control.ceasefire(scatter1)
        """
    )

    expected = as_masm(
        """\
        control enabled reactor false
        control shoot duo1 10 20 1
        control shoot scatter1 0 0 0
        """
    )

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected
