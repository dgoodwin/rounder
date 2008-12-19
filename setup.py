#!/usr/bin/python

""" Rounder Distutils Setup Script """

__revision__ = "$Revision$"


import os

from distutils.core import Command, setup


class SetupBuildCommand(Command):
    """
    Master setup build command to subclass from.
    """

    user_options = []

    def initialize_options(self):
        """
        Setup the current dir.
        """
        self._dir = os.getcwd()

    def finalize_options(self):
        """
        No clue ... but it's required.
        """
        pass


class TODOCommand(SetupBuildCommand):
    """
    Quick command to show code TODO's.
    """

    description = "prints out TODO's in the code"

    def run(self):
        """
        Prints out TODO's in the code.
        """
        import re

        format_str = "%s (%i): %s"

        # If a TODO exists, read it out
        try:
            line_no = 0
            todo_obj = open('TODO', 'r')
            for line in todo_obj.readlines():
                print format_str % ("TODO", line_no, line[:-1])
                line_no += 1
            todo_obj.close()
        except:
            pass

        remove_front_whitespace = re.compile("^[ ]*(.*)$")
        for rootdir in ['src/', 'bin/']:

            for root, dirs, files in os.walk(rootdir):
                for afile in files:
                    if afile[-4:] != '.pyc':
                        full_path = os.path.join(root, afile)
                        fobj = open(full_path, 'r')
                        line_no = 0
                        for line in fobj.readlines():
                            if 'todo' in line.lower():
                                nice_line = remove_front_whitespace.match(
                                    line).group(1)
                                print format_str % (full_path,
                                                       line_no,
                                                       nice_line)
                            line_no += 1


setup(name="rounder",
    version='0.0.1',
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
    package_data={'rounder.ui.gtk': ['data/*.glade', 'data/*.png',
        'data/*.svg']},
    scripts=['bin/rounder', 'bin/rounder-server',
        'bin/rounder-randombot'],
    # TODO: This sucks.
    #data_files=[('../etc/gconf/schemas', ['data/rounder.schema'])],

    # Only valid if we're using setuptools, which we're not due to problems
    # loading glade files inside eggs:
    #test_suite='runtests.suite'
    cmdclass = {'todo': TODOCommand},

)

print "rounder installation complete"
