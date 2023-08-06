#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Get information from the direct beam measurement. 

Usage:
   XS_getbeamcenter.py [-h]
   XS_getbeamcenter.py <direct beam edf file(s)>
   XS_getbeamcenter.py [-h] [-b <box size>] <direct beam edf file(s)>
   XS_getbeamcenter.py [<some options below>] <direct beam edf file(s)>

Options:
   -h      : this help message
   -o      : write results to file "beam_center.info"
   -d      : date
   -e      : date in seconds since epoch
   -m      : mass (integral = total counts) of the beam inside box
   -n      : mass normalized by box area (intensity per pixel)
   -t      : measurement exposure time
   --cx    : horziontal (x) center position in meters 
   --cz    : vertical (z) center position in meters 
   --px    : horziontal (x) center position in pixels
   --pz    : vertical (z) center position in pixels
   --xprof : beam intensity profile of a horizontal section passing through (cx, cz)
   --xprof : beam intensity profile of a vertical section passing through (cx, cz)
   --skewx : skewness of the horizontal profile of the beam, passing through (cx, cz)
   --skewz : skewness of the vertical profile of the beam, passing through (cx, cz)


This program gets information from the direct beam measurement, as
beam center coordinates in pixels and/or meters, the histogram profile
in x and z directions passing through the beam center and the skewness
of these intensity distributions.

With no options, the program returns all the information. When an
option is given, the program returns just what was asked, in the order
given by the parameters at command line.

All information is by default printed to standard output. To store it
in a file, use '-o'.

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

import calendar
import getopt
import fabio
import numpy as np
import os
import pyFAI
import re
import sys
import time
from numba import jit





#sys.path.append('/usr/local/lib/XS-treatment/')

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

from XS_libgetbeamcenter import get_beam_center as GBC
import XS_libfileutils as LFU


#
def reformat_date(filetime):

    # Check if filetime needs to be reformatted.
    if (re.match('[A-Za-z]{3}', filetime)): return filetime
    
    # Split date and time from filetime.
    sd = filetime.split()

    # Date
    dt = sd[0].split('-')
    D = [ int(d) for d in dt ]
    # Get week day and month in abbreviate format.
    weekday = calendar.day_abbr[calendar.weekday(*D)]
    month = calendar.month_abbr[int(dt[1])]
    # Time
    tm = sd[1]

    # Build time standard string.
    tss = '{} {} {} {} {}'.format(weekday, month, D[2], tm, D[0])
    return tss

#
def set_output (dbeam, gbc, boxsize):
    ''' Set the format for output data.
    '''

    # outd = dictionary with data; outs = string for complete output.
    outd, outs = {}, ''

    # Header.
    outs = ('### Center of mass coordinates, P.O.N.I., and total intensity'
            + ' from direct beam EDF image ###\n')
    
    # Box size.
    outd['boxsize'] = boxsize
    outs += '\n {:<30} {} x {} pixels\n'.format('Box size:', boxsize, boxsize)
    
    # Date.
    dt = reformat_date(dbeam.header['Date'])
    outd['date'] = dt 
    outs += '\n {:<30} {}\n'.format('File date:', dt)
    # Epoch.
    outd['epoch'] = calendar.timegm(time.strptime(dt))
    outs += ' {:<30} {}\n'.format('Epoch file date (s):', outd['epoch'])

    # Exposure time.
    outd['Exptime'] = gbc.Exptime
    outs += ' {:<30} {}\n'.format('Exposure time:', gbc.Exptime)
    
    # Center in pixels.
    outd['center'] = (gbc.Cp[0], gbc.Cp[1])
    outs += '\n {:<30} ({}, {})\n'.format('Center (z, x; in pixels):',
                                      gbc.Cp[0], gbc.Cp[1])
    # Poni.
    outd['poni'] = (gbc.C[0], gbc.C[1])
    outs += (' {:<30} {}\n'.format('P.O.N.I. (in m): ', outd['poni']))

    # Integral mass.
    outd['mass'] = gbc.Mass
    outs += '\n {:<30} {}\n'.format('Total mass (in #):', gbc.Mass)
    # Normalized mass.
    outd['normass'] = gbc.Mass / (boxsize * boxsize)
    outs += ' {:<30} {}\n'.format('Normalized mass (#/pixel):',
                                  outd['normass'])

    # Beam profiles through the center.
    outd['xprofile'] = gbc.xprofile
    outd['zprofile'] = gbc.zprofile
    #outs += ' {:<30}\n'.format('\nBeam profiles through the center:') 
    #outs += '{:<5} {}\n'.format('X = ', outd['xprofile'])
    #outs += '{:<5} {}\n'.format('Z = ', outd['zprofile'])

    # Skewness.
    s, sn = gbc.skewness(gbc.xprofile)
    outd['xskew']  = s
    outd['xskewN'] = sn
    outs += '\n {:<30} {} \t (normalized = {:6.3g})\n'.format('Skewness (x):', s, sn)
    s, sn = gbc.skewness(gbc.zprofile)
    outd['zskew']  = s
    outd['zskewN'] = sn
    outs += ' {:<30} {} \t (normalized = {:6.3g})\n'.format('Skewness (z):', s, sn)
    
    return outd, outs

#
def out_opts (opts, Data, zerotime):
    '''Compose the output from Data defined by argument options opts. Return the
    composed table.

    '''

    # Lambda isopt: returns 0 or 1 if option myopt is defined.
    isopt = lambda myopt : len([ True for o in opts if myopt in o[0] ])
    # Set relative time.
    zt = zerotime if (isopt('-r')) else 0
                
    outs = []
    for o in opts:
        if (o[0] == '-d'):
            outs.append(Data['date'])
        elif (o[0] == '-e'):
            outs.append(Data['epoch'] - zt)
        elif (o[0] == '-t'):
            outs.append(Data['Exptime'])
        elif (o[0] == '--cx'):
            outs.append(Data['center'][1])
        elif (o[0] == '--cz'):
            outs.append(Data['center'][0])
        elif (o[0] == '--px'):
            outs.append(Data['poni'][1])
        elif (o[0] == '--pz'):
            outs.append(Data['poni'][0])
        elif (o[0] == '--skewx'):
            outs.append(Data['xskew'])
            outs.append(Data['xskewN'])
        elif (o[0] == '--skewz'):
            outs.append(Data['zskew'])
            outs.append(Data['zskewN'])
        elif (o[0] == '--zprof'):
            zout  = '# Z, C = {} \n'.format(Data['center'])
            zout += '# time(s), z pixel pos., counts \n'
            for z in Data['zprofile']:
                zout += '{} {} {}\n'.format(Data['epoch'] - zt,
                                            str(z[0]), str(z[1]))
            outs.append(zout)
        elif (o[0] == '--xprof'):
            xout  = '# X, C = {} \n'.format(Data['center'])
            xout += '# epoch(s), x pixel pos., counts \n'
            for x in Data['xprofile']:
                xout += '{} {} {}\n'.format(Data['epoch'] - zt,
                                            str(x[0]), str(x[1]))
            outs.append(xout)
        elif (o[0] == '-m'):
            outs.append(Data['mass'])
        elif (o[0] == '-n'):
            outs.append(Data['normass'])
        else:
            pass

    return outs

#
def print_table(tableData, printoutfile):
    ''' Print out the results from table.
    '''
    target = 'beam_center.info' if printoutfile else None
    output = target and open(target, 'a') or sys.stdout
    for t in tableData:
        for d in t:
            output.write('{} '.format(d))
        output.write('\n')
    output.close()
    return

#
def print_out(OutS, printoutfile):
    '''Print out data table, if there were selected options.
    '''
    target = 'beam_center.info' if printoutfile else None
    output = target and open(target, 'w') or sys.stdout
    output.write(f'{OutS}')
    output.close()
    return

#
def main ():
    '''Get command line options, open file(s) and calculate info with class methods
    accordingly to demand.'''
    
    # Get output option.
    try:
        line = getopt.getopt(sys.argv[1:], "hdemnrtob:", ['cx', 'cz', 'px',
                                                          'pz', 'xprof', 'zprof',
                                                          'skewx', 'skewz'])
    except getopt.GetoptError as err:
        print ('\n\n ERROR: ', str(err),'\b.')
        sys.exit(1)

    opts, files = line[0], line[1]

    # Initialize variable for initial time and for final data.
    zerotime  = 0
    tableData = []
        
    # Define a default box size.
    boxsize = 20
    otheropts = False
    printoutfile = False
    for o in opts:
        if (o[0] == '-h'):
            help('XS_getbeamcenter')
            return
        elif (o[0] == '-b'):
            boxsize = int(o[1])
        elif (o[0] == '-o'):
            printoutfile = True
        else:
            otheropts = True
    
    # Title and opening screen
    title      = 'Beam center information for SAXS data treatment.'
    subheading = 'Complex Fluids Group, IF-USP, Brazil'
    opscreen = LFU.opening_screen('*', title, subheading, __author__,
                                  __email__, __date__,
                                  __copyright__, __version__,
                                  __status__)
    print (opscreen)

    # Check input file.
    if (len(files) == 0):
        print (' ERROR: no file given.')
        sys.exit(1)

    # Open edf file.
    for f in files:
        try:
            dbeam = fabio.open(f)
        except Exception as err:
            print (' ERROR opening file {} : {} '.format(f, err))
            print (' Skipping. ')
            
        # Instantiate beam center information.
        gbc = GBC(dbeam, boxsize)

        # Set dictionary and strings for output data.
        Data, OutS = set_output(dbeam, gbc, boxsize)
        
        # Initial time is taken from first sample.
        if (zerotime == 0): zerotime = Data['epoch']

        # Print out file information or accumulate required data.
        if (otheropts):
            tableData.append(out_opts(opts, Data, zerotime))
        else:
            print_out(OutS, printoutfile)

    # If there were argument options, print data.
    if (len(tableData) != 0):
        print_table(tableData, printoutfile)
    return
                
##
if __name__ == '__main__':
    main()
