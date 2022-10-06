# pyndustric

A compiler from Python to Mindustry's assembly (logic programming language).

The language **is** Python, so all simple programs you can imagine are possible.
Check the [supported features][features] to learn what is currently possible.
If you find something is missing, you're welcome to [contribute]!

Beyond that, the supported "system calls" are documented in the [`pyndustri.pyi`] file.

To learn about the possible compiler errors, refer to the `ERR_` and `ERROR_DESCRIPTIONS`
constants in the [`constants.py`] file.

## Getting up and running

To install pyndustric as module run:

```sh
$ pip install https://github.com/Lonami/pyndustric/archive/refs/heads/master.zip
```

Alternatively, you can run it as module without installation by placing your program file at the root of the project directory.
(You can get the source via download button or: `git clone https://github.com/Lonami/pyndustric.git`)


To compile your program, run the [`pyndustric`] module and pass the files to compile as input arguments.
`-` can be used as a file to refer to standard input:

```sh
$ python -m pyndustric yourprogram.py
```

The compiled program will be printed to standard output by default.
You can also redirect the output to a file to create a new file with the compiled program:

```sh
$ python -m pyndustric yourprogram.py > yourprogram.mlog
```

If the optional dependency `autoit` is installed, `-c` or `--clipboard` can be used to
automatically copy the code to the clipboard which allows for very fast edit cycles:

```sh
$ python -m pyndustric -c yourprogram.py
```

## Supported features

Assignment and all operators you know and love:

```python
x = 10
y = x ** 2
y -= 2.5
```

If-elif-else blocks:

```python
if battery_level < 33:
    Screen.clear(255, 0, 0)
elif battery_level < 66:
    Screen.clear(127, 127, 0)
else:
    Screen.clear(0, 255, 0)
```

While and for-loops:

```python
for y in range(80):
    x = 80
    while x > 0:
        x -= 1
```

Built-in functions to print messages, with [f-string] support:

```python
var = 42
print(f'The Answer: {var}')
```

Built-in functions to draw things to a display, like a tree:

```python
# (optional) Get type-hinting in your editor of choice
from pyndustri import *

Screen.clear(80, 150, 255)

Screen.color(50, 200, 50)
Screen.rect(0, 0, 80, 30)

Screen.color(140, 110, 110)
Screen.rect(10, 10, 20, 40)

Screen.color(50, 200, 50)
Screen.poly(20, 50, 20, 100)

Screen.flush()
```

Built-in properties to access the environment, like counter or time:

```python
counter = Env.counter
current_time = Env.time
```

compiles to:

```
set counter @counter
set current_time @time
```

Beyond the ones defined in [`pyndustri.pyi`], this is also the way to write Mindustry built-in variables and constants
(those that start with @). If written as string literals, compiled result will be a string, not a variable. For example:

```python
titanium = "@titanium"  # set titanium "@titanium"
titanium = @titanium  # compile error
titanium = Env.titanium  # set titanium @titanium
```

Built-in properties to access sensors, like the amount of copper or current health:

```python
copper = container1.copper
need_resources = copper == 0  # we're out of copper!

health = duo1.health / duo1.max_health
need_healing = health < 0.5  # less than 50% health!
```

Built-in functions to tell things what to do, like disabling them or shooting:

```python
for reactor in Env.links():
    safe = reactor.heat == 0
    reactor.enabled(safe)  # turn off all reactors with non-zero heat
```

Built-in singleton to bind to units and use them:

```python
Unit.bind('alpha')
print(Unit.x + Unit.y)

enemy_unit = Unit.radar(enemy, flying, order=max, key=distance)
Unit.move(100, 200)

if Unit.within(100, 200, 10):
    Unit.shoot(100, 200)
    Unit.flag = 1
```

Built-in class to access memory:

```python
Mem.cell1[0] = 1
Mem.cell1[1] = 1

for i in range(2, 64):
    Mem.cell1[i] = Mem.cell1[i - 2] + Mem.cell1[i - 1]

# cell1 now has the Fibonacci sequence! (the first few numbers, at least)
print(Mem.cell1[63])
```

> **Note**: if you are using function calls, *pyndustric* will use `cell1` as a call stack, so you might not want to use `cell1` in that case to store data in it. (If you aren't calling any functions in your code, using `cell1` should be fine.)

Custom function definitions:

```python
def is_prime(n):
    for i in range(2, n):
        r = n % i
        if r == 0:
            return False

    return True

p = is_prime(7)
if p:
    print('7 is prime')
else:
    print('7 is not prime???')
```

> **Note**: as of steam build 122.1, the processor state is not reset even if you import new code,
> so functions which rely on a special stack pointer variable may behave strange if you import new
> code. To fix this import empty code (which clears the instruction pointer) and then import the
> real code, or upgrade your Mindustry version. [Original bug report][ip-not-reset].

## Known limitations

Beware of very long programs, [there is a current limitation of 1000 instructions][limit-k].

This program has hardly had any testing, so if you believe your program is misbehaving, there's
a possibility that the compiler has a bug.

## Contributing

Contributors are more than welcome! Maybe you can improve the documentation, add something I
missed, implement support for more Python features, or write a peephole optimizer for the
compiler's output!

More info on contributing can be found in [`CONTRIBUTING.md`]

To run the tests, simply use the following command:

```sh
$ pip install -r dev-requirements.txt
$ pytest
```

[f-string]: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
[ip-not-reset]: https://github.com/Anuken/Mindustry/issues/4189
[limit-k]: https://github.com/Anuken/Mindustry/blob/ab19e6ffbd7a64117cd70d3e3b88806c13822c94/core/src/mindustry/logic/LExecutor.java#L28
[`pyndustri.pyi`]: pyndustri.pyi
[`constants.py`]: pyndustric/constants.py
[`pyndustric`]: pyndustric
[features]: #Supported-features
[contribute]: #Contributing
[`CONTRIBUTING.md`]: CONTRIBUTING.md
