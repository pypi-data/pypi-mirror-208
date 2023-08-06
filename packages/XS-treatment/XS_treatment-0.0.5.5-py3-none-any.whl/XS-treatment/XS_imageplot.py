#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Plot 2D edf images. With no options, enter interactive mode.

Usage: 
  XS_imageplot.py [-hbqs] [-i <format>] [<files>]

where:
  h: this help message.
  b: plot color bar (default: no color bar).
  g: color scheme is gray scale (default: colored).
  i: image format; available formats are: 
    {', '.join(LIP.im_supported)}.
  m: map scale, may be "log" (the default) or "lin".
  q: quiet, do not show the image (for batch mode). Without "-s", do
     nothing.
  s: save image (default: do not save).
  <files>: list of files.

OBS. If only a few options are provided, defaults are used otherwise.
If any option is given, <files> is obligatory. Alternatively, use
interactive mode (no options).

Typical use (in batch mode):
  ximageplot.py -q -s -i png file1.edf file2.edf ...

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
import gzip
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import fabio
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

#sys.path.append('/usr/local/lib/XS-treatment/')
import XS_libimageplot as LIP

    
#
def parse_args (opts, filenames):
    '''Parse command line arguments.
    '''

    # Define default parameters.
    global fopt
    fopt = LIP.fopt
    
    if (len(opts) == 0 and len(filenames) == 0):
        fopt, filenames = LIP.menu_options()
        return fopt, filenames

    if (len(opts) != 0):
        for o in opts:
            if ( o[0] == '-h'):
                '''Help message.'''
                help('XS_imageplot')
                sys.exit(0)
                
            elif ( o[0] == '-b' ):
                fopt['colorbar'] = True
            elif ( o[0] == '-g' ):
                fopt['color'] = False
            elif ( o[0] == '-m' ):
                fopt['cmapscale'] = o[1]
            elif ( o[0] == '-q' ):
                fopt['quiet'] = True
            elif ( o[0] == '-s' ):
                fopt['saveimage'] = True
            elif ( o[0] == '-i' ):
                fopt['imageformat'] = o[1]
                if ( fopt['imageformat'] not in LIP.im_supported ):
                    print (' Image format ({}) not recognized.'.format(fopt['imageformat'])
                           + ' See help (-h). Aborting.')
                    sys.exit(1)
            else:
                print (' Option "{}" not recognized. Aborting.\n'.format(o[0]))
                sys.exit(1)
            
        if ( len(filenames) == 0 ):
            print (' No files specified. See help (option -h).')
            sys.exit(1)

    return fopt, filenames

# ...
def main():
    '''Plot 2D edf images. Color scale may be lin or log; image may be saved (or
    not) in several formats (see LIP.im_supported); colorbar may be plotted.

    '''
    
    # Clear current terminal screen before start
    #os.system('clear')

    # Enter options and files. 
    try:
        opts, filenames = getopt.getopt(sys.argv[1:], "hbgqsi:m:")
    except getopt.GetoptError as err:
        print ('\n ERROR: {}. Aborting.\n'.format(str(err)))
        sys.exit(1)

    # Plot images with given parameters.
    LIP.plot_images(*parse_args(opts, filenames))

    return
    
#
if __name__ == "__main__":
    main()
