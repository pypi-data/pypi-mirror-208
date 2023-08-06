#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Calculate absolute normalizations of intensities.

Absolute scale by water scattering cross section or by certified
glassy carbon plaquette (to be implemented).

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
import itertools
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import scipy.optimize
import time
import fabio
import pyFAI

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
import XS_libfileutils as LFU
import XS_libreadparameters as LRP
from XS_libazimuthalaverage import azimuthal_average as AZaverage
from XS_libazimuthalaverage import subtract_intensity_curves as SICurves

mpl.rc('mathtext',default='regular')

##
def parfile(fpar):
    '''Calculate normalization factor from PAR file.'''
    
    if ( not fpar == [] ):
        # Read PAR files
        with open(fpar[0], 'r') as par:
            I0_water = float(par.readline().split(',')[1])
            # cm-1, theoretical scattering cross section for water, 20oC
            dE = 0.01632
            # normalization factor
            return dE / I0_water
    else:
        print ('\n No \'.PAR\' file chosen. Assuming default normalization factor.')
        return 1.0


# Straight line.
def line(x, a, b):
    return a * x + b


#
def water (fdict, parfilename, maskfile, aintegrator, q, I, sigma, scale, ratio):
    '''Water file integrator.'''

    while True:

        print ('\n Type the q range for fitting:')
        qmin = LFU.type_float('   Qmin (1/A) = ')
        qmax = LFU.type_float('   Qmax (1/A) = ')

        indices = np.intersect1d( np.where(q > qmin)[0], np.where(q < qmax)[0])

        # fit data using Scipy's Levenberg-Marquardt method
        nlfit, nlpcov = scipy.optimize.curve_fit(line,
                                                 q[indices],
                                                 I[indices],
                                                 sigma = sigma[indices] )
      
        # unpack fitting parameters
        A, B = nlfit
        errA, errB = [ np.sqrt(nlpcov[j, j]) for j in range(nlfit.size) ]

        # create fitting function from fitted parameters
        qfit = np.linspace(0.9 * qmin, 1.1 * qmax)
        Ifit = line(qfit, A, B)

        #Calculate residuals and reduced chi squred
        #residuals = I[indices] - line(q[indices], A, B)
        #redchisq = ( (residuals/sigma[indices])**2 ).sum()/float(q[indices].size-2)

        print('\n{}'.format(80 * '*'))
        amin, amax = -180., 180.
        water_txt = '\n\t\t'.join(fdict['WATER'])
        empty_txt = '\n\t\t'.join(fdict['EMPTY'])
        noise_txt = '\n'.join(fdict['NOISE'])
        shadow_txt = '\n'.join(fdict['SHADOW'])
        info = (f'\n\n### Normalization by WATER scattering cross section. ### '
                f'\n\tWATER file:\n\t\t{water_txt}'
                f'\n\tEMPTY file:\n\t\t{empty_txt}'
                f'\n\tNOISE file:\n\t\t{noise_txt}'
                f'\n\tSHADOW CORRECTION file:\n\t\t{shadow_txt}'
                f'\n {"Mask file":.<45}{maskfile}'
                f'\n {"Azimuthal angle range (in degrees)":.<45}'
                f'[{amin:4.1f}, {amax:4.1f}]'
                f'\n {"Options for background subtraction":.<45}'
                f'Only one background file for subtraction.'
                f'\n {"Scales for background subtraction":.<45}{scale:4.3f}'
                f'\n {"Transmittance ratio (Tback/Tsample)":.<45}{ratio:4.3f}'
                f'\n\n\tFit function: I = aq + b'
                f'\n\tQ range for fit: [{qmin:4.2f}, {qmax:4.2f}]'
                f'\n\tResults from fitting:'
                f'\n\t\ta = {A:>10.3g} ({errA:>8.3g})'
                f'\n\t\tb = {B:>10.3g} ({errB:>8.3g})'
                f'\n\n\n Azimuthal integrator data:\n\n{aintegrator}' )
        print(info)

        wname = fdict['WATER'][0].replace('.edf','')
        ename = fdict['EMPTY'][0].replace('.edf','')
        outname = f'water_normalization_{wname}_{ename}'
        
        #Create figure window to plot data
        fig, ax = plt.subplots()
        ax.errorbar(q[indices], I[indices], yerr=sigma[indices],
                    fmt='o', ms=4., c='b')
        ax.plot(qfit, Ifit, 'k-', lw = 1.5)
        #ax.set_xlabel(r'$q\,(\u00c5^{-1})$')
        ax.set_xlabel(r'$q\,(A^{-1})$')
        ax.set_ylabel ('I (a.u.)')
        plt.tight_layout()
        fig.savefig(f'{outname}.png')
        plt.show()

        loop = input('\n Finish fit [ENTER] or retry [r]? ')
        if loop == 'r':
            continue
        else:
            print ('\n Curve fit completed.\n')
            break
    
    # save fitted parameters to a file
    tm = time.strftime("%Y-%m-%d %H:%M:%S")
    sep = 80 * '*'
    header = (f'\n\n{sep}\n Date: {tm}\n Directory: {os.getcwd()}'
              f'\n Used Python libraries: '
              f'\n\t{fabio.__name__} {fabio.version} {fabio.__status__}'
              f'\n\t{pyFAI.__name__} {pyFAI.version}')
    
    with open('normalization.log','a') as recfile:
        recfile.write( header + info )

    with open(parfilename, 'w') as output:
        qS, IS, sigmaS, tS, NS, header = LFU.read_data_file(fdict['WATER'][0], 'rad')
        output.write('{0:.1f}, {1:.6g}\n'.format(tS, B))
        
    I0_water = B
    # cm-1, theoretical scattering cross section for water, 20oC
    dE = 0.01632
    
    return dE / I0_water


#...
def glassy_carbon(prm):

    LFU.section_separator('Normalization by GLASSY CARBON scattering cross section.')
    
    print(' The following calculations assume that you measured the'
          ' glassy carbon sample ???? better accuracy of this normalization procedure,'
          ' the WATER and the EMPTY should be measured at the same capillary'
          ' Normalization data from file: S315_Glassy Carbon N 1.dat')

    # Dictionary for files to be integrated.
    fdict = {}

    # Choose files for azimuthal average, subtraction and correction
    flist = LFU.show_filenames('edf', True, True)

    # Choose samples' files
    s = ' Choose the GLASSY CARBON file (mandatory):'
    fdict['gc'] = LFU.read_filenames(flist, s, onefile_option=True,
                                     mandatory=True)

    # Choose a background file
    s = ' Choose BACKGROUND file (optional):'
    fdict['empty'] = LFU.read_filenames(flist, s, onefile_option=True)
    
    # Choose a noise file
    s = ' Choose only one NOISE file (optional):'
    fdict['noise'] = LFU.read_filenames(flist, s, onefile_option=True)

    # Choose a shadow correction file.
    s = ' Choose only one SHADOW CORRECTION file (optional):'
    fdict['shadow'] = LFU.read_filenames(flist, s,
                                         onefile_option=True)
    
    # Choose mask file.
    maskfile, maskdata = LRP.read_maskfile()
    
    # Loop over edf files.
    # List of all files.
    wlist = [ y for x in fdict.values() for y in x ]
    #wlist = list(itertools.chain(*fdict.values()))
    for wfile in wlist:  
        q, I, sI, tm, detector = AZaverage(wfile, prm, [-180., 180.])

    wdict = LFU.change_fileext(copy.deepcopy(fdict), oldext='.edf',
                               newext='.rad')

    if (fdict['empty'] != []):
        # Data treatment from glassy carbon file.
        LFU.section_separator('#', 'Data Treatment for Glassy Carbon Normalization')
        q, I, sigma, scale, ratio = SIcurves(wdict['gc'][0],
                                             wdict['empty'][0],
                                             wdict['noise'],
                                             wdict['shadow'], 1.,
                                             'rad')
    else:
        q, I, sigma, t, det = LFU.read_file(wdict['gc'][0], 'rad')
        I /= det
        sigma /= det 
        scale = 0.
        ratio = 0.

    # Read the reference glassy carbon file. Known differential
    # scattering cross-section per unit volume.
    gcpath = (os.path.dirname(os.path.abspath(__file__))
              + '/glassy_carbon/S315_Glassy Carbon N 1.dat')
    q_std, I_std, e_std = np.genfromtxt(gcpath, usecols=(0,1,2),
                                        skip_header=45, unpack=True)
    # [thickness] in cm.
    gc_thick = 0.1

    #...
    qmin = max(q.min(),q_std.min())
    qmax = min(q.max(),q_std.max())

    ind = np.intersect1d(np.where(q >= qmin), np.where(q <= qmax)) 
    q, I, sigma = q[ind], I[ind], sigma[ind]
    Int = scipy.integrate.simps(I,q,even='last')

    ind = np.intersect1d(np.where(q_std >= qmin), np.where(q_std <= qmax))
    q_std, I_std, e_std = q_std[ind], I_std[ind], e_std[ind]
    Int_std = scipy.integrate.simps(I_std, q_std, even='last')

    #...
    Kratio = Int_std / Int

    #...
    print('\n{0}'.format(87*'*'))
    amin, amax = -180., 180.
    gc_txt = '\n\t\t'.join(fdict['WATER'])
    empty_txt = '\n\t\t'.join(fdict['EMPTY'])
    noise_txt = '\n'.join(fdict['NOISE'])
    shadow_txt = '\n'.join(fdict['SHADOW'])
    info = ('\n\n Normalization by GLASSY CARBON scattering cross section\n'
            f'\n\tGLASSY CARBON file:\n\t\t{gc_txt}'
            f'\n\tEMPTY file:\n\t\t{empty_txt}'
            f'\n\tNOISE file:\n\t\t{noise_txt}'
            f'\n\tSHADOW CORRECTION file:\n\t\t{shadow_txt}'
            f'\n {"Mask file":.<45}{maskfile}'
            f'\n {"Azimuthal angle range (in degrees)":.<45}'
            f'[{amin:4.1f}, {amax:4.1f}]'
            f'\n {"Options for background subtraction":.<45}'
            f'Only one background file for subtraction.'
            f'\n {"Scales for background subtraction":.<45}{scale:4.3f}'
            f'\n {"Transmittance ratio (Tback/Tsample)":.<45}{ratio:4.3f}'
            f'\n\n\tResults of curves integrations:'
            f'\n\t\tQ range for integrations: [{qmin:4.2f}, {qmax:4.2f}]'
            f'\n\t\tGC reference curve: I = {Int_std:>10.3g}'
            f'\n\t\tGC measured curve:  I = {Int:>10.3g}'
            f'\n\t\tGC sample thickness: {gc_thick:>5.3g} cm'
            f'\n\n\n Azimuthal integrator data:\n\n{aintegrator}')
    print(info)
    
    outname = 'gc_norm_{}'.format(fdict['gc'][0].replace('.edf',''))

    # Create figure window to plot data
    fig, ax = plt.subplots()
    ax.errorbar(q, Kratio * I, yerr=Kratio*sigma, fmt='.',
                label='measured, normalized data')
    ax.errorbar(q_std, I_std, yerr=e_std,fmt='.',
                label='reference data')
    ax.legend()
    ax.set_xlabel(r'$q\,(\AA^{-1})$')
    ax.set_ylabel(r'$I\,(cm^{-1})$')
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.tight_layout()
    fig.savefig(outname+'.png')
    plt.show()
  
    # Save fitted parameters to normalization.log file
    tm = time.strftime("%Y-%m-%d %H:%M:%S")
    sep = 80 * '*'
    header = (f'\n\n{sep}\n Date: {tm}'
              f'\n Directory: {os.getcwd()}'
              f'\n Used Python libraries: '
              f'\n\t{fabio.__name__} {fabio.version} {fabio.__status__}'
              f'\n\t{pyFAI.__name__} {pyFAI.version}')

    # Write out integration information to log file.
    with open('normalization.log','a') as recfile:
        recfile.write( header + info )

    return gc_thick * Kratio


def glassy_carbon():
    print ('\n GLASSY CARBON: Not implemented yet.')
    return 1.


def main():
    help('XS_libnormalizations')

if __name__ == "__main__":
    main()
