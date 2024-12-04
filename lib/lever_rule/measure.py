import numpy as np
from lib.segmentation.bubbles import DropletImage
from lib.parse import parse
import os 

def all_images(parent_folder, min_drop_radius, max_drop_radius, psf, cf1, cf2):

    img_dict, number_of_images, sorted_folders = parse(parent_folder)
        
    for folder_temp_index, temp_folder in enumerate(sorted_folders):

        cur_folder = img_dict[sorted_folders[folder_temp_index]]
        temp_folder = sorted_folders[folder_temp_index]
        
        print(f"fetching {temp_folder}")
        
        print(f"--> {temp_folder} : {img_dict[sorted_folders[folder_temp_index]]}\n")
        
        log_path = f"{parent_folder}/{temp_folder}/{temp_folder} analysis logs/"
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        cur_folder = img_dict[sorted_folders[folder_temp_index]]
            
        for img_name in cur_folder:
            
            try:
                print(f"analyzing {img_name} in {temp_folder}")

                ft_path = f"{parent_folder}/{temp_folder}/ilastik/{img_name}_table.csv"
                img_path = f"{parent_folder}/{temp_folder}/{img_name}.tif"

                di = DropletImage(img_path, ft_path, psf)
                di.write_csv(log_path, img_name, min_drop_radius, max_drop_radius, cf1, cf2)
                di.segmenation_image(f"{parent_folder}/{temp_folder}/", img_name, min_drop_radius, max_drop_radius)
            # Error "handling" - might want to remove this, it might not be a great idea...
            
            except(FileNotFoundError) as fnfe:
                print(f"Critical error fitting {img_name}!")
                print(f"TEMPERATURE FOLDER: {cur_folder} SKIPPED!!! \n")
                print(f"TEMPERATURE FOLDER: {cur_folder} SKIPPED!!! \n")
                print(f"Train ilastik on {cur_folder}!") 
                print(fnfe)
            
            except(RuntimeError) as re:
                print(f"Critical error fitting {img_name}!")
                print(re)
