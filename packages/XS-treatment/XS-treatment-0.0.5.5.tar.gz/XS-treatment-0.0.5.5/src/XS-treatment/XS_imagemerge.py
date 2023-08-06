#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Merge EDF images considering the relative positions of the detector.

Usage:
  The choice of files for merging is interactive, just run 
  XS_imagemerge.py

This program Merge EDF images considering the relative positions of
the detector described in the file header. It calculates the correct
overlaping of the images and add up the intensities at each screen
point. In regions where one of the images brings no information, the
counts of the other one is doubled. In any case, a variance matrix is
created with the correct error propagation.

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

import copy
import fabio
import getopt
import itertools
import matplotlib as mpl
import numpy as np
import os
import re
import sys
import time

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
def paired(iterable):
    "Zip into couples: s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

#
def merge_couple(couple, Detnorm):
    '''Merge each couple images considering their relative positions and
    necessary normalizations.'''
    
    if (not len(couple) == 2):
        print ('\n Only two files at a time are allowed to be merged. Quitting.')
        sys.exit(1)
        
    # List of sample files
    #dfs = [ fabio.open(single) for single in couple ]
    dfs = [ LFU.open_edf(single) for single in couple ]
    
    # Previous method to calculate the relative displacement of images based on
    # direct beam positions. These positions are taken from direct beam
    # measurements or from center position of a Ag behenate measurement.
    #CenterX = [ float(df.header['Center_1']) for df in dfs]
    #distX = int( np.round_( max(CenterX) - min(CenterX) ) )
    #CenterY = [ float(df.header['Center_2']) for df in dfs]
    #distY = int( np.round_( max(CenterY) - min(CenterY) ) )
  
    detectors = [ float(df.header['Detector']) for df in dfs ] 
    Times = [ float(df.header['ExposureTime']) for df in dfs ]

    # Pixels dimensions in horizontal (PSize_1) and vertical (PSize_2)
    # directions, in mm, for Pilatus300k and Pilatus 100k detectors.
    PSize_1 = float(dfs[0].header['PSize_1']) * 1000.     # m to mm
    PSize_2 = float(dfs[0].header['PSize_1']) * 1000.     # m to mm

    # Horizontal and vertical displacements, in pixels.
    DETX = [ float(df.header['detx']) for df in dfs ]
    distDETX = int(np.round_((max(DETX) - min(DETX)) / PSize_1))
    #
    DETZ = [ float(df.header['detz']) for df in dfs ]
    distDETZ = int(np.round_((max(DETZ) - min(DETZ)) / PSize_2))

    # Horizontal growth of both images
    img1 = dfs[np.argmax(DETX)]
    img1.data = np.hstack((-np.ones((img1.data.shape[0], distDETX)),
                           img1.data))
    #
    img2 = dfs[np.argmin(DETX)]
    img2.data = np.hstack((img2.data, -np.ones((img2.data.shape[0],
                                                distDETX))))

    # Vertical growth of both images
    img1 = dfs[np.argmin(DETZ)]
    img1.data = np.vstack((-np.ones((distDETZ, img1.data.shape[1])),
                           img1.data))
    #
    img2 = dfs[np.argmax(DETZ)]
    img2.data = np.vstack((img2.data, -np.ones((distDETZ,
                                                img2.data.shape[1]))))

    # Base matrices for grown image and its variance.
    if (img1.data.shape == img2.data.shape):
        img = np.empty(img1.data.shape, np.float32)
        var = np.empty(img1.data.shape, np.float32)     # Variance.
    else:
        print ('\n ERROR: expanded images do not match, '
               + ' horiz. / vert. dimensions differ.\n Quitting.')
        sys.exit(1)

    # Normalization factor for one image defined by countings ratio. Image-1's
    # counts are taken as reference, image-2's counts are normalized by TN x DN
    # = T1/T2 x D1/D2.
    i1 = np.argmin(DETZ)
    try:
        DN = (detectors[i1] / detectors[1 - i1]) if (Detnorm) else 1.0
    except Exception as err:
        DN = 1.0
        print(f' WARNING: while trying to calculate normalization factor:'
              + f'\n   {err}'
              + '\n Maybe detector values are not defined in EDF header.'
              + '\n Setting normalization to 1.')
    # Normalization factor for one image defined by exposure time.
    TN = (Times[i1] / Times[1 - i1]) if (Detnorm) else 1.0
    
    print ('\n Detector normalization: {} '.format(Detnorm)
           + '\n Normalization factor = {:10.6f}\n'.format(DN))

    print ('\n Time normalization: {} '.format(Detnorm)
           + '\n Normalization factor = {:10.6f}\n'.format(TN))

    # Merge images using weighted (time and transmission) sum. Counts are
    # doubled for pixels whose counts are zero for just one detector. A
    # variance matrix is created for correct error propagation in areas with no
    # superposition.
    for x, y in np.ndindex(img.shape):
        if (img1.data[x, y] < 0 and img2.data[x, y] < 0):
            img[x, y] = 0                                            # No counts at all.
            var[x, y] = 0
        
        elif (img1.data[x,y] < 0 and img2.data[x,y] >= 0):
            img[x, y] = 2.0 * DN * TN * img2.data[x, y]              # Double count of img2.
            var[x, y] = 4.0 *img2.data[x,y] 
        
        elif (img1.data[x,y] >= 0 and img2.data[x,y] < 0):
            img[x, y] = 2.0 * img1.data[x, y]                        # Double count of img1.
            var[x, y] = 4.0 * img1.data[x,y]
            
        elif (img1.data[x,y] >= 0 and img2.data[x,y] >= 0):
            img[x, y] = img1.data[x, y] + DN * TN * img2.data[x, y]  # Just weight-add counts.
            var[x, y] = img1.data[x, y] + img2.data[x,y]
            

    # Name of the output image edf file
    second = re.findall('[0-9]{5}[\._]', couple[1])[-1].strip('._') 
    output_name = couple[0].replace('.edf', f'-{second}_merged.edf')
    #remove file, if it exists
    if (os.path.exists(output_name)): os.remove(output_name) 

    # Header of the output image edf file
    output_header = img1.header
    output_header['title'] = output_name
    output_header['Detector'] = str(sum(detectors))
    #output_header['count_time'] = str(sum(times)) 
    output_header['ExposureTime'] = str(sum(Times))
    # Correct image dimensions based on Dim_1,2, displacement and pixel size. 
    output_header['Dim_1'] = str(int(distDETX + float(dfs[0].header['Dim_1'])))
    output_header['Dim_2'] = str(int(distDETZ + float(dfs[0].header['Dim_2'])))

    # Save output file with name 'output_name'
    output = fabio.edfimage.EdfImage(data=img, header=output_header)
    output.save(output_name)

    # Name of the variance output image edf file
    var_outname = 'var_' + output_name
    if os.path.exists(var_outname): #remove file, if exists
        os.remove(var_outname)
    
    # Header of the output image edf file
    variance_header = copy.deepcopy(output_header)
    variance_header['title'] = var_outname
    
    # Save variance image output file with name 'variance_output_name'
    var_output = fabio.edfimage.EdfImage(data = var, header = variance_header)
    var_output.save(var_outname)
    
    # Filenames and parameters of images assigned to 'info' variable to print
    # and save
    info  = '\n\n {0:<44}:{1:^15}:{2:^10}'.format( 'Files', 'Counts', 'time [s]')
    info += ':{:^8}:{:^8}\n'.format( 'detx', 'detz')
    #for name, det, t, detx, detz in zip(couple, detectors, times, DETX, DETZ):
    for name, det, t, detx, detz in zip(couple, detectors, Times, DETX, DETZ):
        info += '\n {0:<44}:{1:^15}:{2:^10.1f}:{3:^8.1f}:{4:^8.1f}'.format(name, det, t, detx, detz)

    info += '\n\n {0:<44}:{1:^15}:{2:^10.1f}\n'.format(output_name, sum(detectors), sum(Times))
    info += '\n Variance file: {0:<44}'.format(var_outname)
    #info += '\n\n {0:<44}:{1:^15}:{2:^10.1f}\n'.format(output_name, sum(detectors), sum(times))

    print(info)

    # Figure of merged image.
    LIP.plot_images(LIP.fopt, [output_name])

    return info

# ...
def merge_images():
    '''Read images from files, group them for merging and write results
    into files.'''

    LFU.section_separator('*', 'Merge of Images ')

    # Choose images files to merge
    filelist = LFU.show_filenames('edf', mandatory = True, instruction = True)
    s = ' Choose image files to merge:'
    filenames = LFU.read_filenames(filelist, s, mandatory=True)
    
    if (len(filenames) % 2):
        print ('\n Odd number of selected files. The merger is done in pairs.')
        print ('\n Next time, select an even number of files. Quitting.')
        sys.exit(1)

    # Normalization by detector counts.
    #Detnorm = LFU.yes_or_no(' Normalize by detector countings?')
    Detnorm = True
    
    couples = [(x, y) for x, y in paired(filenames)]
    cinfos = ''
    for couple in couples:
        cinfos += merge_couple(couple, Detnorm)

    # Filenames and parameters of images assigned to 'cinfos' variable to print
    # and save. Just in the end of the program to avoid the register of
    # analysis stopped by errors.
    tm = time.strftime("%Y-%m-%d %H:%M:%S")
    sep = 87 * '*'
    header = (f'\n\n{sep}\n Date: {tm}\n Directory: {os.getcwd()}'
              f'\n Used Python libraries: '
              f'\n\t{fabio.__name__} {fabio.version} {fabio.__status__}')
    
    # Generate and print record file
    with open('merge.log','a') as record_file:
        record_file.write(header + cinfos)

#
def main():
    '''Read command line parameters and call merging functions.'''

    # Help message.
    try:
        line = getopt.getopt(sys.argv[1:], "h")
    except getopt.GetoptError as err:
        print('\n\n ERROR: ', str(err),'\b.')
        sys.exit(1)
        
    try:
        if (line[0][0][0] == '-h'):
            help('XS_imagemerge')
            return
    except:
        pass

    # Do merging.
    merge_images()
    return

if __name__ == "__main__":
    main()



