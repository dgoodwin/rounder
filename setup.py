#!/usr/bin/python

""" Rounder Distutils Setup Script """

__revision__ = "$Revision$"

#from setuptools import setup
from distutils.core import setup

setup(name="rounder",
    version='0.0.1b',
    description='Poker for the Gnome desktop.',
    author='Devan Goodwin & James Bowes',
    author_email='dgoodwin@dangerouslyinc.com & jbowes@dangerouslyinc.com',
    url='http://dangerouslyinc.com',
    license='GPL',
#    install_requires=['Cerealizer', 'Twisted'],
    packages=['rounder', 'rounder.network', 'rounder.ui', 'rounder.ui.gtk',
        'rounder.ui.curses'],
    package_dir={
        'rounder': 'src/rounder',
        'rounder.network': 'src/rounder/network',
        'rounder.ui': 'src/rounder/ui',
        'rounder.ui.gtk': 'src/rounder/ui/gtk',
        'rounder.ui.curses': 'src/rounder/ui/curses',
    },
    package_data={'rounder.ui.gtk': ['data/*.glade']},
    scripts=['bin/rounder', 'bin/rounder-server', 'bin/rounder-txt',
        'bin/rounder-randombot'],
    # TODO: This sucks.
    #data_files=[('../etc/gconf/schemas', ['data/rounder.schema'])],

    # Only valid if we're using setuptools, which we're not due to problems
    # loading glade files inside eggs:
    #test_suite='runtests.suite'
)

print "rounder installation complete"
