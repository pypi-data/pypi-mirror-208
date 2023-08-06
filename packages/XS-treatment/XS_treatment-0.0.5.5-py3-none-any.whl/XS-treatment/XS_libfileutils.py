#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''This module defines a set of functions to open, read and write files, 
and to show explanatory texts. It also checks the validity of data sets
for printing (as to eliminate spurious zeros from data).

This module is part of the XS SAXS/WAXS data treatment suite.

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


import glob
import fabio
import numpy as np
import os
import re
import shutil
import string
import subprocess
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

#sys.path.append('/usr/local/lib/SAXS/')

##
def opening_screen(sep, *header, totwidth=80, bsize=3):
    '''Format opening text screen with information about the program.'''

    # Clear current terminal screen before start
    #os.system('clear')
    
    border = bsize * sep 
    skipline = f'{border}{border:>{totwidth-bsize}}\n'
    tblines = str(3 * '{}\n'.format(totwidth * sep))
    
    opscreen = f'{tblines}{skipline}'
    for item in header:
        opscreen += f'{border}{item:^{totwidth-2*bsize}}{border}\n{skipline}'

    opscreen += tblines
    return opscreen

    
##
def section_separator(sep, title):
    '''Print section separators. '''
    topbot = '{}'.format(70 * sep)
    ssep = 5 * sep
    border = f'{ssep}{ssep:>65}'
    spacer = int(30 - len(title) / 2) * ' '
    titleline = f'{ssep}{spacer}{title}{spacer}{ssep}'
    
    print(f'{topbot}\n{border}\n{titleline}\n{border}\n{topbot}\n')
    return


# menu_closed_options()
def menu_closed_options(options_list, seq={}):
    '''Interactive menu of options.  '''
    
    if ( seq != {} ): 
        for item in sorted(seq.keys(), key = lambda x: int(x) ):
            print ('\n {:>2}) {}'.format(item, options_list[seq[item]]))
        print ('\n {0:>2}) {1}'.format('q', 'Quit'))
        print ()
    else:
        print ('\n'.join(options_list))
    
    while True:
        opt = input(' ? > ')
        if ( opt == 'q' ):
            sys.exit(0)
        if opt not in [format(x, 'd') for x in range(1, len(options_list) + 1)]:
            print (' Not a valid option. Try again.')
        else:
            return opt


##
def yes_or_no (question):
    '''Exhibits question. Returns True if answer is 'yes', False otherwise.'''

    question += ' [Y/n] '
    while True:
        try:
            s = input(question).lower()

            if (s == 'q' or s == 'Q'):
                sys.exit(0)
            if (s != "y" and s != "n"):
                raise Exception
            
            return True if (s == 'y') else False
        except Exception as err:
            print (f' Invalid entry. Please, type "y" or "n". {err}')


# Floating point option.
def type_float (s='\n Type a floating point number: '):
    '''Get floating point number from user.'''
    while True:
        try:
            return float(input(s))
        except ValueError:
            print (' Invalid entry. Please, type a float point number.')

#
def isinteger (s):
    '''Tests whether a string is a positive integer number and returns 
    1 if true or 0 otherwise.

    '''
    
    if (s == ''): return False
    for c in s:
        if (c not in (string.digits)):
            return False
    return True

# 
def read_range (ifls, nfls):
    '''Ask interval range. '''
    
    while (True):
        # Read numbers corresponding to file list.
        s = input(' ? > ')
        
        if  (s == ''):
            continue
        elif (s == 'q'):
            sys.exit(0)
            
        try:
            for c in s:
                if (c not in (string.digits + '-' + ' ')):
                    raise Exception (' Please, type only digits '
                                     'and the character \"-\".')   
        except Exception as err:
            print (err)
            continue

        # Test whether chosen files are suitable
        s = re.sub(r'\s+', ' ', s)
        s = re.sub(r'\s*-\s*', '-', s)
        s = re.sub(r'-+', '-', s)
        ss = s.split()
        ts = []
        
        for rg in ss:
            if (re.search('-', rg)):
                try:
                    ffs = rg.split('-')
                    for num in ffs:
                        if (not isinteger(num)):
                            raise Exception(' Expression not recognized.')
                        a = int(ffs[0])
                        b = int(ffs[1])
                        if (a > b):
                            raise Exception(' Range limits are out of order.')
                except Exception as err:
                    print (err, 'Please, type again.')
                    break
                fs = [ x for x in range(a, b + 1) ]
            else:
                fs = [ int(rg) ]
            ts = ts + fs

        #
        if (ts == []): continue

        if min(ts) < ifls or max(ts) > nfls:
            print(f' Error: numbers must be within the interval'
                  f' {ifls} to {nfls}.')
            continue
        
        if 0 in ts:
            if not len(ts) == 1:
                print (' Error: "0" option must be chosen alone, '
                       'not within an interval.')
                continue

        return ts


#
def change_fileext (fdict, oldext='edf', newext='rad'):
    '''Change extension of the file names in the files' dictionary.'''
    for k in fdict:
        try: 
            fdict[k] = [ value.replace(oldext, newext) for value in fdict[k] if
                         re.search(oldext, value) ]
        except:
            continue
    return fdict


#
def show_filenames (*fileext, mandatory=False, instruction=False):
    ''' Show filenames from current directory. '''

    # DEBUG
    print(f' \n\n ############### fileext = {fileext} #############\n\n')
    # DEBUG
    
    # Get files in current directory with file extensions from list 'fileext'
    fls = []
    for ext in fileext:
        fls += sorted(glob.glob('*.%s' % ext))

    fileext_string = ', '.join(fileext)

    # If the files are mandatory
    if (mandatory and fls == []):
        print(f'\n No {fileext_string} file(s) available in current directory.'
              '\n This is mandatory. Quitting.')
        sys.exit(1)
    elif (mandatory):
        print(f'\n Available {fileext_string} files in current directory: ')
    else:
        print(f'\n Available {fileext_string} files in current directory: '
              '   0) None')
        
    # Print available files 
    for i, F in enumerate(fls):
        print(f'   {i+1}) {F}')
        
    if instruction:
        # Menu's use instruction
        print ('\n Type the numbers of the files to be processed'
               ' separated by spaces or the interval in the format'
               ' first-last (e.g.: 2 5 7-10 12-18)')
    
    return fls


#
def read_filenames (filelist, title='', onefile_option=False, mandatory=False):
    ''' Read filenames from current directory. '''
    print ('\n{0}'.format(title))
    while True:
        nfls = len(filelist)
        
        # If the files are mandatory
        if (mandatory):
            range_list = read_range(1, nfls)
        else:
            range_list = read_range(0, nfls)
            
        # For one file option
        if (onefile_option):
            if (len(range_list) == 1):
                break
            else: 
                print (' Just one file must be chosen for this option.')
        else:
            break

    # Build list with chosen files.
    if (range_list == [0]):
        filenames = []
    else:
        filenames = [ filelist[i-1] for i in range_list ]

    # Eliminate empty files from list.
    for f in [ x for x in filenames if (os.path.getsize(x) == 0) ]:
        print (' WARNING: {0} is empty, skipping file.'.format(f))
        filenames.remove(f)

    print ("\n Chosen files:")
    for f in filenames:
        print (f' {f}')
        
    return filenames


#
def read_data_file(filename, fdir='.'):
    ''' Read RAD, RDS, RDN, RSR files.'''
    filepath = os.path.join(fdir, filename)

    header = ''  # Store header.
    with open(filepath, 'r') as fn:
        # Get information on exposure time and detector counts.
        # Skip 1st line of file.
        fn.readline()
        # Get time and detector data.
        time, detector = [ float(x) for x in
                           re.findall('[0-9]*\.[0-9]*', fn.readline()) ]
        # Skip number of lines.
        line = fn.readline()
        
        # Get the remaining header and data.
        line = fn.readline()
        while (re.match('^#', line)):
            header += line
            line = fn.readline()
        
    # Read data.
    q, I, sigma = np.genfromtxt(filepath, skip_header=26,
                                usecols=(0,1,2), unpack=True)

    return (q, I, sigma, time, detector, header)


#
def write_file(filename, q, I, sigma, time, counts, fileext='',
               header=None, waxs=False, wlength=1.5419):
    '''Build RAD, RDS, RDN or RSR files, Windows compatible.
    File extension is assumed given in filename, but may be optionally
    completed.

    '''
    

    if not os.path.exists(fileext):
        os.makedirs(fileext)

    filename = f'{filename}.{fileext}'
    filepath = os.path.join(fileext, filename)

    # 
    print(f'\n ### Generating {filename} ... ', end='')
    with open(filepath, 'w') as f:
        # Info about time, detector and number of lines.
        preheader = ('#   Time        Detector\n'
                     + f'#\t{time}\t{counts}\n# {len(q)}\n')
        f.write(preheader)

        # Header.
        if (header is not None):
            f.write(header)

        # Write out data to file; q in Angstrons^{-1}
        for qi, Ii, si in zip(q, I, sigma):
            if waxs:
                _2theta = np.degrees(2. * np.arcsin(qi * wlength * 0.25 / np.pi))
                f.write(f'{qi:15.8e} {Ii:15.8e} {si:15.8e} {_2theta:15.8e}\n')
            else:
                f.write(f'{qi:15.8e} {Ii:15.8e} {si:15.8e}\n')
    print (' done.')

    # Convert file to DOS format
    try:
        print(f' Converting {fileext} file to DOS format...', end=' ')
        todos = (subprocess.check_output(['which', 'todos'])).strip()
        #todos = shutil.which('todos')
        subprocess.call([todos, filepath])
        print('done.')
    except Exception as err:
        print(f' WARNING: could not transform {fileext} files into DOS format, '
              f'software {todos} not found.\n (Exception: {err})')
    else:
        subprocess.call([todos, filepath])
    print(' done.')
    
    return
    

##
def open_edf (edffile):
    '''Wrapper for fabio.open(). Returns edf image object with correct
    counts of files' header Detector parameter.

    '''

    try:
        im = fabio.open(edffile)
    except Exception as err:
        print (" Could not open file {}: {}".format(edffile, err))
        return None
        
    # Correction for detector counts if transmission count is given by
    # parameter SumForIntensity1 (Xeuss 2). The factor 0.1 corresponds to
    # direct beam exposure time.
    if (float(im.header['Detector']) == 0.0):
        try:
            im.header['Detector'] = str(float(im.header['SumForIntensity1'])
                                        / 0.1 * float(im.header['ExposureTime']))
        except Exception as err:
            msg  = (f' WARNING: could not retrieve information about'
                    f'  counts from file {edffile} : \n {err}'
                    f'\n Detector and SumForIntensity1 are zeroed.')
            print(msg)

    return im
            
#
def CleanData (q, I, sigma):
    ''' Remove points with zeros from the arrays.'''
    sigma_i = np.where(sigma == 0)[0] 
    I_i = np.where(I == 0)[0]
    indices = np.intersect1d(I_i, sigma_i)
    q = np.delete(q, indices)
    I = np.delete(I, indices)
    sigma = np.delete(sigma, indices)
    return q, I, sigma

#
def main():
    '''File utils library for XS-treatment suite. '''
    help('XS_libfileutils')

if __name__ == "__main__":
    main()
