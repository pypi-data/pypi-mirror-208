#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Create a p.o.n.i. file from a calibrant edf file or given parameters.

Usage: 
    XS_ponifile.py [<option(s)> <argument>]

With no options, XS_ponifile.py enters interactive mode to read EDF
calibrant file and generate parameters from substance peaks. It works
as a front-end to the pyFAI-calib2 program, from the pyFAI library.

This script is useful to get all necessary information to perform the
calibration, as type of calibrant, detector, measurement (SAXS / WAXS)
etc.

It can be also used to generate a p.o.n.i. file from parameters given
by the user. This option is useful when some calibrant could not
provide peaks for the calibration, but the parameters are known as is
the case of large sample-detector distances.

To directly generate a poni file from given parameters, use the
following command line arguments:

    -d <distance>: sample-detector distance, in meters
    -p <size>: pixel size, in micron
    -r <rotation>: rotation of the detector (axe 1), in rad
    -w <wavelength>: source material (Cr, Cu or Mo)
    -x <pixels>: x-coordinate of the beam center on the detector, in pixels
    -z <pixels>: z-coordinate of the beam center on the detector, in pixels

If not all parameters are given, default values will be used.

This script is part of the XS-treatment suite for SAXS/WAXS data
treatment.

'''

__version__   = '2.4.1'
__author__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__credits__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__email__ = 'dreis@if.usp.br, agolivei@if.usp.br'
__license__ = 'GPL'
__date__   = '2022-09-14'
__status__   = 'Development'
__copyright__ = 'Copyright 2022 by GFCx-IF-USP'
__local__ = 'GFCx-IF-USP'

import datetime
import getopt
import os
import sys
import fabio

import platform
import imp

global saxspath

try: saxspath = imp.find_module("XS-treatment")
except NameError: print ("Error: The module XS-treatment was not installed.");

if platform.system()== "win32" or platform.system()== "Windows" :
    saxspath =saxspath[1]+'\\'
else :
    saxspath =saxspath[1]+'/'

sys.path.append(saxspath)


#sys.path.append('/usr/local/lib/XS-treatment/')
import XS_libfileutils as LFU
from XS_libgetbeamcenter import get_beam_center as GBC

# DEFAULT PARAMETERS.
# Pilatus' pixel size in microns.
PIXELSIZE = 172
# Pilatus 300k default lengths
Xlength = 487.0
Zlength = 619.0
# Rotation values: incident beam is perpendicular to detector plane.
global rot1, rot2, rot3
rot1, rot2, rot3 = 0.0, 0.0, 0.0
# Source wavelength table.
WL = { 'Cu' : '1.5419',
       'Cr' : '2.1910',
       'Mo' : '0.7107'  }

# Pixel-to-meter calculator.
dist_center = lambda x : (x * 0.5) * PIXELSIZE * 1e-6
    
#
def read_edf_data ():
    '''Pick image (edf) file for SAXS/WAXS calibrant.'''
    
    flist = LFU.show_filenames('edf', mandatory=True, instruction=True)
    s = ' Choose image file to generate a \'.poni\' file:'
    filenames = LFU.read_filenames(flist, s, onefile_option=True, mandatory=True)
    
    return filenames[0]

#
def detector():
    ''' Choose the detector.'''
    
    global rot1
    # Available detectors. Warning: Pilatus 300k is just named 'Detector',
    # since its maximum size may change due to eventual merging process.
    detector = { '1' : 'Pilatus300k',
                 '2' : 'Pilatus100k' }
    print ('\n Pick a detector: ')
    detmenu = ['   1) {} (SAXS/WAXS)'.format(detector['1']),
	       '   2) {} (WAXS)'.format(detector['2'])]
    opt = LFU.menu_closed_options(detmenu)
    
    # rot1 is not zero if detector is Pilatus 100k.
    if (opt == '2'): rot1 = '-0.6283'

    # DEBUG
    #print(f' rot1 = {rot1}')
    # DEBUG
    
    return detector[opt]

#
def wavelength():
    ''' Define source wavelength.'''
    
    srcmenu = [ f' {i+1}) {w[0]} ({w[1]} A)' for i, w in enumerate(WL.items()) ] 
    print ('\n Pick source material to define wavelength: ')
    optw = int(LFU.menu_closed_options(srcmenu)) - 1
    wlk = list(WL.keys())

    return float(WL[wlk[optw]])

#
def calibrant():
    '''Define calibrant substance (AgBh, Al2O3, LaB6) from pyFAI data
    base.'''
    
    # Available Calibrant substances.
    calibrants = { '1' : 'AgBh',
                   '2' : 'alpha_Al2O3',
                   '3' : 'LaB6_SRM660c' }
    substmenu = [ '   1) AgBh  \t\t (Silver Behenate)',
                  '   2) Al2O3 \t\t (Corundum)',
                  '   3) LaB6 SRM 660c \t (Lanthanum hexaboride)' ]
    print ('\n Calibrant substance:')
    sopt = LFU.menu_closed_options(substmenu)
    
    return calibrants[sopt]

#
def direct_beam_center(boxsize = 50):
    '''Calculate the coordinates of the beam center from a direct beam EDF
    file. The estimated box size which covers the entire beam (equivalent
    to a ROI square) may be given as an argument. The pixel sizes are
    obtained from the beam file header. The function returns the
    coordinates of the center based on the calculation of center of mass
    in pixels and the pixel sizes.

    '''

    DB = input ('\n Do you want to extract the beam center coordinates'
                + ' from the direct beam file? [Y/n] ')
    if (DB == 'n' or DB == 'N'): return ()
    
    s = ' Pick the direct beam EDF file: '
    flist = LFU.show_filenames('edf', mandatory=True, instruction=True)
    beamfile = LFU.read_filenames(flist, s, onefile_option=True,
                                       mandatory=True)
    
    try:
        # Open edf file.
        dbeam = fabio.open(beamfile[0])
    except Exception as err:
        print (' ERROR opening file {} : {} '.format(beamfile, err))
        sys.exit(1)
        
    # Instantiate the direct beam image class.
    bc = GBC(dbeam, boxsize)

    return bc.C
    
#
def poni_from_parameters (Xc, Zc, dist, rot, wl, pixelsize = PIXELSIZE):
    '''Create a 'poni' file from a set of parameters: beam center at the
    detector (Xc, Zc), sample-detector distance and pixelsize.

    '''
    
    output  = ('# Note: C-Order, 1 refers to the Z axis, 2 to the X axis\n'
               + '# Calibration done at'
               +' {:%a %b %d %H:%M:%S %Y}\n'.format(datetime.datetime.now()))
    output += ('PixelSize1: {}\n'.format(pixelsize)
               + 'PixelSize2: {}\n'.format(pixelsize)
               + 'Distance: {}\n'.format(dist)
               + 'Poni1: {}\n'.format(Zc)
               + 'Poni2: {}\n'.format(Xc)
               + 'Rot1: {}\n'.format(rot[0])
               + 'Rot2: {}\n'.format(rot[1])
               + 'Rot3: {}\n'.format(rot[2])
               + 'Wavelength: {}\n'.format(wl))
    return output

#
def main():
    '''Read command line arguments or enter interactive mode to get
    p.o.n.i. file parameters. Print out p.o.n.i. file.

    '''
        
    try:
        line = getopt.getopt(sys.argv[1:], "hd:p:r:w:x:z:")
    except getopt.GetoptError as err:
        print ('\n ERROR: {}. Aborting.\n'.format(str(err)))
        sys.exit(1)

    if (line[0] == []):
        # Title.
        LFU.section_separator('*','\'.poni\' File Generator')
        print(' Generating \'.poni\' file from edf data...')

        edfdata = read_edf_data()
        det = detector()
        wlength = wavelength()
        calib = calibrant()
        outname = f'{calib}.edf'
        
        # Command to generate '.poni' file. 
        command = [ 'pyFAI-calib2',
                    '--unit q_A^-1',
                    f'--pixel {PIXELSIZE}',
                    f'-r {edfdata}',
                    f'-D {det}',
                    f'-w {wlength}',
                    f'-c {calib}',
                    f'-o {outname}',
                    f'--rot1 {rot1} --fix-rot1',
                    f'--rot2 {rot2} --fix-rot2',
                    f'--rot3 {rot3} --fix-rot3' ]

        # Define the direct beam coordinates or guess from poni file.
        dbc = direct_beam_center()
        if (len(dbc) != 0):
            print ('\n ##### Calculated direct beam center: {dbc} m\n')
            command += [ f'--poni1 {dbc[0]} --fix-poni1', 
                         f'--poni2 {dbc[1]} --fix-poni2' ]
            
        print (' Executing: {} ...'.format(' '.join(command)))
        os.system(' '.join(command))
    else:
        # Define default values (distances in meters).
        pixelsize = PIXELSIZE * 1e-6
        rot = [rot1, rot2, rot3]
        wl = float(WL['Cu']) * 1e-10
        #Xc, Zc = dist_center(Xlength), dist_center(Zlength)
        Xc, Zc = dist_center(Xlength), dist_center(Zlength)
        dist = 0.86

        opts = line[0]
        for o in opts:
            if (o[0] == '-h'):
                help('XS_ponifile')
                return
            elif (o[0] == '-d'):
                dist = float(o[1])
            elif (o[0] == '-p'):
                pixelsize = float(o[1]) * 1e-6
            elif (o[0] == '-r'):
                rot[0] = float(o[1])
            elif (o[0] == '-w'):
                wl = float(WL[o[1]]) * 1e-10
            elif (o[0] == '-x'):
                Xc = float(o[1]) * pixelsize
            elif (o[0] == '-z'):
                Zc = float(o[1]) * pixelsize
            else:
                print (' Option \'{}\' not recognized. Aborting.\n'.format(o[0]))
                sys.exit(1)

        print(poni_from_parameters(Xc, Zc, dist, rot, wl, pixelsize))
       
    return 0


## 
if __name__ == "__main__":
    main()
