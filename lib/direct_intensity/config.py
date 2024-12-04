
home_dir = '/Users/nanostars/Desktop/phase-diagrams/Low Salt/some temps'
output_dir = '/Users/nanostars/Desktop/phase-diagrams/Low Salt/dioutput'
caps = [1, 2, 3]
concs = [23.2, 48.8, 97.8]
#concs = [1, 1, 1, 1, 1, 1]
removed_capillaries = []

min_radius = 35/2
max_radius = 70/2


class Config:
    def __init__(self):
        self.home_dir = home_dir
        self.output_dir = output_dir
        self.caps = caps
        self.concs = concs
        self.removed_capillaries = removed_capillaries
        self.min_radius = min_radius
        self.max_radius = max_radius