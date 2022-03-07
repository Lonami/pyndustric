import argparse

import pyndustric
import sys
import time


def create_args():
    parser = argparse.ArgumentParser(
        description="A compiler from Python to Mindustry's assembly (logic programming language)."
    )

    parser.add_argument("files", action="store", nargs="+", type=str, help="source files to compile")
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
        masm = pyndustric.Compiler().compile(source)
        complete_masm += masm
        took = time.time() - start
        print(masm)
        print(
            f"# compiled {file} with pyndustric {pyndustric.__version__} in {took:.2f}s",
            file=sys.stderr,
        )

        if args.clipboard:
                import ait
                ait.copy(complete_masm)

if __name__ == "__main__":
    main()
