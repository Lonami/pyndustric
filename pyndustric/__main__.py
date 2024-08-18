import argparse

import pyndustric
import sys
import time
import inspect


def create_args():
    parser = argparse.ArgumentParser(
        description="A compiler from Python to Mindustry's assembly (logic programming language)."
    )

    parser.add_argument("files", action="store", nargs="+", type=str, help="source files to compile")
    parser.add_argument(
        "-i",
        "--inline",
        action="store_true",
        help="inline all the functions (copy/paste them, instead of treating them like functions)",
    )
    parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="copy the generated code to clipboard (requires `autoit`)",
    )

    return parser


def main():
    parser = create_args()
    args = parser.parse_args()
    complete_masm = ""
    for file in args.files:
        print(f"# reading {file}...", file=sys.stderr)
        if file == "-":
            source = sys.stdin.read()
        else:
            with open(file, encoding="utf-8") as fd:
                source = fd.read()

        print(f"# compiling {file}...", file=sys.stderr)
        start = time.time()
        try:
            masm = pyndustric.Compiler().compile(source, inline=args.inline)
        except pyndustric.CompilerError as e:
            trace = inspect.trace()[-1]
            print(f"[{trace.lineno}@{trace.function}]{str(e)}")

            sys.exit(1)
        complete_masm += masm
        took = time.time() - start
        print(masm)
        print(
            f"# compiled {file} with pyndustric {pyndustric.__version__} in {took:.2f}s",
            file=sys.stderr,
        )

    if args.clipboard:
        import pyperclip

        pyperclip.copy(complete_masm)


if __name__ == "__main__":
    main()
