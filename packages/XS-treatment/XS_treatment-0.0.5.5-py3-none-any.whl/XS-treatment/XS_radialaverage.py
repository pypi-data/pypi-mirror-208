#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Calculate SAXS/WAXS curves by radially integrating EDF files.

Usage:
    XS_radialaverage.py [-e] -f <file>
or  XS_radialaverage.py -me
or  XS_radialaverage.py -h

where:
  -h : this message
  -e : examine each curve graphic (default is quiet)
  -m : read parameters from interactive menu
  -f <file> : read parameters from <file>. (Use the program
              extract_saxslog.py to create a parameters file from a
              xlsx spreadsheet log file.

Calculate the intensity curves resulting from radial integration over
given radial (q) and azimuthal (phi) intervals of EDF files performed
by the Python 3 pyFAI Module. The program reads sample, background,
shadow, noise (dark), water (absolute normalization) and mask files,
and performs due integrations, then add or subtracts and normalizes
the resulting curves. The results are written in text format with
three columns (phi, intensity, sigma_intensity) and a header with
lines preceeded by '#'.

This script is part of the XS-treatment suite for SAXS WAXS data
treatment.

'''

__version__   = '2.4.1'
__author__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__credits__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__email__ = 'dreis@if.usp.br ,agolivei@if.usp.br'
__license__ = 'GPL'
__date__   = '2022-09-14'
__status__   = 'Development'
__copyright__ = 'Copyright 2022 by GFCx-IF-USP'
__local__ = 'GFCx-IF-USP'

import copy
import getopt
import itertools
import glob
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import re
import scipy.signal
import sys
import time
import fabio
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

from XS_libazimuthalaverage import result_filename

mpl.rc('mathtext', default = 'regular')
#plt.rcParams['font.size'] = 12.0

## 
def radial_average(edffile, prm, phi, qrad):
    '''Calculate radial average of files. Receives the edf file data to be
    integrated over, the integrator (based on poni data), the mask file and the
    azimuthal and radial ranges. Returns the set of angles and corresponding
    intensities.

    Obs.: Take care with the choice of "radial_range" (tuple(float, float)) and
    "azimuth_range" (tuple (float, float)).

    '''

    # Get some relevant parameters explicitly.
    maskdata    = prm.maskdata
    aintegrator = prm.aintegrator

    # Define the number of bins (points in the integration) as the number of
    # pixels of the diagonal of the detector from the p.o.n.i. to the corner.
    # Formerly, npt = 533.
    nx  = aintegrator.poni1 / aintegrator.pixel1
    nz  = aintegrator.poni2 / aintegrator.pixel2
    npt = int(np.sqrt(nx**2 + nz**2))

    # open edf file object 
    im = fabio.open(edffile)

    # Variance matrix, if exists.
    try:
        varfile    = 'var_' + edffile
        varmatrix  = fabio.open(varfile).data
        errormodel = None
        print('\n WARNING: using variance matrix from file {0}\n'.format(varfile))
    except:
        varmatrix  = None
        errormodel = 'poisson'
        print('\n Obs.: No variance matrix file found.', end = '')
        print(' Using poisson error model for integration.\n')
    
    # Noise file, if it exists.
    noisedata = None
    if (noisefile != None):
        try:
            imdark    = fabio.open(edffile)
            noisedata = imdark.data / imdark.header['ExposureTime']
        except Except as err:
            print(' WARNING: could not open dark file: {}'.format(err))
            print(' Skipping.')
            
    
    #extension = ('_q{0:4.3f}_{1:4.3f}'.format(qrad[0], qrad[1])
    #             + '_a{0:=+04.1f}_{1:=+04.1f}'.format(phi[0], phi[1]))
    #radfile_name = edffile.replace( '.edf', extension)
    #radfile_name = re.sub('../', '', radfile_tmp)
    radfile_name = result_filename(edffile, phi)

    # Time parameter for header of 'rad' file
    time = im.header['ExposureTime']
    # counts parameter for header of 'rad' file
    detector = im.header['Detector']

    # Correct the discontinuity of the integration azimuthal domain.
    # Deep copy of pyFAI integrator, but with discontinuity at zero.
    integrator2 = copy.deepcopy(aintegrator)
    integrator2.setChiDiscAtZero()                 
   
    # Choose the integrator accordingly to azimuth range.
    if (phi[0] < 180. < phi[1]):
        azint = integrator2
    elif (phi[0] < -180. < phi[1]):
        phi[0], phi[1] = phi[0] + 360., phi[1] + 360.
        azint = integrator2
    else:
        azint = aintegrator
    
    # call pyFAI to radial average
    phi, I = integrator.integrate_radial(im.data, 
                                         npt,
                                         filename = outname,
                                         variance = varmatrix,
                                         npt_rad = 100, 
                                         error_model = errormodel,
                                         radial_range = qrad, 
                                         azimuth_range = phi, 
                                         polarization_factor = 0,
                                         correctSolidAngle = True,
                                         mask = maskdata,
                                         dark = noisedata,
                                         method = 'splitpixel', 
                                         unit = 'chi_deg', 
                                         radial_unit='q_A^-1') 

    # Error estimate
    sigma = np.sqrt(I)
    
    return (radfile_name, phi, I, sigma, float(time), float(detector))

## 
def shadow_correction(file_shadow, fdir):
    '''Beam-stopper shadow correction using a glassy carbon measured curve
    
    '''
    
    # ...
    q_GC, I_GC, sigma_GC, t_GC, N_GC = LFU.read_data_file(file_shadow, fdir)

    # Find q value of local maxima at the beggining of the glassy carbon
    # curve. Also, the corresponding intensity and uncertainty values
    locmax = scipy.signal.argrelmax(I_GC, order=3, mode='wrap')[0][0]
    Nfactor =  I_GC[locmax]  
    sigma_Nfactor = sigma_GC[locmax]

    # Normalization of intensities
    normI_GC = np.ones_like(I_GC)
    normI_GC[:locmax] = I_GC[:locmax]/Nfactor

    # Normalization of uncertainties
    normsigma_GC = np.zeros_like(sigma_GC)
    normsigma_GC[:locmax] = np.sqrt((normI_GC[:locmax] * sigma_GC[:locmax] /
                                     I_GC[:locmax])**2 + (normI_GC[:locmax] *
                                                          sigma_Nfactor / Nfactor)**2)

    rdnfile_name  = file_shadow.replace('.rad', '')
    #rdnfile_name = re.sub('../', '', rdnfile_tmp)
    
    LFU.write_file(rdnfile_name, q_GC, normI_GC, normsigma_GC, 1., 1., fileext='RDN')

    return q_GC, normI_GC, normsigma_GC


##
def log_rebinning (q, I, sigma):
    '''Log-rebinning of intensities, according to Cristiano's recipe for SUPERSAXS

    '''
    
    qlog = np.array([])
    Ilog = np.array([])
    slog = np.array([])

    n = 0
    while (n < len(q)):

        if   (q[n] <= 0.03): step = 1
        elif (q[n] <= 0.06): step = 2
        elif (q[n] <= 0.10): step = 4
        #elif (q[n] <= 0.30): step = 8
        else: step = 8

        # Arithmetic mean
        ql = np.mean(q[n : n + step])
        Il = np.mean(I[n : n + step])
        # Error of arithmetic mean
        sl = np.sqrt(sum(sigma[n : n + step]**2)) / float(step)
        # Next step
        n += step
        
        qlog = np.append(qlog, ql)
        Ilog = np.append(Ilog, Il)
        slog = np.append(slog, sl)

    return qlog, Ilog, slog


#
def data_treatment (fsample, fback, fnoise, fshadow, norm, fdir, examine):
    '''Data treatment of the scattering intensity curve: background subtraction,
    noise subtraction, shadow correction, absolute or relative scale
    normalization and so on, examine each graphic or not.

    '''
    print ('\n {0:.<20}{1}'.format('Sample:', fsample))
    print (' {0:.<20}{1}'.format('Background:', fback))
    print (' {0:.<20}{1}'.format('Noise:', fnoise))
    print (' {0:.<20}{1}'.format('Shadow:', fshadow))

    # S for sample
    qS, IS, sigmaS, tS, NS = LFU.read_data_file(fsample, fdir)
    # B for background
    qB, IB, sigmaB, tB, NB = LFU.read_data_file(fback, fdir)

    # Noise for subtraction, N for noise
    if (fnoise == []):
        qN, IN, sigmaN, tN, detector = 0., 0., 0., 1., 1.
    else: 
        qN, IN, sigmaN, tN, detector = LFU.read_data_file(fnoise[0], fdir)

    # Shadow correction, C for glassy carbon
    if (fshadow == []): 
        qC, IC, sigmaC = 0., 1., 0.
    else:
        qC, IC, sigmaC = shadow_correction(fshadow[0], fdir)
        
    '''# Quit if list is empty. <<< ARRUMAR FUNÇÃO

    # Esse teste só terá sentido quando o programa tiver opção para fazer o
    # tratamento a partir dos arqs rad. Por enquanto, como tudo é integrado
    # junto, isso não é necessário.

    if not ( np.array_equal(qS, q_back) ):# and np.array_equal(qS,q_noise) and np.array_equal(q,q_GC) ):
        print ' Different q values. Not suitable for data treatment. Quitting.'
        sys.exit(1)
    else:
        q = qS

    '''
    q = qS
    # Scale factor for background subtraction from sample's intensity
    scale = 1.
    
    ratio = (NB * tS) / (NS * tB)
    print ('\n Transmitance ratio (Tback/Tsample): {0:.4g}'.format(ratio))
    
    while True:
        
        # Same formulas used by Cristiano in SUPERSAXS. See software's manual.
        I = ( (IS / NS - scale * (IB / NB)
               - IN / (tN * ((NS / tS) - (NB / tB)))) * (1 / IC) * norm )
        
        sigma1 = ( ((sigmaS / NS) ** 2 + (scale * sigmaB / NB) ** 2
                  + ( sigmaN / (tN * ((NS / tS) - (NB / tB)))) ** 2)
                   * (norm / IC) ** 2 )
        sigma = np.sqrt (sigma1 + (I * sigmaC / IC) ** 2)

        # figure of ...  # ARRUMAR EXPRESSÕES
        if (examine):
            plt.figure()
            plt.errorbar(q, IS/NS*norm, yerr=sigmaS/NS, label='sample')
            plt.errorbar(q, scale*(IB/NB)*norm, yerr=scale*sigmaB/NB, label='background')
            #if fnoise == []: 
            #    plt.errorbar(q, IN/( tN*((NS/tS)-(NB/tB)) )*norm, label='noise')
            plt.errorbar(q, I*IC, yerr=sigma, label='without shadow correction')
            plt.errorbar(q, I, yerr=sigma, fmt='o', ms=4, label='final')
            plt.legend(numpoints=1,loc=0)
            #plt.xscale('log')                  #<---- OPÇÕES PARTICULARES DA ANÁLISE.
            plt.xscale('linear')                #<---- OPÇÕES PARTICULARES DA ANÁLISE.
            plt.yscale('log')                   #<----
            #plt.xlabel(ur'$q\,(\u00c5^{-1})$') #<----
            plt.xlabel(u'$q\,(A^{-1})$')       #<----
            plt.ylabel('I (a.u.)')              #<----
            #plt.ylabel(ur'$I\,(cm^{-1})$')     #<----
            plt.tight_layout()
            plt.show()
            plt.close()
        
        loop = input('\n Change scale for background subtraction [y/N]? ')
        if loop == 'y':
            while True:
                shot = np.mean(IS[-50:-1])*NB/(np.mean(IB[-50:-1])*NS)    
                try:
                    scale = float(input('   Type new scale of transmission factor'
                                        + ' (shot = {0:.3}): '.format(shot)))
                    break
                except Exception as err:
                    print ('\t ', err)
                    continue    
            continue
        else:
            break


    # CONVERSÃO, LINHA TEMPORÁRIA
    q, I, sigma = LFU.CleanData(q, I, sigma)

    output = fsample.replace('.rad', '') + '__' + fback.replace('.rad', '')
    #output = re.sub('../', '', outtmp)

    # generates RDS, processed data file
    LFU.write_file(output, q, I, sigma, 1.0, 1.0, fileext='RDS')

    # generates RSR, log-rebinned processed data file
    qlog, Ilog, slog = log_rebinning(q, I, sigma)
    LFU.write_file(output, qlog, Ilog, slog, tN, detector, fileext='RSR')

    return  q, I, sigma, scale, ratio



# Data treatment from RAD files
def treat (fdict, nfactor, fdir='.', fromfile = False, multisubt = True, examine = False):

    # Options for background files and corresponding subtractions
    
    scales = []
    transmittances = []

    try:    fnoise  = fdict['NOISE']
    except: fnoise  = []
    #
    try:    fshadow = fdict['SHADOW']
    except: fshadow = []

    # (i) Azimuthal averaging of files with no background.
    if (fdict['BACKGROUND'] == None or fdict['BACKGROUND'] == []):
        subt_option = 'Only azimuthal averaging of the files.'

    # (ii) One background file only.
    elif (len(fdict['BACKGROUND']) == 1):
        subt_option = 'Only one background file for subtraction.'

        try:    fback   = fdict['BACKGROUND'][0]
        except: fback   = []
        
        # Loop over samples' files.
        for sample in fdict['SAMPLE']:
            dt_result = data_treatment(sample, 
                                       fback, fnoise, fshadow,
                                       nfactor, fdir, examine)
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
            
        # (iii-a) One-to-one association.
        if (multisubt == False):
                        
            # Check if background and sample arrays have same length. Quit if not. 
            if (not (len(fdict['BACKGROUND']) == len(fdict['SAMPLE']))):
                print(' Background and sample arrays have different lengths.')
                print(' Equal lengths is mandatory for this option. Quitting.')
                sys.exit(1)
            else: 
                subt_option = 'Multiple background files: one-to-one ordered association.'

            print (" WARNING: subtracting backgrounds in one-to-one association. ")
                
            for bkgd, sample in zip(fdict['BACKGROUND'], fdict['SAMPLE']):
                dt_result = data_treatment(sample, bkgd,
                                           fnoise, fshadow,
                                           nfactor, fdir, examine) 
                scales.append(dt_result[3])
                transmittances.append(dt_result[4])

        # (iii-b) Subtract each background file from all samples.
        else:

            print (" WARNING: subtracting all backgrounds from each sample file. ")

            subt_option = ( 'Multiple background files: subtract all'
                            + ' background files from each sample.' )
            # loop over backgrounds' files
            for bkgd in fdict['BACKGROUND']:
                # loop over samples' files
                for sample in fdict['SAMPLE']:
                    dt_result = data_treatment(sample, bkgd, fnoise, fshadow,
                                               nfactor, fdir, examine) 
                    scales.append(dt_result[3])
                    transmittances.append(dt_result[4])

    return subt_option, scales, transmittances

#
def scattering_data_treatment (prm):
    ''' '''
    
    # Water normalization option uses data_treatment() routine, therefore
    # preliminary integrations are solved here.
    if ('WATER' in prm.intparam['NORM']):

        # Concatenate iterables.
        #wlist = list( itertools.chain( *fdict.values() ) )
        # Loop over edf files
        for wfile in prm.normdict.values() :
            if (wfile != []):
                radial_average( wfile[0], prm.maskdata, prm.aintegrator, [-180.0, 180.0])
            
        # Data treatment
        LFU.section_separator('*', 'Data Treatment for Water')
        wdict = LFU.change_fileext(copy.copy(prm.normdict),
                                   oldext='.edf',
                                   newext='_-180_+180.rad')
            
        # r = (q, I, sigma, scale, ratio)
        r = data_treatment(wdict['WATER'][0],
                           wdict['EMPTY'][0],
                           wdict['NOISE'],
                           wdict['SHADOW'], 1.0, 'rad', prm.examine)
        # Calculate the normalization factor.
        parfilename = (prm.normdict['WATER'][0].replace('.edf', '') + '_'
                       + prm.normdict['EMPTY'][0].replace('.edf', '.PAR')) 
        prm.normfactor = LNORM.water (wdict, parfilename,
                                               prm.param['MASK'][0], prm.aintegrator, *r)

    # Intervals of integration.
    qradii = prm.param['QRADII']

    # DEBUG
    print ("\n QRADII: {}\n".format(qradii))
    # DEBUG
    
    # LFU.section_separator('*','Options for Azimuthal Averaging ')

    # Concatenate iterables.
    fdict = {}
    for item in ['SAMPLE', 'BACKGROUND', 'NOISE', 'SHADOW']:
        if (item in prm.param.keys()):
            fdict[item] = prm.param[item]

    # Loop over all edf files for averaging.
    for item in fdict.keys():
        # Skip if the (non mandatory) parameter is not defined.
        if (fdict[item] == None): continue

        # Angles and radii (actually, q interval) for integration.
        for interval in qradii:
            qrad = interval[0]
            phis = interval[1]
            print ('\n Integrating over angle: {}'.format(phis))
            print ('\n    and over q interval: {}'.format(qrad))
            
            # Loop over edf files for each item and perform radial
            # integration.
            for datafile in fdict[item]:
                radial_average(datafile, prm.maskdata, prm.aintegrator, phis, qrad)

    # Absolute scale normalization.
    #LFU.section_separator('*','Options for Data Treatment')
    print ('\n Normalization factor: {0:.3e}'.format(prm.normfactor))
    
    # Data treatment
    LFU.section_separator('*', 'Results for Data Treatment')
    records = []
    
    for intervals in qradii:
        qrad = interval[0]
        phis = interval[1]
        oldext = '.edf'
        #newext = 'Q_{0:4.3f}_{:4.3f}_A_{0:4.1f}_{:4.1f}.rad'.format(qrad[0], qrad[1], phis[0], phis[1])
        newext = '_q{:4.3f}_{:4.3f}_a{:=+04.1f}_{:=+04.1f}.rad'.format(qrad[0], qrad[1], phis[0], phis[1])
        tempfdict = LFU.change_fileext(copy.copy(prm.param),
                                             oldext, newext)
    
        #print (' tempfdict = ', tempfdict['SAMPLE'])
        
        subtopt, scales, transmittances = treat (tempfdict,
                                                 prm.normfactor,
                                                 'rad',
                                                 prm.fromfile,
                                                 prm.multisubt,
                                                 prm.examine)
        records.append( [qrad, phis, subtopt, scales, transmittances] )

    return p, records


##        
def write_log_file (prm, records, opscreen):
    '''Write out parameters and integration information to log file.''' 
    
    # Processed data and frame integration options assigned to
    # 'info' variable to print and save. Just in the end of the
    # program to avoid the register of analysis stopped by errors.
    tm = time.strftime("%Y-%m-%d %H:%M:%S")
    sep = 80 * '*'
    header = (f'\n\n XS_radialaverage: '
              f'\n\n{sep}\n Date: {tm}\n Directory: {os.getcwd()}'
              f'\n Used Python modules: '
              f'\n\t{fabio.__name__} {fabio.version} {fabio.__status__}'
              f'\n\t{pyFAI.__name__} {pyFAI.version}'
              f'\n\t{__file__} -- {__version__} {__status__}\n' )

    info = ''
    for k, P in prm.param.items():
        try:
            info += (f'\n\t{prm.description[k]}'
                     '\n\t\t{}'.format('\n\t\t'.join(P)))
        except Exception as err:
            print (f'ERROR: {err}')
    
    #
    for record in records:
        transm = [ '{tmt:.2f}' for tmt in record[4] ]
        info += (f'\n\n {"Azimuthal q range (in $A^{-1}$)":.<45}'
                 f' [{record[0][0]:4.3f}, {record[0][1]:4.3f}]'
                 f'\n {"Azimuthal angle range (in degrees)":.<45}'
                 f' [{record[1][0]:4.1f}, {record[1][1]:4.1f}]'
                 f'\n {"Options for background subtraction":.<45}{record[2]}'
                 f'\n {"Scales for background subtraction":.<45}{record[3]}'
                 f'\n {"Transmittance ratio (Tback/Tsample)":.<45}{transm}'
                 f'\n\n Azimuthal integrator data:\n\n{prm.aintegrator}' )

    # Generate and print record file
    with open(prm.logfile,'a') as recfile:
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
        print ('\n\n ERROR: ', str(err),'\b.')
        sys.exit(1)

    # Read all parameters (from file or command line).
    prm = LRP.read_parameters(line)

    # Help message.
    if (prm.help):
        help('XS_radialaverage')
        return
    
    # Title and opening screen
    title      = 'Frame Integrator for SAXS Data Treatment'
    subheading = 'For XEUSS system at Complex Fluids Group, IFUSP, Brazil'
    opscreen = LFU.opening_screen('*', title, subheading, __author__,
                                  __email__, __date__,
                                  __copyright__, __version__,
                                  __status__)
    print (opscreen)

    # Treat data.
    records = scattering_data_treatment(prm)

    # Print out and record results.
    write_log_file (p, records, opscreen)
    

if __name__ == "__main__":
    main()
