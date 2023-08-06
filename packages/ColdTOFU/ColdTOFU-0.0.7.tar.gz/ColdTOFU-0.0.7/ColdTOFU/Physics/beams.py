import numpy as np
import matplotlib.pyplot as plt


class GaussianBeam(object):
    def __init__(self, wLen, w0, n=1):
        self.wLen = wLen/n
        self.w0 = w0
        self.zR = np.pi*w0**2/wLen

    def w(self, z):
        '''Waist of the beam at z'''
        return self.w0*np.sqrt((1+(z/self.zR)**2))

    def R(self, z):
        '''Radius of curvature of the wavefront at z'''
        return z*np.sqrt(1+(z/self.zR)**2)

    def gouyPhase(self, z):
        '''Gouy phase at z'''
        return np.arctan2(z, self.zR)

    def field(self, x, y, z):
        '''Complex field value at (x, y, z)'''
        rsq = x**2 + y**2
        k = 2*np.pi/self.wLen
        amp = (self.w0/self.w(z))*np.exp(-rsq/self.w(z)**2)
        phase = k*(z+rsq/(2*self.R(z)))-self.gouyPhase(z)
        return amp*np.exp(-1j*phase)

    def intensity(self, x, y, z):
        '''Intensity at (x, y, z)'''
        rsq = x**2+y**2
        inten = (self.w0/self.w(z))**2*np.exp(-2*rsq/self.w(z)**2)
        return inten

    def complexBeamParameter(self, z):
        '''complex beam parameter q'''
        q = z+1j*self.zR
        return q


