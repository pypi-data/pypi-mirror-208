#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Library for image plotting.'''

__version__   = '2.4.1'
__author__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__credits__ = 'Dennys Reis & Arnaldo G. Oliveira-Filho'
__email__ =  'dreis@if.usp.br ,agolivei@if.usp.br'
__license__ = 'GPL'
__date__   = '2022-09-14'
__status__   = 'Development'
__copyright__ = 'Copyright 2022 by GFCx-IF-USP'
__local__ = 'GFCx-IF-USP'

import copy
import getopt
import gzip
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import fabio
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

# Generic parameters.
im_supported = ['bmp', 'eps', 'jpg', 'jpeg', 'pdf', 'png', 'raw', 'svg', 'tif']
DEFAULT_IMAGE_FORMAT = 'png'
DEFAULT_MAP_SCALE = 'log'

# Define default parameters.
fopt = {
    'cmapscale'   : DEFAULT_MAP_SCALE,
    'imageformat' : DEFAULT_IMAGE_FORMAT,
    'color'       : True,
    'colorbar'    : False,
    'saveimage'   : False,
    'quiet'       : False
}

# 
def menu_options ():
    '''Pick parameters from interactive menus. Ask for files and plot
    options: map scale (lin/log), save image or not, output format
    (bmp, png, tig, etc.), color ou gray scale.

    '''
    
    # Title
    LFU.section_separator('*', 'Plot Images ')
    
    # Choose images files to be shown.
    filelist = LFU.show_filenames('edf', mandatory=True, instruction=True)
    s = ' Choose image files to plot:'
    filenames = LFU.read_filenames(filelist, s, mandatory=True)
    
    # Options for image plot
    LFU.section_separator('*','Options for Image Plot')
    
    # Option: color map scale
    while True:
        mapscale = input('\n Scale of color map.'
                         + '\n Type \"lin\" for linear scale, or just \"ENTER\"'
                         + ' for default \"log\" scale: ')
        if (mapscale not in ['lin', 'log', '']):
            print (' Option not listed. Choose a valid one!')
        else:
            if (mapscale != ''): fopt['cmapscale'] = mapscale
            break

    # Default saved image format.
    fopt['imageformat'] = DEFAULT_IMAGE_FORMAT
    # Option: save image?
    fopt['saveimage'] = input('\n Save image? [y/N] ')
    if (fopt['saveimage'] == 'y' or fopt['saveimage'] == 'Y'):
        fopt['saveimage'] = True
        # Option: output image format.
        while True:
            imageformat = input('\n Format of output image.'
                                + '\n Type ' + ', '.join(im_supported)
                                + ' or just <ENTER> for tif: ' )
            if (imageformat not in im_supported + ['']):
                print (' Option not listed. Type a valid one.')
            else:
                if (imageformat != ''):
                    fopt['imageformat'] = imageformat
                break
    else:
        fopt['saveimage'] = False
        
    
    # Option: plot color bar?
    cbar = input('\n Plot colorbar? [y/N] ')
    fopt['colorbar'] = True if (cbar == 'y') else False
    
    # Option: color / gray scale?
    clr = input('\n Image(s) in gray scale (g) or in color (c)? [g/C]')
    fopt['color'] = False if (clr == 'g') else True

    # 
    return fopt, filenames

#
def plot_images(fopt, imagefiles):
    '''Plot 2D edf images and save to conventional format
    (png, jpg, tif, eps, pdf, etc.) if requested.

    '''
    
    # Iterate over each image.
    for imagefile in imagefiles:
        image = fabio.open(imagefile)
        
        # Plot figure considering chosen figures' options
        #fig = plt.figure(frameon=False)
        #plt.figure(frameon=False)
        fig = plt.figure(figsize = (15, 15))
        #ax = fig.add_subplot(1,1,1)
        #ax.margins(0)
        #fig.add_axes(ax)
        #plt.add_axes(ax)
        #colormap = mpl.cm.viridis if (fopt['color']) else mpl.cm.gray
        if (fopt['color']):
            colormap = copy.copy(mpl.cm.get_cmap('viridis'))
        else:
            colormap = copy.copy(mpl.cm.get_cmap('gray'))
        colormap.set_bad('k')
        
        if (fopt['saveimage']):
            # Correct extension for image format. Create it in current directory.
            newname  = imagefile.replace('.edf', f".{fopt['imageformat']}").replace('../', '')
            # Calculate log10 of data array (with numpy mask module).
            im  = np.ma.log10(image.data)
            plt.imsave(newname, im, format=fopt['imageformat'])
            # Write image matrix to file.
            #newname = imagefile.replace('.edf', '.dat.gz').replace('../', '')
            ##np.set_printoptions(threshold=np.nan)
            #np.set_printoptions(threshold=sys.maxsize)
            #with gzip.open(newname, "wb") as f: f.write(str(np.array(image.data)))
            
        # Skip to the next image if in batch mode.
        if (fopt['quiet']): continue
            
        if (fopt['cmapscale'] == 'lin'): 
            plt.imshow(image.data, cmap=colormap, vmin=0, visible=True,
                       origin='upper')
        else:
            plt.imshow(image.data, cmap=colormap, interpolation='none',
                       norm=mpl.colors.LogNorm(vmin=1), visible=True,
                       origin='upper')
                
        plt.tick_params(bottom='off', left='off', top='off', right='off',
                        labelbottom='off', labelleft='off', which='both',
                        direction='in')
        
        plt.axis('off')
        if (fopt['colorbar']): plt.colorbar()
        plt.tight_layout()
        plt.show()

    return


def main():
    help('XS_libimageplot')

if __name__ == '__main__':
    main()
