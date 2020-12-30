import pyndustric
import pytest
import textwrap


def test_all_err_have_desc_and_tests():
    error_names = [name for name in dir(pyndustric) if name.startswith('ERR_')]
    error_values = {getattr(pyndustric, name) for name in error_names}

    assert len(error_values) == len(error_names), 'some error constants have duplicate values'
    assert len(error_values) == len(pyndustric.ERROR_DESCRIPTIONS), 'not all errors are documented'

    with open(__file__, encoding='utf-8') as fd:
        source = fd.read()

    for name in error_names:
        assert name in source, 'error is missing a test'


def test_err_multi_assign():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_MULTI_ASSIGN):
        pyndustric.Compiler().compile('a = b = 1')


def test_err_complex_assign():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_COMPLEX_ASSIGN):
        pyndustric.Compiler().compile('a, b = 1, 2')

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_COMPLEX_ASSIGN):
        pyndustric.Compiler().compile('a.b = 1')


def test_err_complex_value():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_COMPLEX_VALUE):
        pyndustric.Compiler().compile('a = 1 + (2 + 3)')


def test_err_unsupported_op():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_OP):
        pyndustric.Compiler().compile('a = m0 @ m1')


def test_err_unsupported_iter():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_ITER):
        pyndustric.Compiler().compile('for x in [1, 2]: pass')


def test_err_bad_iter_args():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_ITER_ARGS):
        pyndustric.Compiler().compile('for x in range(): pass')

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_ITER_ARGS):
        pyndustric.Compiler().compile('for x in range(1, 2, 3, 4): pass')


def test_err_unsupported_import():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_IMPORT):
        pyndustric.Compiler().compile('from math import log')

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_IMPORT):
        pyndustric.Compiler().compile('import pyndustri')


def test_err_unsupported_expr():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_EXPR):
        pyndustric.Compiler().compile('log(10)')


def test_err_unsupported_syscall():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_SYSCALL):
        pyndustric.Compiler().compile('Missing.method()')

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_UNSUPPORTED_SYSCALL):
        pyndustric.Compiler().compile('Screen.missing()')


def test_err_bad_syscall_args():
    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_SYSCALL_ARGS):
        pyndustric.Compiler().compile('Screen.clear(1)')

    with pytest.raises(pyndustric.CompilerError, match=pyndustric.ERR_BAD_SYSCALL_ARGS):
        pyndustric.Compiler().compile('Screen.clear(1, 2, 3, 4)')


def test_assignments():
    source = textwrap.dedent('''\
        x = 1
        z = x + 2
        ''').strip()

    expected = textwrap.dedent('''\
        set x 1
        op add z x 2
        ''').strip()

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_if():
    source = textwrap.dedent('''\
        x = 1
        if x:
            y = 1
        z = 1
        ''').strip()

    # TODO negate initial jmp condition with no else
    expected = textwrap.dedent('''\
        set x 1
        jump 3 notEqual x 0
        jump 4 always
        set y 1
        set z 1
        ''').strip()

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_if_else():
    source = textwrap.dedent('''\
        x = 1
        if x:
            y = 1
        else:
            y = 0
        z = 1
        ''').strip()

    expected = textwrap.dedent('''\
        set x 1
        jump 4 notEqual x 0
        set y 0
        jump 5 always
        set y 1
        set z 1
        ''').strip()

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_while():
    source = textwrap.dedent('''\
        x = 10
        while x:
            x = x - 1
        z = 1
        ''').strip()

    expected = textwrap.dedent('''\
        set x 10
        jump 3 always
        op sub x x 1
        jump 2 notEqual x 0
        set z 1
        ''').strip()

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_for():
    source = textwrap.dedent('''\
        for x in range(10):
            y = x + x
        z = 1
        ''').strip()

    expected = textwrap.dedent('''\
        set x 0
        jump 5 greaterThanEq x 10
        op add y x x
        op add x x 1
        jump 1 always
        set z 1
        ''').strip()

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected


def test_draw():
    source = textwrap.dedent('''\
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
        ''').strip()

    expected = textwrap.dedent('''\
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
        ''').strip()

    masm = pyndustric.Compiler().compile(source)
    assert masm == expected
