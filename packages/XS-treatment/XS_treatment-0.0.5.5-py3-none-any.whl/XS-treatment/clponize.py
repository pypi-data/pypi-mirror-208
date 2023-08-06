#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Copy file data to a new one with '_NH' (no head) extension in basename and
recreate header in C.L.P.O traditional format,

  Time               Detector
  <exposure time>    <detector counts>
<number of lines>

removing trailing hashes (#). All remaining header lines are eliminated.

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

def nohead_name (filename):
    '''Create new name extension 'NH' (no head) for headless files. '''
    ext = os.path.splitext(filename)[1].strip('.')
    try:
        num = re.search('_[SW]([0-9]+)\.', filename).group(1)
        dnum = int(num)
        basename = filename.replace(f'{num}.{ext}', f'{dnum}')
    except:
        basename = filename.replace(f'.{ext}', '')
    return f'{basename}_NH.{ext}'

def main ():
    '''Open files and recreate them with simple header.'''
    
    try:
        line = sys.argv[1:]
    except Exception as err:
        print(' ERROR: No files given. \n'
              f'(Exception: {err})')
        sys.exit(1)

    for f in line:
        # Get data from file. Get first three lines info, skip header.
        with open(f, 'r') as infile:
            data, cnt = '', 0
            sheader = [ infile.readline().replace('#', '') for i in range(2) ]
            header = ''.join(sheader)
            infile.readline()  # Skip line.
            for L in infile:
                if not re.match('^#', L):                         # skipe header
                    cnt += 1                                      # recount lines
                    data += '{}  1.0\n'.format(L.strip('\n'))     # join next data line
            data = f'{header} {cnt}\n{data}'
                    
        # Create new file with former info.
        fname = nohead_name(f)
        with open(fname, 'w') as outfile:
            outfile.write(data)

    return

        
if __name__ == "__main__":
    main()
