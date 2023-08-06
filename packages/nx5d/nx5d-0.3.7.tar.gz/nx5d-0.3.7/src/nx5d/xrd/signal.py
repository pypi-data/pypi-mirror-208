#!/usr/bin/python3

import xrayutilities as xu
from xarray import DataArray, Dataset
import numpy as np

import logging

'''
Generic builder to generate an "experiment setup" dictionary.

Concepts
========

The structure of an experiment setup contains several types
of data:

  - "Static" persistent device geometry data, e.g. the type
    and axes of the goniometer etc

  - "Static" transient data which is valid for a particular
    data set or scan, but not necessarily for others, e.g.
    current center of the detector plate, photon energy etc

  - "Dynamic" data which might changes from frame to frame
    (mostly positioners and auxiliary experimental data like
    ring gurrent etc.

"Static" persistent data
------------------------

All notations and conventions are analogous to `xrayutilities`
device / goniometer setup:

  - `goniometerAxes`: The direction of each of the goniometer axes in
    the `[xyz][+-]` notation. This is a variable-sized array, as there
    can be several axes in any goniometer, and `xrayutilities` apparently
    magically knows what to do.

  - `detectorTARAxes`: The direction of each of the 3 possible movement
    axes of the detector (tilt, azimuth, rotation). Note that there are
    always 3 of these axes each with a very specific purpose in
    `xrayutilties`. If your detector lacks any, complement with `None`.

  - `imageAxes`: The direction of the image axes (x and y) at zero angles.
    The positive direction of the axes should coincide with increasing pixel
    index in the data.

  - `imageCenter`: This is the positio of the center pixel, either absolute
    (integer pixel numbers), or relative to the sensor size (as specified in
    `imageAxes`). If the number is in the range 0.0..1.0, then relative
    positioning is assumed.

  - `imageChannelSpan` / `imageDistAndPixsize`: for Q transformation,
    ultimately the relation between every specific on the detectors and the angle
    of the incoming beam activating that specific pixel is needed. There
    are two distinct ways of specifying this: either using the "channel span",
    i.e. the size, in degrees, of each pixel, in horizontal/vertical direction,
    or by a distance parameter (from detector to sample) and a pixel size.
    `imageChannelSpan` is either a single number or a 2-tuple specifying
    how many degrees one channel takes. `imageChannelSize` specifies the
    spatial size of a pixel relative to the distance between the sample
    and the sensor.

  - `sampleFaceUp`: Direction of the "sample surface facing up", a.k.a.
    "sampleor" in `xrayutilities` lingo. This is the orientation of
    the sample surface at zero angles. This is either an axis notation
    (`[xyz][+-]`) or one of the special words `det`, respectively `sam`.


Example for device geometry:

```
{
  "goniometerAxes": ('y+', 'z+', 'x+'),

  "detectorTARAxes": (None, "z+", None),
  "imageAxes": ("x+", "z+"),
  "imageSize": (1024, 768),
  "imageCenter": (0.5, 0.5),
  "imageChannelSpan": (None, None),
  "imageChannelSize": (None, None),

  "sampleFaceUp": 'x+',
  "beamDirection": (0, 1, 0),
}

```

"Static" itinerant data
-----------------------

Experiment setup contains additional parameters specific to the current
experiment (as opposed to: typical for the experimentl setup). These
include:

  - `sampleNormal`: Direction perpendicular to the surface. Please also
    consult the official `xrayutilites` documentation as to the exact meaning
    of the directions.

  - `beamEnergy`: energy of the x-ray beam (in eV).

  - `detectorTARAngles`: (optional) angle values for tilt, azimuth and
    rotation of the detector. Default values for each of these angles is
    0. Only angles which are not `None` in `detectorTARAxes` are accepted.

Example for the sample geometry setup:
```
{
  "sampleNormal": (0, 0, 1),
  "beamEnergy": 15000.0,
  "detectorTARAngles": (0, 0, 0),
}
```


"Dynamic" measurement data
--------------------------

These include mostly goniometer axes, homing offsets etc. There is either
one of these per scan, or one per frame (i.e. a whole container/array of
such elements per scan). These include:

  - `goniometerAngles`: positioning for each of the angles of the
    goniometer, as specified in `goniometerAxes`

  - `detectorTARAngles`: positioning for the detector tilt, azimuth
    and rotation (as in `detectorTARAxes`)

Some of these configuration parameters (e.g. the goniometer angles) are
inherently "not fixed" as they are an essential part of the measurement.
Others, like the detector angles, may or may not be fixed (e.g. detector
might be permanently fixed at an azimuth different from 0, or may
change with every frame or with every scan, etc).

For this reason, not only scalar numbers are accepted, but actually
HDF5 dataset addresses as string. Here is an example of how such a
setup definition might look like:

```
{
  "goniometerAngles": ("Theta", "Phi", "Chi"),
  "detectorTARAngles": (0, "Psi", 0)
}
```

Here, the dataset "Theta" with respect to the default positioner path
would be used as the first goniometer angle (for ESRF-style HDF5, this
would be "instrument/positioners/Theta".)

There might also be other positioning parameters relevant for data
transformation and analysis, for instance "TwoTheta" instead of "Psi",
which would have a similar meaning except for a different
direction / offset, with respect to "Psi." In essence, it's the
responsibility of higher layers to decide what addresses / angles should
be used here.

There is no data pendant to the `imageAxes` parameter because the angle
information for each image is within the index of its own pixels.
The data set may also contain other data of interest (e.g. "SBcurrent"),
but that is viewed as something to be accessed in parallel to, and not
as a basis of, the main image data.

Each of the data fielts itself (e.g. "image", but also others like
"SBcurrent", "delay", ...) which may be imporant for the physical analysis,
but not to the transformation of data, is not a matter of `ExperimentalSetup`
(FIXME: or is it?) but one of data collection fields within
`ScanReader`.

Placeholder variables
---------------------

When using HDF5 paths as placeholders, `SetupGenerator` can use string
formatting if a dictionary of keys is supplied at `__init__`
or at `__call__`. `ScanReader` supplies the following keys, compatible
with the ESRF flavor of HDF5/Nexus data format:

  - "instrument": The top level directory containing instrument information,
    typically of HDF5 type "NXinstrument" and located at "./instrument"
    within the scan.

  - "positioners": Typically at "./instrument/positioners", usually
    important for all the angle definitions

  - "measurement": Top-level folder (of type "NXcollection") containing
    the measurement data (typically "./measurement").

Usage
=====

The idea is to make a 3-step process:

  1. Create dictionary (with keys above) that specify static
     parameters as far as possible, and contains HDF5 paths/addresses
     for the rest

  2. Pass on dictionary to `ExperimentSetup` class, which stores the
     explicitly passed values, and also offers an interface (upon
     construction or later) to override or modify keys

  3. Override `ExperimentSetup.__call__()` to export a "final" version
     of the data, hand-matched for the current scan dataset (passed on
     as parameter to `__call__()`) which does not contain anything
     else besides pure, usable values :-)

(FIXME: the whole "\\*Angles" section is actually supposd to *not* know
about loading data yet... isn't it? In a way, the Angles section is
less like "experimental setup" and more like "measurement results.")
'''        

class LazyQMap:
    '''
    Container class for a stack of experimental data frames
    and associated metadata.

    The raw / authoritative data is stored in the `Chunk.data`
    container, which has a Python `dict()` like interface.
    Beyond that, this class also offers a number of processed
    data entries that are all lazily evaluated (i.e. only processed
    on first access):

      - `qimg`: A single 2D image of the Q-space converted data stack,
        on a rectantular grid (using an `xrayutilities` gridder, meaning
        that *all* of the original image stack is being used)

      - `qxaxis`: The X-axis of the gridder that produced `qimg`

      - `qyaxis`: The Y-axis of the gridder that produced `qimg`

    All of the computed data being *lazily* evaluated means that any
    processing that must take place on the raw (i.e. untransformed)
    data can -- and must -- take place before first access to any
    of the `q...` properties. E.g. for intensity normalization, you
    could do simething like: `chunk.data['img'] *= intensity` and
    only then proceed to accessing `chunk.qimg`.
    '''

    def __init__(self, setup=None, **data):
        '''
        Parameters:
          - `data`: A dicitonary with string keys (names) and arrays
            as the data fields.

          - `setup`: Experiment definition dictionary (see for instance
            nx5d.xrd.kmc3.ExperimentTemplate).

        '''
        
        self.xdata = self.__make_dataset(**data,
                                         **(setup['goniometerAngles']),
                                         **(setup['detectorTARAngles']))

        self._data_keys = tuple([k for k in data])
        self._angle_keys = tuple([k for k in setup['goniometerAngles'].keys()] +
                                  [k for k in setup['detectorTARAngles'].keys()])
            
        self.hxrd = self.__init_experiment(setup)
        self.Ang2Q = self.hxrd.Ang2Q


    @property
    def angles(self):
        ''' dict-based access to all the "angles" fields (mimics old API).
        '''
        return { k:self.xdata[k].values for k in self._angle_keys }


    @property
    def data(self):
        ''' dict-based access to all the "data" fields (mimics old API).
        '''
        return { k:self.xdata[k].values for k in self._data_keys }
    

    def __make_dataset(self, **dsets):
        ''' Creates an `xarray.Dataset` of data sets within `dsets`.
        The first dimension of all `dsets` is required to be the same.
        This is introduced as the first dimension in the `xarray` dataset,
        with the name "__index__".
        '''

        tmp = next(iter(dsets.items()))
        try:
            xdata = Dataset({'index': np.array(range(tmp[1].shape[0]))})
            for k,p in dsets.items():
                data = self.__arrayify(p, tmp[1].shape[0])
                dims = ["index"] + ["%s_%d" % (k,i) for i in range(1,len(data.shape))]
                xdata[k] = (dims, data)
        except:
            logging.error("Error with dataset: %r" % tmp)
            raise

        return xdata



    def __2tuple(self, data, name=""):
        ''' Returns a 2-tuple (X, Y) from a variety of data sets:
          - from a 2-tuple :-) or an array with size 2
          - from an array (N, 2)
          - from an array or tuple (2, N)
        '''
        if not hasattr(data, "__len__"):
            raise RuntimeError("%s: needs to be a 2-tuple" % name)
        
        if len(data) == 2:
            if hasattr(data[0], "__len__"):
                return ([data[0][0], data[1][0]])
            else:
                return ([data[0], data[1]])

        if len(data) > 2:
            return data[0]

        raise RuntimeError("Oops: don't know how to handle %s: %r" % (name, data))


    def __arrayify(self, val, num_pts):
        return val \
            if hasattr(val, "__len__") \
            else np.array([val]*num_pts)


    def __init_experiment(self, setup):
        '''
        Initializes the Experiment part (i.e. xrayutilities HXRD object etc)
        with specified device and sample geometry. The optional parameter `roi`
        restricts angle-to-Q conversion to solely this region, if it is
        specified. This is a good way to save significant amounts of computing
        time.

        '''

        logging.debug("Expriment setup: %r" % setup)

        detAxes = [x for x in filter(lambda x: x is not None, setup['detectorTARAxes'])]

        # beamEnergy is usually supposed to be a scalar, but sometimes an array
        # (one for each image) will be supplied. In that case, retrieve only the first.
        beamEnergy = setup['beamEnergy'] \
            if not hasattr(setup['beamEnergy'], "__len__") \
               else setup['beamEnergy'][0]

        qconv = xu.experiment.QConversion(sampleAxis=setup['goniometerAxes'],
                                          detectorAxis=detAxes,
                                          r_i=setup['beamDirection'],
                                          en=beamEnergy)

        hxrd = xu.HXRD(idir=setup['beamDirection'],
                       ndir=setup['sampleNormal'],
                       sampleor=setup['sampleFaceUp'],
                       qconv=qconv,
                       # Workaround for buggy xrayutilities: repeat the beam energy
                       en=beamEnergy)

        imageCenter = self.__2tuple(setup['imageCenter'], 'imageCenter')
        imageSize = self.__2tuple(setup['imageSize'], 'imageSize')
        imageDistance = setup['imageDistance'][0] \
            if hasattr(setup['imageDistance'], "__len__") \
               else setup['imageDistance']

        logging.debug("image distance %r, size %r, center at %r" % \
                      (imageDistance, imageSize, imageCenter))
        
        if imageCenter[0] <= 1 and imageCenter[1] <= 1:
            # It's a floaring-point number, relative to the detector size

            # similar considerations for imageSize as for imageCenter: expected to be
            # a 1D array with length 2, but will also accept a 2D array
            # with shape (N, 2).
            
            # FIXME: really, REALLY need to fix this. This is really ugly.
            imgs = imageSize
            assert imgs is not None
            assert imgs[0] is not None
            assert imgs[1] is not None            
            imageCenter = tuple([c*s for c,s in zip(setup['imageCenter'], imgs)])

        chSizeParm = {}
        if ('imageChannelSpan' in setup) and (setup['imageChannelSpan'] is not None):
            # channelSpan is degrees/channel, but need to pass channels/degree to Ang2Q
            imageChannelSize = self.__2tuple(setup['imageChannelSpan'],
                                             'imageChannelSpan')
            chSizeParm = {'chpdeg1': 1.0/imageChannelSpan[0],
                          'chpdeg1': 1.0/imageChannelSpan[1] }

        elif ('imageChannelSize' in setup) and (setup['imageChannelSize'] is not None):
            # Ang2Q takes one explicit distance parameter, but we're assuming that
            # channelSize is relative to the distance itself (putting the distance
            # always at 1.0 units)
            imageChannelSize = self.__2tuple(setup['imageChannelSize'],
                                             'imageChannelSize')
            logging.debug("pixel size: %r" % (imageChannelSize,))
            chSizeParm = { 'pwidth1':  imageChannelSize[0],
                           'pwidth2':  imageChannelSize[1],
                           'distance': imageDistance }

        else:
            raise RuntimeError("Experiment setup needs either the "
                               "channel span or channel size")

        tarAngles = setup.get('detectorTARAngles', [0, 0, 0])

        roi = setup.get('roi', (0, imageSize[0], 0, imageSize[1]))

        hxrd.Ang2Q.init_area(detectorDir1=setup['imageAxes'][0],
                             detectorDir2=setup['imageAxes'][1],
                             cch1=imageCenter[0],
                             cch2=imageCenter[1],
                             Nch1=imageSize[0],
                             Nch2=imageSize[1],
                             tiltazimuth=0, #tarAngles[1],
                             tilt=0,        #tarAngles[0],
                             detrot=0,      #tarAngles[2],
                             roi=roi,
                             **chSizeParm)

        return hxrd    


    def __getitem__(self, label):
        return self.xdata[label]


    def __call__(self, *datasets, **kwargs):
        return self.area_qconv(*datasets, **kwargs)

    def area_qconv(self, *datasets, **kwargs):
        '''
        Front to the ang-to-Q conversion, currently only for area data. Parameters:
        `datasets` is either empty, or a single data label. (No multiple label support
        yet.)
        
        Accepted `kwargs`:

          - `qsize`: Tuple (w, h) of the resulting Q image, or `None` (default).
            If it is `None`, the size of the original angular image(s) is used.

          - `dims`: List with dimension names for resulting Q image.
            Defaults to `["qw", "qh"]`.

          - `_gridderDict`: If specified, this is a dictionary with extra named
            parameters to be passed on to the gridder. Note that this is not portable,
            only works as long as we're using xrayutilities under the hood.

          - `_ang2qDict`: Extra set of parameters to be passed to the data-specific
            `Ang2Q` function (typically `Ang2Q.area()` for stacks of 2D datasets).
        '''

        if len(datasets) > 1:
            raise RuntimeError("Can't transform more than one dataset at a time")

        label = next(iter(datasets  if len(datasets)>0 else self._data_keys))
        img = self.xdata[label].values
        
        dims = kwargs.setdefault('dims', ('qx', 'qy', 'qz'))

        if isinstance(dims, str):
            dims = (dims,)

        if len(dims) < 1 or len(dims) > 3:
            raise RuntimeError("Bad Q-axis specification: %r" % dims)
        
        if len(img.shape) != 3:
            raise RuntimeError("Don't know how to transform objects of shape %r" \
                               % (img.shape,))


        # Make sure all angles are arrays (even those that might have been
        # passed as floats)
        ang = [self.__arrayify(self.xdata[a].values, len(img)) for a in self._angle_keys]
            
        self.q = self.Ang2Q.area(*ang, **(kwargs.get('_ang2qDict', {})))

        # For transforming strings to dimension indices
        qspec = { 'x': 0, 'qx': 0,
                  'y': 1, 'qy': 1,
                  'z': 2, 'qz': 2 }

        # The list of individual Q directions/coordinates, according to user input 'dims'
        qcoord = [self.q[qspec[d]] for d in dims]

        # Default for 'qsize' is the size of the final Q-image -- make sure we account
        # for the possibly twisted order of Q-coordinates the user specified in 'dims'
        kwargs.setdefault('qsize', [img.shape[qspec[d]] for d in dims])

        # Call scheme of all the xrayutilities Gridders is pretty similar.
        Gridder = getattr(xu, "FuzzyGridder%dD" % len(dims))
        grd = Gridder(*(kwargs['qsize']))
        grd( *qcoord, img, **(kwargs.get('_gridderDict', {})) )

        # ...the tricky part is creating the DataArrays. Specifically,
        # retrieving the q coordinates from the gridder. They are in `grd`
        # attributes called 'xaxis', 'yaxis', ... according to dimension.
        # We always use qx/qy/qz for dimension keys.
        coords = {}
        for i,d in enumerate(dims):
            axname = d if len(d)>1 else 'q%s' % d
            axvals = getattr(grd, "%saxis" % ('x', 'y', 'z')[i])
            coords[axname] = axvals

        return DataArray(data=grd.data, coords=coords)

    
## Example for a class that does more than LazyQMap (namely accept angle offsets
## in its constructor), but still uses LazyQMap under the hood.
class OffsetQMap(LazyQMap):
    def __init__(self, offsets=None, **kwargs):
        super().__init__(**kwargs)
        if offsets is not None:
            for k,v in offsets.items():
                self.angles[k] += v
