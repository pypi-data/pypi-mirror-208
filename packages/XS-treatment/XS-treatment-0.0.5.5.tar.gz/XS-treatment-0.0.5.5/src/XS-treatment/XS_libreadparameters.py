#!/usr/bin/python3
# -*- coding: utf-8 -*-

__version__   = '2.4.1'
__author__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__credits__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__email__ =  'dreis@if.usp.br ,agolivei@if.usp.br'
__license__ = 'GPL'
__date__   = '2022-09-14'
__status__   = 'Development'
__copyright__ = 'Copyright 2022 by GFCx-IF-USP'
__local__ = 'GFCx-IF-USP'

import re
import getopt
import sys
import os.path
import datetime
import pyFAI
import fabio
import numpy as np


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

#
class read_parameters ():
    '''Define parameters for SAXS/WAXS data integration.

This class defines the mandatory or optional parameters to be read
from a SAXS / WAXS parameters file or entered manually. It also
implements the following

Methods:
    
  __init__(list of tuples)
  file_or_command_line(list of tuples)
  get_parameters_from_file()
  check_parameters_from_file()
  get_parameters_from_command_line()
  write_logfile()
  read_maskdata()

  _read_angles_from_command_line() -> list of tuples
  _transform_angles(list of tuples) -> list of tuples
  _normalization_from_file()
  _read_water_norm_params()
  _normalization_from_command_line() -> list

  (lambda) pair_in_str(string) -> list of floats
  (lambda) parse_angles(tuple) -> list of lists

'''


    __author__    = 'Dennys Reis and Arnaldo G. Oliveira-Filho'
    __contact__   = 'dreis@if.usp.br, agolivei@if.usp.br'
    __copyright__ = '(C) GPL'
    __date__   = '2022-09-14'
    __status__   = 'Development'
    __version__   = '2.4.1'

    
    # Dictionary for the description of integration parameters.
    description = {
        'XS'           : 'flag: measurements from SAXS or WAXS',
        'PONI'         : 'parameters: from silver behenate or corundum',
        'SAMPLE'       : 'file(s): sample(s) measurement',
        'BACKGROUND'   : 'file(s): buffer measurement',
        'MASK'         : 'file: mask to cover spurious pixels',
        'SHADOW'       : 'file: calibration standard material',
        'NOISE'        : 'file: background noise',
        'PARFILE'      : 'parameters: formerly evaluated for absolute scaling',
        'NORM'         : 'flag: normalization option',
        'WATER'        : 'file: measurement of capillary filled with water',
        'EMPTY'        : 'file: empty capillary measurement',
        'GC'           : 'file: normalization by glassy carbon',
        'MANORM'       : 'flag: (1 or 0) manual normalization',
        'ANGLES'       : 'floats: the angular sectors for integration',
        'QRADII'       : 'floats: the q radial and angular intervals for integration',
        'DIRECT'       : 'file: direct beam profile',
        'MULTISUBT'    : 'flag: multiple background subtraction'
    }

    # Auxiliary index for ordering definition.
    indesc = { 0: 'XS', 1: 'PONI', 2: 'SAMPLE', 3: 'BACKGROUND', 4:
               'MASK', 5: 'SHADOW', 6: 'NOISE', 7: 'PARFILE', 8:
               'NORM', 9: 'WATER', 10: 'EMPTY', 11: 'GC', 12:
               'MANORM', 13: 'ANGLES', 14: 'QRADII', 15: 'MULTISUBT' }


    # Mandatory and usual items for integration.
    mandatory = ['SAMPLE', 'PONI']
    usual = ['BACKGROUND', 'MASK']

    # Possible normalization choices.
    # ('EMPTY') is here for further cleaning of the dictionary.
    normlist  = [None, 'WATER', 'GC', 'PARFILE', 'EMPTY']

    # Angle interval limits.
    amin, amax = -180.0, 180.0

    
    ##
    def __init__ (self, line):
        '''Definition of default parameters and sequence of procedures for paramenters
        file parsing.

        '''
        # SAXS integration parameters are stored in a dictionary.
        self.intparam = {}
        # Default is reading parameters from file.
        self.fromfile = True
        # Default file name base. It can be changed by '-f' option. 
        self.pfilename = 'saxs_parameters'
        # Warnings and other informations to be logged.
        self.info = ''
        # Define default value for normalization.
        self.normfactor = 1.0
        # Define default background subtraction method.
        # True  : all backgrounds subtracted from each sample.
        # False : one-to-one ;
        self.multisubt = True
        # Define if each curve calculated must be examined.
        self.examine = False
        # Help flag.
        self.help = False
        
        # Define a generic log file name.
        self.logfile = self.pfilename + '.log'
        
        # Decide whether to read integration parameters from file or
        # from command line.
        self.file_or_command_line(line)
        # Help.
        if (self.help): return
        
        # Define log file name. Comment this to get a simpler log file
        # name. self.pfilename may be changed by file_or_command_line(), so
        # this line must come here.
        self.logfile = ('{:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
                        + '__' + self.pfilename + '.log')

        # Get parameters.
        if (self.fromfile):
            # Get parameters from file.
            self.get_parameters_from_file()
            # Check consistency and validity of parameters.
            self.check_parameters_from_file()
        else:
            # Get parameters manually.
            self.get_parameters_from_command_line()

        # Log file.
        self.write_logfile ()
        

    ##
    def file_or_command_line (self, line):
        """Decide whether parameters should be read from file or from command line.
        This function changes two class variables:
        1) fromfile: boolean, True if from file, False if from command line 
        2) pfilename: name of the parameters file

        """

        if (line[0] == []):
            warning = ('\n WARNING: no command line arguments given.' 
                       + ' SAXS parameters were read from' 
                       + ' file \'{0}\'.'.format(self.pfilename))
            self.info += warning
            return
        else:
            opts = line[0]
            
        # Parse options.
        manual = True
        for o in opts:
            if (o[0] == '-h'):
                self.help = True
            elif (o[0] == '-e'):
                # Examine each curve.
                self.examine = True
            elif (o[0] == '-m'):
                if (not manual):
                    print (' ERROR: options -m and -f are excludent.')
                    sys.exit(1)
                # Read parameters from command line.
                self.fromfile = False
            elif (o[0] == '-f'):
                manual = False
                self.pfilename = o[1]
                if (not self.fromfile):
                    print (' ERROR: options -m and -f are excludent.')
                    sys.exit(1)
                # Tests whether parameter file exists.
                if (not os.path.exists(self.pfilename)):
                    warning = ('\n ERROR: File \'{0}\''.format(self.pfilename)
                                + ' not found in current directory. Aborting.')
                    self.info += warning
                    self.write_logfile ()
                    print (warning)
                    sys.exit(1)
            else:
                print (' Option not recognized.\n'
                        + ' Known options are: \n\t -m (manual entry of parameters)'
                        + ' or -f <file> (read the parameters from file).\n'
                        + ' If no options are given, parameters will be read from'
                        + ' default file {0}'.format(self.pfilename))
                sys.exit(1)

        #
        return 

    
    ## 
    def get_parameters_from_file (self):
        '''Read parameters from file and fills dictionary param with
        key : files/values.

        '''

        try: 
            pfile =  open(self.pfilename, 'r')
        except Exception as err:
            print (' ERROR opening {} : {}'.format(self.pfilename, err))
            sys.exit(1)
            
        total_line = ''
        # Run through file lines.
        for line in pfile: 

            # Get rid of new line characters.
            L = line.strip()

            # Skip comments or blank lines.
            if (re.match('#|^\ *$', L)): continue

            # Test for continuation of the line. If there is a back slash at
            # the end of the line, rebuild the whole entry.
            if (re.search('\\\\', L)):
                total_line += L.strip('\\\\')
                continue          # Next line, until all paramater data is retrieved.
            else:
                total_line += L   # No continuation, get last result and move on.

            # Gets parameter name.
            if (re.match(r'^[A-Z]+\ *=', total_line)):
                entry = total_line.split('=', 1)
                VAR   = entry[0].strip()
                
                
                if (VAR == 'ANGLES'):
                    # get values for parameter ANGLES 
                    angles_string = re.findall(r'\([-+]?[0-9]*\.?[0-9]+\ *,\ *[-+]?[0-9]*\.?[0-9]+\)',
                                               entry[1])
                    fangles = self.parse_angles(angles_string)
                    self.intparam['ANGLES'] = self._transform_angles(fangles)
                    
                elif (VAR == 'QRADII'):
                    '''Get values for parameter QRADII (radial integration). Radial integration
                    demands radial and angular intervals, so at least two tuples must be given
                    enclosed in []. First tuple is angular, second tuple is radial interval. 
                    Other pairs of tuples must be enclosed in new brackets.'''
                   
                    # Get all lists of pairs [(qi, qf), (angle, delta)].
                    iList = re.findall('\[.*?\]', entry[1].strip())
                    #re.findall(r'\([-+]?[0-9]*\.?[0-9]+\ *,\ *[-+]?[0-9]*\.?[0-9]+\)', entry[1])
                    self.intparam['QRADII'] = []

                    # Parse each list.
                    for L in iList:
                        tup  = re.findall('\([-+]?[0-9]*\.?[0-9]+\ *,\ *[-+]?[0-9]*\.?[0-9]+\)', L)
                        ntup = self.parse_angles(tup)
                        ltup = [ntup[0], list(self._transform_angles([ntup[1]])[0])]                    
                        self.intparam['QRADII'].append(ltup)
                else:
                    # get values for other parameters
                    try:
                        # Add to entry
                        self.intparam[VAR] += entry[1].split()
                    except:
                        # Create entry
                        self.intparam[VAR] = entry[1].split()

            # Reset completed line.
            total_line = ''
                        
        pfile.close()
        return

    ##
    def check_parameters_from_file (self):
        '''Check validity and consistency of parameters read from file.'''
        
        # Check whether read parameters are recognized.
        for key in self.intparam:

            if (key not in self.description):
                warning = ('\n\n ERROR: item {0} not recognized '.format(key)
                            + ' as a valid parameter. Please, check the' 
                            + ' parameters file ({0}).'.format(self.pfilename))
                self.info += warning
                self.write_logfile ()
                sys.exit(1)
                
            # Delete entries whose value is empty.
            if (self.intparam[key] == ['']):
                del self.intparam[key]
                continue
            
            # Clean up empty strings from lists.
            lst = self.intparam[key]
            for item in lst:
                if (item == ''):
                    lst.remove(item)
            
        # Mandatory items: SAMPLE, PONI.
        for item in self.mandatory:
            if (item not in self.intparam or self.intparam[item] == ['']):
                warning = ('\n ERROR: item {0} ({1})'.format(item, self.description[item])
                            + ' is mandatory, but is not defined.'
                            + ' Please, check file {0}.'.format(self.pfilename))
                self.info += warning
                self.write_logfile ()
                sys.exit(1)
                
        # Usual items: BACKGROUND, MASK. They are usually expected in
        # parameters file, but not mandatory.
        for item in self.usual:
            if (item not in self.intparam or self.intparam[item] == ['']):
                warning = ('\n WARNING: item {0} ({1})'.format(item, self.description[item])
                            + ' is not defined.\n'
                            +  'Performing calculations without {0}.'.format(item))
                self.intparam[item] = None
                self.info += warning

        # Define background subtraction method.
        if ('MULTISUBT' in self.intparam):
            self.multisubt = False if self.intparam['MULTISUBT'][0] == 'False' else True
        else:
            print (' WARNING: Option for subtraction of backgrounds not defined.'
                   + ' Assuming all backgrounds must be subtracted from each sample.')
            
        # Read mask data.
        # (Just once: it'll be the same for all files)
        self.read_maskdata()
       
        # Azimuthal integrator with parameters from chosen ponifile (beam
        # center, sample-detector distance, and so on). These data are
        # necessary for normalization.
        self.aintegrator = pyFAI.load(self.intparam['PONI'][0])

        # If absolute normalization should be calculated, test for consistency.
        #if (self.fromfile):
        self._normalization_from_file ()
        #else:
        #    self._normalization_from_command_line ()
            
        # Set default angular interval if not defined.
        if ('ANGLES' not in self.intparam or self.intparam['ANGLES'] == []):
            self.intparam['ANGLES'] = [(-180.0, 180.0)]
        else:
            # Check validity of angles.
            for a in self.intparam['ANGLES']:
                if (a[0] < -180.0 or a[0] > 180.0 or a[1] < -180.0 or a[1] > 180.0):
                    warning = ('\n\n ERROR: ANGLE {0} deg is out of limits! '.format(a[0])
                               + ' Check parameters file {0}.'.format(self.pfilename)
                               +  'Aborting.')
                    self.info += warning
                    self.write_logfile()
                    print(warning)
                    sys.exit(1)

        # Tests for the existence of every file defined in parameters file.
        for name in self.intparam:

            # Skip if the (non mandatory) parameter is not defined.
            if (self.intparam[name] == None): continue

            # Skip if the parameter is not of type 'file'.
            if (name in [ 'ANGLES', 'NORM', 'MULTISUBT', 'QRADII']): continue

            # Check existence of files and if they are not empty.
            for f in self.intparam[name]:
                msg = ''
                try:
                    if (f != '' and  not os.path.exists(f)):
                        # Check whether file exists.
                        msg = ('\n\n ERROR: file \'{0}\', corresponding to item'.format(f)
                                + ' {0} ({1}), '.format(name, self.description[name])
                                + 'not found in current directory.\n Please, check'
                                + ' the parameters file ({0}).'.format(self.pfilename) 
                                + ' Aborting.')
                        raise Exception (msg)
                    elif (os.path.getsize(f) == 0):
                        # Check whether file is empty.
                        msg = ('\n\n ERROR: file \'{0}\', corresponding to item'.format(f)
                                + ' {0} ({1}), '.format(name, self.description[name])
                                + 'is empty. Aborting.')
                        raise Exception (msg)
                except Exception as err:
                    self.info += str(err) + msg
                    print (' ERROR (check_parameters_from_file), file existence check: ', err, '\n', msg)
                    self.write_logfile ()
                    sys.exit(1)

        return


    ##
    def get_parameters_from_command_line (self):
        '''Asks for parameters in command line.'''
    
        LFU.section_separator('*', 'Options for Azimuthal Averaging ')
        # Default file extension for data files.
        fileext = 'edf'
        
        # Choose files for azimuthal average, subtraction and correction
        flist = LFU.show_filenames('edf', mandatory=False, instruction=True)

        # Choose samples' files
        s = ' Choose SAMPLE files (mandatory):'
        self.intparam['SAMPLE'] = LFU.read_filenames(flist, s, mandatory=True)

        # Choose a background file
        s = ' Choose BACKGROUND files (optional):'
        self.intparam['BACKGROUND'] = LFU.read_filenames(flist, s)

        # Choose a noise file
        s = ' Choose only one NOISE file (optional):'
        self.intparam['NOISE'] = LFU.read_filenames(flist, s, onefile_option=True)

        # Choose a shadow correction file
        s = ' Choose only one SHADOW CORRECTION file (optional):'
        self.intparam['SHADOW'] = LFU.read_filenames(flist, s, onefile_option=True)

        # Choose poni file
        pfls = LFU.show_filenames('poni', mandatory=True, instruction=False)
        s = ' Choose poni file (mandatory):'
        self.intparam['PONI'] = LFU.read_filenames(pfls, s, onefile_option=True,
                                                   mandatory=True)
        print (' Using \'{0}\' as poni file. '.format(self.intparam['PONI']))
        # Azimuthal integrator with parameters from chosen ponifile (beam
        # center, sample-detector distance, and so on). These data are
        # necessary for normalization.
        self.aintegrator = pyFAI.load(self.intparam['PONI'][0])

        # Choose mask file. Read mask data.
        # (Just once: it'll be the same for all files)
        title = ' Choose mask file (optional):'
        # Show available masks.
        mfls = LFU.show_filenames('msk', 'txt', mandatory=False, instruction=False)
        # Gets mask file name.
        self.intparam['MASK'] = LFU.read_filenames(mfls, title,
                                                   onefile_option=True,
                                                   mandatory=False)

        # Read mask.
        self.read_maskdata()
        
        # Define the interval list of azimuthal angle range.
        self.intparam['ANGLES'] = self._read_angles_from_command_line()

        # Choose normalization method.
        self.intparam['NORM'] = self._normalization_from_command_line()

        return

    ##
    def write_logfile (self):
        '''Write parameters and report of integration to log file. The name of
        the log file is built from de parameters file name plus da
        current date and time.

        '''

        # Header message.
        stars = 80 * '*'
        msg = (f'{stars}'
               f'\n Log file {self.logfile} from SAXS measurements.'
               f'\n {stars}\n\n' 
               f' Azimuthal avearging will be performed with'
               f' the following parameters.')
        
        # Write to file.
        with open (self.logfile, 'w') as logname:

            logname.write(msg)

            for i in self.indesc:
                name = self.indesc[i]
            
                if (name in self.intparam):
                    # Skip if the (non mandatory) parameter is not defined.
                    if (self.intparam[name] == None or self.intparam[name] == []): continue

                    nm = ' ({0})'.format(name.lower())
                    ds = self.description[name].capitalize() + ' '
                    logname.write('\n{0:>12} {1:.<55}'.format(nm, ds),)
                    namelist = [ x for x in sorted(self.intparam[name]) if x != '' ]
                    logname.write(" {:42}".format(str(namelist[0])))

                    L = len(self.intparam[name])
                    V = ' {0:>11} {1}'.format('[', L)
                    V += ' entry ]' if (L == 1) else ' entries ]'
                    logname.write(V)
                    
                    for item in namelist[1:]:
                        if (item != ''):
                            logname.write('\n' + 69 * ' ' + '{:<40}'.format(item))
                    logname.write('\n')

            # Write out warnings and other informations to log file.
            if (self.info != ''):
                print ('\n There were warning messages. Please, check'
                       + ' the log file ({0}).'.format(self.logfile))
            logname.write(self.info + '\n')

        logname.close()
        #
        return

    # Lambda: extract ordered pairs from tuple in string.
    pair_in_str = lambda self, S: [ float(t) for t in S.strip('()').split(',') ]
    
    # Lambda: create a list of ordered pairs from string with pairs.
    # If string is empty, skip it.
    parse_angles = lambda self, A : [ self.pair_in_str(S) for S in A if S != '' ]
    
    ## 
    def read_maskdata (self):
        '''Read mask data from mask file. Make due corrections accordingly to foxtrot
        or fit2d generated mask.

        '''

        try:
            msk = self.intparam['MASK'][0]
            if (msk.endswith('.msk')):
                # Fit2D mask, open it using fabio module
                self.maskdata = fabio.open(msk).data
            elif (msk.endswith('.txt')):
                # Foxtrot mask
                self.maskdata = np.loadtxt(msk, dtype='uint8', delimiter=';')
                # Invert Foxtrot mask
                self.maskdata = 1 - self.maskdata
            elif (msk.endswith('.npy')):
                # Numpy mask.
                self.maskdata = np.load(msk)
            else:
                raise Exception(' No valid mask found.')
            warning = '\n Using "{}" as mask.\n'.format(self.intparam['MASK'][0])
        except:
            warning = '\n No mask previously defined, a transparent one will be created.\n'
            # Use first sample as dimension reference.
            im = fabio.open(self.intparam['SAMPLE'][0])
            # Create matrix with zeros.
            self.maskdata = np.zeros((int(im.header['Dim_1']),
                                      int(im.header['Dim_2'])), dtype=np.float)
            
        print(warning)
        self.info += warning
        return
    
    ##
    def _read_angles_from_command_line (self):
        '''Asks an angle interval.'''
        
        print ('\n Choose angular range for azimuthal integration (optional).'
                + '\n Type the integration ranges using the structure: (angle, delta).'
                + '\n For example, \"(0,20) (-45,10)\" will integrate in both'
                + ' angular ranges, [-10, 10] and [-50, -40].'
                + '\n Any other entry structure will be disregarded.')
        
        print (' The angles are given in degrees, from 0 to 360'
                + ' counterclockwise.')
    
        while True:
            print ('\n Type the central angle and total range of integration \n'
                    + ' or just \'ENTER\' for default range (from 0 to 360 degrees).')

            ainput = input(' ? > ')
            try:
                angles = re.findall(r'\([-+]?[0-9]*\.?[0-9]+\ *,\ *[-+]?[0-9]*\.?[0-9]+\)', ainput)
            except:
                print (' Error: could not extract angular ranges from user\'s entry.')
                continue
    
            if (angles == []):
                fangles = [(0, 360)]
                warning = ('\n Integrating from 0 to 360 degrees.'
                           + '\n WARNING: assuming equal angular ranges '
                           + 'for all files to be processed.')
                self.info += warning
                break
            else:
                # Strings must be converted into numerical tuples for validity
                # checking.
                fangles = self.parse_angles(angles)
            
            # Check validity of angles.
            for fangle in fangles:
                while (fangle[0] < 0.0 or fangle[0] > 360.0):
                    print ('\n\n ERROR: {0} is out of limits! '.format(fangle))
                    opt = input(' Retype or ignore? [r/I] > ')
                    if (opt == 'r'):
                        ra = input(' Retype tuple: ')
                        na = self.pair_in_str(ra)
                        fangles.remove(fangle)
                        fangles.append(na)
                        print (' Substituted old pair {0} '.format(fangle)
                                + 'for new pair {1} in the list. '.format(na))
                    else:
                        print (' Eliminating the pair {0} from list.'.format(fangle))
                        fangles.remove(fangle)

            # Confirm choices
            print ('\n These are the chosen angular ranges: \n')
            for a in fangles:
                print (' ', tuple(a))
            conf = input('\n Confirm? [Y/n] ',)
            if (conf == 'n'):
                print (' Type again.')
            else:
                warning = ('\n WARNING: assuming equal angular ranges' 
                           + 'for all files to be processed.')
                self.info += warning
                break
        
        # Reformat angles to accomplish module pattern:
        # (mean angle, delta) --> (initial, final), clockwise integration.
        return self._transform_angles(fangles)
    
    ##
    def _transform_angles (self, angles):
        '''Calculate angle interval for integration accordingly to module
        standards.

        '''        
        newangles = []
        for a in angles:
            # Special case: reset interval for whole circle.
            if (a[1] == 360.0):
                newangles.append((-180.0, 180.0))
                continue
        
            # Convert angles from (mean angle, angular interval) to
            # conventional range (inital angle, final angle).
            A, B = a[0] - a[1] * 0.5, a[0] + a[1] * 0.5
            newpair = (A, B)

            # Ignore redundant pair.
            if (newpair in newangles):
                warning = ('\n WARNING: '
                           + ' ignoring redundant pair {0}'.format(newpair)
                           + ' in variable ANGLES (after transformation).')
                self.info += warning
            else:
                newangles.append(newpair)
        return newangles
    
    ##
    def _normalization_from_file (self):
        '''Check normalization parameter and define normalization value.

        '''
        try:
            # Test whether the normalization flag NORM is defined.
            if ('NORM' not in self.intparam
                or self.intparam['NORM'] == ['']
                or self.intparam['NORM'] == ['None']):
                warning = ('\n WARNING: normalization parameter not pre-defined.'
                           + ' The value 1.0 will be used.')
                self.info += warning
                print (warning)
                self.intparam['NORM'] = [ 1.0 ]
                
            # If NORM is defined.
            else:
                # Normalization by water reference.
                if (self.intparam['NORM'][0] == 'WATER'):
                    # Check whether EMPTY and WATER are both defined.
                    if ('WATER' not in self.intparam or
                        'EMPTY' not in self.intparam):
                        raise Exception (
                            '\n\n ERROR: absolute normalization by water'
                            ' demands a water file as well as a file for'
                            ' an empty capillary; either is not defined.')
                    else:
                        # Define dictionary of files for water integration. The
                        # normalization factor is calculated in main program.
                        self.normdict = {}
                        for p in [ 'WATER', 'EMPTY', 'NOISE', 'SHADOW' ]:
                            try    :
                                self.normdict[p] = self.intparam[p]
                            except :
                                self.normdict[p] = []
                        # self.normfactor = LNORM.water(self.aintegrator)
                        
                # Normalization by glassy carbon reference.
                elif (self.intparam['NORM'][0] == 'GC'):
                    if (self.intparam['GC'][0] == ''):
                        raise Exception ('\n\n ERROR: GC not defined. ')
                    else:
                        self.normfactor = LNORM.glassy_carbon()

                # Normalization from formerly calculated parameters (PARFILE).
                elif (self.intparam['NORM'][0] == 'PARFILE'):
                    if (self.intparam['PARFILE'][0] == ''):
                        raise Exception ('\n\n ERROR: PARFILE not defined. ')
                    else:
                        self.normfactor = LNORM.parfile(self.intparam['PARFILE'])
                        
                # If a floating point is given as normalization factor.
                elif (re.match(r'[0-9]*\.?[0-9]+\ *', self.intparam['NORM'][0])):
                    #pat = re.compile(r'[0-9]*\.?[0-9]+\ *')
                    #self.intparam['NORM'] = pat.findall(self.intparam['NORM'][0])
                    self.normfactor = float(self.intparam['NORM'][0])
                    
                # Otherwise.
                else:
                    warning = ('\n\n WARNING: '
                               + 'Normalization factor cannot be obtained. '
                               + ' The value 1.0 will be used.')
                    self.info += warning
                    
        #
        except Exception as err:
            self.info += str(err)
            print (err)
            print (' ERROR: Please, check the parameters file'
                   + ' ({0}). Aborting.'.format(self.pfilename))
            self.write_logfile ()
            sys.exit(1)
        
        # Remove not used normalizations from list of parameters.
        for item in self.normlist:
            if (item != self.intparam['NORM'][0] and
                 item in self.intparam):
                del self.intparam[item]
        
        #
        return
    
    ##
    def _read_water_norm_params (self):
        '''Read files for normalization by water scattering cross section from
        command line: water, empty, noise and shadow files.

        '''
        
        LFU.section_separator('*', 'Normalization by WATER scattering cross section ')
    
        print (' ATTENTION! For better accuracy of this normalization procedure,')
        print (' the WATER and the EMPTY should be measured at the same capillary')
        print (' or sample holder.')
        
        self.normdict = {}
    
        # Choose files for azimuthal average, subtraction and correction
        flist = LFU.show_filenames('edf', mandatory=True, instruction=True)
        
        # Choose samples' files
        s = ' Choose WATER file (mandatory):'
        self.normdict['WATER'] = LFU.read_filenames(flist, s,
                                                         onefile_option=True,
                                                         mandatory=True)
    
        # Choose a background file
        s = ' Choose EMPTY file (optional):'
        self.normdict['EMPTY'] = LFU.read_filenames(flist, s,
                                                         onefile_option=True)
        
        # Choose a noise file
        s = ' Choose only one NOISE file (optional):'
        self.normdict['NOISE'] = LFU.read_filenames(flist, s,
                                                         onefile_option=True)
    
        # Choose a shadow correction file
        s = ' Choose only one SHADOW CORRECTION file (optional):'
        self.normdict['SHADOW'] = LFU.read_filenames(flist, s,
                                                        onefile_option=True)

        return

    ##
    def _normalization_from_command_line (self):
        '''Define normalization method or value.

        '''
        
        print ('\n Absolute scale NORMALIZATION? ')
        norm_options = ['   1) None (nomalization factor = 1.0)',
                        '   2) Water scattering cross section',
                        '   3) Glassy Carbon standard sample (not implemented yet)',
                        '   4) .PAR file from SUPERSAXS XEUSS',
                        '   5) Type the normalization factor (a value)']

        opt = LFU.menu_closed_options(norm_options)
        self.norm_option = norm_options[int(opt)-1].strip()
        # Define normalization accordingly to choice.
        if   (opt == '1'):
            self.normfactor = 1.0
        elif (opt == '2'):
            # Read file names for water normalization: water, empty, noise,
            # shadow an store them in self.normdict. Normalization factor for
            # water case is calculated in the main program.
            self._read_water_norm_params()
        elif (opt == '3'):
            self.normfactor = LNORM.glassy_carbon()
        elif (opt == '4'):
            # Choose PAR files
            flist = LFU.show_filenames('PAR', mandatory=False, instruction=True)
            s = ' Choose PAR file:'
            fpar = LFU.read_filenames(flist, s, onefile_option=True, mandatory=False)
            self.normfactor = LNORM.parfile(fpar)
        elif (opt == '5'):
            self.normfactor = LFU.type_float('\n Type the normalization factor: ')

        return [ self.normfactor ]

        
## 
def main():
    '''
    Main function.
    '''
    
    try:
        line = getopt.getopt(sys.argv[1:], "hemf:")
    except getopt.GetoptError as err:
        print (f' ERROR: {err}.')
        sys.exit(1)

    try:
        if (line[0][0][0] == '-h'):
            help('XS_libreadparameters.read_parameters')
            return
    except:
        pass
    
    p = read_parameters(line)
    

## 
if __name__ == "__main__":
    main ()
