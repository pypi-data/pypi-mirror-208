#!/usr/bin/python3

'''
Experiment geometry defintion dictionary as needed by `LazyQMap`.
Strongly influenced by typical `xrayutilities` API. This was 
the correct geometry at one point in time (for proposal 3381/Bargheer
in April 2023), but might have changed for *your* experiment.
'''
experimentTemplate = {
    "goniometerAxes": ('y-', 'z+', 'x+'),
    "detectorTARAxes": ("y-", None, None),

    "imageAxes": ("y-", "x+"),
    "imageSize": "$/detector_size",
    "imageCenter": "$/detector_centre",

    # same unit as imageChannelSize
    "imageDistance": "@/sdd",

    # same unit as imageDistance (mm)    
    "imageChannelSize": ("@/pixel_size", "@/pixel_size"),

    "imageSize": "@/detector_size",

    'sampleFaceUp': 'x-',

    'beamDirection': (0, 0, 1),
    'sampleNormal': (1, 0, 0),

    "beamEnergy": "@/photon_energy",

    'goniometerAngles': {'omega': '@/omega', 'chi': '@/chi', 'phi': '@/phi'},
    'detectorTARAngles': {'2theta': '@/twotheta', },
}
