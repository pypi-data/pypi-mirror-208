from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pyHC128',
    version='1.0.2',
    description="pyHC128 is a Python package for the HC-128 stream cipher. It uses a 128-bit key and IV to generate a keystream.",
    py_modules=['hc128'],
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
