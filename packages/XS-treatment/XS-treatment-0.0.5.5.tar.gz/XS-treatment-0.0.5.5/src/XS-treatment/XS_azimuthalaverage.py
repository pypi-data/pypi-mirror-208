#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Calculate SAXS/WAXS q x I(q) curves by azimuthally integrating EDF files.

Usage:
    XS_azimuthalaverage.py [-e] -f <file>
or  XS_azimuthalaverage.py -me
or  XS_azimuthalaverage.py -h

where:
  -h : this message
  -e : examine each curve graphic (default is quiet)
  -m : read parameters from interactive menu
  -f <file> : read parameters from <file>. (Use the program
              extract_saxslog.py to create a parameters file from a
              xlsx spreadsheet log file.

This program calculates the intensity curves resulting from azimuthal
integration over given angular intervals of EDF files performed by the
Python 3 pyFAI Module. The program reads sample, background, shadow,
noise (dark), water (absolute normalization) and mask files, and
performs due integrations, then add or subtracts and normalizes the
resulting curves. The results are written in text format with three
columns (q, intensity, sigma_intensity) and a header with lines
preceeded by '#'.

This script is part of the XS-treatment suite for SAXS/WAXS data
treatment.

'''

__version__   = '2.4.1'
__author__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__credits__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__email__ =  'dreis@if.usp.br ,agolivei@if.usp.br'
__license__ = 'GPL'
__date__   = '2022-09-14'
__status__   = 'Development'
__copyright__ = 'Copyright 2022 by GFCx-IF-USP'
__local__ = 'GFCx-IF-USP'

import copy
import fabio
import getopt
import glob
import itertools
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import re
import scipy.signal
import sys
import time
import pyFAI

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
import XS_libnormalizations as LNORM
import XS_libreadparameters as LRP
import XS_libazimuthalaverage as LAZ






mpl.rc('mathtext', default='regular')
#plt.rcParams['font.size'] = 12.0

   

##
def curve_treatment (fdict, nfactor, fdir='.', fromfile=False,
                     multisubt=True, examine=False):
    '''Data treatment from RAD files.'''

    # Options for background files and corresponding subtractions
    scales = []
    transmittances = []

    try:
        fnoise  = fdict['NOISE']
    except:
        fnoise  = []
    #
    try:
        fshadow = fdict['SHADOW']
    except:
        fshadow = []

    # (i) Azimuthal averaging of files with no background.
    
    # Warning about no background.
    if (fdict['BACKGROUND'] is None or len(fdict['BACKGROUND']) == 0):
        subt_option = 'No backgrounds provided, performing only azimuthal averaging.'

    # (ii) One background file only.
    elif (len(fdict['BACKGROUND']) == 1):
        subt_option = 'Only one background file for subtraction.'
        try:
            fback   = fdict['BACKGROUND'][0]
        except:
            fback   = []
        
        # Loop over samples' files.
        for sample in fdict['SAMPLE']:
            dt_result = LAZ.subtract_intensity_curves(sample, fback, fnoise,
                                                      fshadow, nfactor, fdir,
                                                      examine)
            scales.append(dt_result[3])
            transmittances.append(dt_result[4])

    # (iii) Multiple background files.
    else:
        if (not fromfile):
            print('\n Options for multiple background subtractions: ')
            multi_options = ['   1) One-to-one ordered association',
                             '   2) Subtract each background file from all samples']
            opt = LFU.menu_closed_options(multi_options)
            multisubt = False if opt == 1 else True
            
        # (iii-a) One-background-to-one-sample (1-to-1) association.
        if (multisubt == False):
            # Check if background and sample arrays have same length. Quit if not. 
            if (not (len(fdict['BACKGROUND']) == len(fdict['SAMPLE']))):
                print(' Background and sample arrays have different lengths.')
                print(' Equal lengths is mandatory for this option. Quitting.')
                sys.exit(1)
            else: 
                subt_option = 'Multiple background files: one-to-one ordered association.'

            print(' WARNING: subtracting backgrounds in one-to-one association.')
            for sample, bkgd in zip(fdict['SAMPLE'], fdict['BACKGROUND']):
                dt_result = LAZ.subtract_intensity_curves(sample, bkgd, fnoise,
                                                          fshadow, nfactor,
                                                          fdir, examine) 
                scales.append(dt_result[3])
                transmittances.append(dt_result[4])

        # (iii-b) Subtract all background files from each sample.
        else:
            print(' WARNING: subtracting all backgrounds from each sample file. ')
            subt_option = ('Multiple background files: subtract all'
                           ' background files from each sample.')
            # loop over backgrounds' files
            for bkgd in fdict['BACKGROUND']:
                # loop over samples' files
                for sample in fdict['SAMPLE']:
                    dt_result = LAZ.subtract_intensity_curves(sample, bkgd,
                                                              fnoise, fshadow,
                                                              nfactor, fdir,
                                                              examine)
                    scales.append(dt_result[3])
                    transmittances.append(dt_result[4])

    return subt_option, scales, transmittances

##
def scattering_data_treatment (prm):
    '''Define treatment conditions, perform azimuthal average and subtract
    files with suitable normalizations. 

    '''

    wdict = {}
    
    # Water normalization option uses data_treatment() routine, therefore
    # preliminary integrations are solved here.
    if ('WATER' in prm.intparam['NORM']):
        # Concatenate iterables.
        #wlist = list(itertools.chain(*fdict.values()))
        # Loop over edf files
        for item, wfile in prm.normdict.items() :
            wdict[item] = []
            if (wfile != []):
                circle = [-180.0, 180.0]
                water_res = LAZ.azimuthal_average(wfile[0], prm, circle)
                # Names are changed after integration.
                wdict[item].append(f'{water_res[0]}.rad')
                
        # Data treatment
        LFU.section_separator('*', 'Data Treatment for Water')
            
        # r = (q, I, sigma, scale, ratio)
        watersub = LAZ.subtract_intensity_curves(wdict['WATER'][0],
                                                 wdict['EMPTY'][0],
                                                 wdict['NOISE'],
                                                 wdict['SHADOW'], 1.0, 'rad',
                                                 prm.examine)
        
        # Calculate the normalization factor.
        parfilename = wdict['WATER'][0].replace('.rad', '.PAR')
        prm.normfactor = LNORM.water(wdict, parfilename,
                                      prm.intparam['MASK'][0],
                                      prm.aintegrator, *watersub)
        
    # Angles for integration.
    phis = prm.intparam['ANGLES']
    
    # LFU.section_separator('*','Options for Azimuthal Averaging ')

    # Table (dictionary) of data files: samples, backgrounds, noise and shadow.
    fdict = {}
    for item in ['SAMPLE', 'BACKGROUND', 'NOISE', 'SHADOW']:
        if (item in prm.intparam):
            fdict[item] = prm.intparam[item]

    # Dictionary for file names after integration.
    newfdict = {}
    # Loop over all edf files for averaging.
    for item in fdict:
        # Skip if the (non mandatory) parameter is not defined.
        if (fdict[item] == None):
            newfdict[item] = None
            continue
        else:
            newfdict[item] = []

        # Loop over all integration intervals.
        for phi in phis:
            print(f'\n Integrating over: {phi}')
            # Loop over edf files of each item.
            for datafile in fdict[item]:
                # Azimutal averaging.
                data_res = LAZ.azimuthal_average(datafile, prm, phi)
                # Names are changed after integration.
                newfdict[item].append(f'{data_res[0]}.rad')

                # Formerly, rad files were recorded by this routine instead of
                # using integrate1d rsource.
                # LFU.write_file(*data_res, fileext='rad')

    # Absolute scale normalization.
    print(f'\n Normalization factor: {prm.normfactor:.3e}')
    
    # 
    LFU.section_separator('*', 'Results for Data Treatment')
    records = []

    # Curve subtractions.
    for phi in phis:
        #oldext = '.edf'
        #newext = '_{0:=+04.0f}_{1:=+04.0f}.rad'.format(phi[0], phi[1])
        #tempfdict = LFU.change_fileext(copy.deepcopy(prm.intparam),
        #oldext, newext)
        subtopt, scales, transmittances = curve_treatment(newfdict,
                                                          prm.normfactor,
                                                          fdir='rad',
                                                          fromfile=prm.fromfile,
                                                          multisubt=prm.multisubt,
                                                          examine=prm.examine)
        records.append([phi, subtopt, scales, transmittances])

    return records

##        
def write_log_file (prm, records, opscreen):
        
    # Processed data and frame integration options assigned to
    # 'info' variable to print and save. Just in the end of the
    # program to avoid the register of analysis stopped by errors.
    tm = time.strftime("%Y-%m-%d %H:%M:%S")
    sep = 80 * '*'
    header = (f'\n\n XS_azimuthalaverage: '
              f'\n\n{sep}\n Date: {tm}'
              f'\n Directory: {os.getcwd()}'
              f'\n Used Python modules: '
              f'\n\t {fabio.__name__} {fabio.version} {fabio.__status__}'
              f'\n\t {pyFAI.__name__} {pyFAI.version}'
              f'\n\t {__file__} -- {__version__} -- {__status__}\n')
    
    info = ''
    for k, P in prm.intparam.items():
        #for item in prm.intparam[k]:
        try:
            if (k == 'ANGLES'):
                info += f'\n\t{prm.description[k]}\n\t\t{P}'
            else:
                info += '\n\t{}\n\t\t{}'.format(prm.description[k], '\n\t\t'.join(P))
        except Exception as err:
            print(f'ERROR: {err}')
        
    for record in records:
        transm = ['{0:.2f}'.format(tmt) for tmt in record[3] ]
        info += (f'\n\n {"Azimuthal angle range (in degrees)":.<45}'
                 f'[{record[0][0]:4.1f}, {record[0][1]:4.1f}]' 
                 f'\n {"Options for background subtraction ":.<45}{record[1]}'
                 f'\n {"Scales for background subtraction ":.<45}{record[2]}'
                 f'\n {"Transmittance ratio (Tback/Tsample) ":.<45}{transm}'
                 f'\n\n Azimuthal integrator data \n\n{prm.aintegrator}' )
        
    # Generate and print record file
    with open(prm.logfile, 'a') as recfile:
        recfile.write(opscreen)
        recfile.write(header)
        recfile.write(info)        

    # Repeat log information to stdout.
    print(header)
    print(info)

    return
        

##
def main ():
    # Read all parameters (from file or command line).
    try:
        line = getopt.getopt(sys.argv[1:], "hemf:")
    except getopt.GetoptError as err:
        print('\n\n ERROR: ', str(err),'\b.')
        sys.exit(1)

    prm = LRP.read_parameters(line)

    # Help message.
    if (prm.help):
        help('XS_azimuthalaverage')
        return
    
    # Title and opening screen
    title = 'Frame Integrator for SAXS Data Treatment'
    subheading = 'Complex Fluids Group, IF-USP, Brazil'
    opscreen = LFU.opening_screen('*', title, subheading, __author__,
                                   __email__, __date__, __copyright__,
                                   __version__, f'({__status__})')
    print(opscreen)
    
    # Treat data.
    records = scattering_data_treatment(prm)
    
    # Print out and record results.
    write_log_file(prm, records, opscreen)
    
    return

if __name__ == "__main__":
    main()
