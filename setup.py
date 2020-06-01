from setuptools import setup

# Tutorial https://python-packaging.readthedocs.io/en/latest/minimal.html
# Example https://github.com/OneGov/onegov.search

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='mreschke-serverbackups',
    version='1.0.0',
    description='Complex full server backups that feel like a single backups.py script',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Matthew Reschke',
    author_email='mail@mreschke.com',
    license='MIT',
    url='http://github.com/mreschke/server-backups',

    # I am using "Native namespaces" see https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages
    packages=['mreschke.serverbackups'],
    zip_safe=False,
    python_requires='>=3.7',
    install_requires=[
        'click==7.1.*',
        'prettyprinter==0.18.*',
        'pyyaml==5.3.*',
        'sarge==0.1.*',
        'sh==1.13.*',
    ],
    entry_points={
        'console_scripts': [
            'serverbackups=mreschke.serverbackups.commands:cli'
        ],
    },
)
