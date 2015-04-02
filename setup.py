from setuptools import setup

setup(
    name = 'tup-export',
    version = '0.0.1',
    author = 'Rendaw',
    author_email = 'spoo@zarbosoft.com',
    url = 'https://github.com/Rendaw/tup-export',
    download_url = 'https://github.com/Rendaw/tup-export/tarball/v0.0.1',
    license = 'BSD',
    description = 'Creates a dumb build script from a tup project.',
    long_description = open('readme.md', 'r').read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
    ],
    py_modules = ['tup-export'],
    entry_points = {
        'console_scripts': [
            'tup-export = tup-export:main',
        ],
    },
)
