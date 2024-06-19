from lib.measure import all_images
from lib.analyze import run_all_temps
from lib.run_ilastik import run_ilastik
import argparse

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# --- analysis settings ---
# treat this as a table
# CAPILLARIES
caps = [1, 2, 3, 4, 5, 6]
concs = [15, 76.9, 30.6, 104.6, 5.7, 55.7]
uncs = [0.5, 3.9, 3.0, 9.2, 0.3, 2.9]
removed_capillaries = [1, 2]
# MELTING POINTS
mp_concs = [15, 76.9, 30.6, 104.6, 5.7, 55.7, 220]
mp_concs_u = [0.5, 3.9, 3.0, 9.2, 0.3, 2.9, 20]
mp = [39.1, 38.7, 39.2, 37.9, 38.6, 39.1, 34.3]
mp_u = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2]

# --- ilastik settings --- 
path_to_ilastik = '/Users/nanostars/ilastik-1.4.0.post1-OSX.app/Contents/ilastik-release/run_ilastik.sh' # path to where ilastik is stored on the computer
ilastik_project = '/Users/nanostars/Desktop/ilastik_training_May2024.ilp' # path to .ilp condensate recognition project
file_extension = 'tif' # file extension of both input and output images
export_source = 'object identities' # export image source option in ilastik

# --- IO settings ---
parent = "/Users/nanostars/Desktop/phase-diagrams/2024 03 26/levers"
output_parent = "/Users/nanostars/Desktop/phase-diagrams/2024 03 26/June Output 2"

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
        
settings = Settings()

if args.i:
    run_ilastik(settings) # segment with ilastik to find centers
if args.s:
    all_images(parent)
if args.a:
    run_all_temps(settings)
