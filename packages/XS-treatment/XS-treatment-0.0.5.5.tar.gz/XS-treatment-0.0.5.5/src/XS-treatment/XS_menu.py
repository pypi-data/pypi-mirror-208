#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Show an interactive menu for XS-treatment suite.

Usage:
  The menu is interactive, just run XS_menu.py.

This menu acts a guide for the main operations to be performed along a
SAXS/WAXS data treatment process.

CAVEAT. This menu is intended as a mere guide to the suite data treatment and
does not fulfill all possibilities neither some necessary operations for each
case. The best option is to run each script individually, after reading its
instructions with the help option (run the XS script with -h option).  Also,
you can run XS_help.py to read general instructions.

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

import sys
import os

#global saxspath
#saxspath = '/usr/local/lib/XS-treatment/'
#sys.path.append(saxspath)

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

import XS_extractlog as extractlog
import XS_azimuthalaverage as xazimuthalaverage
import XS_curveplot as xcurveplot
import XS_libfileutils as LFU
import XS_imagemerge as ximagemerge
import XS_imageplot as ximageplot
import XS_imageadd as ximageadd
import XS_ponifile as xponifile
import XS_help as xhelp

# Title and opening screen.
sep = '*'
title = 'SAXS / WAXS Data Treatment'
subheading = 'For XEUSS at Group of Complex Fluids, IFUSP, Brazil '

# Menu of operations.
menu_options = {
    'param'      : 'Extract parameters from log file',
    'f_az_avrg'  : ('Azimuthal averaging and data treatment,'
                    ' read parameters from saxs_parameters file'),
    'm_az_avrg'  : ('Azimuthal averaging and data treatment,'
                    ' read parameters from command line'),
    'sum'        : 'Sum of images',
    'merge'      : 'Merge images',
    'plot1D'     : 'Plot scattering curves (1D curves)',
    'plot2D'     : 'Plot scattering images (2D \'edf\' images)',
    'points'     : 'Extraction of points\' coordinates from 1D curves',
    'poni'       : '\'.PONI\' file generator',
    'help'       : 'Help guide with generic instructions',
    'menuhelp'   : 'Help for this menu.',
    'quit'       : 'Exit program'
}


# Dictionary for executables.
program = {
    'poni'       : 'xponifile.main()',
    'param'      : 'extractlog -m',
    'sum'        : 'ximageadd.sum_images()',
    'merge'      : 'ximagemerge.merge_images()',
    'f_az_avrg'  : 'xazimuthalaverage -rs -f saxs_parameters',
    'm_az_avrg'  : 'xazimuthalaverage -m',
    'plot1D'     : 'xcurveplot.plot_curves_menu()',
    'plot2D'     : 'ximageplot.plot_images_menu()',
    'points'     : 'xcurveplot.curve_analysis_menu()',
    'help'       : 'xhelp',
    'menuhelp'   : 'help("XS_menu")',
    'quit'       : 'quit()',
}

# Enumrated dictionary for program keys list.
seq = { str(i + 1) : v for i, v in enumerate(program) }


##
def main ():
    '''Show the menu options and execute the respective programs chosen. '''
    
    opscreen = LFU.opening_screen(sep, title, subheading, __author__,
                                  __date__, __version__)
    print (opscreen)

    # ...
    print('\n  Codes for operations and data treatment of X-ray scattering data.'
          '\n  Choose one of the following options:' )
    opt = LFU.menu_closed_options(menu_options, seq)
    
    if (seq[opt] == 'quit'):
        exec(program['quit'])
    if (seq[opt] == 'menuhelp'):
        eval(program['menuhelp'])
    elif (seq[opt] in ['param', 'f_az_avrg', 'm_az_avrg' ]):
        os.system(saxspath + program[seq[opt]])
    else:
        print (' Executing ', program[seq[opt]], '...')
        exec(program[seq[opt]])

##
if __name__ == "__main__":
    main()


'''
## Old list.

if   opt=='1': xazimuthalaverage.scattering_data_treatment()
elif opt=='2': ximageadd.sum_images()
elif opt=='3': ximagemerge.merge_images()
elif opt=='4': xcurveplot.plot_curves_menu()
elif opt=='5': ximageplot.plot_images_menu()
elif opt=='6': xcurveanalysis.curve_analysis_menu()
elif opt=='7': xponifile.ponifile_generator()
'''
