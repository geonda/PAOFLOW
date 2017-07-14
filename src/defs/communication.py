# 
# PAOFLOW
#
# Utility to construct and operate on Hamiltonians from the Projections of DFT wfc on Atomic Orbital bases (PAO)
#
# Copyright (C) 2016,2017 ERMES group (http://ermes.unt.edu, mbn@unt.edu)
# This file is distributed under the terms of the
# GNU General Public License. See the file `License'
# in the root directory of the present distribution,
# or http://www.gnu.org/copyleft/gpl.txt .
#

import numpy as np

from mpi4py import MPI
from load_balancing import *

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Scatters first dimension of an array of arbitrary length
def scatter_array ( arr, auxshape, pydtype, sroot ):
    # An array to store the size and dimensions of scattered arrays
    lsizes = np.empty((size,3), dtype=int)
    if rank == 0:
        lsizes = load_sizes(size, arr.shape[0], arr[0].size)
    comm.Bcast([lsizes, MPI.INT], root=0)

    # Change the first dimension of auxshape to the correct size for scatter
    auxshape = list(auxshape)
    auxshape[0] = lsizes[rank][2]

    # Initialize aux array
    arraux = np.empty(auxshape, dtype=pydtype)

    # Get the datatype for the MPI transfer
    mpidtype = MPI._typedict[np.dtype(pydtype).char]

    # Scatter the data according to load_sizes
    comm.Scatterv([arr, lsizes[:,0], lsizes[:,1], mpidtype], [arraux, mpidtype], root=sroot)

    return arraux

# Scatters first dimension of an array of arbitrary length
def gather_array ( arr, arraux, pydtype, sroot ):
    # An array to store the size and dimensions of gathered arrays
    lsizes = np.empty((size,3), dtype=int)
    if rank == 0:
        lsizes = load_sizes(size, arr.shape[0], arr[0].size)
    comm.Bcast([lsizes, MPI.INT], root=0)

    # Get the datatype for the MPI transfer
    mpidtype = MPI._typedict[np.dtype(pydtype).char]


    # Gather the data according to load_sizes
    comm.Gatherv([arraux, mpidtype], [arr, lsizes[:,0], lsizes[:,1], mpidtype], root=sroot)
