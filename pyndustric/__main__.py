import pyndustric
import sys
import time


def main():
    for file in sys.argv[1:]:
        print(f'# reading {file}...', file=sys.stderr)
        if file == '-':
            source = sys.stdin.read()
        else:
            with open(file, encoding='utf-8') as fd:
                source = fd.read()

        print(f'# compiling {file}...', file=sys.stderr)
        start = time.time()
        masm = pyndustric.Compiler().compile(source)
        took = time.time() - start
        print(masm)
        print(f'# compiled {file} with pyndustric {pyndustric.__version__} in {took:.2f}s',
              file=sys.stderr)


if __name__ == '__main__':
    main()
