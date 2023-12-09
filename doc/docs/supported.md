# Supported Features

## Basic operations and logic

### Assignment and all operators

```python
x = 10
y = x ** 2
y -= 2.5
z = x < y > (4 if x < 2 else 6)
```

### If-elif-else blocks

```python
if battery_level < 33:
    Screen.clear(255, 0, 0)
elif battery_level < 66:
    Screen.clear(127, 127, 0)
else:
    Screen.clear(0, 255, 0)
```

### While and for-loops

```python
for y in range(80):
    x = 80
    while x > 0:
        x -= 1
```

### Built-in functions to print messages

[f-string](https://docs.python.org/3/reference/lexical_analysis.html#f-strings) support

```python
var = 42
print(f'The Answer: {var}')
```

## Mindustry operations

### Screen drawing

Tree:

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

### Enviornment

`Env.<property>` for enviornment variables, like counter or time

```python
counter = Env.counter
current_time = Env.time
```

Compiles to:

```mlog
set counter @counter
set current_time @time
```

Beyond the ones defined in `pyndustri.pyi`, there is also a way to write Mindustry built-in variables and constants (those that start with @, like `@titanium`).

If written as string literals, compiled result will be a string, not a variable. For example:

```python
titanium = @titanium  # compile error
titanium = "@titanium"  # set titanium "@titanium"
titanium = Env.titanium  # set titanium @titanium
```

#### Links

Easy way to loop through links:

```python
for switch in Env.links():
    switch.enabled(not switch.enabled)
```

### Sensors

```python
copper = container1.copper
need_resources = copper == 0  # we're out of copper!

health = duo1.health / duo1.max_health
need_healing = health < 0.5  # less than 50% health!
```

### Control

Built-in functions to tell things what to do, like disabling them or shooting:

```python
for reactor in Env.links():
    safe = reactor.heat == 0
    reactor.enabled(safe)  # turn off all reactors with non-zero heat
```

### Units

```python
Unit.bind('alpha')
print(Unit.x + Unit.y)

enemy_unit = Unit.radar(enemy, flying, order=max, key=distance)
Unit.move(100, 200)

if Unit.within(100, 200, 10):
    Unit.shoot(100, 200)
    Unit.flag = 1
```

### Memory cells

```python
Mem.cell1[0] = 1
Mem.cell1[1] = 1

for i in range(2, 64):
    Mem.cell1[i] = Mem.cell1[i - 2] + Mem.cell1[i - 1]

# cell1 now has the Fibonacci sequence! (the first few numbers, at least)
print(Mem.cell1[63])
```

### Functions

!!! info
    If you are using function calls, *pyndustric* will use `cell1` as a call stack, so you might not want to use `cell1` in that case to store data in it. (If you aren't calling any functions in your code, using `cell1` should be fine.)

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

!!! warning
    As of steam build 122.1, the processor state is not reset even if you import new code,
    so functions which rely on a special stack pointer variable may behave strange if you import new
    code. To fix this import empty code (which clears the instruction pointer) and then import the
    real code, or upgrade your Mindustry version. [Original bug report](https://github.com/Anuken/Mindustry/issues/4189).
