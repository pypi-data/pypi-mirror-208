'''Check whether libraries are correctly imported.

 This program is part of the XS-treatment suite for SAXS WAXS data
 treatment. It must be run from the installation script.

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

#
def main():
    '''Run over a list of libraries and try to import each one.'''
    
    # Get command line arguments.
    try:
        outfail = sys.argv[1:][0]  # Output file.
    except Exception as err:
        print("ERROR: {}")
        sys.exit(0)
    
    LIBS = sys.argv[1:][1:]    # List of libraries to be checked.
    if (len(LIBS) == 0):
        print(" ERROR: the list of libraries is empty, nothing to be checked.")
        sys.exit(1)

    faillibs = []  # List of libraries which could not be imported.

    # Check whether each library in list can be imported.
    for L in LIBS:
        msg = f'   * {L}: '
        print(f'{msg:25}', end='')
        try:
            module = __import__(L)
            print(" OK.")
        except Exception as err:
            print(' ERROR: {}'.format(err))
            faillibs.append(L)

    # Write out to file list of failed imports. 
    with open(outfail, "w") as f:
        for L in faillibs:
            f.write('{}\n'.format(L))

    return
#
if __name__ == "__main__":
    main()
