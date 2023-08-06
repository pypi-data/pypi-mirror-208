============
Installation
============


Requirements
------------

 * pymadx is developed exclusively for Python 3. 3.7 is the minimum version.
 * Matplotlib
 * Numpy

Installation
------------

pymadx can be installed using pip with internet access without downloading
the git repository:

::
   pip install pymadx


Alternatively, ff cloning the git repository and installing locally, a set of
useful commands are provided in a simple Makefile included in the main
directory. In this case, to install pymadx, simply run ``make install`` from
the root pymadx directory.::

  cd /my/path/to/repositories/
  git clone http://bitbucket.org/jairhul/pymadx
  cd pymadx
  make install

Alternatively, run ``make develop`` from the same directory to ensure
that any local changes are picked up.

For Developers
--------------

If you want to create a package that depends on pymadx, it has the optional
component pytransport that can be requested as :code:`pymadx[pytransport]` in
the `pyproject.toml`.
