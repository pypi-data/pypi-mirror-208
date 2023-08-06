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
    name='bool-to-int8-ray',
    version=get_version("bool_to_int8_ray/__init__.py"),
    description='bool to int8 serialization with ray.io',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='http://github.com/satzbeleg/bool-to-int8-ray',
    author='Ulf Hamster',
    author_email='554c46@gmail.com',
    license='Apache License 2.0',
    packages=['bool_to_int8_ray'],
    install_requires=[
        "numpy>=1.19.5,<2",
        "ray>=2,<3",
        "psutil>=5"
    ],
    python_requires='>=3.7',
    zip_safe=True
)
