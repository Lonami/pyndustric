# pyndustric

A compiler from Python to Mindustry's assembly (logic programming language).

To run the tests, simply use the following command:

```sh
$ pip install -r dev-requirements.txt
$ pytest
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

Built-in properties to access the environment, like time or links:

```python
current_time = Env.time
link_count = Env.link_count
```

Built-in functions to access sensors, like the amount of copper or current health:

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

## Documentation

The language is Python, so all simple programs you can imagine are possible. Beyond that, the
supported "system calls" are documented in the [`pyndustri.pyi`] file.

To learn about the possible compiler errors, refer to the `ERR_` and `ERROR_DESCRIPTIONS`
constants in the [`constants.py`] file.

To install pyndustric as module run:
```sh
$ git clone https://github.com/Lonami/pyndustric.git
$ pip install -e pyndustric
```
To compile your program, run the [`pyndustric`] module and pass the files to compile as input
arguments. The compiled program will be printed to standard output. `-` can be used as a file
to refer to standard input:

```sh
$ python -m pyndustric yourprogram.py
```

## Known limitations

Beware of very long programs, [there is a current limitation of 1000 instructions][limit-k].

Currently only one memory cell is supported, which is used for the call stack.

This program has hardly had any testing, so if you believe your program is misbehaving, there's
a possibility that the compiler has a bug.

## Contributing

Contributors are more than welcome! Maybe you can improve the documentation, add something I
missed, implement support for more Python features, or write a peephole optimizer for the
compiler's output!

[f-string]: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
[ip-not-reset]: https://github.com/Anuken/Mindustry/issues/4189
[limit-k]: https://github.com/Anuken/Mindustry/blob/ab19e6ffbd7a64117cd70d3e3b88806c13822c94/core/src/mindustry/logic/LExecutor.java#L28
[`pyndustri.pyi`]: pyndustri.pyi
[`pyndustric.py`]: pyndustric.py
