import setuptools
import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        s = fp.read()
    return s


def get_version(path):
    with open(path, "r") as fp:
        lines = fp.read()
    for line in lines.split("\n"):
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name='torch-hrp',
    version=get_version("torch_hrp/__init__.py"),
    description='Hashed Random Projection layer for PyTorch',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='http://github.com/satzbeleg/torch-hrp',
    author='Ulf Hamster',
    author_email='554c46@gmail.com',
    license='Apache License 2.0',
    packages=['torch_hrp'],
    install_requires=[
        'torch>=1,<2',
        'numpy>=1.19.5,<2'
    ],
    python_requires='>=3.7',
    zip_safe=True
)
