from setuptools import setup, find_packages

setup(
    name='hearthstone_lab10',
    version='0.1',
    packages=find_packages(),
    author='Mikołaj Pastuszek',
    description='lab10 hearthstone',
    long_description=open('README.md').read(),
    install_requires=['enum', 'requests', 'typing']
)
