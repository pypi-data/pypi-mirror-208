plib3.stdlib
============

The PLIB3.STDLIB package contains a number of useful packages
and modules that extend the Python 3 standard library. The
latest official release is available on PyPI at
https://pypi.org/project/plib3.stdlib/
and the latest source code is available on Gitlab at
https://gitlab.com/pdonis/plib3-stdlib.

PLIB3.STDLIB is built using the ``build`` PEP 517 build tool
with the ``setuputils_build`` backend, which uses the
``setuputils`` helper module to build the setup.cfg file that
is included with the distribution. This module and build backend
are available at https://gitlab.com/pdonis/setuputils3.

The PLIB3.STDLIB Packages and Modules
-------------------------------------

The following modules or sub-packages are available in the
``plib.stdlib`` namespace:

- The ``builtins`` module contains some funtions that should be
  Python builtins, but aren't. :) Importing the module adds those
  functions to the built-in namespace; this is mostly useful for
  interactive shells. The functions can also be imported directly
  from ``plib.stdlib.builtins``, to make it easier to understand
  where the functions are coming from in module code.

- The ``classtools`` module provides some utilities for working
  with classes and class attributes.

- The ``cmdline`` module provides utilities useful for command
  line programs and interactive shells.

- The ``coll`` sub-package provides various collection classes,
  including abstract collections built on the ``collections``
  ABCs from the standard library.

- The ``copytools`` module provides functions to copy function
  and code objects, which ``copy.copy`` in the Python standard
  library just returns unchanged. This allows copies of such
  objects to be made with selected attributes changed.

- The ``csvtools`` module provides useful functions for working
  with CSV files.

- The ``decotools`` module provides functions and factories for
  working with decorators.

- The ``examples`` module contains entry point functions for the
  example programs shipped with ``plib3.stdlib``.

- The ``fdtools`` module provides utilities for working with file
  descriptors.

- The ``imp`` module provides the ``import_from_module`` function,
  which should be in the standard library ``importlib`` module
  but isn't. :)

- The ``ini`` sub-package implements an abstract 'INI file' API that
  uses ``ConfigParser`` on POSIX systems, and the Windows registry
  on Windows systems. This API allows the configuration file
  structure to be declared using Python lists and dicts.

- The ``iters`` module provides various functions dealing with
  or returning iterables.

- The ``jsontools`` module provides convenience functions for
  loading and saving JSON files, and for "extended" JSON that
  allows "literal" Python types like tuples that standard JSON
  does not support.

- The ``localize`` module provides useful functions for getting
  locale-specific information.

- The ``mail`` module provides a useful shortcut function for
  sending email from programs.

- The ``mathlib`` module provides some additional math functions
  to supplement those in the standard library.

- The ``net`` sub-package provides simple network socket client
  and transport objects, and utilities for getting information
  about networks.

- The ``options`` module provides an easier-to-use overlay for
  the ``argparse`` module which allows you to express your option
  configuration in the form of Python lists, tuples, and dicts.

- The ``ostools`` module provides utilities for working with the
  operating system.

- The ``postinstall`` module provides utilities to obtain information
  about the installation of a project and to run scripts from the
  shared data directory tree installed for the project, such as
  example programs.

- The ``proc`` module provides two shortcut functions for getting
  the output of a subprocess.

- The ``sigs`` module provides a context manager for installing
  signal handlers.

- The ``strings`` module provides functions and constants for
  working with strings.

- The ``systools`` module provides a context manager for temporarily
  changing ``sys.path``.

- The ``timer`` module provides functions for timing code, with
  an alternate API to the standard library's ``timeit`` module
  that is easier to use when timing functions that you already
  have as objects, instead of source code strings.

- The ``tztools`` module provides some useful ``tzinfo`` subclasses
  based on those in the Python docs for the ``datetime`` module,
  and a function to return the local system timezone name.

- The ``util`` sub-package provides the ``ModuleProxy`` class, which
  is used by a number of PLIB3 sub-packages. See the docstrings
  for the class and the sub-packages using it for more information.

Installation
------------

The simplest way to install PLIB3.STDLIB is by using ``pip``:

    $ python3 -m pip install plib3.stdlib

This will download the latest release from PyPI and install it
on your system. If you already have a downloaded source tarball or
wheel, you can have ``pip`` install it directly by giving its
filename in place of "plib3.stdlib" in the above command line.

Example Programs
----------------

PLIB3.STDLIB comes with example programs that illustrate key features
of some sub-packages. After installation, these can be found in the
``$PREFIX/share/plib3.stdlib/examples`` directory. If you have a
POSIX system (Linux or Mac OSX), script wrappers to run these
programs will be installed into the ``$PREFIX/bin`` directory.

The Zen of PLIB3
----------------

There is no single unifying purpose or theme to PLIB3, but
like Python itself, it does have a 'Zen' of sorts:

- Express everything possible in terms of built-in Python
  data structures.

- Once you've expressed it that way, what the code is
  going to do with it should be obvious.

- Avoid boilerplate code, *and* boilerplate data. Every
  piece of data your program needs should have one and
  only one source.

Copyright and License
---------------------

PLIB3.STDLIB is Copyright (C) 2008-2022 by Peter A. Donis.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. (See the LICENSE.txt file for a
copy of version 2 of the License.)

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
