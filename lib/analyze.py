import numpy as np
import pandas as pd
import os
from lib.parse import parse, parse_caps_only, extract_cap_number, extract_cap_part
from lib.lever_rule import lever_rule_data, fit_lever_rule, plot_lever_rule, plot_multi_lever
from lib.capillary_data import Log
from lib.phase_diagram import phase_diagram
from rich.status import Status
from rich.spinner import Spinner

status = Status(status = None, spinner = "moon")

def create_directory(directory_path: str):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    else:
        pass
    
def clone(home, temps, img_dict):
    for temp in temps:
        create_directory(f"{home}/{temp}")
        for img in img_dict[temp]:
            create_directory(f"{home}/{temp}/{img}")
            
def cap_conc_index(caps, concs, uncs):
    dict = {}
    for i, cap in enumerate(caps):
        dict[cap] = [concs[i], uncs[i]]
    return dict

def get_log_path(parent, temp, img):
    path = f"{parent}/{temp}/{temp} analysis logs/{img}_analysis_log.csv"
    return path


def run_all_temps(settings):
    
    #settings 
    caps = settings.caps 
    concs = settings.concs 
    uncs = settings.uncs 
    mp_concs = settings.mp_concs 
    mp_concs_u = settings.mp_concs_u 
    mp = settings.mp 
    mp_u = settings.mp_u 
    parent = settings.parent
    output_parent = settings.output_parent
    removed_capillaries = settings.removed_capillaries
    
    create_directory(output_parent)
    imgs, img_count, temps = parse(parent) 

    # create analysis output folder
    clone(output_parent, temps, imgs)

    # match capillaries with their concentrations
    index = cap_conc_index(caps, concs, uncs)
    #print(f"INDEX: {index}")

    lever_data_li = []
    fit_data_li = []
    
    for temp in temps:
        
        log_li = []
        status.update(f"[light blue]{temp}")
        status.start()
        
        # Create an index specific to a single temp folder, this allows for capillaries to drop out 
        names = imgs[temp]
        #print(f"IMGS: {imgs}")
        #print(f"NAMES: {names}")
        temp_caps = []
        temp_concs = []
        temp_uncs = []
        for name in names:
            cap_index = extract_cap_number(extract_cap_part(name))
            if cap_index in removed_capillaries:
                continue
            #print(f"CAP_INDEX: {cap_index}")
            temp_caps.append(cap_index)
            temp_concs.append(index[cap_index][0])
            temp_uncs.append(index[cap_index][1])
        single_index = cap_conc_index(temp_caps, temp_concs, temp_uncs)
        #print(f"SINGLE INDEX: {single_index}")
        for k, img in enumerate(imgs[temp]):
            
            path = get_log_path(parent, temp, img)
            if (k + 1) in removed_capillaries:
                print(f"cap {k+1} SKIPPED")
                continue
            else:
                log = Log(path, single_index)
                log_li.append(log)
            
            # make histogram for each capilary
            cap_output_path = f"{output_parent}/{temp}/{img}"
            hist_name = f"{img}_vf_hist.png"
            filt_name = f"{img}_vf_hist_filtered.png"
            log.make_vf_histogram(cap_output_path, hist_name)
            log.make_filt_vf_histogram(cap_output_path, filt_name)
            
        temp_output_path = f"{output_parent}/{temp}"
        lr_filename = f"{temp_output_path}/{temp}_lever_rule_data.csv"
        lrfit_filename = f"{temp_output_path}/{temp}_lever_rule_fit_data.csv"
        lrplot_filename = f"{temp_output_path}/{temp}_lever_rule.png"
        lever_data, conc, vf, conc_unc, vf_unc = lever_rule_data(log_li, lr_filename, use_root_N = False)
        fit_data, dendil, dendil_u = fit_lever_rule(conc, vf, conc_unc, vf_unc, lrfit_filename)
        plot_lever_rule(lever_data, fit_data, lrplot_filename)
        lever_data_li.append(lever_data)
        fit_data_li.append(fit_data)
        
    multi_lrplot_filename = f"{output_parent}/multi_lever_rule.png"
    plot_multi_lever(lever_data_li, fit_data_li, multi_lrplot_filename, temps)
    status.update(status = "making phase diagram")
    print(len(mp), len(mp_u), len(mp_concs), len(mp_concs_u))
    phase_diagram(output_parent, mp, mp_u, mp_concs, mp_concs_u)
    status.stop()