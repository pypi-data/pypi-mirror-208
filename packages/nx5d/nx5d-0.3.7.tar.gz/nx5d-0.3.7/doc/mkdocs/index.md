# Nx5d -- A Rapid Data Analysis Framework

Nx5d is a Python framework for rapid data processing and analysis workflows
in scienfic enviroments. It is aimed to be the first thing a physicist
imports and uses in his or her Jupyter Lab notebook for on-line analysis
during data acquisition.

This is all it should take to visualize your X-ray diffraction data in 
reciprocal space:

```
import nx5d, h5py, json

experiment_template = json.load(open("experiment.json").read())
reader = nx5d.scan.ScanReader(h5py.File, "data.h5", "r")
qspace = next( nx5d.xrd.LazyQMap(**(reader.streaks(image="@detector", setup=exp_template)) )

qspace.sum("qx").plot()
```

## Installation and First Steps

#### Via PyPI

You can install nx5d from its official PyPI repository:

```
pip install nx5d
```

#### Directly form Git

Or you can download it via git and install it manually:

```
git clone https://gitlab.com/codedump2/nx5d.git
cd nx5d && pip install .
```

#### From Tarball

...or you can download a regular
[ZIP file](https://gitlab.com/codedump2/nx5d/-/archive/master/nx5d-master.zip)
or [Tarball](https://gitlab.com/codedump2/nx5d/-/archive/master/nx5d-master.tar.gz)
of the latest code and install *that*:

```
wget https://gitlab.com/codedump2/nx5d/-/archive/master/nx5d-master.tar.gz
tar xf nx5d-master.tar.gz
cd nx5d
pip install .
```

## Documentation

Chances are you're already looking at it :-)
Otherwise you can visit the [ReadTheDocs page of nx5d](https://nx5d.readthedocs.io/).

## How to Participate

nx5d being a Free Software project, and the solutions only having a chance
of becoming as good as the interesting problems its users are kind enough
to share, you are encouraged to participate. Tasks include:

  - Using, testing, using, testing, ...
  
  - Improving documentation
  
  - Improving code, e.g. by writing unit tests, developing data
    analysis methods, adding HDF5-like interfaces for new data
	formats or experimental setups
	
  - ...or diving straight in and contributing to the concepts and
    core part of the code :-)
	
So pick your fight! And remember that [if you break it, you get to keep both pieces.](https://english.stackexchange.com/questions/118717/how-is-the-phrase-when-your-program-breaks-you-get-to-keep-both-pieces-commo) :-)

The main repository around which nx5d development happens is
[over at GitLab](https://gitlab.com/codedump2/nx5d). If enough
interest prevails, we're pondering setting up a mailing list
and a dedicated website.



