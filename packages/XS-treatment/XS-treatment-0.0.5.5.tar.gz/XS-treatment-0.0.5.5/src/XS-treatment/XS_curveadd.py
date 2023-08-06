#!/usr/bin/python3
# -*- encoding: utf-8 -*-

'''Add up or average over a set of curves.

Usage:
   XS_curveadd.py [-hansw] <file(s)>

where: 
  h: show this help message and exit
  a: only add curves, do not normalize by counts and time
  s: file has no header (3 lines, with detector, time etc.)
  w: do not write out header file with sum of total time and counts
     (maybe good for rad files, not for RDS files).

This program averages or adds up the ordinates in the second column of
<files> and propagates the errors in the third column, providing they all
have the same abscissas (first column). Averaging is done by weighing
relative times of measurement. If an abscissa x0 of a given set has no
correspondent in other sets, a new line with the triple (x0, 0.0, 0.0) is
inserted in these other sets.

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

import getopt
from math import sqrt
import re
import numpy as np
import os
import sys

import sys
import platform
import imp

import sys
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

##
def cmd_line ():
    '''Get file names and options from command line and return a list of files
    and flags. Options are:

    -h : show help message and exit.
    -a : proportionally add curves, but do not normalize by counts and time (result is adimensional)
    -s : file has no header (with time, detector and other info)
    -w : write out header with total time and counts, returns 'writeheader'

    '''
    
    try:
        optline = getopt.getopt(sys.argv[1:], "handswS:")
    except getopt.GetoptError as err:
        print ('\n\n ERROR: {}. Aborting.'.format(str(err)))
        sys.exit(1)
        
    # Default options: do normalization, skip header lines when reading
    #the data sets, and do not write out final header.
    opts = optline[0]

    # Define defaults. prm is a dictionary of all command line options.
    prm = { 'doaverage'     : True,
            'doskipheader'  : True,
            'dowriteheader' : True,
            'subtractfile'  : []
           }
    
    for o in opts:
        if   ( o[0] == '-h' ):
            help('XS_curveadd')
            sys.exit(0)
        elif ( o[0] == '-a' ):
            prm['doaverage'] = False
        elif ( o[0] == '-s' ):
            prm['doskipheader'] = False
        elif ( o[0] == '-w' ):
            prm['dowriteheader'] = False
        elif ( o[0] == '-S' ):
            prm['subtractfile']  = [ o[1] ]
        else:
            print(f' WARNING: Option \'{o[0]}\' not recognized.'
                  ' Aborting.')
            sys.exit(1)
                
    # Create files list and check if all they exist.
    if (len(optline[1]) == 0):
        print (' No files specified.'
               ' Give at least one file to be processed.')
        sys.exit(0)
    else:
        files = optline[1]
        for f in files:
            if (not os.path.isfile(f)):
                print (f' File "{f}" not found in current directory.'
                       f' Aborting.')
                sys.exit(1)

    return files, prm


##
def read_data (files, prm):
    '''Open all files, read their content and return a list with it.'''

    # List of file handlers.
    pfiles = []
    # List with all data sets.
    data = []
    # List of detector (pin diode) intensities.
    detector = []
    # List of measurement times.
    Times = []
    #
    skiplines = 0
    
    # Read data from files.
    dataF = {}
    for FL in files:
        print(f' Reading data from file {FL} ...', end=' ')
        with open(FL, 'r') as pF:
            dataF[FL] = pF.read().splitlines()
        print('done.')
            
    for FL, DT in dataF.items():
        try:
            # Read measurement time and counts.
            linedata = re.sub("#", "", DT[1]).strip().split()
            Times.append(float(linedata[0]))  # Time
            detector.append(float(linedata[1]))    # Detector counts
        except Exception as err:
            print('\n WARNING: could not extract Time/Counts information'
                  f' from {FL}. Check header file.\n Exception: {err} \n')
       
        # Scan lines and extract three first columns, casting strings
        # to floats. Skip the 3 first lines (Time/Detector already
        # read above) and ignore extra columns. Store previous header
        # info, if it exists..
        dat, header = [], ''
        if prm['doskipheader']: skiplines = 3 
        for line in DT[skiplines:]:
            if (re.match('^#', line)):
                header += f'{line}\n'
                continue
            dat.append([ float(x) for x in line.split() ][:3])
        data.append(dat)
        
    return data, detector, Times, header

##
def get_abscissas (data):
    '''Return a list with all abscissas of all measurement.'''
    return sorted(set([ x[0] for d in data for x in d ]))

##
def include_subtraction (prm, data):
    '''Include subtraction of curve(s). [** WARNING: under development! ]'''
    dataSub, detectorSub, totalTimeSub, header = read_data(prm)
    normalize_by_time(dataSub, detectorSub, totalTimeSub, prm)
    # Reverse intensity values for subtraction.
    for e in dataSub[0]: e[1] = -e[1]
    return dataSub[0], detectorSub, totalTimeSub, header
            
##
def add_data (data, Qs, detector, Times, prm):
    '''Scan data lines, identify equal abscissas (Qs), add second row elements
    and propagate errors from the third row. The average is made by the
    number of elements with the same Q and proportional times. Input:
    'data' are all data sets (lists of triples q, I, sI); 'Qs' is the set
    of all abscissas of all sets; detector is the list of detector
    measured values; Times is the list of measurement time of all sets;
    prm is the list of parameters defined in command line (or
    defaults). The function returns the sum or the average of data sets.

    '''

    # Define an abscissa counter for each data set.
    Ndata = len(data)
    Cnt = [ 0 for i in range(Ndata) ]

    # Normalization by transmission (counts/s) and time rates, rate = detector
    # (counts/s) * exposure time = 1 / counts. In RDS files, intensities are in
    # absolute scale, so detector counts and exposure time are set to 1, which
    # makes no diference here.
    Nrate = np.array([ 1./(n * t) for n, t in zip(detector, Times) ])
    
    # Run over all abscissas. If a set has the given Q-abscissa, the
    # intensity is taken into account. The average is performed over
    # those intensities only.
    datasum = []
    for Q in Qs:
        Itot, sigma = 0.0, 0.0
        # Flags to include only defined q values.
        Setnorm = np.zeros(Ndata)
        # Scan data sets to corresponding Q.
        for k, dt in enumerate(data):
            # k-th data set, cn-th line.
            cn = Cnt[k]
            # Check whether cn-th element in data set k corresponds to
            # abscissa Q, provided cn is still in a valid range.
            if (cn < len(dt) and dt[cn][0] == Q):
                # Add intensity proportionally to rate.
                Itot += dt[cn][1] * Nrate[k]
                # Propagate error.
                s = dt[cn][2] * Nrate[k]
                sigma += s * s
                    
                # Increase counter (next line in k-th data set).
                Cnt[k] += 1
                # Q-value is defined, consider Itot.
                Setnorm[k] = 1.
                
        # Normalize average. This procedure accounts for the number of curves
        # added, also in the case of 'detector' and 'time' set to 1.
        if (prm['doaverage']):
            totrate = 1. / np.sum(Nrate * Setnorm)
            Itot *= totrate
            sigma = sqrt(sigma) * totrate    # Standard deviation.
        datasum.append([Q, Itot, sigma])

    return datasum

#
def output_file (filenames, prm):
    '''Name of the output curve file.'''

    numbers = []
    
    for f in filenames:
        nn = re.search('([0-9]{5})\.[Rr]', f).group(1)
        numbers.append(str(int(nn)))
    bn = re.search('([.\w-]+?)_', f)
    if bn: basename = bn.group(1).strip('_')
    wrhead = '' if prm['dowriteheader'] else '_NH'

    numext = '{}'.format('+'.join(numbers))
    addtype = 'avr' if (prm['doaverage']) else 'sum'
    fileext = os.path.splitext(filenames[0])[1]
    outname = f'{basename}_{numext}_{addtype}{wrhead}{fileext}'

    return outname
    
#
def printout_file (outname, header, datasum):
    '''Write out header and data to file. '''
    
    # Remove file, if it exists.
    if os.path.exists(outname): os.remove(outname)

    with open(outname, 'w') as of:
        of.write(header)
        for line in datasum:
            of.write(' {:15.8f} {} {} \n'.format(*line))

    print(f' Average written out to {outname}. End.')
    return
        

##
def main ():
    '''This program takes the data files given in the command line and
    add up the second columns of each respectively, propagating the errors
    in the third column. It considers the abscissas as equal (the x
    coordinates coincide). In future versions, the program should add
    curves in the correct intervals, regardless the coincidence of points
    in abscissas.

    '''

    # Get parameters and files from command line.
    files, prm = cmd_line()
                
    # Read data files and return a list with their content,
    # measurement times and the respcetive countings.
    data, detector, Times, header = read_data(files, prm)

    # Repeat procedures for file to be subtracted.
    if (len(prm['subtractfile']) != 0):
        DataSub, DetSub, totTSub = include_subtraction(prm)
        data.append(DataSub)
        detector   += DetSub
        Times += totTSub
    
    # Get the set of all times in all data sets (in sorted order).
    Qs = get_abscissas(data)
        
    # Add up all data with due normalizations.
    datasum = add_data(data, Qs, detector, Times, prm)
    
    # Print data sum to standard output.
    if (prm['dowriteheader']):
        # Normalize each detector count by respective exposure time and
        # add it up.
        if (prm['doaverage']):
            totTime, totDet = 1.0, 1.0
        else:
            totTime = np.sum(Times)
            totDet = np.sum([ d * T for d, T in zip(detector, Times) ]) / totTime
            
        # New header contains '#' at the beginning of lines for compatibility
        # with graphic softwares.
        header = (f'#\tTime\tDetector\n'
                  + f'#\t{totTime}\t{totDet}\n'
                  + f'# {len(datasum)}\n'
                  + header)
    else:
        header = ''
    
    outname = output_file(files, prm)
    printout_file(outname, header, datasum)
    
#
if __name__ == "__main__":
    main()
