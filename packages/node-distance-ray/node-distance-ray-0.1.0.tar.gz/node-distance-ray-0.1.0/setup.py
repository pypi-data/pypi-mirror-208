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
    name='node-distance-ray',
    version=get_version("node_distance_ray/__init__.py"),
    description='ray.io wrapper for node-distance package',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='http://github.com/satzbeleg/node-distance-ray',
    author='Ulf Hamster',
    author_email='554c46@gmail.com',
    license='Apache License 2.0',
    packages=['node_distance_ray'],
    install_requires=[
        "node-distance>=0.1.0,<1",
        "ray>=2,<3",
        "psutil>=5"
    ],
    # scripts=['scripts/examplescript.py'],
    python_requires='>=3.6',
    zip_safe=True
)
