# Copyright (C) <2022>  <Zheng-Zhi Sun>
# This file is part of QuantumIntelligence. QuantumIntelligence 
# is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. 
# QuantumIntelligence is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details. You should have received a 
# copy of the GNU General Public License along with QuantumIntelligence. 
# If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from QuantumIntelligence.BasicFunSZZ import wheel_function as wf

sx = np.array([[0, 1], [1, 0]])
sy = np.array([[0, -1j], [1j, 0]])
sz = np.array([[1, 0], [0, -1]])


# [1, 0] is |0>, [0, 1] is |1>


def generate_hamiltonian(n_site=5, name='Heisenberg', para=None, periodic=False):

    i_2d = np.eye(2)
    i_2d_list = list(range(n_site))
    i_2d_list[0] = 1

    sx2 = np.kron(sx, sx)
    sy2 = np.kron(sy, sy)
    sz2 = np.kron(sz, sz)

    for nn in range(1, n_site):
        i_2d_list[nn] = np.kron(i_2d_list[nn - 1], i_2d)

    # give Hamiltonian
    h_matrix = np.zeros((2 ** n_site, 2 ** n_site))

    if name == 'Heisenberg':
        # H = sum(-s_i*s_j)
        if para is None:
            jx = -1
            jy = -1
            jz = -1
            hz = -1
            hx = 0
        else:
            jx = para['jx']
            jy = para['jy']
            jz = para['jz']
            hz = para['hz']
            hx = para['hx']
        # print(jx,jy,jz,hz,para)
        # add sz
        for nn in range(n_site):
            h_matrix = h_matrix - np.kron(np.kron(i_2d_list[nn], sz * hz), i_2d_list[n_site - 1 - nn])
        # add sx
        for nn in range(n_site):
            h_matrix = h_matrix - np.kron(np.kron(i_2d_list[nn], sx * hx), i_2d_list[n_site - 1 - nn])
        # add sx2
        for nn in range(n_site - 1):
            h_matrix = h_matrix - np.kron(np.kron(i_2d_list[nn], jx * sx2), i_2d_list[n_site - 2 - nn])
        # add sy2
        for nn in range(n_site - 1):
            h_matrix = h_matrix - np.kron(np.kron(i_2d_list[nn], jy * sy2), i_2d_list[n_site - 2 - nn])
        # add sz2
        for nn in range(n_site - 1):
            h_matrix = h_matrix - np.kron(np.kron(i_2d_list[nn], jz * sz2), i_2d_list[n_site - 2 - nn])

        # periodic
        if periodic:
            h_matrix = h_matrix - jx * np.kron(np.kron(sx, i_2d_list[n_site - 2]), sx)
            h_matrix = h_matrix - jy * np.kron(np.kron(sy, i_2d_list[n_site - 2]), sy)
            h_matrix = h_matrix - jz * np.kron(np.kron(sz, i_2d_list[n_site - 2]), sz)

    if name == 'MaxCut':
        if para is None:
            para = ((0, 1), (1, 2), (2, 3), (1, 4))
        for oo in para:
            # print(oo)
            h_matrix = h_matrix + wf.np_kron(
                i_2d_list[oo[0]], sz, i_2d_list[oo[1] - oo[0] - 1], sz, i_2d_list[n_site - oo[1] - 1])

    return h_matrix


def str2matrix(str_input):
    tmp_matrix = np.ones(1, 1)
    for xx in str_input:
        tmp_matrix = np.kron(tmp_matrix, str2matrix(xx))
    return tmp_matrix


def str2pauli(str_single):
    if str_single == 'x':
        return sx
    elif str_single == 'y':
        return sy
    elif str_single == 'z':
        return sz
    else:
        raise ValueError('Input string should be x, y, or z.')