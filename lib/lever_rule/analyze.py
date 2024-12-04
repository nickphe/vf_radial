import numpy as np
import pandas as pd
import os
from lib.parse import parse, parse_caps_only, extract_cap_number, extract_cap_part
from lib.lever_rule.lever_rule import lever_rule_data, fit_lever_rule, plot_lever_rule, plot_multi_lever
from lib.segmentation.capillary_data import Log
from lib.lever_rule.phase_diagram import phase_diagram
from rich.status import Status

status = Status(status = None)

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
    vf_statistic = settings.vf_statistic
    min_emulsion_radius = settings.min_emulsion_radius
    root_n = settings.root_n
    use_filt = settings.use_filt
    iqr_range = settings.iqr_range
    bins_for_mode = settings.bins_for_mode
    
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
        status.update(f"(Lever Rule) analyzing lever: {temp}")
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
        for img in imgs[temp]:
            
            path = get_log_path(parent, temp, img)
            cap_num = extract_cap_number(extract_cap_part(path))
            if cap_num in removed_capillaries:
                print(f"cap {cap_num} SKIPPED")
                continue
            else:
                log = Log(path, single_index, iqr_range)
                log_li.append(log)
            
            # make histogram for each capilary
            cap_output_path = f"{output_parent}/{temp}/{img}"
            hist_name = f"{img}_vf_hist.png"
            filt_name = f"{img}_vf_hist_filtered.png"
            log.make_vf_histogram(cap_output_path, hist_name, bins_for_mode)
            log.make_filt_vf_histogram(cap_output_path, filt_name, bins_for_mode)
            
        temp_output_path = f"{output_parent}/{temp}"
        lr_filename = f"{temp_output_path}/{temp}_lever_rule_data.csv"
        lrfit_filename = f"{temp_output_path}/{temp}_lever_rule_fit_data.csv"
        lrplot_filename = f"{temp_output_path}/{temp}_lever_rule.png"
        lever_data, conc, vf, conc_unc, vf_unc = lever_rule_data(log_li, lr_filename, vf_statistic, use_root_N = root_n, use_filtered = use_filt, bins_for_mode = bins_for_mode)
        fit_data, dendil, dendil_u = fit_lever_rule(conc, vf, conc_unc, vf_unc, lrfit_filename)
        plot_lever_rule(lever_data, fit_data, lrplot_filename)
        lever_data_li.append(lever_data)
        fit_data_li.append(fit_data)
        
    multi_lrplot_filename = f"{settings.figure_output_parent}/LR_Multi.png"
    plot_multi_lever(lever_data_li, fit_data_li, multi_lrplot_filename, temps)
    multi_lrplot_filename = f"{settings.figure_output_parent}/LR_Multi.svg"
    plot_multi_lever(lever_data_li, fit_data_li, multi_lrplot_filename, temps)
    status.update(status = "making phase diagram")
    # print(len(mp), len(mp_u), len(mp_concs), len(mp_concs_u))
    phase_diagram(output_parent, settings.figure_output_parent, mp, mp_u, mp_concs, mp_concs_u)
    status.stop()