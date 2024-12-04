import numpy as np
from scipy.special import erf
import random

def simultaneous_sort(keys, arr):
    return arr[keys.argsort()]

def chauvenet(arr):
    # this sucks
    a = np.copy(arr)
    
    #sort a based on distance from mean
    m = np.mean(a)
    resid = np.abs(a - m)
    d = np.flip(simultaneous_sort(resid, a))
    
    for i, x in enumerate(d):

        N = len(d)
        mean = np.mean(d)
        std = np.std(d)
        
        za = (-1.0*x - mean) / (np.sqrt(2) * std)
        zb = (x - mean) / (np.sqrt(2) * std)
        p_out = 1 - (erf(zb) - erf(za))
        
        n_out = p_out * N
        print(n_out)
        
        if n_out < 0.5:
            d[i] = 0
    
    nonzero = d[d != 0]
    
    return nonzero

def bootstrap(arr, sample_size, num_samples):
    a = np.copy(arr)
    N = len(arr)
    
    boot = []
    for k in range(num_samples):
        sample = []
        for j in range(sample_size):
            i = random.randint(0,N - 1)
            v = a[i]
            sample.append(v)
        sample_mean = np.mean(sample)
        boot.append(sample_mean)
    
    return boot

def remove_outliers(arr, quantile_a, quantile_b):
    
    if arr.size != 0:
        if quantile_a > quantile_b:
            print("quantile_a must be greater than quantile_b")
        
        a = np.copy(arr)
        median = np.median(a)
        qa = np.quantile(a, quantile_a)
        qb = np.quantile(a, quantile_b)
        iqr = qb - qa
        
        filt1 = a > qa
        filt2 = a < qb
        filt = filt1 * filt2
        
        outliers_removed = a[filt]
        return(outliers_removed)
    else:
        return np.array([0])
    
def remove_outliers_mask(arr, quantile_a, quantile_b):
    
    if arr.size != 0:
        if quantile_a > quantile_b:
            print("quantile_a must be greater than quantile_b")
        
        a = np.copy(arr)
        median = np.median(a)
        qa = np.quantile(a, quantile_a)
        qb = np.quantile(a, quantile_b)
        iqr = qb - qa
        
        filt1 = a > qa
        filt2 = a < qb
        filt = filt1 * filt2
        
        return(filt)
    else:
        return np.array([0])
    
def remove_unphysical(arr):
    not_small = arr[arr > 0.001]
    just_right = not_small[not_small < 1]
    
    return just_right

import numpy as np

def find_mode_bin(arr, num_bins):
    # Convert the array to a numpy array
    arr = np.array(arr)
    
    if arr.size == 0:
        return 0
    
    # Get the minimum and maximum values of the array
    min_val = np.min(arr)
    max_val = np.max(arr)
    
    # Create the bins
    bins = np.linspace(min_val, max_val, num_bins + 1)
    
    # Digitize the data into the bins
    bin_indices = np.digitize(arr, bins)
    
    # Find the bin with the most data
    bin_counts = np.bincount(bin_indices)
    mode_bin_index = np.argmax(bin_counts)
    
    # Return the range of the bin with the most data
    mode_bin = (bins[mode_bin_index-1], bins[mode_bin_index])
    center = (mode_bin[0] + mode_bin[1])/2
    return center
