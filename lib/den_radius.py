import numpy as np
import time
from rich.console import Console
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from scipy.interpolate import CubicSpline, KroghInterpolator
from math import ceil

import matplotlib.pyplot as plt # test

console = Console()

def mask_droplet(img, x_cen, y_cen, radius):
    y_grid, x_grid = np.ogrid[:img.shape[0], :img.shape[1]]
    drop_mask = np.where((x_grid - x_cen)**2 + (y_grid - y_cen)**2 <= radius**2, 1, 0)
    return drop_mask

def cart_to_pol(x, y):
    r = np.sqrt(np.square(x)+np.square(y))
    theta = np.arctan(y/x)
    return r, theta

def bin_and_average(r, values):
    # averages rho and I values for each pixel interval
        BINSIZE = 1
        limit = ceil(np.max(r))
        rho_avg = []
        val_avg = []
        x = 0
        while x < limit - BINSIZE:
            mask = (r > x) * (r < x + BINSIZE)
            va = np.mean(values[mask])
            ra = np.mean(r[mask])
            val_avg.append(va)
            rho_avg.append(ra)
            x += BINSIZE
        return rho_avg, val_avg
    
def FWHM(max_loc, x, y):
    amax = y[max_loc]
    stop = amax * 0.5
    indR = max_loc
    while indR < len(y) and y[indR] > stop:
        indR += 1
    indL = max_loc
    while indL >= 0 and y[indL] > stop:
        indL += -1
    indR = min(indR, len(x) - 1)
    indL = max(indL, 0)
    fw = x[indR] - x[indL]
    return fw
    
def get_r_den(rho, d2i):
    index = np.argmax(d2i)
    r_den = rho[index]
    fwhm = FWHM(index, rho, d2i)
    return r_den, fwhm
    
def droplet_signal(r, values):
    order = np.argsort(r)
    rho = r[order]
    I = values[order]
    return rho, I

def norm(arr):
    norm_arr = arr / np.max(np.abs(arr))
    return norm_arr

def diff(r, values):
    I = values
    
    DI = np.gradient(I)
    D2I = np.gradient(DI)
    D3I = np.gradient(D2I)
    
    return DI, D2I, D3I

def den_radii(droplet_image, droplet_list):
    img = droplet_image.img
    locs = droplet_image.locs()
    drop_li = droplet_list
    
    den_radius_li = []
    
    for i, droplet in enumerate(drop_li):
        
        droplet.mask = mask_droplet(img, droplet.x, droplet.y, droplet.dil_radius)
        pos = np.where(droplet.mask == 1)
        x_pos = pos[1]
        y_pos = pos[0]
        r_pos, theta_pos = cart_to_pol(x_pos - droplet.x, y_pos - droplet.y)
        values = img[y_pos, x_pos]
        
        try:
            x, y = bin_and_average(r_pos, values)
            rho, I = droplet_signal(np.array(x), np.array(y))
            DI, D2I, D3I = diff(rho, I)
            r_den, fwhm = get_r_den(rho, D2I)
            den_radius = r_den
            den_radius_li.append(den_radius) 
        
        except:
            den_radius = 0.0
            den_radius_li.append(den_radius) 
        
        # if i >= 17 and i <= 17:
            
        #     plt.plot(r_pos, norm(values), marker = "o", linestyle = "", color = "black", alpha = 0.4)
        #     plt.plot(rho, norm(I), marker = "o", linestyle = "", color = "red", alpha = 1)
        #     # plt.plot(np.linspace(0,30,100), double_sphere_radial(np.linspace(0,30,100), popt[0], popt[1], popt[2], popt[3], popt[4]), color = color[i-17])
        #     plt.plot(rho, norm(DI), color = "red", marker = "", linestyle = ":")
        #     plt.plot(rho, norm(D2I), color = "green", marker = "", linestyle = "--")
        #     plt.plot(rho, norm(D3I), color = "blue", marker = "", linestyle = "-.")
        #     plt.xlabel("$\\rho$ (px)")
        #     plt.ylabel("Gray Value (a.u.)")
            
    return den_radius_li