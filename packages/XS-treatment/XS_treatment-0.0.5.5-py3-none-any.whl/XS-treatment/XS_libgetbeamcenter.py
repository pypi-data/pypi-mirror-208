#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np

class get_beam_center ():
    '''This class contains the basic methods to calculate the center of mass of a
    direct beam SAXS imagem in EDF format.

    '''
    def __init__ (self, dbeam, boxsize):
        
        # Pixel size definition.
        self.PSize1 = float(dbeam.header['PSize_1'])
        self.PSize2 = float(dbeam.header['PSize_2'])

        # Exposure time.
        self.Exptime = float(dbeam.header['ExposureTime'])
        
        # The center of mass of the whole image.
        M = np.float64(dbeam.data)
        (imcz, imcx), imm = self.matrix_center(M)

        # Narrow the array down to a box of size 'boxsize' around the center
        # formerly calculated and recalculate its center.
        R = 0.5 * boxsize
        az, bz  = int(imcz - R), int(imcz + R)
        ax, bx  = int(imcx - R), int(imcx + R)

        # Calculate the center of mass of the box in pixels.
        (cz, cx), self.Mass = self.matrix_center(M[az:bz, ax: bx])
        self.Cp = (cz + az, cx + ax)

        # Define beam profile histogram.
        self.profile(M, boxsize)
        
        # Recalculate the center in meters.
        self.C  = self.center() 
        
    #
    #@jit #(nopython = False , parallel = True)
    def matrix_center (self, M):
        '''  Center of mass of a given numpy array M. '''
        
        cz, cx, mass = np.float64((0., 0., 0.))
        L = M[:,0].size   # Number of lines of M.
        C = M[0].size     # Number of columns of M.

        #print(' TYPES : {} {}'.format(type(M[5,5]), type(cx)))
        #sys.exit(0)
        
        # Run through elements of M and add weighted positions.
        for i in range(L):
            for j in range(C):
                # Skip if value is not well defined (= -1, usually masked
                # positions).
                if (M[i, j] == -1): continue
                # Weighted coordinates.
                cz += M[i, j] * i
                cx += M[i, j] * j
                mass += M[i, j]     # Total mass (integral) of the area.
        # Normalize the coordinates.
        cz /= mass
        cx /= mass

        # (Poni1, Poni2) correspond to axes (z, x). m is the total "mass" (the
        # integral of the image).
        return np.float64((cz, cx)), np.float64(mass)

    # Calculate the center, given the Pixel size and the pixel coordinates.
    #@jit(nopython=True)
    def center (self):
        return (self.Cp[0] * self.PSize1, self.Cp[1] * self.PSize2)

    # Beam profile.
    #@jit(nopython=True)
    def profile (self, M, boxsize):
        R = 0.5 * boxsize
        az, bz = int(self.Cp[0] - R), int(self.Cp[0] + R)
        ax, bx = int(self.Cp[1] - R), int(self.Cp[1] + R)
        self.zprofile = np.array([ (z, M[z, int(self.Cp[1])]) for z in range(az, bz + 1) ])
        self.xprofile = np.array([ (x, M[int(self.Cp[0]), x]) for x in range(ax, bx + 1) ])
        return

    #
    #@jit(nopython=True)
    def skewness (self, profile):
        '''Calculate the skewness of the given histogram. This function
        considers the 'profile' of the beam, in the vertical or
        horizontal direction, through the beam center, as a
        distribution and evaluates its assymmetry by the calulation of
        its skewness. The unbiased (sample) Fisher's definition is
        used here, which is the standardized third momentum.

        '''
        # The profile through the center.
        v  = profile[:, 1]
        nv = float(v.size)   # Number of bins.
        # Average value of the 'distribution'.
        av = np.average(v)
        # Third momentum of the distribution.
        v3 = np.array([ (x - av)**3  for x in v ]) 
        m3 = np.average(v3)                          
        # Standard deviation of the sample.
        v2 = np.array([ (x - av)**2  for x in v ])
        s2 = np.sum(v2) / (nv - 1)                   
        # Skewness and "normalized" skewness (by interval size).
        s = m3 / s2**1.5
        return s, s / float(nv)
