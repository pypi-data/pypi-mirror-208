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

import torch as tc
import numpy as np
from QuantumIntelligence.TEBD import TNclass
from QuantumIntelligence.BasicFunSZZ import wheel_function as wf


class MPS(TNclass.TensorNetwork):
    def __init__(self, n_site=4, bond_limit=32, dv=2,
                 dtype=tc.complex128, device='cpu',
                 cut_off=1e-14):
        # Prepare parameters
        TNclass.TensorNetwork.__init__(self)
        self.n_site = n_site
        self.bond_limit = bond_limit
        self.dv = dv
        self.cut_off = cut_off
        self.n_site = n_site
        self.regular_center = None
        self.device = device
        self.dtype = dtype

    def initialize_mps(self, method=None, rand_seed=None):
        if method is None:
            method = 'rand'
        if rand_seed is not None:
            tc.manual_seed(rand_seed)
        self.tensor_data = list()

        dv = self.dv

        for nn in range(self.n_site):
            if method == 'rand':
                self.tensor_data.append(tc.rand((1, dv, 1), device=self.device, dtype=self.dtype))
            elif method == 'ones':
                self.tensor_data.append(tc.ones((1, dv, 1), device=self.device, dtype=self.dtype))


    def mps_regularization(self, regular_center, if_force=True):
        tmp_bond_limit = self.bond_limit
        regular_center = regular_center % self.n_site
        if self.regular_center is None:
            self.regular_center = 0
            if if_force:
                self.bond_limit = np.inf
            while self.regular_center < self.n_site-1:
                self.move_regular_center2next()
            self.bond_limit = tmp_bond_limit
        while self.regular_center < regular_center:
            self.move_regular_center2next()
        while self.regular_center > regular_center:
            self.move_regular_center2forward()

    def move_regular_center2next(self, norm_mode=True, cut_off=None, bond_limit=None):
        if cut_off is None:
            cut_off = self.cut_off
        if bond_limit is None:
            bond_limit = self.bond_limit

        tensor_index = self.regular_center
        tmp_tensor = self.tensor_data[tensor_index]
        d0, dv, d1 = tmp_tensor.shape
        u, s, v = wf.safe_svd(tmp_tensor.reshape(d0*dv, d1))
        if norm_mode:
            s = s/s.norm()
        s = s[s > cut_off]
        dm = min(s.numel(), bond_limit)
        u = u[:, :dm]
        s = s[:dm]
        v = v[:dm, :]

        self.tensor_data[tensor_index] = u.reshape(d0, dv, -1)
        self.tensor_data[tensor_index + 1] = tc.einsum('b,bc,cde->bde', s, v, self.tensor_data[tensor_index + 1])
        self.regular_center += 1

    def move_regular_center2forward(self, norm_mode=True, cut_off=None, bond_limit=None):
        if cut_off is None:
            cut_off = self.cut_off
        if bond_limit is None:
            bond_limit = self.bond_limit

        tensor_index = self.regular_center
        tmp_tensor = self.tensor_data[tensor_index]
        d0, dv, d1 = tmp_tensor.shape
        u, s, v = wf.safe_svd(tmp_tensor.reshape(d0, dv * d1))
        if norm_mode:
            s = s/s.norm()
        s = s[s > cut_off]
        dm = min(s.numel(), bond_limit)
        u = u[:, :dm]
        s = s[:dm]
        v = v[:dm, :]
        self.tensor_data[tensor_index] = v.reshape(dm, dv, d1)
        self.tensor_data[tensor_index - 1] = tc.einsum(
            'abc,cd,d->abd', self.tensor_data[tensor_index - 1], u, s).reshape(-1, dv, dm)
        self.regular_center -= 1

