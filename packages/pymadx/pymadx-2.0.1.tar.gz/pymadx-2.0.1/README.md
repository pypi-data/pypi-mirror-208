#pymadx#

A python package containing both utilities for processing and analysing MADX output.

## Authors ##

L. Nevay
S. Boogert
S. Walker
A. Abramov
W. Shields
J. Snuverink

## Setup ##

pip install pymadx

Or from source, from the main directory:

$ make install

or for development where the local copy of the repository is used
and can be reloaded with local changes:

$ make develop

Look in the Makefile for the various pip commands (e.g. for with a venv).


```
$> python
>>> import pymadx
>>> t = pymadx.Data.Tfs("twiss.tfs")
```

## Dependencies ##

 * matplotlib
 * numpy
 * pytransport (optional)

