# Tutorial https://python-packaging.readthedocs.io/en/latest/minimal.html
# Example https://github.com/OneGov/onegov.search

#from setuptools import setup, find_packages
from setuptools import setup

setup(
    name='mreschke-serverbackups',
    version='1.0.0',
    description='Server Backups that feel like a single backups.py script',
    long_description='',


    author='Matthew Reschke',
    author_email='mail@mreschke.com',
    license='MIT',
    url='http://github.com/mreschke/serverbackups',

    # I am using "Native namespaces" see https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages
    packages=['mreschke.serverbackups'],
    zip_safe=False,
    python_requires='>=3.7',
    install_requires=[
        'click'
    ],
    entry_points={
        'console_scripts': [
            'serverbackups=mreschke.serverbackups.commands:cli'
        ],
    },
)
