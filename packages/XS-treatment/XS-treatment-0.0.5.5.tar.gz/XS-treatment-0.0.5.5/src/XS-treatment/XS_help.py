#!/usr/bin/python3
# -*- encoding: utf-8 -*-

'''General description of the SAXS/WAXS XS-treatment suite.

Here it is presented a summary of the basic procedures for the SAXS/WAXS data
treatment using the scripts. For detailed explanations, run each script with -h
(help) option.

 0) You can use the program

$ XS_menu.py

as a guide through the sequence of steps for the data treatment, since
it works as a menu for the core programs. Be aware that many options
below are quite restricted in XS_menu.py. A reasonable option is to
read the sequence below and use XS_menu.py altogether with advanced
options of specific programs, as in item 2, if necessary.

 1) Get the beam center and generate a poni file.

It is absolutely necessary to know the center of the beam and the
sample-detector distance.  Enter the directory with the 
behenate / corundum / LaB6 EDF file and:

 1.a) You can obtain an accurate position of the beam center with

$ XS_getbeamcenter.py <beam-center EDF file>

Which will provide many informations about the beam center, including its
profile characteristics. The beam center coordinates may be used afterwards for
the p.o.n.i file generation. It is possible to get specific information about
the beam profile, get the options with -h.

 1.b) Calculate the sample-detector distance with

$ XS_ponifile.py

Just follow the procedures through the interactive menus. At the end, a
<name>.poni file must have been created. YOu can use the data from 1.a for the
beam center; take due care to check that this information is correctly inserted
and used in the pyFAI-calib2 respective field.

 2) Extract parameters for integration from a log spreadsheet xlsx file.

This step considers the existence of a log file of the experiment,
according to some standards, which can be read from

$ XS_extractlog.py -h

An example log file (saxs_log_example.xlsx) is provided with the suite. The
main idea is to organize all the sets for the treatment under separate
dierctories (folders). It can be useful in the case of many samples or for
measurements of the same sample at many different temperatures.

A generic use of XS_extractlog.py would be, for instance,

$ XS_extractlog.py -sr -f saxs_log.xlsx -i <n>

which will extract all parameters from file saxs_log.xlsx, create directories
with the names of samples (-s) and renamed (-r) links to the original EDF files
inside the new directories (new names are based on the description of the log
file). The option -i <n> stands for the n-th sheet in the saxs_log file (0 is
the default). The program creates a directory named 
Treatment__<n>__<sheet name> for each <n>-th named <sheet named> extracted.

 CAVEATS.

  i.  Check out the saxs_parameter file created in each treatment subdirectory
      before proceeding with the integration. Although the program
      XS_extractlog.py tries to find out the correct correspondence between
      sample files and its respective backgrounds, it is not aware of the
      specific conditions of your experiment.

 ii.  Whenever XS_extractlog.py finds more than one file with same
      functionality (as p.o.n.i. files or masks), it creates links for each one
      and includes all them in saxs_parameters, then comments all but the first
      one. It's up to you to comment or uncomment the right ones.

 iii. Eventually, it is possible that some file names or variables have to be
      included in saxs_parameters. Check out for those. Read below (item 4)
      about adding files and correcting the entries in the log file.

  iv. The integration ranges have to be manually defined on each saxs_parameter
      file, through parameters ANGLES and QRADII. See XS_extractlog.py -h.


 3) Merge or add files.

If necessary, merge files with

$ XS_imagemerge.py -g <file 1> <file 2> <file 3> ... <file n>

Or add up EDF files with

$ XS_imageadd.py -g <file 1> <file 2> <file 3> ... <file n>

The sum may be performed BEFORE the extraction of information from the log file
or AFTERWARDS. If you decide to add up all the BACKGROUND files of certain
sample beforehand, do not forget to change the corresponding entry in the log
spreadsheet. If you make the sum after the extraction, the files may be added
with the option

$ XS_imageadd.py [-f <file> <parameter>] [<n>]

(XS_imageadd.py -h to see usage help).

Usually <parameter> is SAMPLE or BACKGROUND and <n> is 1 (the default) or
2. The sum must be repeated separately for each parameter. This must be done
under the respective working directory. If no arguments are given,
XS_ximageadd.py will show a menu and ask you to type the files. With -f, files
are read from parameter <file> (as saxs_parameters); then <file> is modified
with new files (also with extension '_sum').

OBS.: after the first summing with option -f, the new parameters file name
acquires an extension '_sum'. Therefore, further operations must be done
considering this new file.


 4) Change or insert parameters in saxs_parameters files.

After checking the parameter file for a sample (and temperature), change it
accordingly. Most commonly, it may be necessary to change to the correct mask
or calibration file (when measurements were performed at different
sample-detector distances, for instance). The ANGLES variable may be inserted
or changed, if the treatment must be done over angular sectional areas ('cuts')
of the images (see item 6 below).

If water is used as an absolute scale reference, you might also change the
corresponding parameter from 'NORM = 1' to 'NORM = WATER' and copy the .PAR
file formerly generated to the current directory. The normalization parameter
may be defined in the spreadsheet, see XS_extractlog.py -h.


 5) Normalization by water reference.

If water is used as the absolute normalization reference, it must be done along
the integration process at least once. Use the program

$ XS_azimuthalaverage.py -e -f <log file>

(or -m to type values from menus) under the respective working directory. Then
follow the self-explained procedures. The option '-e' stands for 'examine'.
Without '-e', the program treats all chosen files with no inspection whasoever
(except for the water file, if it is the case); this is useful for a large
batch of files with similar aspect.


 6) Angular cuts for azimuthal integration.

If it is necessary to integrate over azimuthal angle 'cuts', you have to add
the ANGLES parameter to the respective saxs_parameters files. Type the
integration ranges using the structure: (central angle, delta).  For example,

ANGLES = (0, 20) (-45, 10)

will integrate in both angular ranges, [-10, 10] (namely, center = 0 deg, delta
= 20 deg) and [-50, -40] (namely, center = -45 deg, delta = 10 deg).


 7) Repeat the necessary procedures for each sample.

Enter each sample directory, check the saxs_parameters(_sum) file, make the
summings (item 3) and the averaging (item 4). If the PAR file was already
generated and copied (and NORM = PAR, PARFILE = <normfile>.PAR), the
normalization calculation will be skipped (former water normalization water
will be used instead).

This script is part of the XS-treatment suite for SAXS/WAXS data treatment.

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

import os
import re
import sys
import pydoc
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

## Table of color characters.
CC = { 'BLK' : '[0m',      # black
       'red' : '[01;31m',  # red
       'gre' : '[01;32m',  # green
       'yel' : '[01;33m',  # yellow
       'blu' : '[01;35m',  # blue
       'cya' : '[01;36m'   # cyan
      }

# Dictionary of patterns and respective substitutions.
Psub = {
    # Argument inside <...>
    '([\<\(\[])(.*?)([\>\]\)])' : '{}{}{}{}{}{}'.format(CC['BLK'], '\\1', CC['cya'],
                                                        '\\2', CC['BLK'], '\\3'),

    # Command option, -<letter>
    #'\ -h' : ' {}-h{}'.format(CC['cya'], CC['BLK']),
    '\ (\-[A-Za-z]+)' : ' {}{}{}'.format(CC['cya'], '\\1', CC['BLK']),
    
    # Command line, starting with $
    '^\$ (.*) ' : '$ {}{}{} '.format(CC['yel'], '\\1', CC['BLK']),
    
    # Command inline, ending with .py
    #'([A-Za-z\-]*\.py)'     : '{}{}{}'.format(CC['yel'], '\\1', CC['BLK']),
    'XS_([A-Za-z]*\.py)'     : '{}XS_{}{}'.format(CC['yel'], '\\1', CC['BLK']),
    
    # Parameter in capital letters
    '^([A-Z]+)\ *=(.*)$' : '{}{}{} {} {}{}{}'.format(CC['gre'], '\\1', CC['BLK'],
                                       '=', CC['cya'], '\\2', CC['BLK']),

    # Commentary;
    '^\#(.*)$'           : '{}{}{}'.format(CC['yel'], '#\\1', CC['BLK']),

    # Title of section, starting with number and ')'
    '^\ ([0-9]+\).*)$'   : '{}{}{}{}'.format('\n  ', CC['red'], '\\1', CC['BLK']) 
}

# The same dictionary with compiled patterns.
PSC = { re.compile(p) : Psub[p] for p in Psub }

##
def main ():
    '''Parse __doc__ text and colorize it or fall back to conventional
    help mode.'''

    # Conventional help mode, if set in command line.
    try:
        if (sys.argv[1] == '-h'):
            help('XS_colorhelp')
            return
    except:
        pass
    
    # Run over text lines.
    Text = __doc__.split('\n')
    newtext = ''
    for line in Text:
        # Check for pattern match.
        for P in PSC.keys():
            if (re.search(P, line)):
                line = re.sub(P, PSC[P], line)
        newtext += f'{line}\n'

    try:
        # Set pager to less with option to read escape characeters.
        os.environ['PAGER'] = "less -r"
        # Use pager if color option is defined.
        pydoc.pager(newtext)
    except Exception as err:
        print(f' WARNING: {err}')
        print(help('XS_colorhelp'))

    return

##
if __name__ == "__main__":
    main()
