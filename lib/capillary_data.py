import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lib.filter import remove_outliers
from lib.parse import extract_cap_part, extract_cap_number
import scienceplots

class Log:
    def __init__(self, log, cap_conc_index):
        data = pd.read_csv(log)
        
        self.path = log
        self.rden = data["rden"]
        self.rdil = data["rdil"]
        self.xcen = data["xcen"]
        self.ycen = data["ycen"]
        self.vfs = (self.rden ** 3) / (self.rdil ** 3)
        
        self.cap_num = extract_cap_number(extract_cap_part(self.path))
        
        self.conc = cap_conc_index[self.cap_num][0]
        self.conc_unc = cap_conc_index[self.cap_num][1]
        
        nonzero = self.vfs[self.vfs != 0]
        self.filt_vfs = remove_outliers(nonzero, 0.1, 0.9) # remove outliers w/ percentile lower than Qa, higher than Qb
    
    def make_vf_histogram(self, output_path, name):
        BINS = np.linspace(0,1,100)
        with plt.style.context(["science","nature"]):
            fig, ax = plt.subplots(dpi = 400)
            ax.hist(self.vfs, BINS)
            ax.set_xlabel("$\\phi$")
            plt.savefig(f"{output_path}/{name}")
            plt.close()

    def make_filt_vf_histogram(self, output_path, name):
        BINS = np.linspace(0,1,100)
        with plt.style.context(["science","nature"]):
            fig, ax = plt.subplots(dpi = 400)
            ax.hist(self.filt_vfs, BINS)
            ax.set_xlabel("$\\phi$")
            plt.savefig(f"{output_path}/{name}")
            plt.close()
            