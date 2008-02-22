""" Rounder Distutils Setup Script """

__revision__ = "$Revision$"

from setuptools import setup

setup(name="rounder",
    version='0.0.1b',
    description='Poker for the Gnome desktop.',
    author='Devan Goodwin & James Bowes',
    author_email='dgoodwin@dangerouslyinc.com & jbowes@dangerouslyinc.com',
    url='http://dangerouslyinc.com',
    license='GPL',
#    install_requires=['Cerealizer', 'Twisted'],
    packages=['rounder'],
    package_dir={'rounder': 'src/rounder'},
    package_data={'rounder': ['data/*.xml', 'data/*.glade', 'data/*.png']},
    scripts=['bin/rounder'],
    # TODO: This sucks.
    data_files=[('../etc/gconf/schemas', ['data/rounder.schema'])],
    test_suite='runtests.suite'
)

print "rounder installation complete"
