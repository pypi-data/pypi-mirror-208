#!/usr/bin/python3

from silx.io.spech5 import SpecH5, SpecH5LazyNodeDataset, SpecH5NodeDataset
from silx.io.commonh5 import Group as H5Group, SoftLink as H5SoftLink
from h5py import File as H5File
from os import path
import tifffile
import numpy as np

import logging

'''
Provides a series of objects to mock an "ESRF dialect" of a HDF5-based Nexus
data file for X-ray diffraction experiments for SPEC files.
As an extra provision, detector data is loaded from external `.tiff` files
with an easily computable path. This is typical for older installation of
SPEC which couldn't handle and store large(-ish) 2D detector images.

The "ESRF dialect" is essentially this:

  - There is 1D or 2D detector data ("images" or "frames").

  - The data is organized in "scans", i.e. images are oranized in series.
    One scan typically consists of several images with the same hard characteristics
    (i.e. same geometry), but taken under systematically differing external parameters:
    e.g. by "scanning" one or several parameter devices (angle? time delay?) and
    obtaining an image at each of the scan points.

  - The data format where the images are stored is a 3-dimensional block of NxWxH,
    where 'WxH' is the width/height of one frame, and 'N' is the number of frames
    in a scan. For a scan performed along a single paramter, each subsequent frame
    corresponds to a different parameter instance; for a scan taken along 2 parameters
    (e.g. inside a 2D parameter space), the scans are interleaved: there are actually
    (n*m)xWxH frames. This is still a 3D dataset with images of geometry WxH, but
    the first "chunk" of 'n' images are scanned along the first paramter and a specific
    'm' value (i.e. all have the same 'm'), the next chunk is scanned again along the
    whole N space but for a different 'm', and so on.

  - Besides detector data, there are also associated metadata -- e.g. the parameter
    arrays along which the scans took place. These are also Nx(...) data sets; in the
    simplest cases, they are 2D (parameter is scalar).

  - The both detector data and scan metadata are stored at specific "paths" within
    the data container. In HDF5 terminology, this is the literal HDF5 path within
    the file (e.g. "data/rayonix/detector"). We don't make any assumptions about
    the tree organisation (yes, typically it follows NX data format rules, but...).

  - A data container (i.e. a "file") can contain one or several scans. Each scan
    has a top-level subdirectory of its own.

  - Beyond data series (detector and metadata), there can also exist single scalar
    values setting the state for the entire experiment (e.g. "photon_energy", or
    "center_pixel", ...).

  - [FIXME: haven't decided yet whether top-level scalar metadata still needs to
    be embedded into a scan (i.e. is per-scan only), or can also be at the very
    top. I think ESRF has the former...]

'''

class SpecH5LazyTiffNode(SpecH5LazyNodeDataset):
    '''
    Implements a NodeDataset that lazily loads a list of TIFF files,
    specified as a path format that relies on an index variable.
    '''
    def __init__(self, *args, tiffPathFmt="{frameidx}.tiff", numFrames=0, **kwargs):
        super().__init__(*args, **kwargs)
        self._tiff_path_fmt = tiffPathFmt
        self._tiff_frames_no = int(numFrames)


    def _create_data(self):
        data = []
        shape = None
        lasterr = None
        missing = []
        for i in range(self._tiff_frames_no):
            try:
                tiff = tifffile.imread(self._tiff_path_fmt.format(frameidx=i))
                shape = tuple([s for s in tiff.shape])
            except FileNotFoundError as e:
                lasterr = e
                if len(missing) == 0:
                    logging.warning(str(e)+". Assuming bad frame, "
                                    "similar errors will be suppressed.")
                missing.append(i)
                tiff = None
            data.append(tiff)


        # It happens a lot that individual files are missing, so
        # we're just ignoring those and replace them with NaN arrays
        # of the appropriate shape. But if we have no shape at this
        # point, this means that _all_ TIFFs are missing. We
        # want to get loud about that (don't we?...)
        if shape is None:
            logging.warning("Dataset had no frames at all.")
            return np.array(np.NaN)
        
        return np.array([ (i if i is not None else np.full(shape, np.nan)) \
                          for i in data])
    

    def __getitem__(self, item):
        '''
        Apparently we can optimize this so that only a single file is
        loaded if not already initialized (...so we don't have to load
        the whole bunch for single-frame access). In that case, `item`
        is the index of the file, and all we have to do is plug it
        into the name formatter.

        OTOH the ESRF H5 library is slow af in specific instances (e.g.
        when doing itermittend slicing a 3D dataset from HDF5.) Not sure if
        this is a problem of HDF5 or of some ESRF trickery. So we might keep
        an eye on this (...in case it's something like this).
        '''
        if not self._is_initialized: 
            try:            
                idx = None
                slc = None
                if isinstance(item, int):
                    idx = item
                    slc = None
                else:
                    idx, slc = item
                    assert isinstance(idx, int)

                # Access the frame from 'idx'
                p = self._tiff_path_fmt.format(index=item)
                frame = np.array([tifffile.imread(p)])

                # ...and possibly a sub-slice ('None' is the same as [:])
                return frame[slc]

            except:
                pass

        return super().__getitem__(item)

    
class SpecTiffH5(SpecH5):
    '''
    Mocks a HDF5 file using the Spec H5 module from Silx.

    In addition the "regular" `slix.io.spech5.SpecH5` functionality, after loading the
    SPEC file, this module also injects lazy-loading nodes for the TIFF files
    correspondng to a typical KMC3 setup.
    '''

    def __init__(self, *args, instrumentName="pilatus",
                 framePathFmt='{dirname}/{instr}/S{scannr:05}/{basename}_{scannr}_{frameidx}.tif',
                 **kwargs):
        '''
        Parameters:

          - `instrument`: A name/label for the instrument. For one, this is used to compile
            the location of where to insert the data from the external TIFF files (as
            specified by `tiffInsertFmt` and `tiffLinkFmt`); for another, this is used
            to determine the location of the TIFF files on disk relative to the
            SPEC file (as specified by `scanPathFmt`).
        
          - `framePathFmt`: format for the image scan filepath.

          - `scanIndexNameFmt`: string formatting that ties the scan number (on disk)
            and scan name (in teh SpecH5 naming) together.

         All string formatters can make use of any or all of the following variables:
        
           - `{dirname}`: folder-only component of the spec file name
        
           - `{basename}`: base name the SPEC file, with the last component after a dot
             (typically ".spec" removed

           - `{scannr}`: scan number; this is typically an integer, assigned by "the
             algorithm", and typically starting with 1 for the first scan

           - `{scanidx}`: scan index; this is an integer starting with 0 and designating
             the cosecutive index value of the scan.

           - `{frameidx}`: the index (starting with 0) of the frame being processed
             (i.e. the TIFF file).

        In addition to the explicit parameters, we also use the following positional
        parameters from `args`:

           - `filename` (position 0): the path of the SPEC file to read
        
        '''
        super().__init__(*args, **kwargs)
        
        self._specBaseName = '.'.join(path.basename(self.filename).split('.')[:-1]) \
            or path.base(self.filename)
        self._specDirName = path.abspath(path.dirname(self.filename))

        for scanName in self.keys():
            
            scan = self[scanName]
            scanNr, foo = scanName.split('.')

            tiffPartialFmt = framePathFmt.format(**{
                "basename": self._specBaseName,
                "dirname": self._specDirName,
                "scannr": int(scanNr),
                "instr": instrumentName,
                "scanidx": "{scanidx}",
                "frameidx": "{frameidx}"
            })
            
            self._adopt_scan(scan, instrumentName, tiffPartialFmt)

            self._enter_cnt = 0
            self._enter_data = None


    def __enter__(self, *args, **kwargs):
        '''
        Opening / closing a SpecTiffH5 is pretty expensive. We usually want to
        employ with-guards (enter/exit) when doing that, but the original SpecH5
        does not support "nested" guards (i.e. entering/exitting multiple
        times on the same object).

        This is an extension to do just that. (Need to check if h5py.File supports
        this... the original Python open() / file object definitely does.)
        '''
        if self._enter_cnt == 0:
            self._enter_data = super().__enter__(*args, **kwargs)
        self._enter_cnt += 1
        return self._enter_data


    def __exit__(self, *args, **kwargs):
        if self._enter_cnt > 0:
            self._enter_cnt -= 1
        if self._enter_cnt == 0:
            super().__exit__(*args, **kwargs)


    def _adopt_scan(self, scanObj, instrumentName, tiffFormat):

        measRoot = scanObj['measurement']
        instrRoot = scanObj['instrument']
        posnrs = instrRoot['positioners']
        

        # Let's hope they're all the same... :-)
        numFrames = 0
        #print("Positioners:", posnrs.keys())
        for p in posnrs.keys():
            #print("Positioner:", p, "length", posnrs[p].size)
            numFrames = max(numFrames, posnrs[p].size)

        # place data inside "instrument/<name>/data"
        instrRoot.add_node(H5Group(parent=instrRoot, name=instrumentName,
                                   attrs={'NX_class': 'NXinstrument'} ))
        instrObj = instrRoot[instrumentName]

        instrObj.add_node(SpecH5LazyTiffNode(tiffPathFmt=tiffFormat,
                                             numFrames=numFrames,
                                             name="data",
                                             parent=instrObj))

        # create a link inside "measurement" that points to "instrument/<name>/data"
        link_target = instrObj.name.replace('measurement', 'instrument')
        measRoot.add_node(H5SoftLink(name=instrumentName,
                                     path=link_target + "/data",
                                     parent=measRoot))
