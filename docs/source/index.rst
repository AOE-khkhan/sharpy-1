.. SHARPy documentation master file, created by
   sphinx-quickstart on Wed Oct 19 16:40:48 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Simulation of High Aspect Ratio planes in Python [SHARPy]
=========================================================


.. image:: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FImperialCollegeLondon%2Fsharpy%2Fmaster%2F.version.json

.. image:: https://codecov.io/gh/ImperialCollegeLondon/sharpy/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ImperialCollegeLondon/sharpy

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
   :target: https://opensource.org/licenses/BSD-3-Clause

.. image:: https://readthedocs.org/projects/ic-sharpy/badge/?version=master

.. image:: https://joss.theoj.org/papers/f7ccd562160f1a54f64a81e90f5d9af9/status.svg
   :target: https://joss.theoj.org/papers/f7ccd562160f1a54f64a81e90f5d9af9

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3531965.svg
   :target: https://doi.org/10.5281/zenodo.3531965

Welcome to SHARPy (Simulation of High Aspect Ratio aeroplanes in Python)!

SHARPy is an aeroelastic analysis package currently under development at the Department of Aeronautics,
Imperial College London. It can be used for the structural, aerodynamic, aeroelastic and flight dynamics
analysis of flexible aircraft, flying wings and wind turbines. Amongst others, it offers the following solutions to the user:

* Static aerodynamic, structural and aeroelastic solutions
* Finding trim conditions for aeroelastic configurations
* Nonlinear, dynamic time domain simulations under a large number of conditions such as:

    + Prescribed trajectories.
    + Free flight.
    + Dynamic follower forces.
    + Control inputs in thrust, control surface deflection...
    + Arbitrary time-domain gusts, including non span-constant ones.
    + Full 3D turbulent fields.
    + Multibody dynamics with hinges, articulations and prescribed nodal motions.
    + Linearisation around a nonlinear equilibrium.
    + Frequency response analysis.
    + Model order reduction.

The modular design of SHARPy allows to simulate complex aeroelastic cases involving very flexible aircraft.
The structural solver supports very complex beam arrangements, while retaining geometrical nonlinearity.
The UVLM solver features different wake modelling fidelities while supporting large lifting surface deformations in a
native way. Detailed information on each of the solvers is presented in their respective documentation packages.

Contents
--------

.. toctree::
   :maxdepth: 1

   content/installation
   content/sharpy_intro
   content/contributing
   content/casefiles
   content/examples
   content/solvers
   content/postproc
   includes/index
   content/test_cases

Citing SHARPy
-------------

SHARPy is archived in Zenodo. If you need to cite it, use this:

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3531965.svg
   :target: https://doi.org/10.5281/zenodo.3531965

This DOI which represents all the versions of the given software package, i.e. the concept of
the software package and the ensemble of versions. In Zenodo you can find the DOI of a specific version.

For more information on citing and Zenodo, read more_.

.. _more: https://help.zenodo.org/#versioning


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Contact
-------

SHARPy is developed at the Department of Aeronautics, Imperial College London. To get in touch, visit the `Loads Control
and Aeroelastics Lab <http://imperial.ac.uk/aeroelastics>`_ website.
