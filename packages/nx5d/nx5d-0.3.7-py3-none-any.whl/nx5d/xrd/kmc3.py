#!/usr/bin/python3

#
#        nx5d - The NX5 Duct Tape
#        Copyright (C) 2022-2023 Florin Boariu
#
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

'''
Experiment configuration template to use with `nx5d.xrd.data.ExperimentSetup`.
Contains goniometer and detector layout for the Pilatus detector, as well
as HDF5 addresses for the goniometer and detector angles.
'''
ExperimentTemplate = {
    "goniometerAxes": ('x+', 'y+', 'z+'),
    
    "detectorTARAxes": ("x+", None, None),
    
    "imageAxes": ("x-", "z-"),
    "imageSize": (195, 487),
    "imageCenter": (90, 245),

    # This could also be used instead of 'imageChannelSize' below.
    # It's the same physical quantity, but in degrees/channel
    # instead of relative length.
    "imageChannelSpan": None,

    "imageDistance": "@{positioners}/PilatusYOffset",
    "imageChannelSize": (0.172, 0.172), # same unit as imageDistance (mm)
    
    "sampleFaceUp": 'z+',
    "beamDirection": (0, 1, 0),
    
    "sampleNormal": (0, 0, 1),
    
    "beamEnergy": "@{positioners}/monoE",

    "goniometerAngles": {
        'theta': "@{positioners}/Theta",
        'chi':   "@{positioners}/Chi",
        'phi':   "@{positioners}/Phi" },

    "detectorTARAngles": {
        'azimuth': "@{positioners}/TwoTheta",
    }
}
