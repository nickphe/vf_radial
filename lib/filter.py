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
