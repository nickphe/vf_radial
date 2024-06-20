from lib.measure import all_images
from lib.analyze import run_all_temps
from lib.run_ilastik import run_ilastik
import argparse

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# --- analysis settings ---
# treat this as a table
# CAPILLARIES
caps = [1, 2, 3, 4, 5, 6, 7]
concs = [26.1, 6.3, 107.3, 62.5, 15.1, 50.7, 0]
uncs = [0.7, 0.2, 7.5, 2.8, 0.8, 0.9, 0]
removed_capillaries = [7]
# MELTING POINTS
mp_concs = [26.1, 6.3, 107.3, 62.5, 15.1, 50.7]
mp_concs_u = [0.7, 0.2, 7.5, 2.8, 0.8, 0.9]
mp = [31.05, 30.6, 28.45, 29.0, 30.7, 30.75]
mp_u = [.15, .2, .25, .2, .2, .15]
# STATISTICS
vf_statistic = "mode"

# --- ilastik settings --- 
path_to_ilastik = '/Users/nanostars/ilastik-1.4.0.post1-OSX.app/Contents/ilastik-release/run_ilastik.sh' # path to where ilastik is stored on the computer
ilastik_project = '/Users/nanostars/Desktop/4xMag_ilastikproj.ilp' # path to .ilp condensate recognition project
file_extension = 'tif' # file extension of both input and output images
export_source = 'object identities' # export image source option in ilastik

# --- IO settings ---
parent = "/Users/nanostars/Desktop/phase-diagrams/2024 06 18/levers"
output_parent = "/Users/nanostars/Desktop/phase-diagrams/2024 06 18/output (radial integration)"

#-------------------------------------------------------------------------------------------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("-i", action = 'store_true', help="run ilastik on image set")
parser.add_argument("-s", action = 'store_true', help="run inflation segmentation")
parser.add_argument("-a", action = 'store_true', help="run analysis")
args = parser.parse_args()
#-i controls ilastik, -s controls segmenations, -a controls analysis
# to run all:
# python3 master.py -i -s -a

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
        self.output_parent = output_parent
        self.path_to_ilastik = path_to_ilastik
        self.ilastik_project = ilastik_project
        self.file_extension = file_extension
        self.export_source = export_source
        self.removed_capillaries = removed_capillaries
        self.vf_statistic = vf_statistic 
        
settings = Settings()

if args.i:
    run_ilastik(settings) # segment with ilastik to find centers
if args.s:
    all_images(parent)
if args.a:
    run_all_temps(settings)
