# These are utility functions to read txt grids.
import numpy as np
from multiprocess import Pool

from . import Initialize as Ini
from .logging import console
from .parameters import charges, default_masses


def read1D(path_to_file):
    """
    Read a space-separated txt file and return a 1-Dimensional list of the values

    Parameters:
        path_to_file : str
            file to open
    Returns:
            : list
        list of values
    """
    for line in open(path_to_file):
        listWord = line.split(" ")
    mylist = [float(item) for item in listWord]
    return mylist


def readND(path_to_file):
    """
    Read a space-separated txt file and return a N-Dimensional list of the values

    Input:
        path_to_file : str
            file to open
    Returns:
            : list
        list of values
    """
    mylist = []
    for line in open(path_to_file):
        listWord = line.split(" ")
        mylist.append(listWord)
    list = [
        [
            float(item)
            if item != "-nan" and item != "nan"
            else float(mylist[a][mylist[a].index(item) - 1])
            for item in mylist[a]
        ]
        for a in range(len(mylist))
    ]
    return list


class Construct_Grid:
    def __init__(self, func, h_id, path, grid_type, n_pools=8):
        self.func = func
        self.mass = default_masses(h_id)
        self.path = path
        self.xgrid = Ini.ZList
        self.qgrid = Ini.QList
        self.n_pools = n_pools
        self.nf = h_id
        self.e_h = charges(h_id)
        self.grid_type = grid_type
        if self.grid_type == "tilde":
            self.xgrid = self.xgrid[:-1]

    def construct_single_x(self, z):
        z_func_values = []
        p = []
        i = self.xgrid.index(z)
        console.log(f"[green]Computing x = {z},  {i}/{len(self.xgrid)}")
        for q in self.qgrid:
            p = [self.mass, q, self.e_h]
            if self.grid_type == "matching":
                z_func_values.append(self.func(z, p, self.nf, use_analytic=True))
            elif self.grid_type == "tilde":
                z_func_values.append(self.func(z, q, p, self.nf, use_analytic=True))
        return z_func_values

    def run(self):
        args = (self.construct_single_x, self.xgrid)
        with Pool(self.n_pools) as pool:
            result = pool.map(*args)

        func_values = []
        for res in result:
            func_values.append(res)
        console.log(f"Computation finished, saving to {self.path}")
        np.savetxt(self.path, func_values)
        return func_values
