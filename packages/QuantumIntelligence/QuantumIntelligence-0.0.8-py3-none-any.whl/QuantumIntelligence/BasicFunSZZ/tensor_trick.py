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

from collections.abc import Iterable
import torch as tc


def inverse_permutation(perm):
    # perm is a torch tensor
    if not isinstance(perm, tc.Tensor):
        perm = tc.tensor(perm)
    inv = tc.empty_like(perm)
    inv[perm] = tc.arange(perm.size(0), device=perm.device)
    return inv.tolist()


def have_same_iterable(a_list, b_list):
    if isinstance(a_list, Iterable) and isinstance(b_list, Iterable):
        xx = [x for x in a_list if x in b_list]
        if len(xx) > 0:
            return True
        else:
            return False
    else:
        return False


def is_str_same(a_str, b_str):
    flag = True
    if len(a_str) != len(b_str):
        return False
    else:
        for nn in range(len(a_str)):
            if a_str[nn] != b_str[nn]:
                flag = False
        return flag
