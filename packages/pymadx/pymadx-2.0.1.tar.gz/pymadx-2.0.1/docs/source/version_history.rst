===============
Version History
===============

v2.0.1 - 2023 / 05 / 15
=======================

* Reduce Python version requirement to >3.6 instead of 3.7.
* :code:`pymadx[dev]` installation feature in pip to allow testing / manual requirements.
* Start of R-Matrix plots - in development.

v2.0.0 - 2023 / 03 / 16
=======================

* Move to Python 3 entirely. Require at least Python 3.7.
* Package layout and build system changed to more modern declarative package.
  All source code is now in :code:`pymadx/src/pymadx`. The version number
  throughout the code is dynamically generated from the git tag.
* Added plot for 1 or 2 machine diagrams only.
* Fix aperture plots due to typo in code.
* Fix string type comparison for modern Python (i.e. don't use numpy internal alises).


v1.8.2 - 2021 / 06 / 16
=======================

* Fix for plot name filtering.
* Tweaked orange for solenoids.


v1.8.1 - 2020 / 12 / 16
=======================

* Fix for step size in Tfs slicing.
* More tolerant plotting for machine diagrams with just keyword, S and L as colums (ignoring K1L).
* Ensure machine diagram x limit is full machine length by default.


v1.8.0 - 2019 / 06 / 08
=======================

New Features
------------

* Switch to Python 3. Should be Python 2.7 compatible.
* Venv support in Makefile thanks to Kyrre Ness Sjoebaek.
* Ability to write out a Tfs instance permitting comlete loading, editing and writing.
* Plus operator for Tfs instances to add them together.

Bug Fixes
---------

* Use exact Hamiltonian for PTC jobs prepared from pymadx as we commonly
  use it to compare larger amplitude particle tracking where the approximate
  Hamiltonian can be quite wrong.
* Tolerate minimal aperture columns. i.e. only APER_1. Have to do this
  as there's no standard in writing out apertures and everyone picks their
  own with missing bits of information.


v1.7.1 - 2019 / 04 / 20
=======================

Bug Fixes
---------

* Fix Data.Aperture.RemoveBelowValue logic, which also applies to GetNonZeroItems.
* Tolerate no pytransport at import.


v1.7 - 2019 / 02 / 27
=====================

New Features
------------

* Return PTC beam definition from the Beam class.
* Print basic beam summary from TFS file for given element.
* Ability to split an element loaded from a TFS file correctly.

General
-------

* Update copyright for 2019.


v1.6 - 2018 / 12 / 12
=====================

General
-------

* Reimplemented machine diagram drawing to be more efficient when zooming and
  fix zordering so bends and then quadrupoles are always on top.
* Dispersion optional for optics plotting.
* H1 and H2 now passed through conversion of MADX TFS to PTC input format.
* Solenoid added to MADX TFS to PTC converter.
* Revised bend conversion for MADX TFS to PTC converter.
  

v1.5 - 2018 / 08 / 24
=====================

New Features
------------

* Support for tkicker.
* Support for kickers in MADX to PTC.

General
-------

* Improved aperture handling.

Bug Fixes
---------

* Several bugs in Aperture class fixed.


v1.4 - 2018 / 06 / 23
=====================

New Features
------------

* Support of just gzipped files as well as tar gzipped.

General
-------

* Improved SixTrack aperture handling.

v1.2 - 2018 / 05 / 23
=====================

New Features
------------

* Write a beam class instance to a separate file.
* Add ptc_track maximum aperture to a model.
* Concatenate TFS instances.
* N1 aperture plot as well as physical aperture plot.
* Output file naming for plots for MADX MADX comparison.
* MADX Transport comparison plots.

General
-------

* Changes to some plot arguments.
* 'Plot' removed from plot functions name as redundant.
* Transport conversion moved to pytransport.
  
Bug Fixes
---------

* Machine plot now deals with 'COLLIMATOR' type correctly.


v1.1 - 2018 / 04 / 10
=====================

New Features
------------

* Improved options for writing PTC job for accurate comparison.
* Support for subrelativistic machines - correct MADX definition of dispersion.
* Plots for beam size including dispersion.
* MADX MADX Twiss comparison plots.

Bug Fixes
---------

* Removal of reverse slicing as it didn't work and is very difficult to support
  as MADX typically returns optical functions at the end of an element. Some
  columns however are element specific (such as L).
* Fixed exception catching.
* Fix beam size for subrelativistic machines. MADX really provides Dx/Beta.
* Fix index searching from S location.
* Fix PTC analysis.
* Fix conversion to PTC for fringe fields.

v1.0 - 2017 / 12 / 05
=====================

New Features
------------

* GPL3 licence introduced.
* Compatability with PIP install system.
* Manual.
* Testing suite.
