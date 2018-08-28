#!/usr/bin/env python
"""SNI_ads: a one-line command to manage citations for SNI
"""
import os
from setuptools import setup


DOCLINES = __doc__.split('\n')
CLASSIFIERS = """\
Programming Language :: Python
Topic :: Engineering
Operating System :: POSIX
Operating System :: Unix
"""
NAME = "SNIads"
MAJOR = 7
MINOR = 3
ISRELEASED = True
VERSION = '%d.%d' % (MAJOR, MINOR)
REVISION = 0 + int(os.popen("git rev-list --all | wc -l").read())


def write_version_py(filename=NAME+'/version.py'):
    if os.path.exists(filename):
        os.remove(filename)
    cnt = """\
# THIS FILE IS AUTOMATICALLY GENERATED BY ENPLOT SETUP.PY
version = '%(version)s'
revision = %(revision)s
release = %(isrelease)s
"""
    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'revision': REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()

write_version_py()

setup(
    name=NAME,
    version=VERSION,
    packages=['SNIads'],
    author="Christophe Morisset",
    author_email="chris.morisset@gmail.com",
    license="LGPL",
    description=DOCLINES[0],
    long_description="\n".join(DOCLINES[2:]),
    keywords="text, search, command-line",
    url="http://github.com/Morisset",
    platforms=["Linux", "Unix"],
    entry_points={
        'console_scripts': [
            'SNIads = SNIads.SNIads:main'
        ]
    }
)
