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

import random
from collections import Counter
import numpy as np
import qiskit
import qiskit_aer
import stim
import cirq
import qsimcirq
import torch as tc
from QuantumIntelligence.QuantumSimulator.Circuit import Circuit
from QuantumIntelligence.BasicFunSZZ.BasicClass import DefaultValuedDict as DVD
from QuantumIntelligence.BasicFunSZZ import BasicFunctions_szz as bf


# [1, 0] is |0>, [0, 1] is |1>
# do not use fake functions, it will be removed soon
# please apply gate on position as list(range(?)) as much as possible, this will make it faster
# please control gate on position as list(range(?, n_qubit)) as much as possible, this will make it faster

class SimulatorProcess:
    def __init__(self, n_qubit, device='cuda:0', dtype=tc.complex64,
                 rand_seed=1, fast_mode=False, state_acc=1e-5,
                 circuit_size=None, default_simulator='QI', qubit_position=None):
        self.n_qubit = n_qubit
        self.device = device
        self.dtype = dtype
        self.rand_seed = rand_seed
        self._state = None
        self.shape = (2,) * self.n_qubit
        self.default_simulator = default_simulator
        self.initialize_state()
        self.tmp_gate = None
        self.chi = 2 ** self.n_qubit
        self.fast_mode = fast_mode
        self.state_acc = state_acc
        self.circuit_size = circuit_size
        self.circuit = Circuit(n_qubit, device=device, dtype=dtype, size=circuit_size, qubit_position=qubit_position)

    def initialize_state(self):
        self._state = tc.zeros(2 ** self.n_qubit, device=self.device, dtype=self.dtype)
        self._state[0] = 1
        self._state = self._state.view(self.shape)

    def simulate(self, clear_circuit=True, method=None, fast_mode=None, state_acc=None):
        if method is None:
            method = self.default_simulator
        self.circuit.regularize_all_position()
        if method == 'QI':
            self.qi_simulate(clear_circuit=clear_circuit, fast_mode=fast_mode, state_acc=state_acc)
        elif method == 'qsim':
            self.qsim_simulate(clear_circuit=clear_circuit)
        elif method == 'qiskit':
            self.qiskit_simulate(clear_circuit=clear_circuit)
        else:
            raise ValueError('The simulator of', method, 'is not supported.')


    def qi_simulate(self, clear_circuit=True, fast_mode=None, state_acc=None):
        self.circuit.regularize_all_position()
        if fast_mode is None:
            fast_mode = self.fast_mode

        if state_acc is None:
            state_acc = self.state_acc

        if len(self.circuit) > 0:

            # check auto grad
            if fast_mode:
                flag = self.circuit.requires_grad
                for ff in flag:
                    if ff:
                        raise ValueError('fast mode does not support auto grad')

            # check state
            if tc.abs(self._state.norm() - 1) > state_acc:
                raise ValueError('the norm of state is not 1. The diff is ', np.abs(self._state.cpu().norm() - 1))
            self._state = self._state.view(self.shape)
            for ii in range(len(self.circuit)):
                cc = self.circuit[ii]
                if fast_mode:
                    if cc[0].is_fast:
                        self.act_single_gate_fast(label=cc[0].label, position=cc[1], control=cc[2])
                    else:
                        self.act_single_gate(gate=cc[0], position=cc[1], control=cc[2], fast_mode=fast_mode)
                else:
                    self.act_single_gate(gate=cc[0], position=cc[1], control=cc[2], fast_mode=fast_mode)
        if clear_circuit:
            self.circuit.clear()

    def qsim_simulate(self, clear_circuit=True):
        if 'cuda' in self.device:
            # gpu_options = qsimcirq.QSimOptions(use_gpu=True)
            print('warning, the qsim can simulate quantum circuit only by cpu')
            gpu_options = qsimcirq.QSimOptions(use_gpu=False)
        else:
            gpu_options = qsimcirq.QSimOptions(use_gpu=False)
        self.circuit.regularize_all_position()
        cirq_circuit = self.circuit.to_cirq()
        cirq_order = self.circuit.cirq_qubit_order()
        qsim_simulator = qsimcirq.QSimSimulator(qsim_options=gpu_options)
        result = qsim_simulator.simulate(program=cirq_circuit, qubit_order=cirq_order,
                                         initial_state=self._state.to(tc.complex64).cpu().numpy().reshape(-1))
        self.state = tc.from_numpy(result.final_state_vector).to(self.device).to(self.dtype)
        if clear_circuit:
            self.circuit.clear()

    def qiskit_simulate(self, clear_circuit=True):
        self.circuit.regularize_all_position()
        if 'cuda' in self.device:
            # device = 'GPU'
            device = 'CPU'
        else:
            device = 'CPU'
        if self.dtype == tc.complex128:
            precision = 'double'
        else:
            precision = 'single'
        double_precision = (tc.complex128 == self.dtype)
        qiskit_circuit = qiskit.QuantumCircuit(self.n_qubit)
        state_numpy = self.state.cpu().to(tc.complex128).numpy().reshape(-1, order='F')
        state_numpy = state_numpy / np.linalg.norm(state_numpy)
        qiskit_circuit.initialize(state_numpy)
        qiskit_circuit.compose(self.circuit.to_qiskit(), inplace=True)
        qiskit_simulator = qiskit_aer.StatevectorSimulator(device=device, precision=precision)
        result = qiskit_simulator.run(qiskit_circuit).result()
        self._state = tc.tensor(result.get_statevector(), device=self.device, dtype=self.dtype)
        self._state = self._state.reshape(self.shape).permute(*reversed(list(range(self.n_qubit))))
        if clear_circuit:
            self.circuit.clear()

    @property
    def state(self):
        return self._state.clone()

    @state.setter
    def state(self, state):
        self._state = state.clone().reshape(self.shape).to(self.device).to(self.dtype)

    def act_single_gate_fast(self, label, position, control=None):
        if label == 'asdasd':
            pass
        else:
            raise ValueError('The label ', label, ' has not been supported')

    def act_single_gate(self, gate, position, control=None, fast_mode=False):
        # the position and control need to be canonized

        if control is None:
            control = []
        # gate can be sparse, but there seems to be no speedup
        # one should be careful when add inverse gates
        m_p = len(position)
        m_c = len(control)
        old_position = position + control
        new_position = list(range(m_p)) + list(range(-m_c, 0))
        if gate.inverse:
            tmp_gate = gate.tensor.conj().t()
        else:
            tmp_gate = gate.tensor
        tmp_gate = tmp_gate.to(self.device).to(self.dtype)
        self._state = self._state.movedim(old_position, new_position).contiguous().view(2 ** m_p, -1, 2 ** m_c)

        if fast_mode:
            # auto grad will fail
            self._state[:, :, -1] = tmp_gate.mm(self._state[:, :, -1])
        else:

            # The reason to introduce tmp_state is for the auto grad
            tmp_state = self._state.new_empty(self._state.size())
            tmp_state[:, :, -1] = tmp_gate.mm(self._state[:, :, -1])
            tmp_state[:, :, :-1] = self._state[:, :, :-1]
            self._state = tmp_state

        self._state = self._state.view(self.shape).movedim(new_position, old_position)

    def sampling(self, n_shots=1024, position=None, basis=None, if_print=True, rand_seed=None, return_weight=False):
        if rand_seed is None:
            rand_seed = self.rand_seed
        if rand_seed is not None:
            random.seed(rand_seed)
        if basis is not None:
            tmp_state = self.change_measure_basis(position, basis)
        else:
            tmp_state = self._state.clone().detach()
        if position is None:
            position = list(range(self.n_qubit))
            weight = tc.abs(tmp_state.contiguous().view(-1)) ** 2
            m_p = len(position)
        else:
            m_p = len(position)
            tmp_state = tmp_state.movedim(position, list(range(m_p))).contiguous().view(2 ** m_p, -1)
            weight = tc.abs(tc.einsum('ab,ba->a', tmp_state, tmp_state.conj().t()))

        population = list()
        for pp in range(2 ** m_p):
            element = bin(pp)[2:]
            element = (m_p - len(element)) * '0' + element
            population.append(element)

        res = Counter(random.choices(population, weight, k=n_shots))
        if if_print:
            for key in res.keys():
                print(key, res[key])
        if return_weight:
            return res, weight
        else:
            return res

    @staticmethod
    def count_sample(res, ss, position, if_print=True):
        new_res = dict()
        for key in res.keys():
            flag = True
            for pp in position:
                if key[pp] != ss[position.index(pp)]:
                    flag = False
            if flag:
                new_res[key] = res[key]
        if if_print:
            for key in new_res.keys():
                print(key, new_res[key])
        return new_res

    def change_measure_basis(self, position, basis):
        if position is None:
            position = list(range(self.n_qubit))
        x_basis = tc.tensor([[1, 1], [1, -1]], device=self.device, dtype=self.dtype) / np.sqrt(2)
        y_basis = tc.tensor([[1, 1], [-1j, 1j]], device=self.device, dtype=self.dtype) / np.sqrt(2)
        tmp_state = self._state.clone().detach()
        for nn in range(len(position)):
            pp = position[nn]
            if basis[nn] == 'x':
                tmp_state = tc.einsum('abc,bd->adc', tmp_state.reshape(2 ** pp, -1, 2 ** (self.n_qubit - pp - 1)), x_basis)
            elif basis[nn] == 'y':
                tmp_state = tc.einsum('abc,bd->adc', tmp_state.reshape(2 ** pp, -1, 2 ** (self.n_qubit - pp - 1)), y_basis)
            tmp_state = tmp_state.view(self.shape).contiguous()
        return tmp_state

    def collapse(self, position=None, basis=None):
        m_p = len(position)
        if position == None:
            position = list(range(self.n_qubit))
        if basis is None:
            basis = '0' * m_p
        if m_p != len(basis):
            raise ValueError('error in extend, check position')
        index = int(basis, 2)
        new_position = list(range(-m_p, 0))
        tmp_state = self.state.movedim(position, new_position).reshape(-1, 2 ** m_p)
        return tmp_state[:, index]

    def fake_local_measure(self, position, operator):
        reduce_rho = self.fake_local_rho(position=position)
        measure_result = tc.einsum('ab,ba->', reduce_rho, operator.to(self.device).to(self.dtype))
        return measure_result

    def fake_local_rho(self, position):
        sorted_position = sorted(position)
        index_contract = list(range(self.n_qubit))
        permute_index0 = [sorted_position.index(ii) for ii in position]
        permute_index1 = [ii + len(position) for ii in permute_index0]
        for pp in position:
            index_contract.remove(pp)
        reduce_rho = tc.tensordot(self._state, self._state.conj(), dims=[index_contract, index_contract])
        reduce_rho = reduce_rho.permute(permute_index0 + permute_index1)
        # print(permute_index0 + permute_index1)
        return reduce_rho.reshape(2**len(position), -1)

    def fake_measure_circuit(self, circuit:Circuit):
        if len(self.circuit) > 0:
            print('warning, there are gates that are not simulated before this fake measure. '
                  'Measured results are based on the current state')
        backup_circuit = self.circuit
        backup_state = self.state
        self.circuit = circuit
        self.simulate()
        fidelity = tc.einsum('a,a->', backup_state.reshape(-1), self._state.reshape(-1).conj())
        self.circuit = backup_circuit
        self._state = backup_state
        return fidelity


# This program only provides interfere to stim
class SimulatorStabilizer:
    def __init__(self, n_qubit, device='cuda:0', dtype=tc.complex64,
                 rand_seed=1, state_acc=1e-3, circuit_size=None):
        self.n_qubit = n_qubit
        self.device = device
        self.dtype = dtype
        self.rand_seed = rand_seed
        self.circuit = Circuit(n_qubit, device=device, dtype=dtype, size=circuit_size)
        self._stim_circuit = None
        self.simulator = stim.TableauSimulator()
        self.circuit_size = circuit_size


    @property
    def stim_circuit(self):
        self._stim_circuit = self.circuit.to_stim()
        return self._stim_circuit

    @stim_circuit.setter
    def stim_circuit(self, stim_circuit: stim.Circuit):
        print('warning, you should not set the stim circuit. This feature needs to be fixed. Be careful!!')
        self._stim_circuit = stim_circuit

    def simulate(self, clear_circuit=True, force_mode=False):
        if force_mode:
            self.simulator.do(self._stim_circuit)
        else:
            self.simulator.do(self.stim_circuit)
        if clear_circuit:
            self.circuit.clear()

    def fake_measure_circuit(self, circuit: Circuit):
        pauli_string = stim.PauliString(self.n_qubit)
        pauli_list = []
        for ii in range(len(circuit)):
            tmp_str = pauli_string[circuit.position_list[ii][0]]
            if tmp_str == 0:
                pauli_string[circuit.position_list[ii][0]] = circuit.gate_list[ii].label
            else:
                pauli_list.append(pauli_string)
                pauli_string = stim.PauliString(self.n_qubit)
                assert pauli_string[circuit.position_list[ii][0]] == 0
                pauli_string[circuit.position_list[ii][0]] = circuit.gate_list[ii].label
        for pau in pauli_list:
            pauli_string = pau * pauli_string
        return self.simulator.peek_observable_expectation(pauli_string)


# temporary program
class SimulatorSparse(SimulatorProcess):
    def initialize_state(self):
        self._state = DVD(default_value=0)
        self._state[self.n_qubit*'0'] = 1

    def simulate(self, clear_circuit=True):
        print('this is a test progarm!!!!!!!!!!!!!!!!!')
        self.circuit.regularize_all_position()
        if len(self.circuit) > 0:
            for ii in range(len(self.circuit)):
                cc = self.circuit[ii]
                if len(cc[2])>0:
                    raise ValueError('Does not support controlled gate')
                self.act_single_gate(gate=cc[0], position=cc[1])
        if clear_circuit:
            self.circuit.clear()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def act_single_gate(self, gate, position, control=None, fast_mode=False):
        new_state = DVD(default_value=0)
        if len(position) == 1:
            # single qubit gate
            pp = position[0]
            gmatrix = gate.tensor
            for kk in self._state.keys():
                new_state[kk]  = new_state[kk] + self._state[kk] * gmatrix[int(kk[pp]), int(kk[pp])]
                kk1 = kk[:pp] + str(int(kk[pp]=='0')) + kk[pp+1:]
                new_state[kk1]  = new_state[kk1] + self._state[kk] * gmatrix[1 - int(kk[pp]), int(kk[pp])]
        elif len(position) == 2:
            if not gate.label == 'CZ':
                raise ValueError('Only CZ is supported as two-qubit gate')
            pp0 = position[0]
            pp1 = position[1]
            for kk in self._state.keys():
                if (kk[pp0]=='1') and (kk[pp1]=='1'):
                    new_state[kk] = self._state[kk]
                else:
                    new_state[kk] = -self._state[kk]
        else:
            raise ValueError('Gate not supported')
        pop_keys = []
        for kk in new_state.keys():
            if tc.abs(new_state[kk]) < 1e-8:
                pop_keys.append(kk)
        for kk in pop_keys:
            new_state.pop(kk)
        self._state = new_state

    def sampling(self, n_shots=1024, position=None, if_print=True, rand_seed=None, return_weight=False):
        if rand_seed is None:
            rand_seed = self.rand_seed
        if rand_seed is not None:
            random.seed(rand_seed)
        if position is None:
            position = list(range(self.n_qubit))
        m_p = len(position)
        population = list()
        weight = 2**m_p *[0]
        for pp in range(2 ** m_p):
            element = bin(pp)[2:]
            element = (m_p - len(element)) * '0' + element
            population.append(element)
            for kk in self._state.keys():
                pointer = {kk[position[ii]] == element[ii] for ii in range(m_p)}
                if False not in pointer:
                    weight[pp] = weight[pp] + tc.abs(self._state[kk])**2
        res = Counter(random.choices(population, weight, k=n_shots))
        if if_print:
            for key in res.keys():
                print(key, res[key])
        if return_weight:
            return res, weight
        else:
            return res
