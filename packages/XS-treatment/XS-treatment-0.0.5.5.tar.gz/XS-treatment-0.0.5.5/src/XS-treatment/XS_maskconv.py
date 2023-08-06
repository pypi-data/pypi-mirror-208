#!/bin/python3
# -*- encoding: utf-8 -*-

'''Convert mask files.

Usage:
  XS_maskconv.py -h 
  XS_maskconv.py -i <infile> [-o <outfile>]
 
Where: 
  -h             : this help message
  -i <infile>    : input mask file name
  -o <outfile>   : output mask file name
    
 Accepted types of mask are: 
 - msk \t (fit2d)
 - txt \t (Foxtrot numpy-array)
 - npy \t (numpy binary format)

 OBS.: The extensions of the files are used as mask type identifier.

This script is part of the XS-treatment suite for SAXS WAXS data
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
import numpy as np
import os
import sys

global acceptmask
acceptmask = { 'msk' : 'fit2d',
               'txt' : 'Foxtrot numpy-array',
               'npy' : 'numpy binary format' }

##
def cmd_args():
    '''Reads command line options. Returns input and output file names and
    respective mask types.'''
    
    try:
        line = getopt.getopt(sys.argv[1:], "hi:o:")
        if (len(line[0]) == 0):
            print('ERROR: No arguments given.'
                  +' Rerun with "-h" option to see alternatives.'
                  +' Quitting.')
            sys.exit(1)
    except getopt.GetoptError as err:
        warning = ' ERROR: ' + str(err) + '.'
        print (warning)
        sys.exit(1)

    outfile = ""
        
    opts = line[0]
    for o in opts:
        if (o[0] == '-h'):
            help('XS_maskconv')
            sys.exit(0)
        elif (o[0] == '-i'):
            # Input mask file.
            infile  = o[1]
        elif (o[0] == '-o'):
            # Output mask file.
            outfile  = o[1]
        else:
            pass

    intype  = os.path.splitext(infile)[1].strip('.')
    outtype = os.path.splitext(outfile)[1].strip('.')
        
    if intype not in acceptmask.keys():
        print(' ERROR: input mask type "{}" not recognized. '.format(outtype))
        sys.exit(1)

    if outtype not in acceptmask.keys():
        print(' ERROR: output mask type "{}" not recognized. '.format(outtype))
        sys.exit(1)

    return (intype, outtype, infile, outfile)
    
    

##
def main ():
    '''Convert mask types.
    '''

    # Input and output file names and types.
    intype, outtype, infile, outfile = cmd_args()

    # Import data from input file.
    try:
        if (intype == 'txt'):
            msk = 1- np.loadtxt(infile, dtype='uint8', delimiter=';')
        elif (intype == 'npy'):
            msk = np.load(infile)
        elif (intype == 'msk'):
            # Fit2D mask, open it using fabio module
            msk = fabio.open(infile).data
        else:
            print(' No files imported. Quitting.')
            sys.exit(0)
            
    except Exception as err:
        print(f'ERROR importing file {infile}: {err}')
        sys.exit(1)

    # Export data to output file.
    try:
        if (outtype == 'txt'):
            newmsk = 1 - msk
            np.savetxt(outfile, newmsk, fmt='%d', delimiter=';')
        elif (outtype == 'npy'):
            np.save(outfile, msk)
        elif (outtype == 'msk'):
            # Fit2D mask, open it using fabio module
            msk.save(outfile)
        else:
            print(' No files exported. Quitting.')
            sys.exit(0)
        
    except:
        print('ERROR exporting file {} : {}'.format(outfile, err))
        sys.exit(1)

    print('Done.')


if __name__ == "__main__":
    main()
