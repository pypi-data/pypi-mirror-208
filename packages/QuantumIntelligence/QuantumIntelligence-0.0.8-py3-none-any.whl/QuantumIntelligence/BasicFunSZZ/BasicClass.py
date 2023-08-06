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

class MultiDimensionDict(dict):
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            super().__setitem__(item, MultiDimensionDict())
            return super().__getitem__(item)


class DefaultValuedDict(dict):
    
    def __init__(self, default_value=0):
        super().__init__()
        self.default_value = default_value
    
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            super().__setitem__(item, self.default_value)
            return super().__getitem__(item)