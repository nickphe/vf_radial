from lib.measure import all_images
from lib.analyze import run_all_temps
from lib.run_ilastik import run_ilastik
import argparse

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# --- analysis settings ---
# treat this as a table
# CAPILLARIES
caps = [1,2,3,4,5,6,7,8,9]
concs = [25.7,55.9,123.0,13.5,84.0,32.5,6.9,73.2,41.9]
uncs = [2.1,3.1,14.0,0.5,7.5,0.8,0.5,4.2,2.3]
# MELTING POINTS
mp_concs = [26.9,   6.3,   80.1, 33.7, 106.3,  20.4,  60.8,  15.7, 46.7]
mp_concs_u = [0.7, 0.8, 4.5, 0.5, 0.7, 0.74, 2.5, 0.7, 2.1]
mp = [38.1, 37.7, 36.8, 38.0, 34.3, 38.2, 36.9, 37.8, 37.0]
mp_u = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

# --- ilastik settings --- 
path_to_ilastik = '/Users/nanostars/ilastik-1.4.0.post1-OSX.app/Contents/ilastik-release/run_ilastik.sh' # path to where ilastik is stored on the computer
ilastik_project = '/Users/nanostars/Desktop/ilastik_training_May2024.ilp' # path to .ilp condensate recognition project
file_extension = 'tif' # file extension of both input and output images
export_source = 'object identities' # export image source option in ilastik

# --- IO settings ---
parent = "/Users/nanostars/Desktop/test2/levers"
output_parent = "/Users/nanostars/Desktop/test2/output"

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
        
settings = Settings()

if args.i:
    run_ilastik(settings) # segment with ilastik to find centers
if args.s:
    all_images(parent)
if args.a:
    run_all_temps(settings)
