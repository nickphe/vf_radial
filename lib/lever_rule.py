import numpy as np
import pandas as pd
from scipy.odr import Model, Data, ODR
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import scienceplots

# def mode(arr, bin_count: int):
#     bins = np.linspace(0, 1, bin_count + 1)
#     count = np.digitize(arr, bins)
#     print(count)
#     x = Counter(count)
#     #print(f"count: {count}, bins: {bins}")
#     # np.histogram bins are half open except for last 
#     # e.g. [1,2,3], bins would be [1,2), [2,3]
#     print(x.most_common(1))
#     tallest_bin_index = x.most_common(1)[0][0]
#    # print(f"tallest bin index: {tallest_bin_index}")
#     a = bins[tallest_bin_index]
#     b = bins[tallest_bin_index + 1]
#     m = (a + b) / 2.0
#     #print(f"mode: {m}")
#     print(m)
#     return m

# CURRENTLY TESTING MODE, MEAN, ETC. 

def lever_rule_data(logs, output_path, use_root_N = True):
    
    mean_vf_li = []
    std_vf_li = []
    conc_li = []
    conc_unc_li = []
    N_li = []
    vf_unc_li = []
    
    for log in logs:
        
        vfs = log.filt_vfs
        
        N = len(vfs)
        N_li.append(N)
        
        mean_vf = np.mean(vfs)
        mean_vf_li.append(mean_vf)
        
        std_vf = np.std(vfs)
        #std_vf = np.std(vfs) / len(vfs)
        std_vf_li.append(std_vf)
        
        conc_li.append(log.conc)
        conc_unc_li.append(log.conc_unc)
        
        if use_root_N == True:
            vf_unc = std_vf / np.sqrt(N)
        else:
            vf_unc = std_vf
        vf_unc_li.append(vf_unc)
        
    lever_data = {"conc": conc_li, "conc_unc": conc_unc_li, "vf": mean_vf_li, "vf_unc": vf_unc_li, "vf_std": std_vf_li, "N (vf)": N_li}
    
    lddf = pd.DataFrame(lever_data)
    lddf.to_csv(output_path)
    
    return lddf, conc_li, mean_vf_li, conc_unc_li, vf_unc_li
    
def lin_model_odr(params, x):
    #b = params[1] ** 2 restrict b negative <=> positive x-intercept restriction
    return params[0] * x + params[1]

def linear_odr(x, y, x_u, y_u, m_inguess, b_inguess):

    x = np.array(x)
    y = np.array(y)
    x_u = np.array(x_u)
    y_u = np.array(y_u)
    data = Data(x, y, wd=1.0/y_u**2, we=1.0/x_u**2)
    
    # ceate ODR Model object
    model = Model(lin_model_odr)

    # initialize ODR object with the data and model
    odr = ODR(data, model, beta0=[m_inguess, b_inguess])
    odr_result = odr.run()

    popt_odr = odr_result.beta
    pcov_odr = odr_result.cov_beta
    psd_odr = odr_result.sd_beta
    
    return popt_odr, pcov_odr, psd_odr
    
def fit_lever_rule(conc, vf, conc_u, vf_u, output_path):  
      
    popt, pcov, psd = linear_odr(conc, vf, conc_u, vf_u, 0, 0) # use orthogonal distance regression to fit line
    #print(popt, pcov, psd)
    m = popt[0]
    #b = -1.0 * popt[1] ** 2 #because of current b^2 to ensure negative intercept
    b = popt[1]
    sigma_m = psd[0]
    sigma_b = psd[1]
    #sigma_b = np.sqrt((-2 * b * psd[1] ) ** 2) #because of current b^2 to ensure negative intercept
    ns_den = (1-b)/m
    ns_dil = (-b)/m
    ns_den_uncertainty = np.sqrt( np.square(sigma_b/m) + (np.square(1-b)*np.square(sigma_m)) / (m ** 4) )
    ns_dil_uncertainty = np.sqrt( np.square(sigma_b/m) + (np.square(b) * np.square(sigma_m)) / (m ** 4) )\
        
    concs = [ns_den, ns_dil]
    uncs = [ns_den_uncertainty, ns_dil_uncertainty]
    
    out = pd.DataFrame({"nsden": concs[0], "nsdil": concs[1], "nsden_u": uncs[0], "nsdil_u": uncs[1], "m": m, "b": b}, index=[0])
    out.to_csv(output_path)
    
    return out, concs, uncs
    

def plot_lever_rule(lever_data, fit_data, output_path):
    conc = lever_data["conc"]
    conc_u = lever_data["conc_unc"]
    vf = lever_data["vf"]
    vf_u = lever_data["vf_unc"]
    m = fit_data["m"][0]
    b = fit_data["b"][0]
    ns_den = fit_data["nsden"][0]
    ns_dil = fit_data["nsdil"][0]
    ns_den_uncertainty = fit_data["nsden_u"][0]
    ns_dil_uncertainty = fit_data["nsdil_u"][0]
    
    with plt.style.context(["science","nature"]):
        fig, ax = plt.subplots(dpi = 400)
        ax.errorbar(conc, vf, xerr = conc_u, yerr = vf_u, marker = "o", linestyle = "", capsize = 2)
        x = np.linspace(0, np.max(conc) + 10, 10)
        params = np.array([m, b])
        y = lin_model_odr(params, x)
        ax.plot(x, y, label = "[NS]$_{\\mathrm{den}}=$" + 
                        f"{round(ns_den,2)}$\\pm${round(ns_den_uncertainty,2)}($\\mu$M)\n"+
                        "[NS]$_{\\mathrm{dil}}=$" +
                        f"{round(ns_dil,2)}$\\pm${round(ns_dil_uncertainty,2)}($\\mu$M)")
        ax.legend()
        ax.set_xlabel("[NS]")
        ax.set_ylabel("$\\phi$")
        plt.savefig(output_path)
        plt.close()
    
def plot_multi_lever(lever_data_li, fit_data_li, output_path, temps):
    with plt.style.context(["science","nature"]):
        fig, ax = plt.subplots(dpi = 400)
        c = cm.rainbow(np.linspace(0, 0.95, len(lever_data_li)))
        
        for i, lever_data in enumerate(lever_data_li):
            temp = temps[i]
            fit_data = fit_data_li[i]
            
            conc = lever_data["conc"]
            conc_u = lever_data["conc_unc"]
            vf = lever_data["vf"]
            vf_u = lever_data["vf_unc"]
            m = fit_data["m"][0]
            b = fit_data["b"][0]
            ns_den = fit_data["nsden"][0]
            ns_dil = fit_data["nsdil"][0]
            ns_den_uncertainty = fit_data["nsden_u"][0]
            ns_dil_uncertainty = fit_data["nsdil_u"][0]

            ax.errorbar(conc, vf, xerr = conc_u, yerr = vf_u, 
                        marker = "o", linestyle = "", capsize = 2,
                        color = c[i], alpha = 0.9,
                        label = f"{temp}")
            x = np.linspace(0, np.max(conc) + 10, 10)
            params = np.array([m, b])
            y = lin_model_odr(params, x)
            ax.plot(x, y, color = c[i], alpha = 0.7)
            ax.legend(fontsize = "xx-small")
            ax.set_xlabel("[NS]")
            ax.set_ylabel("$\\phi$")
            
        plt.savefig(output_path)
        plt.close()
        