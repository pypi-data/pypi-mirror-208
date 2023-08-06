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
import math


_pauli_x = tc.tensor([[0, 1], [1, 0]])
_pauli_y = tc.tensor([[0, -1j], [1j, 0]])
_pauli_z = tc.tensor([[1, 0], [0, -1]])

def get_pauli(name='Z'):
    if name == 'X':
        return _pauli_x
    elif name == 'Y':
        return _pauli_y
    elif name == 'Z':
        return _pauli_z
    else:
        raise ValueError


class Gate:
    def __init__(self, unitary, label=None, inverse=False, independent=True,
                 check_unitary=False, unitary_acc=1e-6):
        if isinstance(unitary, Gate):
            self.inverse = unitary.inverse
            self.label = unitary.label
            if inverse:
                self.inverse = not self.inverse
            if independent:
                self._tensor = unitary.tensor.clone().detach()
            else:
                self._tensor = unitary.tensor

        elif isinstance(unitary, tc.Tensor):
            self.inverse = inverse
            self.label = label
            if independent:
                self._tensor = unitary.clone().detach()
            else:
                self._tensor = unitary

        elif unitary is None:
            self.inverse = inverse
            self._tensor = None
            self.label = label
        else:
            raise ValueError('unitary is wrong')
        if check_unitary:
            self.check_unitary(unitary_acc)

    @property
    def tensor(self):
        if isinstance(self._tensor, tc.Tensor):
            return self._tensor
        elif self._tensor is None:
            self.assign_tensor()
            return self._tensor

    @tensor.setter
    def tensor(self, unitary):
        self._tensor = unitary


    @property
    def requires_grad(self):
        return self._tensor.requires_grad

    @requires_grad.setter
    def requires_grad(self, requires_grad):
        self._tensor.requires_grad = requires_grad

    @property
    def grad(self):
        return self._tensor.grad

    @grad.setter
    def grad(self, value):
        self._tensor.grad = value

    # core functions start

    def check_unitary(self, acc=1e-6):
        identity_matrix = tc.eye(self._tensor.shape[0], device=self._tensor.device, dtype=self._tensor.dtype)
        diff = tc.dist(self._tensor.mm(self._tensor.conj().t()), identity_matrix)
        flag = (diff > acc)
        if flag:
            raise ValueError('the gate is not unitary. distance is ', diff)

    def inv(self):
        self.inverse = not self.inverse

    def square(self):
        if self._tensor.is_sparse:
            self._tensor = tc.sparse.mm(self._tensor, self._tensor)
        else:
            self._tensor = self._tensor.mm(self._tensor)

    def controlled_gate(self, n_control=1, output=False):
        # this function has not been tested
        c_gate = self._tensor.clone().detach()
        a_m = tc.tensor([[1, 0], [0, 0]], device=self._tensor.device, dtype=self._tensor.dtype)
        b_m = tc.tensor([[0, 0], [0, 1]], device=self._tensor.device, dtype=self._tensor.dtype)
        new_shape = c_gate.shape
        for nn in range(n_control):
            n_dim = round(c_gate.numel() ** 0.5)
            eye_m = tc.eye(n_dim, dtype=self._tensor.dtype, device=self._tensor.device)
            new_shape = new_shape + (2, 2)
            c_gate = tc.kron(a_m, eye_m) + tc.kron(b_m, c_gate.view(n_dim, n_dim))
        if output:
            return c_gate.view(new_shape)
        else:
            self._tensor = c_gate

    def to(self, device_or_dtype):
        self._tensor = self._tensor.to(device_or_dtype)
        return self

    def __copy__(self):
        return Gate(self)

    def assign_tensor(self):
        # _labelled_gate_no_params = ('X', 'Y', 'Z', 'H', 'CX', 'CY', 'CZ')
        # _labelled_gate_with_params = ('RX', 'RY', 'RZ')
        if self.label is None:
            raise ValueError('label is None. Can not assign tensor data')
        if self.label in ('X', 'Y', 'Z'):
            self.tensor = get_pauli(name=self.label)
        elif self.label == 'NOT':
            self.tensor = _pauli_x
        elif self.label == 'H':
            self.tensor = tc.tensor([[1, 1], [1, -1]]) / np.sqrt(2)
        elif self.label == 'CX':
            self.tensor =  tc.diag(tc.tensor([1, 1, 0, 0]))
            self.tensor[2, 3] = 1
            self.tensor[3, 2] = 1
        elif self.label == 'CZ':
            self.tensor =  tc.diag(tc.tensor([1, 1, 1, -1]))
        elif self.label == 'SWAP':
            self.tensor = tc.zeros(4, 4)
            self.tensor[0, 0] = 1
            self.tensor[1, 2] = 1
            self.tensor[2, 1] = 1
            self.tensor[3, 3] = 1
        elif self.label == 'CCX':
            self.tensor =  tc.diag(tc.tensor([1, 1, 1, 1, 1, 1, 0, 0]))
            self.tensor[6, 7] = 1
            self.tensor[7, 6] = 1
        elif self.label[0] in ('RX', 'RY', 'RZ'):
            theta = self.label[1]
            self.tensor = tc.eye(2)*math.cos(theta/2) - 1j * np.sin(theta/2)*get_pauli(name=self.label[0][1])
        elif self.label[0] in ('U3', 'U4'):
            theta = self.label[1]
            self.tensor = tc.tensor([[np.cos(theta[0]/2), -np.exp(1j*theta[2])*np.sin(theta[0]/2)],
                      [np.exp(1j*theta[1])*np.sin(theta[0]/2), np.exp(1j*(theta[1] + theta[2]))*np.cos(theta[0]/2)]],)
            if self.label[0] == 'U4':
                self.tensor = np.exp(1j*theta[3])*self.tensor
        elif self.label[0] in ('S'):
            self.tensor = tc.tensor([[1, 0], [0, np.exp(1j*np.pi/2)]])
        elif self.label[0] in ('T'):
            self.tensor = tc.tensor([[1, 0], [0, np.exp(1j*np.pi/4)]])
        else:
            raise ValueError('The label', self.label, 'is not supported')
        if self.inverse:
            self.tensor = self.tensor.T.conj()


    # core function end

# labelled gate

def labelled_simple_gate(name, params=None):
    if params is None:
        return Gate(unitary=None, label=name)
    else:
        return Gate(unitary=None, label=(name, params))


# Experimental univerisal gate set


def rx_gate(theta=np.pi):
    # exp(-i*theta * x/2)
    return Gate(unitary=None, label=('RX', theta))


def ry_gate(theta=np.pi):
    # exp(-i*theta * y/2)
    return Gate(unitary=None, label=('RY', theta))


def rz_gate(theta=np.pi):
    # exp(-i*theta * z/2)
    return Gate(unitary=None, label=('RZ', theta))

def r_gate(theta=np.pi, label='RZ', device='cpu', dtype=tc.complex64):
    if label in ('RZ', 'RX', 'RY'):
        return Gate(unitary=None, label=(label, theta))
    else:
        raise ValueError('Label must be RX, RY or RZ.')


def cz_gate():
    return Gate(unitary=None, label='CZ')

def cx_gate():
    return Gate(unitary=None, label='CX')

def ccx_gate(device='cpu', dtype=tc.complex64):
    return Gate(unitary=None, label='CCX')

# practical gates with label

def u3(theta:tuple):
    return Gate(unitary=None, label=('U3', theta))

def u4(theta:tuple, device='cpu', dtype=tc.complex64):
    return Gate(unitary=None, label=('U4', theta))

def hadamard():
    return Gate(unitary=None, label='H')


def phase_shift(theta, device='cpu', dtype=tc.complex64):
    gate = tc.eye(2, device=device, dtype=dtype)
    gate[1, 1] = tc.exp(tc.tensor(theta * 1j))
    return Gate(gate)


def not_gate():
    # this gate will be discarded
    return Gate(unitary=None, label='NOT')


def x_gate():
    return Gate(unitary=None, label='X')


def y_gate():
    return Gate(unitary=None, label='Y')


def z_gate():
    return Gate(unitary=None, label='Z')

def t_gate():
    return Gate(unitary=None, label='T')

def s_gate():
    return Gate(unitary=None, label='S')


def swap_gate():
    return Gate(unitary=None, label='SWAP')

# gate without label


def rand_gate(dim=2, device='cpu', dtype=tc.complex64, requires_grad=False):
    # Haar random gate
    tmp_tensor = tc.randn(dim, dim, device=device, dtype=dtype)
    q, r = tc.linalg.qr(tmp_tensor)
    sign_matrix = tc.sign(tc.real(tc.diag(r)))
    gate = tc.einsum('ij,j->ij', q, sign_matrix)
    gate = Gate(gate)
    gate.requires_grad = requires_grad
    return gate


def noise_gate_single_gaussian(strength=0.01, device='cpu', dtype=tc.complex64):
    theta = tc.randn(1, device=device) * (strength ** 0.5)
    direction = tc.randn(3, device=device)
    direction = direction / direction.norm()
    sigma = direction[0] * _pauli_x.to(device) + direction[1] * _pauli_y.to(device) + direction[2] * _pauli_z.to(device)
    gate_matrix = tc.cos(theta)*tc.eye(2, device=device) + tc.sin(theta) * 1j * sigma
    gate_matrix = gate_matrix.to(device).to(dtype)
    return Gate(gate_matrix)



def time_evolution(hamiltonian, time, device='cpu', dtype=tc.complex64):
    hamiltonian = hamiltonian.to(device).to(dtype)
    if hamiltonian.is_sparse:
        gate = tc.matrix_exp(-1j * hamiltonian.to_dense() * time)
        gate = gate.to_sparse()
    else:
        gate = tc.matrix_exp(-1j * hamiltonian * time)
    return Gate(gate)
