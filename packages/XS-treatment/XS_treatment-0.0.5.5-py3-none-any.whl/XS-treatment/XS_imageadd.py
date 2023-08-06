#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Add up EDF files using Python fabIO and pyFAI libraries. 

Usage:
   XS_imageadd.py [-h]
or XS_imageadd.py [-f <file> -p <parameter>] [-n <n>]
or XS_imageadd.py [-g <files>]

The avaliable options are:
            -h : this message
     -f <file> : read parameters from <file>
-p <parameter> : parameter relative to which the files be summed;
                 usual values are SAMPLE or BACKGROUND
        -n <n> : an integer number, files will be added in groups of n;
                 default value is 1 (all files of an entry are added up
                 at once)
    -g <files> : add up <files>

Obs.: option -f demands <parameters file> AND <parameter>. With no
options, choices are defined interactvely from command line. You can
also use the program extract_saxslog.py to create a parameters file
from a log spreadsheet file.

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


import numpy as np
import re
import os
import time
import sys
import getopt
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
import XS_libimageplot as LIP


#
def cmd_opt ():
    ''' Read command line arguments and return respective list.'''

    global paramlist
    paramlist = [ 'SAMPLE', 'BACKGROUND', 'NOISE' ]
    
    try:
        line = getopt.getopt(sys.argv[1:], "hg:f:p:n:")
    except getopt.GetoptError as err:
        warning = ' ERROR: ' + str(err) + '.'
        print (warning)
        sys.exit(1)

    # Options and arguments.
    opts = line[0]
    extrarg = line[1]

    # No options, enter interactive menu.
    if (len(line[0]) == 0):
        print('\n No command line arguments given, ' 
              ' edf files will be read from interactive menu.')
        return ('interactive', None, None, None)

    # Default values for parameters.
    paramfile, parameter, files, ngroup = None, None, None, 1
    
    for o in opts:
        if (o[0] == '-h'):
            return ('help', None, None, None, ngroup)
    
        elif (o[0] == '-g'):
            # Files defined in command line.
            files = [ o[1] ]
            if (len(extrarg) > 0):
                files += extrarg
            return ('cmdlinefiles', None, None, files, ngroup)
        
        elif (o[0] == '-n'):
            # Add up in groups of ngroup files.
            ngroup = o[1]

        elif (o[0] == '-f'):
            # Parameter file to be read.
            option = 'paramfile'
            paramfile = o[1]
        
        elif (o[0] == '-p'):
            # Parameter to define files to be added up.
            parameter = o[1]

        else:
            print(' Parameter not recognized. Quitting.')
            sys.exit(1)

    # Check consistency of options -f and -p.
    if (option == 'paramfile'):
        # Tests whether parameter file exists.
        if (not os.path.exists(paramfile)):
            print(f' ERROR: File "{paramfile}"'
                  ' not found in current directory. Aborting.')
            sys.exit(1)
        # 
        if (parameter is None):
            print(' ERROR: no paramter given (option -p).'
                  '\n Please, rerun with a valid parameter.')
            sys.exit(1)
        #    
        if (parameter not in paramlist):
            print(' ERROR: no valid parameter given.'
                  '\n Please, rerun with: -p <valid parameters>,'
                  f'\n valid parameters: {paramlist}')
            sys.exit(1)
            
    return ('paramfile', paramfile, parameter, files, ngroup)

    
##
def add_images (filenames) :
    '''Add up images given in filenames list using python 3 fabio library.

    '''
    
    # List of sample files
    try:
        dfs = [ fabio.open(f) for f in filenames ]
    except Exception as err:
        print(f' ERROR while opening file list: {err}')
        sys.exit(1)

    # Take parameters data from each file to lists
    detectors = [ float(d.header['Detector']) for d in dfs ]
    Times = [ float(d.header['ExposureTime']) for d in dfs ]
    times = Times[:]
    det_pos  = [ (float(d.header['detx']), float(d.header['detz'])) for d in dfs ]

    #centers = [(float(d.header['Center_1']),float(d.header['Center_2'])) for d in dfs]
    #sample_distances = [float(d.header['SampleDistance']) for d in dfs]
    #times = [float(d.header['count_time']) for d in dfs]
    
    # Generate a blank output image and the corresponding parameters
    dim = (int(dfs[0].header['Dim_2']), int(dfs[0].header['Dim_1']))
    # Sum of the images
    try:
        outimage = np.zeros(dim, 'int32')
        for df in dfs:
            outimage += df.data
    except:
        outimage = np.zeros(dim, 'float64')
        for df in dfs:
            outimage += df.data

    # Name of the output image edf file
    numbers = []
    for f in filenames:
        nn = re.search('([0-9]{5}).edf', f).group(1)
        numbers.append(str(int(nn)))
    try:
        basename = re.match('.*__', f).group(0).strip('_')
    except:
        basename = re.match('(.*)_[0-9]{5}', f).group(1).strip('_')

    newext = '{}'.format('+'.join(numbers))
    outname = f'{basename}__{newext}.edf'

    # Remove file, if it exists.
    if os.path.exists(outname): os.remove(outname)
   
    # Header of the output image edf file
    Sdet = sum(detectors)
    Stime = sum(times)
    outheader = df.header
    outheader['title'] = outname
    outheader['Detector'] = str(Sdet)
    outheader['count_time'] = str(Stime)
    outheader['ExposureTime'] = str(sum(Times))

    # Save output file with name 'outname'
    outfile = fabio.edfimage.EdfImage(data=outimage, header=outheader)
    outfile.save(outname)

    # Filenames and parameters of images assigned to 'info' variable to
    # print and save. Just in the end of the program to avoid the register
    # of analysis stopped by errors.
    outlen = len(outname) + 1
    tm = time.strftime("%Y-%m-%d %H:%M:%S")
    sep = 87 * '*'
    header = (f'\n\n{sep}\n Date: {tm}\n Directory: {os.getcwd()}'
              f'\n Used Python libraries: '
              f'\n\t{fabio.__name__} {fabio.version} {fabio.__status__}')
    
    info = f'\n\n\t{"Files":<{outlen}}:{"Detector counts":^20}:{"Times":^15}\n'
    for name, det, tm in zip(filenames, detectors, times):
        info += f'\n\t{name:<{outlen}}:{det:^20}:{tm:^15.1f}'
    info += f'\n\n\t{outname:<{outlen}}:{Sdet:^20}:{Stime:^15.1f}\n'

    print(header + info)
    
    # Generate and print record file
    with open('imageadd.log', 'a') as recfile:
        recfile.write(header + info)

    # Figure of summed image  
    #ximageplot.plot_images([outname])
    return outname

#
def interactive_menu ():
    '''Get image file names from interactive menu. Return the respective
    list of files.

    '''
    # Clear current terminal screen before start
    #os.system('clear')
    LFU.section_separator('*', 'Sum of Images ')
    # Choose images files to add
    filelist = LFU.show_filenames('edf', mandatory=True, instruction=True)
    s = ' Choose image files to sum:'
    return LFU.read_filenames(filelist, s, mandatory=True)

#
def add_from_parameters_file (paramfile, parameter, ngroup):
    '''Read parameters file to add up images from given parameter. Rewrite
    parameter value with new entry.

    '''

    # Initialize copies of parameters file.
    pfdata_bot, pfdata_top, pfdata_mid = '', '', ''
    pftop = True
    
    try:
        with open (paramfile, 'r') as pf:
            # Read the file and store in a string.
            pfdata = pf.read()
            
        total_line, old_line = '', ''
        # Run through string lines.
        for line in pfdata.split('\n'):

            # Skip comments or blank lines.
            if (re.match('#|^\ *$', line)):
                if (pftop):
                    pfdata_top += f'{line}\n'
                else:
                    pfdata_bot += f'{line}\n'
                continue

            # Get rid of new line characters.
            LN = line.strip()

            # Test for continuation of the line. If there is a back slash at
            # the end of the line, rebuild the whole entry.
            if (re.search('\\\\', LN)):
                total_line += LN.strip('\\\\')
                old_line += f'{line}\n'
                continue          # Next line, until all paramater data is retrieved.
            else:
                total_line += LN  # No continuation (\), get last entry and move on.
            old_line += f'{line}\n'
            
            # Check for parameter.
            if (re.match(parameter, total_line)):
                # Get the list of files.
                files = total_line.split('=')[1].strip()
                flist = files.split()
                pftop = False
            else:
                pass
                # Rebuild entry
                if (pftop):
                    pfdata_top += old_line
                else:
                    pfdata_bot += old_line
            #
            total_line, old_line = '', ''

        nfl = len(flist)
        if (nfl == 1):
            # Skip summing if there is only one file.
            if (ngroup > 1):
                print(f' WARNING: only one file ({files}), '
                      f' although grouping was defined as {ngroup}.'
                      f' Skipping sum.' )
                sys.exit(0)
                
        elif ((nfl % ngroup) != 0):
            # Skip summing if the number of files may not be
            # grouped accordingly to demand.
            print(f' WARNING: number of files in entry is not a'
                  f' multiple of {ngroup}, skipping sum.'
                  f'\n Entry: {files}' )
            
        else:
            pfdata_mid = f'{parameter} = '
            if (ngroup == 1):
                outname = add_images(flist)
            else:
                for i in range(0, nfl, ngroup):
                    outname = add_images(flist[i : i + ngroup])
            pfdata_mid += f'\ \n{outname}'


                
        # Create line to substitute old file names in
        # parameters file.
        new_pfdata = f'{pfdata_top}\n{pfdata_mid}\n{pfdata_bot}\n'
                    
        # Write modified string into new parameter file.
        if (not re.search('_sum',  paramfile)):
            new_paramfile = f'{paramfile}_sum'
        else:
            new_paramfile = paramfile
        with open (new_paramfile, 'w') as pf:
            pf.write(new_pfdata)
            
    except Exception as err:
        print ( ' ERROR: ' + str(err) + '\n Could not open'
                + ' file {}. Aborting.'.format(paramfile) )
        sys.exit(1)

    return

#
def add_cmd_line_files (filenames):
    for f in filenames:
        if (not os.path.exists(f)):
            print(' ERROR: File \'{0}\''.format(f)
                  + ' not found in current directory. Aborting.')
            sys.exit(1)
    add_images(filenames)
    return

##        
def main():

    # Get command line options.
    opt, paramfile, parameter, files, ngroup = cmd_opt()

    # Help message.
    if (opt == 'help'):
        help('XS_imageadd')

    elif (opt == 'interactive'):
        add_images(interactive_menu())

    # Parameter file name.
    elif (opt == 'paramfile'):
        add_from_parameters_file(paramfile, parameter, ngroup)

    # Files given in command line.
    elif (opt == 'cmdlinefiles'):
        add_cmd_line_files(files)

    # Unknown option.
    else:
        print(' Option not recognized.\n')
        sys.exit(1)

    return


#   
if __name__ == "__main__":
    main ()
