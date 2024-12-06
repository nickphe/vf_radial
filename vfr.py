#----------------------------------------------------SETTINGS---------------------------------------------------------------------
# ---  CAPILLARIES --- 
caps = range(1, 320)
concs = range(1, 320)
uncs = range(1, 320)
removed_capillaries = []

# --- MELTING POINTS --- 
mp_concs = []
mp_concs_u = []
mp = []
mp_u = []
# PSF
psfpath = '/Users/nickphelps/Desktop/vf_radial PSF/moreaccurate4xpsf_REAL.tif'

# --- Integrated Density Measurement --- 
subtract_local_background = True # subtract background locally about each droplet when doing droplet integrated density math. 

# --- Integrated Density Measurement --- 
subtract_local_background = True # subtract background locally about each droplet when doing droplet integrated density math. 
k_range = [0,1]

# --- Rden correction factor --- 
cf1 =1.0 # 1.03 # slope
cf2 = 0.0 # 2.43 # intercept

# STATISTICS
vf_statistic = "mode"
bins_for_mode = 200 # number of bins mode is computed from (within range of [0,1])
# if binning uncertainty > std of vfs, takes binning uncertainty as error. 
use_root_n = True # boolean, divide by root N on vf errorbars
use_filtered_vfs = True # remove unphysical vfs and vfs set to be rejected by iqr_range
iqr_range = [0,1] # Just don't use this. 
                  # if use_filtered_vfs == True, then this will also filter from the [a/1 * 100, b/1 * 100] percentile
                  # to have no filtering like this, set to [0,1]. If i wanted to maintain only the middle 80% of data and 
                  # reject the top and bottom 10th percentile, I would set to [0.1, 0.9]
                  # good practice is to keep this at [0,1], otherwise you're cheating. 
min_emulsion_radius = 15 # minimum emulsion drop radius (in pixels), interfaces directly with measure.py in segmentation step
max_emulsion_radius = 35 # maximum emulsion drop radius (in pixels), --""--

# --- ilastik settings --- 
path_to_ilastik = '/Users/nickphelps/ilastik-1.4.0rc6-OSX.app/Contents/ilastik-release/run_ilastik.sh' # path to where ilastik is stored on the computer
ilastik_project = '/Users/nickphelps/Desktop/2024 09 26/4xMag_ilastikproj.ilp' # path to .ilp condensate recognition project
file_extension = 'tif' # file extension of both input and output images
export_source = 'object identities' # export image source option in ilastik

# --- IO settings ---
parent = "/Users/nickphelps/Desktop/droplet_movies/2024 10 16 120 uM a3/120 uM a3/parent" # directory that contains all temperature subdirectories
lever_rule_output_parent = "/Users/nickphelps/Desktop/droplet_movies/2024 10 16 120 uM a3/120 uM a3/lr" # where you want to output lever rule data to 
di_output_parent = "/Users/nickphelps/Desktop/droplet_movies/2024 10 16 120 uM a3/120 uM a3/di"  #  where you want to output intensity density data to
figure_output_parent = "/Users/nickphelps/Desktop/droplet_movies/2024 10 16 120 uM a3/120 uM a3/fig" # where you want to output some of the figures
#-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Don't touch!
if __name__ == "__main__":
    from lib.lever_rule.measure import all_images
    from lib.lever_rule.analyze import run_all_temps
    from lib.ilastik.run_ilastik import run_ilastik
    from lib.direct_intensity.measure import di_measure
    from lib.direct_intensity.analyze import di_analyze
    from lib.figures.phase_diagrams import *
    import argparse
    import os
    from datetime import datetime
    from skimage import io

    parser = argparse.ArgumentParser()
    parser.add_argument("--ilastik", action = 'store_true', help = "run ilastik on image set")
    parser.add_argument("--segment", action = 'store_true', help = "run inflation segmentation")
    parser.add_argument("--lever", action = 'store_true', help = "run lever rule analysis")
    parser.add_argument("--idm", action = 'store_true', help = "run integrated density math")
    parser.add_argument("--ida", action = 'store_true', help = "run integrated density analysis")
    parser.add_argument("--figs", action = 'store_true', help = "create figures")
    parser.add_argument("--all", action = 'store_true', help = "do everything!")

    args = parser.parse_args()
    #-i controls ilastik, -s controls segmenations, -a controls analysis
    # to run all:
    # python3 master.py -i -s -l -d -m -f

    class Settings:
        def __init__(self):
            self.caps = caps
            self.concs = concs
            self.uncs = uncs
            self.mp_concs = mp_concs
            self.mp_concs_u = mp_concs_u
            self.mp = mp
            self.mp_u = mp_u
            self.parent = parent
            self.output_parent = lever_rule_output_parent
            self.di_output_parent = di_output_parent
            self.figure_output_parent = figure_output_parent
            self.path_to_ilastik = path_to_ilastik
            self.ilastik_project = ilastik_project
            self.file_extension = file_extension
            self.export_source = export_source
            self.removed_capillaries = removed_capillaries
            self.vf_statistic = vf_statistic 
            self.min_emulsion_radius = min_emulsion_radius
            self.max_emulsion_radius = max_emulsion_radius
            self.root_n = use_root_n
            self.use_filt = use_filtered_vfs
            self.iqr_range = iqr_range
            self.subtract_local_background = subtract_local_background
            self.k_range = k_range
            self.bins_for_mode = bins_for_mode
            
    settings = Settings()

    with open('vfr.py','r') as vfr, open(os.path.join(parent, f'../vfr_copy_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.txt'), 'w') as copy:
        copy.write(f'# Last run: {datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}\n')
        for line in vfr:
            copy.write(line)
            
    # make output directories 
    if args.idm or args.lever or args.ida or args.figs or args.all:
        try:
            os.mkdir(lever_rule_output_parent)
        except FileExistsError:
            print('LR output parent directory already exists.')
        try:
            os.mkdir(di_output_parent)
        except FileExistsError:
            print('IntDen output parent directory already exists.')
        try:
            os.mkdir(figure_output_parent)
        except FileExistsError:
            print('Figure output parent directory already exists.')
            
    # load PSF
    psf = io.imread(psfpath)

    # run specific scripts based on command-line arguments
    if args.ilastik or args.all:
        run_ilastik(settings) # segment with ilastik to find centers
    if args.segment or args.all:
        all_images(parent, min_emulsion_radius, max_emulsion_radius, psf, cf1, cf2)
    if args.lever or args.all:
        run_all_temps(settings)
    if args.idm or args.all:
        di_measure(settings)
    if args.ida or args.all:
        di_analyze(settings)
    if args.figs or args.all:
        intden_datapath = f'{di_output_parent}/DI_DenDil_data.csv'
        if mp is []:
            mp_datapath = None
        else:
            mp_datapath = f'{lever_rule_output_parent}/LR_MP_data.csv'
        intden_pds(intden_datapath, figure_output_parent, mp_datapath, '[NS] ($\\mu$M)', 'Temperature ($^\\circ$C)', '$\\mu$M')
        phiT(di_output_parent, figure_output_parent, vf_statistic)