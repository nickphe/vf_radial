import os 
import re
import json
import numpy as np
import pandas as pd
from skimage.io import imread
import matplotlib.pyplot as plt
from lib.direct_intensity.data_io import *
from lib.direct_intensity.figures import *
from scipy.stats import mode

four_thirds = 4.0/3.0
pi = np.pi
CAPILLARY_HEIGHT = 65.7 # IN PIXELS, DOOFUS # make this settings

# Sphere math:
# Region 'a' refers to the pure dilute phase forming the ring about the dense phase. Its volume is a sphere with a cyclindrical 'core' bored out.  
# Region 'b' refers to the dilute phase in the 'core'.
# Region 'c' refers to the dense phase in the 'core'.

# R_dil, the radius of the dilute phase is the radius of the emulsion droplet.
# R_den, the radius of the dense phase is the radius of the condensate droplet. 

def _volume_abc(r_dil):
    """
    Calculate the volume of the droplet. 
    Args:
        r_dil (_type_): Radius of dilute phase. 
    Returns:
        Volume of sphere. 
    """
    return four_thirds * pi * (r_dil ** 3)

def _volume_a(r_den, r_dil):
    """
    Calculate the volume of 'donut' forming the ring about dense phase. 
    Args:
        r_den (_type_): Radius of dense phase. 
        r_dil (_type_): Radius of dilute phase. 

    Returns:
        _type_: Volume of the 'donut'.
    """
    # ORIGNAL SCRIPT FOR H 
    # h = np.sqrt(( np.square(r_dil) - np.square(r_den + 1) ))
    h = np.sqrt(( np.square(r_dil) - np.square(r_den) ))
    return four_thirds * pi * (h ** 3)

def _volume_bc(r_den, r_dil):
    """
    Calculate the volume of the 'core' of the sphere. The 'core' is the cylinder with spherical caps. 
    Args:
        r_den (_type_): Dense phase radius, used for radius of cylinder. 
        r_dil (_type_): Dilute phase radius, used for radius of spherical caps. 
    Returns:
        _type_: Volume of 'core'.
    """
    v_donut = _volume_a(r_den, r_dil)
    return ( four_thirds * pi * (r_dil ** 3) ) - v_donut

def _volume_c(r_den):
    """_summary_
    Calculate the volume of the condensate droplet. 
    Args:
        r_den (_type_): Dense phase radius. 
    Returns:
        _type_: Volume of dense phase radius. 
    """
    return four_thirds * pi * (r_den ** 3)

def _volume_b(r_den, r_dil):
    """
    Calculate the volume of the dilute phase inside the 'core'.
    Args:
        r_den (_type_): Dense phase radius. 
        r_dil (_type_): Dilute phase radius. 
    Returns:
        _type_: Volume of dilute phase inside 'core'. 
    """
    return _volume_bc(r_den, r_dil) - _volume_c(r_den)

def _mask_droplet(img, x_cen, y_cen, radius):
    """
    Generate a circular mask of the droplet. 
    Args:
        img (_type_): Image to be masked. 
        x_cen (_type_): Droplet center, x position. 
        y_cen (_type_): Droplet center, y position. 
        radius (_type_): Droplet radius for circular mask. 

    Returns:
        _type_: Array of binary integers. 1 where droplet is, 0 where it isn't. 
    """
    y_grid, x_grid = np.ogrid[:img.shape[0], :img.shape[1]]
    drop_mask = np.where((x_grid - x_cen)**2 + (y_grid - y_cen)**2 <= radius**2, 1, 0)
    return drop_mask

# def find_bg(img, mask_all, xcen, ycen, sample_size, camera_noise):
#     mask_all = np.array(mask_all)
#     mask_all = np.sum(mask_all, 0)
#     anti_mask_all = np.where(mask_all == 1, 0, 1)
    
#     x_com = np.mean(xcen) # find com of droplets
#     y_com = np.mean(ycen)

#     circle = mask_droplet(img, x_com, y_com, sample_size) # draw 200 pixel radius circle to consider average of
#     x = np.ndarray.flatten(img * circle * anti_mask_all)

#     considered_pixels = x[x != 0]
#     count, bins = np.histogram(considered_pixels, 100)
#     plt.stairs(count, bins)
#     plt.show()
#     bg = mode(considered_pixels)[0]
#     bg_std = np.std(considered_pixels)
#     area = np.size(considered_pixels)
#     return bg, bg_std, area

# def _find_ambient_bg(img):
#     """_summary_

#     Args:
#         img (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     bg = mode(np.ndarray.flatten(img))[0]
#     return int(bg)

def _find_local_bg(img, xcen, ycen, rdil):
    """
    Find the background value around a given droplet location. 
    Args:
        img (_type_): Image to be masked. 
        xcen (_type_): Droplet center, x position. 
        ycen (_type_): Droplet center, y position. 
        rdil (_type_): Dilute phase radius.

    Returns:
        list:   means of background considered,
                modes of background considered, 
                stds of background considered, 
                areas of background considered
    """
    # per - droplet background correction
    mask_all = np.zeros_like(img)
    # this is written such that if bg value is actually zero everything breaks soo uhhhhh use a litte gain or something (unlikely to happen)
    for i, x in enumerate(xcen):
        y = ycen[i]
        r = rdil[i]
        mask = _mask_droplet(img, x, y, r)
        mask_all = mask_all + mask
    # mask away all droplets from image
    anti_mask = np.where(mask_all > 0, 0, 1) 
    masked_img = anti_mask * img
    
    means = []
    modes = []
    stds = []
    areas = []
    
    # for each droplet, go 2 r_dil out from center, mask that region, calculate background stats from there. 
    for i, x in enumerate(xcen):
        y = ycen[i]
        r = rdil[i]
        bg_pixels = masked_img * _mask_droplet(masked_img, x, y, 2 * r) # make mask 2r about circle center
        
        bg_pixels = np.ndarray.flatten(bg_pixels)
        bg_pixels = bg_pixels[bg_pixels != 0]
        
        area = np.size(bg_pixels)
        bg_mean = np.mean(bg_pixels)
        bg_mode = mode(bg_pixels)[0]
        bg_std = np.std(bg_pixels)
        
        means.append(float(bg_mean))
        modes.append(float(bg_mode))
        stds.append(float(bg_std))
        areas.append(float(area))
    
    return means, modes, stds, areas

# deprecated background subtraction supposing oil glows

    # def _correct_bg_abc(bg_density, r_dil, capillary_height):
    #     v_bg = pi * r_dil ** 2 * capillary_height - four_thirds * pi * r_dil ** 3
    #     correction = bg_density * v_bg
    #     return correction

    # def _correct_bg_bc(bg_density, r_den, r_dil, capillary_height):
    #     v_cyl = pi * r_den ** 2 * capillary_height
    #     v_donut = _volume_a(r_den, r_dil)
    #     v_bg = v_cyl - (four_thirds * pi * r_dil ** 3 - v_donut)
    #     correction = bg_density * v_bg
    #     return correction

# def _subtract_bg(intden, bg, area):
#     return intden - (bg * area)

def _conc_math(r_den, r_dil, intden_bc, intden_abc, conc):
    """
    Calculates concentrations of droplets from integrated density and radii measurements. 
    Args:
        r_den (_type_): Dense phase radius.
        r_dil (_type_): Dilute phase radius
        intden_bc (_type_): Integrated density of the combined 'b' and 'c' regions. 
                            This is the integrated density of the circle forming the dense phase. 
        intden_abc (_type_): Integrated density of the entire droplet. 
        conc (_type_): Initial (average) concentration of the droplet. 

    Returns:
        list:   Dense phase concentration, 
                dilute phase concentration, 
                conversion factor for translating gray value to concentration. 
    """
    # does the intensity density math using the donut integral result
    # region a - donut
    # region b - dilute phase within core
    # region c - dense phase wihtin core (spherical)
    # returns cden, cdil
    intden_a = intden_abc - intden_bc
    rho_dil = intden_a / _volume_a(r_den, r_dil)
    intden_c = intden_bc - rho_dil * _volume_b(r_den, r_dil)
    rho_den = intden_c / _volume_c(r_den)
    rho_avg = intden_abc / _volume_abc(r_dil)
    conversion = 1 / ((1.0 / conc) * rho_avg)
    
    conc_den = conversion * rho_den
    conc_dil = conversion * rho_dil

    return [conc_den, conc_dil, conversion]

def measure_image(log, img, conc, subtract_local_background:bool):
    """
    For all droplets within an image, return a dictionary of their statistics. 
    Args:
        log (_type_): Analysis log output by segmentation script.
        img (_type_): Image of capillary containing many droplets. 
        conc (_type_): Concentration corresponding to that capillary. 
        subtract_local_background (bool): Whether or not to subtract background. 
    Returns:
        cap_data (dict): Dictionary of per-droplet statistics. 
    """
    rden = log["corrected_rden"].to_numpy()
    original_rden = log["rden"]
    rdil = log["rdil"].to_numpy()
    xcen = log["xcen"].to_numpy()
    ycen = log["ycen"].to_numpy()

    intden_abc = np.zeros_like(rden)
    intden_bc = np.zeros_like(rden)
    area_abc = np.zeros_like(rden)
    area_bc = np.zeros_like(rden)

    bg_means, bg_modes, bg_stds, bg_areas = _find_local_bg(img, xcen, ycen, rdil)
    bg_density = []
    
    for k, _ in enumerate(rden):
        # iterate over each droplet
        mask_abc = _mask_droplet(img, xcen[k], ycen[k], rdil[k])
        mask_bc = _mask_droplet(img, xcen[k], ycen[k], rden[k]) 
        im_abc = img * mask_abc
        im_bc = img * mask_bc
        
        a_abc = np.sum(mask_abc)
        a_bc = np.sum(mask_bc)
        id_abc = np.sum(im_abc)
        id_bc = np.sum(im_bc)

        # bg_density.append(bg_modes[k] / (bg_areas[k] * CAPILLARY_HEIGHT))
        # bg_density.append(0.0)
        
        # intden_abc[k] = id_abc - _correct_bg_abc(bg_density[k], rdil[k], CAPILLARY_HEIGHT)
        # intden_bc[k] = id_bc - _correct_bg_bc(bg_density[k], rden[k], rdil[k], CAPILLARY_HEIGHT)
        
        #subtract background from mode of local background calculation
        if subtract_local_background:
            intden_abc[k] = id_abc - bg_modes[k]
            intden_bc[k] = id_bc - bg_modes[k]
        else:
            intden_abc[k] = id_abc
            intden_bc[k] = id_bc
            
        area_abc[k] = a_abc
        area_bc[k] = a_bc

    cden, cdil, conversion = _conc_math(rden, rdil, intden_bc, intden_abc, conc)
    
    cap_data = {
        'conc': conc,
        # 'ambient bg': ambient_bg,
        'bg_mean': list(bg_means),
        'bg_mode': list(bg_modes),
        # 'bg_density': list(bg_density),
        'bg_std': list(bg_stds),
        'bg_area': list(bg_areas),
        'conversion_factor': list(conversion),
        'corrected_rden': list(rden),
        'original_rden': list(original_rden),
        'rdil': list(rdil),
        'xcen': list(xcen),
        'ycen': list(ycen),
        'intden_abc': list(intden_abc),
        'intden_bc': list(intden_bc),
        'area_abc': list(area_abc),
        'area_bc': list(area_bc),
        'cden': list(cden),
        'cdil': list(cdil)
    }

    return cap_data

def measure_temperature(log_directory, img_directory, concs_keyval, subtract_local_background):
    """
    Measure all the images of capillaries within a temperature directory. 
    Args:
        log_directory (_type_): Directory containing all segmentation logs. 
        img_directory (_type_): Directory containing all capillary images. 
        concs_keyval (dict): Dictionary containing capillaries and their corresponding concentrations. 
    Returns:
        temp_data (dict): Dictionary of capillary data for a given temperature. 
    """
    img_paths = [os.path.join(img_directory, img) for img in gather_tif_files(img_directory)]
    imgs = [imread(img) for img in img_paths]
    logs = [pd.read_csv(os.path.join(log_directory, log)) for log in gather_csv_files(log_directory)]
    cap_nums = [extract_cap_number(img_path) for img_path in img_paths]
    
    temp_data = {}
    
    for i, cap_num in enumerate(cap_nums):
        img = imgs[i]
        log = logs[i]
        img_path = img_paths[i]
        
        cap_data = measure_image(log, img, concs_keyval[cap_num], subtract_local_background)
        temp_data[f'cap{cap_num}'] = cap_data
    
    return temp_data



        
            