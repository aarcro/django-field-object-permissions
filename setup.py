#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import sys


package = 'fieldobjectpermissions'
install_requires = [
    'Django>=1.7',
    # 'six',  # uncomment when I find stuff that needs six
]


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

# python setup.py register
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r pypi')
    args = {'version': get_version(package)}
    print('You probably want to also tag the version now:')
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print('  git push --tags')
    sys.exit()


setup(
    name='django-field-object-permissions',
    version=get_version(package),
    url='http://github.com/aarcr/django-role-permissions',
    license='MIT',
    description='Provides an object permission system based on field values (eg: object.owner == user)',
    author='Aaron McMillin',
    author_email='fieldobject@aaron.mcmillinclan.org',
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Framework :: Django',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    # test_suite='tox'  # someday, in theory
)
