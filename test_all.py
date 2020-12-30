import pyndustric
import pytest
import textwrap


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
