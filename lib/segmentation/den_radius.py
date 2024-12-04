import numpy as np
import time
from rich.console import Console
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from scipy.interpolate import CubicSpline, KroghInterpolator
from math import ceil
from scipy.stats import mode
from scipy.signal import convolve2d
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from scipy.interpolate import griddata

import matplotlib.pyplot as plt # test

console = Console()

def mask_droplet(img, x_cen, y_cen, radius):
    y_grid, x_grid = np.ogrid[:img.shape[0], :img.shape[1]]
    drop_mask = np.where((x_grid - x_cen)**2 + (y_grid - y_cen)**2 <= radius**2, 1, 0)
    return drop_mask

def cropdrop(img, x_cen, y_cen, radius):
    invsqrt = 1/np.sqrt(2)
    # Convert center and radius values to integer slices
    x_min = int(max(0, x_cen - invsqrt*radius))
    x_max = int(min(img.shape[1], x_cen + invsqrt*radius))
    y_min = int(max(0, y_cen - invsqrt*radius))
    y_max = int(min(img.shape[0], y_cen + invsqrt*radius))
    # Crop the region from the image
    just_drop = img[y_min:y_max, x_min:x_max].flatten()
    # Generate the x and y grid for the cropped region
    y_grid, x_grid = np.mgrid[y_min:y_max, x_min:x_max]
    # Calculate x and y coordinates relative to the center
    x = (x_grid - x_cen).flatten()
    y = (y_grid - y_cen).flatten()
    i = y_max - y_min
    j = x_max - x_min
    print(f'jd len {just_drop.size}, x len {x.size}, y len {y.size}')
    return just_drop, x, y, i, j

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

# def den_radii(droplet_image, droplet_list):
#     img = droplet_image.img
#     locs = droplet_image.locs()
#     drop_li = droplet_list
    
#     den_radius_li = []
    
#     for i, droplet in enumerate(drop_li):
        
#         droplet.mask = mask_droplet(img, droplet.x, droplet.y, droplet.dil_radius)
#         pos = np.where(droplet.mask == 1)
#         x_pos = pos[1]
#         y_pos = pos[0]
#         r_pos, theta_pos = cart_to_pol(x_pos - droplet.x, y_pos - droplet.y)
#         values = img[y_pos, x_pos]
        
#         try:
#             x, y = bin_and_average(r_pos, values)
#             rho, I = droplet_signal(np.array(x), np.array(y))
#             DI, D2I, D3I = diff(rho, I)
#             r_den, fwhm = get_r_den(rho, D2I)
#             den_radius = r_den
#             den_radius_li.append(den_radius) 
        
#         except:
#             den_radius = 0.0
#             den_radius_li.append(den_radius) 
        
#         # if i >= 17 and i <= 17:
            
#         #     plt.plot(r_pos, norm(values), marker = "o", linestyle = "", color = "black", alpha = 0.4)
#         #     plt.plot(rho, norm(I), marker = "o", linestyle = "", color = "red", alpha = 1)
#         #     # plt.plot(np.linspace(0,30,100), double_sphere_radial(np.linspace(0,30,100), popt[0], popt[1], popt[2], popt[3], popt[4]), color = color[i-17])
#         #     plt.plot(rho, norm(DI), color = "red", marker = "", linestyle = ":")
#         #     plt.plot(rho, norm(D2I), color = "green", marker = "", linestyle = "--")
#         #     plt.plot(rho, norm(D3I), color = "blue", marker = "", linestyle = "-.")
#         #     plt.xlabel("$\\rho$ (px)")
#         #     plt.ylabel("Gray Value (a.u.)")
            
#     return den_radius_li

# make cartesian coordinate mesh
def mesh(im):
    x = np.arange(im.shape[1])
    y = np.arange(im.shape[0])
    xv, yv = np.meshgrid(x, y, indexing='xy')
    return (xv, yv)

def reshape_flattened_image(flattened_array, original_shape):
    """
    Helper funcction for den_radii
    Reshapes a flattened array back into its original image shape.
    
    Parameters:
        flattened_array (numpy.ndarray): The flattened array of the image.
        original_shape (tuple): The original shape of the image (height, width, channels).
        
    Returns:
        numpy.ndarray: The reshaped array in the original image shape.
    """
    # Check if the flattened array size matches the product of the original shape dimensions
    if flattened_array.size != np.prod(original_shape):
        raise ValueError("The size of the flattened array does not match the specified original shape.")
    # Reshape the flattened array back to the original shape
    reshaped_image = flattened_array.reshape(original_shape)
    return reshaped_image

def dist(x1, y1, x2, y2):
    return np.sqrt(np.square(x1-x2)+np.square(y1-y2))

def plot_surface_and_scatter(intensity_surface, x_surface, y_surface, intensity_scatter, x_scatter, y_scatter):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Surface plot part
    xi = np.linspace(min(x_surface), max(x_surface), 100)
    yi = np.linspace(min(y_surface), max(y_surface), 100)
    X, Y = np.meshgrid(xi, yi)
    
    # Interpolate intensity values for the surface plot using scipy's griddata
    Z = griddata((x_surface, y_surface), intensity_surface, (X, Y), method='linear')
    
    # Create the surface plot
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, edgecolor='none', alpha=0.7)

    # Scatter plot part
    sc = ax.scatter(x_scatter, y_scatter, intensity_scatter, c=intensity_scatter, cmap='plasma', s=50, edgecolor='k')

    # Add labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Intensity')

    # Add color bars for surface and scatter plot
    fig.colorbar(surf, ax=ax, pad=0.1, label='Surface Intensity')
    fig.colorbar(sc, ax=ax, pad=0.1, label='Scatter Intensity')

    # Show the plot
    plt.show()
    
def plot_surface_3d(intensity, x, y):
    # Generate grid for x and y values
    xi = np.linspace(min(x), max(x), 100)
    yi = np.linspace(min(y), max(y), 100)
    X, Y = np.meshgrid(xi, yi)
    
    # Interpolate intensity values onto the grid using scipy's griddata
    Z = griddata((x, y), intensity, (X, Y), method='linear')
    
    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the surface
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, edgecolor='none')

    # Add labels for each axis
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Intensity')

    # Add a color bar for the intensity values
    cbar = fig.colorbar(surf, ax=ax, pad=0.1)
    cbar.set_label('Intensity')

    # Show the plot
    plt.show()
    
def redchisq(obs, exp, stdev, dof):
    return np.sum(np.square(obs-exp)/np.square(stdev))/dof


def den_radii(droplet_image, droplet_list, psf):
    img = droplet_image.img
    drop_li = droplet_list
    den_radius_li = []
    
    psfnorm = (psf - 142)/np.sum(psf - 142)
    
    for i, droplet in enumerate(drop_li):
        print(f'\nFitting droplet {i}')
        drop_data, X, Y, i, j = cropdrop(img, droplet.x, droplet.y, droplet.dil_radius)
        
        drop = drop_data
        # drop = drop/np.sum(drop)
        
        # get condrop fit guess
        droplet.mask = mask_droplet(img, droplet.x, droplet.y, droplet.dil_radius)
        pos = np.where(droplet.mask == 1)
        x_pos = pos[1]
        y_pos = pos[0]
        r_pos, _ = cart_to_pol(x_pos - droplet.x, y_pos - droplet.y)
        values = img[y_pos, x_pos]
        
        try:
            x, y = bin_and_average(r_pos, values)
            rho, I = droplet_signal(np.array(x), np.array(y))
            DI, D2I, D3I = diff(rho, I)
            r_den_guess, _ = get_r_den(rho, D2I)
            print(f'r den guess = {r_den_guess}')
        except:
            print('Could not guess r_den.')
            r_den_guess = 0
        
        
         # condrop intensity profile function (sphere height profile convolved with psf) 
        def profile(xy_tuple, R, bg, A, B, shape = (i, j)):
            x, y = xy_tuple
            sp = np.where(dist(x, y, 0, 0)<R, A*2*np.sqrt(R**2-(x)**2-(y)**2), 0)
            sp = sp + np.where(dist(x,y,0,0)<droplet.dil_radius, B*2*np.sqrt(droplet.dil_radius**2 - x**2 - y**2),0)
            spr = reshape_flattened_image(sp, shape)
            #print(f'spr shape {spr.shape} | psfnorm shape {psfnorm.shape}')
            con = convolve2d(spr, psfnorm, mode ='same')
            res = bg + con.flatten()
            return res
        
        # x,y = np.mgrid[-100:100, -100:100]
        # p = profile((x.flatten(),y.flatten()), 10, 0, 10, shape = (x.shape))
        # print(f'LEN p = {len(p)}, len x = {len(x)}')
        # im = reshape_flattened_image(p, x.shape)
        # plt.imshow(im)
        # plt.show()
        
        def sphere_profile(x, y, x_cen, y_cen, R, bg, A):
            return np.where(dist(x, y, x_cen, y_cen)<R, bg + A*2*np.sqrt(R**2-(x-x_cen)**2-(y-y_cen)**2), bg)
        
        # x,y = np.mgrid[:15, :15]
        # im = convolve2d(sphere_profile(x, y, 8, 8, 4, 1, 10), psfnorm)
        # s = im.shape
        # im = im.flatten()
        # im = reshape_flattened_image(im,s)
        # plt.imshow(im)
        # plt.show()
        
        # prepare fitting data
        I = drop
        XY = (X, Y)
    
        empty = [0,0,0,0]
        try:
            if len(I) < 25:
                raise ValueError('Not enough data for fit, skipping')
            guess = [r_den_guess, mode(drop, axis = None)[0], np.max(drop)/(2*r_den_guess), np.min(drop)/(2*r_den_guess)]
            # the max height of the sphere profile is A * r, so roughtly np.max(drop)/r_den_guess will be "A"
            try:
                if guess:
                    popt, pcov, info, _, _ = curve_fit(profile, XY, I, p0 = guess, maxfev = 1000, method = 'lm', full_output=True)
                    print(f'guesses: radius={guess[0]}, bg={guess[1]}, A={guess[2]}, B={guess[3]}')
                    print(f'fit:\n\tr_den={popt[0]}\n\tr_dil={droplet.dil_radius}\n\tbg={popt[1]}\n\tA={popt[2]}\n\tB={popt[3]}')
                    print(f'inguess - output = {guess[0]-popt[0]}')
                    dof = len(I)-len(popt)-1
                    GRAYNOISESTD = 45
                    chisq = redchisq(I, profile(XY, *popt), GRAYNOISESTD, dof)
                    print(f'\tchisq={chisq}')
                    print(f'\tnfev:{info["nfev"]}')
                    
                    # plot_surface_and_scatter(profile(XY, *popt), X, Y, I, X, Y)
                    # plot_surface_3d(profile(XY, *popt), X, Y)
                else:
                    raise ValueError('Unable to provide guesses for this fit.')
            except UnboundLocalError as ule:
                print(ule)
                popt = np.zeros_like(empty)
                pcov = np.zeros_like(empty)
            except ValueError as ve:
                print(ve)
                popt = np.zeros_like(empty)
                pcov = np.zeros_like(empty)
            except RuntimeError as re:
                print(re)   
                popt = np.zeros_like(empty)
                pcov = np.zeros_like(empty)
            except:
                print("Something bad happened to this fit. Whatver that something was happened to be so bad that it was entirely unpredictable so you are getting this message. This fit should be skipped entirely, but perhaps take caution when interpreting the results.")
                popt = np.zeros_like(empty)
                pcov = np.zeros_like(empty)
                
        except ValueError as E:
            print(E)
            print('flub it we ball')
            popt = np.zeros_like(empty)
            pcov = np.zeros_like(empty)
        
        fit_rden = popt[0]
        fit_bg = popt[1]
        fit_A = popt[2]
        uncs = np.sqrt(np.diag(pcov))
        fit_rden_u = uncs[0]
        fit_bg_u = uncs[1]
        fit_A_u = uncs[2]
        
        den_radius_li.append(fit_rden)
    
    print(f'Average dense phase radius: {np.mean(np.array(den_radius_li))}')
    return den_radius_li