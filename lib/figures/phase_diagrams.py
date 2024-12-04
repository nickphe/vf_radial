import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os, re
from lib.direct_intensity.data_io import *
from scipy.stats import mode
import scienceplots

markers = [ # thanks ChatGPT for making this list
    'o',  # circle marker
    's',  # square marker
    '^',  # triangle_up marker
    'v',  # triangle_down marker
    '<',  # triangle_left marker
    '>',  # triangle_right marker
    'D',  # diamond marker
    'p',  # pentagon marker
    '*',  # star marker
    'h',  # hexagon1 marker
    'H',  # hexagon2 marker
    '+',  # plus marker
    'x',  # x marker
    'd',  # thin_diamond marker
    '1',  # tri_down marker
    '2',  # tri_up marker
    '3',  # tri_left marker
    '4',  # tri_right marker
    '.',  # point marker
    ',',  # pixel marker
    '|',  # vline marker
    '_'   # hline marker
]

# def list_folders(directory):
#     if not isinstance(directory, (str, bytes, os.PathLike)):
#         raise TypeError("The directory must be a string, bytes, or os.PathLike object.")
    
#     if not os.path.isdir(directory):
#         raise ValueError("The provided directory path does not exist or is not a directory.")
    
#     folders = [entry.name for entry in os.scandir(directory) if entry.is_dir()]
#     return folders

# def extract_temp_part(string):
#     match = re.search(r'(\d+\.?\d*)C', string)
#     if match:
#         return float(match.group(1))  # Use float to handle decimal numbers
#     else:
#         return None

def intden_pds(pd_data_path: str, output_path: str, mp_data_path:str, xlabel:str, ylabel:str, conc_units:str):
    df = pd.read_csv(pd_data_path)
    cinit = df['cinit'].to_numpy()
    concs = sorted(set(cinit))
    temp = df['temp'].to_numpy()
    cden = df['cden_mean'].to_numpy()
    cdil = df['cdil_mean'].to_numpy()
    cden_std = df['cden_std'].to_numpy()
    cdil_std = df['cdil_std'].to_numpy()
    N = df['N']
    if mp_data_path == None:
        melting_points = False
    else:
        melting_points = True
        df = pd.read_csv(mp_data_path)
        mp_conc = df['conc'].to_numpy()
        mp_conc_u = df['conc_u'].to_numpy()
        mp = df['mp'].to_numpy()
        mp_u = df['mp_u'].to_numpy()
    
    # NO ROOT N, STANDARD SCALE
    with plt.style.context(['science','nature']):
        fig, ax = plt.subplots(dpi = 400)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        for i, conc in enumerate(concs):
            f = cinit == conc
            c_temp = temp[f]
            c_cden = cden[f]
            c_cdil = cdil[f]
            c_cden_std = cden_std[f]
            c_cdil_std = cdil_std[f]
            c_N = N[f]
            
            x = np.concatenate((c_cdil, c_cden))
            xerr = np.concatenate((c_cdil_std ,c_cden_std))
            y = np.concatenate((c_temp, c_temp))
            yerr = np.ones_like(y) * 0.1 # temperature uncertainty is resolution limited by thermocouple
            
            if melting_points:
                m = mp_conc == conc
                m_x = mp_conc[m]
                m_xerr = mp_conc_u[m]
                m_y = mp[m]
                m_yerr = mp_u[m]
                x = np.concatenate((x, m_x))
                y = np.concatenate((y, m_y))
                xerr = np.concatenate((xerr, m_xerr))
                yerr = np.concatenate((yerr, m_yerr))
        
            ax.errorbar(x, y, xerr = xerr, yerr = yerr, marker = markers[i], linestyle = '', capsize = 3, label = f'{conc} {conc_units}')
            
        ax.legend(loc = (1,0.35), fontsize = 'small')
        plt.savefig(f'{output_path}/PD_IntDen_StdDev.png')
        plt.savefig(f'{output_path}/PD_IntDen_StdDev.svg')
        plt.close()
        
    # NO ROOT N, LOG X SCALE
    with plt.style.context(['science','nature']):
        fig, ax = plt.subplots(dpi = 400)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        for i, conc in enumerate(concs):
            f = cinit == conc
            c_temp = temp[f]
            c_cden = cden[f]
            c_cdil = cdil[f]
            c_cden_std = cden_std[f]
            c_cdil_std = cdil_std[f]
            c_N = N[f]
            
            x = np.concatenate((c_cdil, c_cden))
            xerr = np.concatenate((c_cdil_std ,c_cden_std))
            y = np.concatenate((c_temp, c_temp))
            yerr = np.ones_like(y) * 0.1 # temperature uncertainty is resolution limited by thermocouple
            
            if melting_points:
                m = mp_conc == conc
                m_x = mp_conc[m]
                m_xerr = mp_conc_u[m]
                m_y = mp[m]
                m_yerr = mp_u[m]
                x = np.concatenate((x, m_x))
                y = np.concatenate((y, m_y))
                xerr = np.concatenate((xerr, m_xerr))
                yerr = np.concatenate((yerr, m_yerr))
        
            ax.errorbar(x, y, xerr = xerr, yerr = yerr, marker = markers[i], linestyle = '', capsize = 3, label = f'{conc} {conc_units}')
            
        ax.legend(loc = (1,0.35), fontsize = 'small')
        ax.set_xscale('log')
        plt.savefig(f'{output_path}/PD_IntDen_LogX_StdDev.png')
        plt.savefig(f'{output_path}/PD_IntDen_LogX_StdDev.svg')
        plt.close()
        
    # YES ROOT N, STANDARD SCALE
    with plt.style.context(['science','nature']):
        fig, ax = plt.subplots(dpi = 400)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        for i, conc in enumerate(concs):
            f = cinit == conc
            c_temp = temp[f]
            c_cden = cden[f]
            c_cdil = cdil[f]
            c_cden_std = cden_std[f]
            c_cdil_std = cdil_std[f]
            c_N = N[f]
            
            x = np.concatenate((c_cdil, c_cden))
            xerr = np.concatenate((c_cdil_std/np.sqrt(c_N) ,c_cden_std/np.sqrt(c_N)))
            y = np.concatenate((c_temp, c_temp))
            yerr = np.ones_like(y) * 0.1 # temperature uncertainty is resolution limited by thermocouple
            
            if melting_points:
                m = mp_conc == conc
                m_x = mp_conc[m]
                m_xerr = mp_conc_u[m]
                m_y = mp[m]
                m_yerr = mp_u[m]
                x = np.concatenate((x, m_x))
                y = np.concatenate((y, m_y))
                xerr = np.concatenate((xerr, m_xerr))
                yerr = np.concatenate((yerr, m_yerr))
        
            ax.errorbar(x, y, xerr = xerr, yerr = yerr, marker = markers[i], linestyle = '', capsize = 3, label = f'{conc} {conc_units}')
             
        ax.legend(loc = (1,0.35), fontsize = 'small')
        plt.savefig(f'{output_path}/PD_IntDen_StdError.png')
        plt.savefig(f'{output_path}/PD_IntDen_StdError.svg')
        plt.close()
        
    # YES ROOT N, LOG X SCALE
    with plt.style.context(['science','nature']):
        fig, ax = plt.subplots(dpi = 400)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        for i, conc in enumerate(concs):
            f = cinit == conc
            c_temp = temp[f]
            c_cden = cden[f]
            c_cdil = cdil[f]
            c_cden_std = cden_std[f]
            c_cdil_std = cdil_std[f]
            c_N = N[f]
            
            x = np.concatenate((c_cdil, c_cden))
            xerr = np.concatenate((c_cdil_std/np.sqrt(c_N) ,c_cden_std/np.sqrt(c_N)))
            y = np.concatenate((c_temp, c_temp))
            yerr = np.ones_like(y) * 0.1 # temperature uncertainty is resolution limited by thermocouple
            
            if melting_points:
                m = mp_conc == conc
                m_x = mp_conc[m]
                m_xerr = mp_conc_u[m]
                m_y = mp[m]
                m_yerr = mp_u[m]
                x = np.concatenate((x, m_x))
                y = np.concatenate((y, m_y))
                xerr = np.concatenate((xerr, m_xerr))
                yerr = np.concatenate((yerr, m_yerr))
        
            ax.errorbar(x, y, xerr = xerr, yerr = yerr, marker = markers[i], linestyle = '', capsize = 3, label = f'{conc} {conc_units}')
            
        ax.legend(loc = (1,0.35), fontsize = 'small')
        ax.set_xscale('log')
        plt.savefig(f'{output_path}/PD_IntDen_LogX_StdError.png')
        plt.savefig(f'{output_path}/PD_IntDen_LogX_StdError.svg')
        plt.close()
        
def phiT(output_data_dir, figure_output_path, vf_statistic):
    temp_dirs = sorted(list_folders(output_data_dir))
    conc_phi = {}
    conc_phi_std = {}
    conc_phi_ste = {}
    temps = []
    for i, temp_dir in enumerate(temp_dirs):
        cap_dirs = sorted(list_folders(os.path.join(output_data_dir, temp_dir)))
        temps.append(float(extract_temp_part(temp_dir)))
        for k, cap_dir in enumerate(cap_dirs):
            df = pd.read_csv(f'{output_data_dir}/{temp_dir}/{cap_dir}/{temp_dir}_cap{k + 1}_filtered_droplet_data.csv')
            conc = pd.read_csv(f'{output_data_dir}/{temp_dir}/{cap_dir}/{temp_dir}_cap{k + 1}_droplet_data.csv')['conc'].to_numpy()[0]
            match vf_statistic:
                case 'mean':
                    vf = (np.mean(df['rden'].to_numpy()) ** 3) / (np.mean(df['rdil'].to_numpy()) ** 3)
                case 'mode':
                    vf = mode(((df['rden'].to_numpy()) ** 3) / ((df['rdil'].to_numpy()) ** 3))[0]
            vf_std = np.std(((df['rden'].to_numpy()) ** 3) / ((df['rdil'].to_numpy()) ** 3))
            vf_ste = vf_std/np.size(df['rden'].to_numpy())
            try:
                conc_phi[conc].append(vf)
            except KeyError:
                conc_phi[conc] = []
                conc_phi[conc].append(vf)
            try:
                conc_phi_std[conc].append(vf_std)
            except KeyError:
                conc_phi_std[conc] = []
                conc_phi_std[conc].append(vf_std)
            try:
                conc_phi_ste[conc].append(vf_ste)
            except KeyError:
                conc_phi_ste[conc] = []
                conc_phi_ste[conc].append(vf_ste)
    # Std Dev
    with plt.style.context(['science','nature']):
        fig, ax = plt.subplots(dpi = 400)
        ax.set_xlabel('Temperature ($^\\circ$C)')
        ax.set_ylabel(vf_statistic+' $\\phi_{\\bullet}$')
        for i, phi in enumerate(conc_phi.values()):
            y = phi
            x = temps
            yerr = list(conc_phi_std.values())[i]
            ax.errorbar(x, y, yerr, marker = markers[i], linestyle = '', capsize = 3, label = f'{list(conc_phi.keys())[i]}')
        ax.legend(loc = (1,0.35))
        plt.savefig(f'{figure_output_path}/PhiT_StdDev.png')
        plt.savefig(f'{figure_output_path}/PhiT_StdDev.svg')
    # Std Err
    with plt.style.context(['science','nature']):
        fig, ax = plt.subplots(dpi = 400)
        ax.set_xlabel('Temperature ($^\\circ$C)')
        ax.set_ylabel(vf_statistic+' $\\phi_{\\bullet}$')
        for i, phi in enumerate(conc_phi.values()):
            y = phi
            x = temps
            yerr = list(conc_phi_ste.values())[i]
            ax.errorbar(x, y, yerr, marker = markers[i], linestyle = '', capsize = 3, label = f'{list(conc_phi.keys())[i]}')
        ax.legend(loc = (1,0.35))
        plt.savefig(f'{figure_output_path}/PhiT_StdErr.png')
        plt.savefig(f'{figure_output_path}/PhiT_StdErr.svg')
    print(conc_phi)
