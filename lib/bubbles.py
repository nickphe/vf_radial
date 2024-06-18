import numpy as np
from rich.console import Console
from skimage import io
import pandas as pd
from lib.dil_radius import dil_radii
from lib.den_radius import den_radii
import matplotlib.pyplot as plt
console = Console()

class DropletImage:
    def __init__(self, img_path, feature_table_path):
        
        self.img = io.imread(img_path)
        self.ft = pd.read_csv(feature_table_path)
        
        locs = self.locs()
        drop_li = []
        dil_radius_li = dil_radii(locs)
        
        for i, (x, y) in enumerate(locs):
            drop = Droplet(x, y)
            drop.dil_radius = dil_radius_li[i]
            
            imheight, imwidth = self.img.shape
            
            if (
                drop.x + drop.dil_radius < imwidth
                and
                drop.x - drop.dil_radius > 0
                and
                drop.y + drop.dil_radius < imheight
                and
                drop.y - drop.dil_radius > 0
                ):
                
                drop_li.append(drop)
                
        den_radius_li = den_radii(self, drop_li)
        
        for i, drop in enumerate(drop_li):
            drop.den_radius = den_radius_li[i]
    
        self.droplets = drop_li
    
    #Here, we call a function to identify the center for a given condrop and write it into an array
    def locs(self):
        ft = self.ft
        x_cen = ft["Center of the object_0"]
        y_cen = ft["Center of the object_1"]
        loc_arr = np.array([x_cen, y_cen]).T # create array of points in R2
        return loc_arr
    
    def write_csv(self, path, name):
        
        x = []
        y = []
        r_den = []
        r_dil = []

        for droplet in self.droplets:
                x.append(droplet.x)
                y.append(droplet.y)
                r_den.append(droplet.den_radius)
                r_dil.append(droplet.dil_radius)
                
        r_den = np.array(r_den)
        r_dil = np.array(r_dil)
            
        droplets = self.droplets
        self.log = {"rden": r_den, "rdil": r_dil, "xcen": x, "ycen": y}
        
        df = pd.DataFrame(self.log)
        csv_path = path + name + "_analysis_log.csv"
        df.to_csv(csv_path)
        del (df)
        
    def segmenation_image(self, path, name):
        fig, ax = plt.subplots(dpi = 500)
        ax.imshow(self.img)
        
        x = []
        y = []
        r_den = []
        r_dil = []

        for droplet in self.droplets:
                x.append(droplet.x)
                y.append(droplet.y)
                r_den.append(droplet.den_radius)
                r_dil.append(droplet.dil_radius)
                x_arr, y_arr = droplet.get_dil_circle(360)
                ax.plot(x_arr, y_arr, color = droplet.color, linewidth = 0.4, alpha = 0.7)
                x_arr, y_arr = droplet.get_den_circle(360)
                ax.plot(x_arr, y_arr, color = droplet.color, linewidth = 0.4, alpha = 0.7)
        
        plt.savefig(path + name + "_segmentation_image.png")
        
        r_den = np.array(r_den)
        r_dil = np.array(r_dil)
        
    
class Droplet:
# point class contains individual information about the points associated with the center of circles and the circles themselves
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.loc = [self.x, self.y]
            self.dil_radius = 0.0
            self.den_radius = 0.0
            self.mask = None
            self.color = np.random.rand(3) # for differentiating when plotting
            
        def get_dil_circle(self, steps):
        # return a discrete set of points describing a circle, used for plotting
            theta = np.linspace(0, 2*np.pi, steps)
            x_arr = self.dil_radius * np.cos(theta) + self.x
            y_arr = self.dil_radius * np.sin(theta) + self.y
            return x_arr, y_arr    
        
        def get_den_circle(self, steps):
        # return a discrete set of points describing a circle, used for plotting
            theta = np.linspace(0, 2*np.pi, steps)
            x_arr = self.den_radius * np.cos(theta) + self.x
            y_arr = self.den_radius * np.sin(theta) + self.y
            return x_arr, y_arr  
            