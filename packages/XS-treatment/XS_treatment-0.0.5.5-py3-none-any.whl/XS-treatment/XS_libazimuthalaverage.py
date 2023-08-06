#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Perform azimuthal integration using pyFAI module.'''

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
import fabio
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import scipy
import sys
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

##
def result_filename (edffilename, angle):
    '''Define output file basename from edf file name. Return new name. Extensions
    as rad, rds, rdn or rsr must be added aftewards.

    General template:

    <file name>_<* azim int>_<S/W><file number>

    S/W : SAXS or WAXS
    file number: preserve number from original file for safety

    azim int: azimuthal interval, only * if different from (-180, 180)

    File extensions are added in later functions.

    '''
    # The basename from original edf file.
    basename = edffilename.replace('.edf', '')
    
    # Get sample name.
    fname = re.match('.AXS_+([A-Za-z0-9\-]+)_+(.*)_*', basename)
    if fname is None:
        fname = edffilename
        print(f' WARNING: file name does not match pattern;'
              f' falling back to former name ({fname}).')

    try: 
        filetype = re.sub('_+', '_', fname.group(1)).strip('_')
        filename = re.sub('_+', '_', fname.group(2)).strip('_')
        rootname = re.sub('_+[0-9]+', '', filename)        
    except:
        rootname = basename
        filetype = ''
        
    # Azimuthal angle interval is added if not the default (-180, 180).
    if (abs(float(angle[0])) == 180.0 and abs(float(angle[1])) == 180.0):
        anglestr = ''
    else:
        anglestr = '_{0:=+04.0f}_{1:=+04.0f}'.format(angle[0], angle[1])
        
    # File number (from edf file).
    try:
        filenum = re.search('_[0-9]{4}.', basename).group(0).strip('._')
    except:
        filenum = ''

    # Get SAXS / WAXS experiment type.
    try:
        sws = re.search('_([01])_', edffilename)  # Standard file name.
        if sws is None:
            # Name changed by extractlog.
            sws = re.search('[SW]AXS', edffilename, re.I) 
        sw = sws.group(0)    # Get 'SAXS' or 'WAXS'.
    except Exception as err:
        # Nothing found, fall back to SAXS as default.
        print(f'WARNING: could not identify {basename} file type,'
              f' assuming SAXS. Please, check file names in directory.'
              f'\n (Exception: {err})')
        sw = 'SAXS'

    # Define measurement type suffix.
    swtype = 'W' if (sw not in ['SAXS', '0']) else 'S'
        
    # Final name. Background file is distinguished by prefix, since
    # its name is usually the same as samples.
    #if (filetype == 'background'):
    #    finalname = f'BACK_{rootname}{anglestr}_{swtype}{filenum}'
    #else:
    #    finalname = f'{rootname}{anglestr}_{swtype}{filenum}'
    
    if (filetype in ['background', 'direct', 'water', 'empty']):
        finalname = f'{filetype[:5]}_{rootname}{anglestr}_{swtype}{filenum}'
    else:
        finalname = f'{rootname}{anglestr}_{swtype}{filenum}'
        
    return finalname

##
def complete_header_file(filename, time, detector, qlen):
    '''Prepend time, detector and number of lines to file header.'''

    # Read data from file.
    with open(filename, 'r') as fn:
        data = fn.read()

    # Write complementary information and reinsert data to file (the
    # file must be rewritten).
    with open(filename, 'w') as fn:
        fn.write(f'#   Time        Detector\n'
                 f'#  {time}      {detector}\n'
                 f'# {qlen}\n')
        fn.write(data)

    return

## 
def shadow_correction(file_shadow, fdir):
    '''Beam-stopper shadow correction using a glassy carbon measured curve.'''
    
    # ...
    q_GC, I_GC, sigma_GC, t_GC, N_GC, shheader = LFU.read_data_file(file_shadow, fdir)

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
    normsigma_GC[:locmax] = np.sqrt((normI_GC[:locmax] *
                                     sigma_GC[:locmax] /
                                     I_GC[:locmax])**2 +
                                    (normI_GC[:locmax] *
                                     sigma_Nfactor / Nfactor)**2)

    # Write out data to RDN file.
    rdnfile_name  = file_shadow.replace('.rad', '')
    LFU.write_file(rdnfile_name, q_GC, normI_GC, normsigma_GC, 1., 1.,
                   fileext='RDN', header=shheader)

    return q_GC, normI_GC, normsigma_GC

## 
def azimuthal_average(edffile, prm, phi, noisefile=None):
    '''Calculate azimuthal average of files, given edf file name, data
    parameters (prm), azimuthal interval (phi) and noise file
    (optional). Act as a front-end to pyFAI integrate1d.

    Return a tuple with rad file name, data (q, I, sigma I), and header
    info (time, detector).

    '''

    # Get some relevant parameters explicitly.
    maskdata    = prm.maskdata
    aintegrator = prm.aintegrator

    # Define the number of bins (points in the integration) as the number
    # of pixels of the diagonal of the detector from the p.o.n.i. to the
    # corner.  Formerly, npt = 533.
    nx  = aintegrator.poni1 / aintegrator.pixel1
    nz  = aintegrator.poni2 / aintegrator.pixel2
    npt = int(np.sqrt(nx**2 + nz**2))
    
    # Open edf file object 
    #im = fabio.open(edffile)
    im = LFU.open_edf(edffile)
    
    # Variance matrix, if exists.
    try:
        varfile    = 'var_' + edffile
        #varmatrix  = fabio.open(varfile).data
        varmatrix  = LFU.open_edf(varfile).data
        errormodel = None
        print(f'\n WARNING: using variance matrix from file {varfile}\n')
    except:
        varmatrix  = None
        errormodel = 'poisson'
        print(f'\n Obs.: No variance matrix file found for {edffile}.'
              ' Using poisson error model for integration.')
    
    # Noise file, if it exists.
    noisedata = None
    if (noisefile != None):
        try:
            imdark = LFU.open_edf(edffile)
            noisedata = imdark.data / imdark.header['ExposureTime']
        except Except as err:
            print('\n WARNING: could not open dark file: {err}. Skipping.')

    # Output file name.
    newname = result_filename(edffile, phi)
    outname = f'rad/{newname}.rad'
    
    # Create rad directory if necessary.
    if not os.path.exists('rad'):
        os.makedirs('rad')
    
    # Time parameter for header of 'rad' file.
    time = im.header['ExposureTime']
    # Counts parameter for header of 'rad' file
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
    
    # Azimuthal averaging with pyFAI methods.
    # Polarization_factor: 0 (random), -1 (total V), +1 (total H).
    q, I, sigma = azint.integrate1d(im.data,
                                    npt,
                                    filename = outname,
                                    variance = varmatrix,
                                    error_model = errormodel,
                                    azimuth_range = phi,
                                    polarization_factor = 0,
                                    correctSolidAngle = True,
                                    mask = maskdata,
                                    dark = noisedata,
                                    method = "splitpixel",
                                    unit="q_A^-1")

    # Prepend time, detector count and number of q entries to file. This is
    # necessary for compatibility with former versions of the program (mostly,
    # CLPO's version) and to calculate normalizations.
    complete_header_file(outname, float(time), float(detector), len(q))
    
    return (newname, q, I, sigma, float(time), float(detector))

##
def log_rebinning (q, I, sigma):
    '''Log-rebinning of intensities, according to CLP Oliveira's recipe
    for SUPERSAXS.

    '''

    qlog = np.array([])
    Ilog = np.array([])
    slog = np.array([])

    n = 0
    while (n < len(q)):
        # Define rebinning step for each interval.
        if   (q[n] <= 0.03): step = 1
        elif (q[n] <= 0.06): step = 2
        elif (q[n] <= 0.10): step = 4
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

##
def plot_curves (q, I, IS, IB, IC, IN, sigma, sigmaS, sigmaB, sigmaN,
                 scBG, NS, NB, fnoise, noiseNorm, WaterNorm):
    '''Plot intensity curves for examination.'''

    plt.figure()
    plt.errorbar(q, IS / NS * WaterNorm, yerr = sigmaS / NS * WaterNorm, label='sample')
    plt.errorbar(q, scBG * (IB / NB) * WaterNorm, yerr = scBG * sigmaB / NB * WaterNorm,
                 label='background')
    if (len(fnoise) != 0): 
        plt.errorbar(q, IN * noiseNorm * WaterNorm,
                     yerr = sigmaN * noiseNorm * WaterNorm , label='noise')
    plt.errorbar(q, I * IC, yerr = sigma, label='without shadow correction')
    #plt.plot(q, I, label='final')
    plt.errorbar(q, I, yerr = sigma, fmt='o', ms=4, label='final')
    plt.legend(numpoints=1, loc=0)
    plt.xscale('linear')                  # Abscissas scale
    plt.yscale('log')                     # Ordinates scale
    plt.xlabel(u'$q\,(A^{-1})$')          # Abscissas unit
    #plt.xlabel(u'$q\,(\u00c5^{-1})$')    # Abscissas unit (alternative)
    plt.ylabel('I (a.u.)')                # Ordinates unit
    #plt.ylabel(u'$I\,(cm^{-1})$')        # Ordinates unit (alternative)
    plt.tight_layout()
    #plt.imshow(origin = 'lower')
    plt.show()
    plt.close()

    return
    
##
def subtract_intensity_curves (fsample, fback, fnoise, fshadow,
                               WaterNorm, fdir, examine):
    '''Data treatment of the scattering intensity curve (fsample) under directory
    fdir: background subtraction (fback), noise subtraction (fnoise), shadow
    correction (fshadow), absolute or relative scale normalization
    (WaterNorm). Examine each graphic (boolean examine) to redefine background
    scale.

    '''
    
    out = (f'\n {"Sample ":.<20} {fsample}'
           f'\n {"Background ":.<20} {fback}'
           f'\n {"Noise ":.<20} {fnoise}'
           f'\n {"Shadow ":.<20} {fshadow}')
    print(out)

    '''In the following, t (tS, tB) is measurement time and N (NS, NB,
    etc.) is detector counts, given in header file. So N is already
    beam intensity X transmittance. '''
    
    # S for sample.
    qS, IS, sigmaS, tS, NS, sampheader = LFU.read_data_file(fsample, fdir)
    # B for background.
    qB, IB, sigmaB, tB, NB, backheader = LFU.read_data_file(fback, fdir)

    # Noise for subtraction, N for noise.
    if (fnoise == []):
        qN, IN, sigmaN, tN, detnoise = 0., 0., 0., 1., 1.
    else: 
        qN, IN, sigmaN, tN, detnoise, noiseheader = LFU.read_data_file(fnoise[0], fdir)

    # Shadow correction, C for glassy carbon
    if (fshadow == []): 
        qC, IC, sigmaC = 0., 1., 0.
    else:
        qC, IC, sigmaC = shadow_correction(fshadow[0], fdir)
        
    # Use the same abscissa for all sets.
    q = qS
    # Scale factor for background subtraction from sample's intensity
    scaleBG = 1.
    # Transmitance ratio.
    ratio = (NB * tS) / (NS * tB)
    print(f'\n Transmitance ratio (Tback / Tsample): {ratio:.4g}')

    # Loop over all samples as many times as necessary for fixing background levels.
    while (True):
        
        # Same formulas used by Cristiano in SUPERSAXS. See software's manual.
        noiseNorm = (1. / tN) * (tS / NS - tB / NB)
        I = ((IS / NS) - scaleBG * (IB / NB) - (noiseNorm * IN)) * (1. / IC) * WaterNorm
        #
        sigma1sq = ((sigmaS / NS)**2. + (scaleBG * sigmaB / NB)**2.
                    + (sigmaN * noiseNorm)**2.) * (WaterNorm / IC)**2.
        sigma = np.sqrt(sigma1sq + (I / IC * sigmaC)**2.)
        
        # Plot curves if they must be examined.
        if (examine):
            plot_curves(q, I, IS, IB, IC, IN, sigma, sigmaS, sigmaB, sigmaN,
                        scaleBG, NS, NB, fnoise, noiseNorm, WaterNorm)
        
        loop = input('\n Change scale for background subtraction [y/N]? ')
        if (loop == 'y'):
            while True:
                shot = np.mean(IS[-50:-1]) * NB / (np.mean(IB[-50:-1]) * NS)
                try:
                    scaleBG = float(input('  Type new scale of transmission factor'
                                        f' (shot = {shot:.3}): '))
                    break
                except Exception as err:
                    print('\t {err}')
                    continue    
            continue
        else:
            break


    # 
    q, I, sigma = LFU.CleanData(q, I, sigma)

    # Output file name.
    outfile = fsample.replace('.rad', '')

    # RDS: processed data file.
    LFU.write_file(outfile, q, I, sigma, 1.0, 1.0, fileext='RDS',
                   header=sampheader)

    # RSR: log-rebinned processed data file
    qlog, Ilog, slog = log_rebinning(q, I, sigma)
    LFU.write_file(outfile, qlog, Ilog, slog, tS, 1.0, fileext='RSR',
                   header=sampheader)

    #
    return q, I, sigma, scaleBG, ratio
                    

def main():
    help('XS_libazimuthalaverage')

if __name__ == '__main__':
    main()
