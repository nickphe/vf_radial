import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lib.parse import parse, extract_numeric_part
import scienceplots

def phase_diagram(data_output, figure_output, mp, mp_u, mp_concs, mp_concs_u):
    output_parent = data_output
    _, _, temps = parse(data_output)

    den_li = []
    dil_li = []
    den_u_li = []
    dil_u_li = []
    
    temp_li = []
    
    for temp in temps:
        # print(temp)
        temp_num = extract_numeric_part(temp)

        data = pd.read_csv(f"{output_parent}/{temp}/{temp}_lever_rule_fit_data.csv")

        den_li.append(data["nsden"][0])
        dil_li.append(data["nsdil"][0])
        den_u_li.append(data["nsden_u"][0])
        dil_u_li.append(data["nsdil_u"][0])
        
        temp_li.append(temp_num)
    
    dendil = pd.DataFrame({"nsden": den_li, "nsdil": dil_li, "nsden_u": den_u_li, "nsdil_u": dil_u_li})
    dendil.to_csv(f"{data_output}/LR_DenDil_data.csv")
    
    melt_point = pd.DataFrame({"conc": mp_concs, "conc_u": mp_concs_u,"mp": mp, "mp_u": mp_u})
    melt_point.to_csv(f"{data_output}/LR_MP_data.csv")
    
    with plt.style.context(["science","nature"]):
        
        fig, ax = plt.subplots(dpi = 1000)
        ax.errorbar(den_li, temp_li, yerr = np.ones(len(den_li))*0.1, xerr = den_u_li, linestyle = "", marker = "o", capsize = 3)
        ax.errorbar(dil_li, temp_li, yerr = np.ones(len(den_li))*0.1, xerr = dil_u_li, linestyle = "", marker = "o", capsize = 3)
        ax.errorbar(mp_concs, mp, yerr = mp_u, xerr = mp_concs_u, linestyle = "", marker = "o", capsize = 3)
        ax.set_xlabel("[NS]")
        ax.set_ylabel("T ($^\\circ$C)")
        plt.savefig(f"{figure_output}/LR_PD.png")
        plt.savefig(f"{figure_output}/LR_PD.svg")
        plt.close()
        
        fig, ax = plt.subplots(dpi = 1000)
        ax.errorbar(den_li, temp_li, yerr = np.ones(len(den_li))*0.1, xerr = den_u_li, linestyle = "", marker = "o", capsize = 3)
        ax.errorbar(dil_li, temp_li, yerr = np.ones(len(den_li))*0.1, xerr = dil_u_li, linestyle = "", marker = "o", capsize = 3)
        ax.errorbar(mp_concs, mp, yerr = mp_u, xerr = mp_concs_u, linestyle = "", marker = "o", capsize = 3)
        ax.set_xlabel("[NS]")
        ax.set_ylabel("T ($^\\circ$C)")
        ax.set_xscale('log')
        plt.savefig(f"{figure_output}/log_LR_PD.png")
        plt.savefig(f"{figure_output}/log_LR_PD.svg")
        plt.close()
