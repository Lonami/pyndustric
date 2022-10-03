from distutils.core import setup

def load_version():
    with open('pyndustric/version.py', 'r', encoding='utf-8') as f:
        g, l = {}, {}
        # This exec is fine. The installed program would execute this exact file once imported anyway.
        # A regex or other hand-rolled parsed would be error-prone and silly just to avoid the exec.
        exec(f.read(), g, l)
    return l['__version__']

setup(name='pyndustric', version=load_version(), packages=['pyndustric'])
