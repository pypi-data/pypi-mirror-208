from setuptools import setup, find_packages

setup(
    name='pyrc-test-python-package',
    version='0.0.6',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    url='',
    license='',
    author='Paul Vienneau',
    author_email='',
    description='Test python package to better understand packaging',
    install_requires=[],
)
