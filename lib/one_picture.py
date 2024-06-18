import numpy as np
from lib.bubbles import DropletImage
import matplotlib.pyplot as plt

img_path = "/Users/nanostars/Desktop/2024 04 13/levers/21.4C/110uM 21.4C 10X.tif"
ft_path = "/Users/nanostars/Desktop/2024 04 13/levers/21.4C/ilastik/110uM 21.4C 10X_table.csv"
di = DropletImage(img_path, ft_path) 

########### FOR THOMAS ############
# di is a "droplet image" object which is parent to the list of droplets.
# Call di.droplets to get a list of droplet objects.
# Droplet attributes can be found in the bubble.py program.
# I created arrays of r_den, r_dil, and vf for you to play with. 
###################################

r_den = np.zeros_like(di.droplets)
r_dil = np.zeros_like(di.droplets)
vf = np.zeros_like(di.droplets)

for i, droplet in enumerate(di.droplets):
    r_den[i] = droplet.den_radius
    r_dil[i] = droplet.dil_radius
    vf[i] = (r_den[i] ** 3) / (r_dil[i] ** 3)

count, bins = np.histogram(vf, 30)
fig, ax = plt.subplots()
ax.stairs(count, bins)
plt.show()