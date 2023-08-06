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
import torch as tc
from QuantumIntelligence.TEBD import MPSclass
from QuantumIntelligence.BasicFunSZZ import BasicClass, wheel_function as wf


class TEBD(MPSclass.MPS):

    def __init__(self, n_site=4, bond_limit=32, dv=2,
                 dtype=tc.complex128, device='cpu',
                 cut_off=1e-14, tau_init=1e-1, tau_acc=1e-5,
                 tensor_acc=1e-6, bin_max=10000, energy_acc=1e-6):

        MPSclass.MPS.__init__(self, n_site=n_site, bond_limit=bond_limit, dv=dv,
                              dtype=dtype, device=device, cut_off=cut_off)

        # initialize parameters
        self.tau_init = tau_init
        self.tau_acc = tau_acc
        self.tau = tau_init
        self.tensor_acc = tensor_acc
        self.bin_max = bin_max
        self.energy_acc = energy_acc

        # initialize mps
        self.initialize_mps(method='ones')
        self.mps_regularization(0)
        self.tensor_data[0] = self.tensor_data[0] / self.tensor_data[0].norm()
        self.s_list = BasicClass.MultiDimensionDict()
        self.old_tensor_data = self.tensor_data.copy()
        self.energy = None

    @staticmethod
    def calculate_exp_ham(ham, tau):
        return tc.matrix_exp(-tau * ham)

    def evolute_one_site(self, index, exp_ham):
        self.tensor_data[index] = tc.einsum('abc,bd->adc', self.tensor_data[index], exp_ham)
        self.regular_center = None

    def evolute_two_site(self, index, exp_ham):
        index0 = index
        index1 = index + 1
        d0, dv, d1 = self.tensor_data[index0].shape
        d2 = self.tensor_data[index1].shape[-1]
        cut_off = self.cut_off
        tmp_tensor = tc.einsum('abc,cde->abde', self.tensor_data[index0], self.tensor_data[index1])
        new_tensor = tc.einsum('abde,bdij->aije', tmp_tensor, exp_ham)
        # error = (tmp_tensor - new_tensor).norm()

        u, s, v = wf.safe_svd(new_tensor.reshape(d0 * dv, dv * d2))

        s = s / s.norm()
        s = s[s > cut_off]
        dm = len(s)
        u = u[:, :dm]
        v = v[:dm, :]
        self.tensor_data[index0] = u.reshape(d0, dv, -1)
        self.tensor_data[index1] = tc.einsum('b,bc->bc', s, v).reshape(dm, dv, d2)
        self.regular_center = None

    def evolute_three_site(self, index, exp_ham):
        index0 = index
        index1 = index + 1
        index2 = index + 2
        d0, dv, d1 = self.tensor_data[index0].shape
        d2 = self.tensor_data[index2].shape[-1]
        cut_off = self.cut_off
        tmp_tensor = tc.einsum('abc,cde,efg->abdfg', self.tensor_data[index0],
                               self.tensor_data[index1], self.tensor_data[index2])
        new_tensor = tc.einsum('abdfg,bdfijk->aijkg', tmp_tensor, exp_ham)
        # error = (tmp_tensor - new_tensor).norm()
        u, s, v = wf.safe_svd(new_tensor.reshape(d0 * dv, dv * dv * d2))
        s = s / s.norm()
        s = s[s > cut_off]
        dm0 = len(s)
        u = u[:, :dm0]
        v = v[:dm0, :]
        self.tensor_data[index0] = u.reshape(d0, dv, dm0)
        new_tensor = tc.einsum('b,bc->bc', s, v).reshape(dm0 * dv, dv * d2)
        # u, s, v = tc.linalg.svd(new_tensor, full_matrices=False)
        u, s, v = wf.safe_svd(new_tensor)
        s = s / s.norm()
        s = s[s > cut_off]
        dm1 = len(s)
        u = u[:, :dm1]
        v = v[:dm1, :]
        self.tensor_data[index1] = u.reshape(dm0, dv, dm1)
        self.tensor_data[index2] = tc.einsum('b, bc->bc', s, v).reshape(dm1, dv, d2)
        self.regular_center = None

    def evolute_all_once(self, exp_ham):
        n_interval = round(np.log2(exp_ham.numel()) / 2)
        exp_ham = exp_ham.reshape(2 * n_interval * (2, ))
        # print(n_interval)
        for nn in range(n_interval):
            tmp_index = nn
            while (tmp_index + n_interval) <= self.n_site:
                if n_interval == 1:
                    self.evolute_one_site(tmp_index, exp_ham)
                elif n_interval == 2:
                    self.evolute_two_site(tmp_index, exp_ham)
                elif n_interval == 3:
                    self.evolute_three_site(tmp_index, exp_ham)
                tmp_index = tmp_index + n_interval
            self.mps_regularization(0)
            self.tensor_data[0] = self.tensor_data[0] / self.tensor_data[0].norm()

    def evolute_all_two_site_second(self, ham, t):
        exp_ham0 = self.calculate_exp_ham(ham, t/2)
        exp_ham1 = self.calculate_exp_ham(ham, t)
        n_interval = 2
        exp_ham0 = exp_ham0.reshape(2 * n_interval * (2, ))
        exp_ham1 = exp_ham1.reshape(2 * n_interval * (2, ))
        tmp_index = 0
        while (tmp_index + n_interval) <= self.n_site:
            self.evolute_two_site(tmp_index, exp_ham0)
            tmp_index = tmp_index + n_interval
        self.mps_regularization(0)
        self.tensor_data[0] = self.tensor_data[0] / self.tensor_data[0].norm()

        tmp_index = 1
        while (tmp_index + n_interval) <= self.n_site:
            self.evolute_two_site(tmp_index, exp_ham1)
            tmp_index = tmp_index + n_interval
        self.mps_regularization(0)
        self.tensor_data[0] = self.tensor_data[0] / self.tensor_data[0].norm()

        tmp_index = 0
        while (tmp_index + n_interval) <= self.n_site:
            self.evolute_two_site(tmp_index, exp_ham0)
            tmp_index = tmp_index + n_interval
        self.mps_regularization(0)
        self.tensor_data[0] = self.tensor_data[0] / self.tensor_data[0].norm()

    def evolute_all_energy(self, ham_list):
        # self.tau = self.tau_init
        n_iter = 0
        bin_num = 0
        tmp_energy = np.inf
        while self.tau > self.tau_acc:
            self.mps_regularization(0)
            exp_ham_list = list()
            for ham in ham_list:
                exp_ham_list.append(self.calculate_exp_ham(ham, self.tau/2))
            for exp_ham in exp_ham_list:
                self.evolute_all_once(exp_ham)
            exp_ham_list.reverse()
            for exp_ham in exp_ham_list:
                self.evolute_all_once(exp_ham)

            self.energy = self.calculate_energy(ham_list)/self.n_site
            tmp_error = tmp_energy - self.energy
            tmp_energy = self.energy
            if tmp_error < (self.cut_off * self.bond_limit):
                print('error is too small, stop this iteration. energy diff = ' + str(tmp_error))
                tmp_error = 0
            tmp_error = tmp_error / self.tau
            n_iter = n_iter + 1
            bin_num = bin_num + 1
            if (tmp_error < self.tensor_acc) or (bin_num >= self.bin_max):
                self.tau = self.tau / 2
                bin_num = 0
                print('n_iter = ' + str(n_iter) + ' tau = ' + str(self.tau) + ' error = ' + str(tmp_error))
        self.mps_regularization(0)
        self.tensor_data[0] = self.tensor_data[0] / self.tensor_data[0].norm()

    def evolute_all_fidelity(self, ham_list):
        # self.tau = self.tau_init
        n_iter = 0
        bin_num = 0
        while self.tau > self.tau_acc:
            self.mps_regularization(0)
            exp_ham_list = list()
            for ham in ham_list:
                exp_ham_list.append(self.calculate_exp_ham(ham, self.tau/2))
            for exp_ham in exp_ham_list:
                self.evolute_all_once(exp_ham)
            exp_ham_list.reverse()
            for exp_ham in exp_ham_list:
                self.evolute_all_once(exp_ham)

            tmp_fidelity = self.calculate_fidelity(self.old_tensor_data)
            self.old_tensor_data = self.tensor_data.copy()
            tmp_error = (1 - tmp_fidelity)/self.n_site
            if tmp_error < (self.cut_off * self.bond_limit):
                print('error is too small, stop this iteration. 1 - fidelity = ' + str(tmp_error))
                tmp_error = 0
            tmp_error = tmp_error / self.tau
            n_iter = n_iter + 1
            bin_num = bin_num + 1
            if (tmp_error < self.tensor_acc) or (bin_num >= self.bin_max):
                self.tau = self.tau / 2
                bin_num = 0
                print('n_iter = ' + str(n_iter) + ' tau = ' + str(self.tau) + ' error = ' + str(tmp_error))
        self.mps_regularization(0)
        self.tensor_data[0] = self.tensor_data[0] / self.tensor_data[0].norm()

    def calculate_fidelity(self, other_mps):
        # do not use this if fidelity is too small
        nn = 0
        init_tensor = tc.einsum('abc,abd->cd', self.tensor_data[nn], other_mps[nn].conj())
        # init_norm = 0
        for nn in range(1, self.n_site):
            init_tensor = tc.einsum('cd,cef->def', init_tensor, self.tensor_data[nn])
            init_tensor = tc.einsum('def,deg->fg', init_tensor, other_mps[nn].conj())
            # init_norm = init_norm + tc.log(init_tensor.norm())
            # init_tensor = init_tensor / init_tensor.norm()
            # print(init_tensor.norm())
        return init_tensor.norm()

    def calculate_fidelity_log(self, other_mps):
        nn = 0
        init_tensor = tc.einsum('abc,abd->cd', self.tensor_data[nn], other_mps[nn].conj())
        init_norm = 0
        for nn in range(1, self.n_site):
            init_tensor = tc.einsum('cd,cef->def', init_tensor, self.tensor_data[nn])
            init_tensor = tc.einsum('def,deg->fg', init_tensor, other_mps[nn].conj())
            init_norm = init_norm + tc.log(init_tensor.norm())
            init_tensor = init_tensor / init_tensor.norm()
            # print(init_tensor.norm())
        return init_norm

    def calculate_energy(self, ham_list):

        energy = 0
        self.mps_regularization(0)
        self.tensor_data[0] = self.tensor_data[0] / self.tensor_data[0].norm()

        if not isinstance(ham_list, list):
            raise ValueError('ham needs to be a list')

        new_ham_list = ham_list.copy()

        while len(new_ham_list) > 0:
            sum_ham, n_interval_list = self.merge_ham(new_ham_list)
            interval_max = max(n_interval_list)
            while (self.regular_center + interval_max) <= self.n_site:
                tmp_energy = self.calculate_energy_once(sum_ham)
                energy = energy + tmp_energy
                if self.regular_center < (self.n_site - 1):
                    self.move_regular_center2next()
                else:
                    break

            new_ham_list = []
            for nn in range(len(n_interval_list)):
                if n_interval_list[nn] < interval_max:
                    new_ham_list.append(ham_list[nn])
        return energy

    def merge_ham(self, ham_list):
        n_interval_list = list()
        for ham in ham_list:
            n_interval_list.append(round(np.log2(ham.numel()) / 2))
        interval_max = max(n_interval_list)
        sum_ham = 0
        for nn in range(len(ham_list)):
            inter_diff = interval_max - n_interval_list[nn]
            one_matrix = tc.eye(2 ** inter_diff, device=self.device, dtype=self.dtype)
            tmp_ham = tc.kron(ham_list[nn], one_matrix)
            sum_ham = sum_ham + tmp_ham

        return sum_ham, n_interval_list

    def calculate_energy_once(self, ham):
        tmp_index = self.regular_center
        n_interval = round(np.log2(ham.numel()) / 2)
        if n_interval == 1:
            init_tensor = tc.einsum('abc,adc->bd', self.tensor_data[tmp_index], self.tensor_data[tmp_index].conj())
        else:
            init_tensor = tc.einsum('abc,ade->bdce', self.tensor_data[tmp_index], self.tensor_data[tmp_index].conj())
            end_tensor = tc.einsum('abc,xdc->axbd',
                                   self.tensor_data[tmp_index + n_interval - 1],
                                   self.tensor_data[tmp_index + n_interval - 1].conj())
            tmp_dv = 2
            for nn in range(1, n_interval - 1):
                tmp_dv = tmp_dv * 2
                tmp_shape = self.tensor_data[tmp_index + nn].shape
                init_tensor = tc.einsum('bdce,cfg,emn->bfdmgn', init_tensor,
                                        self.tensor_data[tmp_index + nn], self.tensor_data[tmp_index + nn].conj())

                init_tensor = init_tensor.reshape(tmp_dv, tmp_dv, tmp_shape[2], tmp_shape[2])
            tmp_dv = tmp_dv * 2
            init_tensor = tc.einsum('dbce,cefg->dfbg', init_tensor, end_tensor).reshape(tmp_dv, tmp_dv)
        energy = tc.einsum('ab,ab->', init_tensor, ham)
        if tc.abs(energy.imag) > 1e-15:
            raise ValueError('energy is complex')
        return energy.real






