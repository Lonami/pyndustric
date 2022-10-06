# Contributing to pyndustric

First of all, thank you for considering to contribute!

Contributions, in the form of [praise], [issues], suggestions, or [pull requests] are all welcome!
If you want to contribute code but worry that the pull request won't be merged, open an issue
instead to gather some feedback and get the green light beforehand.

## Getting the code

If you just want to download the code, the easiest thing is to download the project's `master`
branch zipped from https://github.com/Lonami/pyndustric/archive/master.zip.

If you plan on contributing to the main repository or just want to hack on the code by yourself,
it's recommended that you fork the project and clone that repository to work on it instead.

When you install the module with pip (if you go that route opposed to running from within project folder), it is recommended to pass `-e` flag to pip:
```sh
$ git clone https://github.com/<path_to_your_fork>
$ pip install -e pyndustric
```

## Understanding the code

The compiler itself lives in the `pyndustric/` directory. It makes use of the constants defined
in `constants.py` for things like errors, special variable names, or other mappings (dictionaries)
like converting a node into a mlog instruction.

This code uses Python's standard [`ast`] module. It's used to parse Python code into an Abstract
Syntax Tree, which is a representation of Python code that is much easier to work with. Instead
of parsing keywords, names and constants, `ast` gives us nodes representing these with a
well-defined structure.

Because we're dealing with Python code here, the [`inspect`] module is used to introspect certain
properties of these objects.

Python 3.6 features like [`dataclasses`] are used to simplify representing [PODs], like
functions for which we need to remember their starting line and other stuff.

The `Compiler` is a `NodeVisitor`, which enables it to visit the entire AST from top to bottom in
a very convenient way. As nodes get visited, like expressions, they get transformed into mlog,
and these instructions are stored.

After the process is completed, all the instructions are formatted into a valid mlog program,
ready to run in Mindustry's logic processors.

If you ever wonder how a Python expression will get converted into AST, you can use the following
snippet in a Python REPL to try it out (the `indent` parameter is Python 3.9 only):

```python
expr = '''
x = 1
y = x + 2
'''

import ast
print(ast.dump(ast.parse(expr), indent=4))
```

## Sending a Pull Request

Before sending a pull request, you need some new or changed code that you want to add:

* Fork the repository.
* Clone your fork.
* Run `pip install -r dev-requirements.txt` to install the dependencies.
* Make the changes.
* Commit the changes.
* Push your changes.
* Send a pull request from GitHub's UI.

Before your pull request can be merged into the main repository, it will be reviewed. In
particular, make sure it meets all of the following criteria for a much higher chance to have it
merged:

* Make sure the commits are as small and self-contained as possible. Try to keep a single pull
  request for a specific change. Different changes should belong in different pull requests.
* Code style must be formatted with [*Black*]. This ensures the codebase style remains consistent,
  and differences in opinion won't matter because *Black* forces a certain style. You can run a
  different formatter to develop locally, but the style should be reverted back with this tool
  before the pull request can be merged.
* Try to follow consistent naming with the rest of the codebase. For example, use `snake_case` for
  methods and variables, not `camelCase`,
* If you're changing stuff, make sure there's a test for it in the file `test_all.py`. You can
  run the tests by running `pytest` from the project's root.
* Please avoid excessive comments. They should be used sparingly when the behaviour is not obvious
  from reading the code.
* Please avoid documenting external modules. This documentation is better suited in the respective
  modules, or a quick introduction can be included in this file if you feel it's necessary.

If your changes don't make it, don't be upset! You can keep them in your fork and develop it on
your own to suit your needs.

If your changes make it, congratulations! You're now part of pyndustric's git history.

[praise]: https://github.com/Lonami/pyndustric/issues/1
[issues]: https://github.com/Lonami/pyndustric/issues
[pull requests]: https://github.com/Lonami/pyndustric/pulls
[`ast`]: https://docs.python.org/3/library/ast.html
[`inspect`]: https://docs.python.org/3/library/inspect.html
[`dataclasses`]: https://docs.python.org/3/library/dataclasses.html
[PODs]: https://en.wikipedia.org/wiki/Passive_data_structure
[*Black*]: https://pypi.org/project/black/
