import numpy as np
import requests
import zipfile
import io
import os
import pprint
import re
import time
import h5py as h
import ee
import folium

class gt:
    def __init__(self, alt, lon, lat):
        self.alt = alt
        self.lon = lon
        self.lat = lat

class gt1l(gt):
    def __init__(self, alt, lon, lat):
        super().__init__(alt, lon, lat)

class gt1r(gt):
    def __init__(self, alt, lon, lat):
        super().__init__(alt, lon, lat)

class gt2l(gt):
    def __init__(self, alt, lon, lat):
        super().__init__(alt, lon, lat)

class gt2r(gt):
    def __init__(self, alt, lon, lat):
        super().__init__(alt, lon, lat)
    
class gt3l(gt):
    def __init__(self, alt, lon, lat):
        super().__init__(alt, lon, lat)
    
class gt3r(gt):
    def __init__(self, alt, lon, lat):
        super().__init__(alt, lon, lat)

class granule:
    def __init__(self, hFile, short_name):
        f=h.File(hFile, 'r+')
        self.product = short_name
        if self.product=='ATL06': 
            path='/land_ice_segments/'
            alt=path+'h_li'
            lon=path+'longitude'
            lat=path+'latitude'
        elif self.product=='ATL03': 
            path='/geolocation/reference_photon_'
            alt='heights'
            lon=path+'lon'
            lat=path+'lat'
        tracks = ['gt1l', 'gt1r', 'gt2l', 'gt2r', 'gt3l', 'gt3r']
        self.tracks = tracks
        alts = [np.array(np.array(f[t+path+'h_li']).tolist()) for t in tracks]
        lons = [f[t+path+'longitude'][:] for t in tracks]
        lats = [f[t+path+'latitude'][:] for t in tracks]
        self.alt = alts
        for a in alts:
            a[a>1e20] = float('nan')
        self.lon = lons
        self.lat = lats
        self.gt1l = gt1l(self.alt[0], self.lon[0], self.lat[0])
        self.gt1r = gt1r(self.alt[1], self.lon[1], self.lat[1])
        self.gt2l = gt2l(self.alt[2], self.lon[2], self.lat[2])
        self.gt2r = gt2r(self.alt[3], self.lon[3], self.lat[3])
        self.gt3l = gt3l(self.alt[4], self.lon[4], self.lat[4])
        self.gt3r = gt3r(self.alt[5], self.lon[5], self.lat[5])

# not in use currently, separates path directories and puts them into a list
def pullDirs(path):
	dirs = []
	path = path[1:]
	while len(path)>0:
		slash = path.find('/')
		dirs.append(path[:slash])
		path = path[(slash+1):]
	return dirs

def getPolygon(file):
    res = np.genfromtxt(file, delimiter=',')
    return res.reshape([int(len(res)/2), 2])

def getGranulePaths(shelfname):
    paths = []
