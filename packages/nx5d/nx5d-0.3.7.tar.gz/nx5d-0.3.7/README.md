NX5 Duct Tape
=============

`nx5d` a.k.a. `nx5duct` a.k.a. *NX5 Duct Tape* is a collection of tools
that factilitate rapid generation and hacking of HDF5/Nexus files.
It's used to transform experimental data of specific origins
(e.g. [Uni Potsdam's UDKM Group's](https://www.uni-potsdam.de/en/udkm/))
into a Nexus compliant format.

Treat this as "work in progress", and, it being Free Software, if you break
it you get to keep both halves ¯\\\_(ツ)\_/¯

Contents:
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Functionality Overview](#functionality-overview)
  - [The `nx` module](#the-nx-module)
  - [The `DataSource` module](#the-datasource-module)
  - [XRD helpers](#xrd-helpers)

Dependencies
------------

`nx5d` uses the following linraries:

  - `fabio`, the [SilX Fable I/O library](https://github.com/silx-kit/fabio)
  - `h5py`, the [Python HDF5 library](https://www.h5py.org/)
  - `numpy`, the [Python numerical framework](https://numpy.org/) which
    hopefully needs no introduction ;-)
  - `scipy`, a Python framework for
    [scientific data analysis](https://scipy.org/)
  - `xrayutilities`, Dominik Kriegner's library for processing and simulating
    [X-ray diffraction](https://github.com/dkriegner/xrayutilities)
	data and geometries
  - `xarray`, framework for [N-dimensional labeled arrays](https://xarray.dev/)
  - ...possibly a few others, too...
	
	
Installation
------------

Work in progress. Should work in PyPI soon (`pip install nx5d` or so).

Functionality Overview
----------------------

Note that the `nx5d` package is in very early stages of development.
Project scope is shifting, having essentially started off as a repository
of "things I need to do XRD data analysis" and currently aiming to reach
more specific, general-purpose tool character.

As of now, there are several distinct components to `nx5d`:

 - [The `nx` module](#the-nx-module): provides synthetisation of "NX5-Files"
   ([Nexus](https://www.nexusformat.org/) packaged in
   [HDF5](https://www.hdfgroup.org/solutions/hdf5)) from the former ESRF
   Logfile beamline format. This format is obsolete as of 2022, but may
   be needed for legacy data.
   
 - [The `DataSource` module](#datasource-module): provides high-level
   I/O functionality for x-ray diffraction data (XRD) based on the
   [xrayutilities](https://github.com/dkriegner/xrayutilities).
   
 - [The XRD helpers](#xrd-helpers): distinct bits and snippets of
   algorithms to help with numerical data analysis, specifically with
   XRD data as provided by the [`DataSource` module](#the-datasource-module)


Caveats & Bugs
--------------

Not enough code to call them "bugs" yet. We call them "gaping, deep,
dark holes." :-p
