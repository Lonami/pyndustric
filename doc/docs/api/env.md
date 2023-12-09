# Environmental variables

Accesed to as `Env.property`

## this

Returns the (`Building`)[] object of the processor running the code

```python
thisproc = Env.this # Set to the current processor
```

```mlog
set thisproc @this
```

## `x` and `y`

Return the respective `x` or `y` coordinate of [`this`](#this)

```python
x = Env.x
y = Env.y
```

```mlog
set x @thisx
set y @thisy
```

## counter

Return the Program Counter. Represents the index of the **next** instruction.

```python
pc = Env.counter
```

```mlog
set pc @counter
```

## links()

Used in a for loop to iterate over links

```python
for link in Env.links():
    # Do something
```

## link_count

Number of links

```python
links = Env.link_count
```

```mlog
set links @links
```

## time

Returns the UNIX timestamp of the current time, in ms

```python
links = Env.time
```

```mlog
set links @time
```

## `width` and `height`

Width and height of the map, respectively

```python
links = Env.width
height = Env.height
```

```mlog
set width @width
set height @height
```

## ips

Instructions Per Seconds of the current processor

## Arbitary variables

Other variables like `@titanium`

```python
titanium = Env.titanium
tit_conv = Env.titanium_conveyor
```

```mlog
set titanium @titanium
set tit_conv @titanium-conveyor
```
