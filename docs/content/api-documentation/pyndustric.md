<a id="pyndustric"></a>

# pyndustric

<a id="pyndustric.constants"></a>

# pyndustric.constants

<a id="pyndustric.compiler"></a>

# pyndustric.compiler

<a id="pyndustric.compiler.Function"></a>

## Function Objects

```python
@dataclass
class Function()
```

Stores information about a user-defined functions which are callable within a compilable program.

<a id="pyndustric.compiler.Function.start"></a>

#### start

label pointing to the function's prologue

<a id="pyndustric.compiler.Function.argc"></a>

#### argc

count of number of arguments the function takes

<a id="pyndustric.compiler.Compiler"></a>

## Compiler Objects

```python
class Compiler(ast.NodeVisitor)
```

<a id="pyndustric.compiler.Compiler.visit_While"></a>

#### visit\_While

```python
def visit_While(node)
```

This will be called for any* while loop.

<a id="pyndustric.compiler.Compiler.as_value"></a>

#### as\_value

```python
def as_value(node, output: str = None)
```

Returns the string representing either a value (like a number) or a variable.

If a temporary variable needs to be created, it will be called `output`.
If `output` is not set, it will be a random name.

<a id="pyndustric.__main__"></a>

# pyndustric.\_\_main\_\_

<a id="pyndustric.version"></a>

# pyndustric.version

