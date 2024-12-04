import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scienceplots

def background_intensity_figures(img, mask_all, bg, output_path):
    
    im = img * mask_all
    with plt.style.context(["science","nature"]):
        fig, ax = plt.subplots(dpi = 400)
        ax.imshow(im)
        plt.savefig(output_path + '_masked_droplets.png')
        
# this doesn't do anything