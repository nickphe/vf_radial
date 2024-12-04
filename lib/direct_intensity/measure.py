import os, json
from lib.direct_intensity.data_io import *
from lib.direct_intensity.di import * 
from rich.console import Console

def di_measure(settings):
    """
    Wrapper for 'measure' script which does all the concentration math over and over again. 
    """
    console = Console()

    #SETTINGS
    config = settings
    home_dir = config.parent
    output_dir = config.di_output_parent
    caps = config.caps
    concs = config.concs
    subtract_local_background = config.subtract_local_background
    removed_capillaries = config.removed_capillaries

    considered_caps = [cap_num for cap_num in caps if cap_num not in removed_capillaries]
    concs_keyval = dict(zip(caps,concs))

    log_directories = [find_logs_dir(os.path.join(home_dir, temp_folder))[0] for temp_folder in list_folders(home_dir)]
    img_directories = [os.path.join(home_dir, temp_folder) for temp_folder in list_folders(home_dir)]

    for i, log_directory in enumerate(log_directories):
        img_directory = img_directories[i]
        temp = extract_temp_part(img_directory)
        with console.status(f'(IntDen) measuring temperature: {temp}C') as status:
            temp_data = measure_temperature(log_directory, img_directory, concs_keyval, subtract_local_background)
            status.update(f'Temperature {temp}C complete.')
        # save temp data to json file inside its folder
        with open(os.path.join(img_directory, f'{temp}C_data.json'), 'w') as f:
            json.dump(temp_data,f)
