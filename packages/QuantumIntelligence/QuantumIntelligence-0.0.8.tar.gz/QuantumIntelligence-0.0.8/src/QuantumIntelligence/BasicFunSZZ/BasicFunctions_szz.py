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
import pynvml
import os
import pickle
import torch as tc
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


def info_contact():
    """Return the information of the contact"""
    info = dict()
    info['name'] = 'Sun Zheng-Zhi'
    info['email'] = 'sunzhengzhi.work@gmail.com'
    info['affiliation'] = 'Tsinghua University'
    return info

# These are from the original functions of Sun Zheng-Zhi


def get_best_gpu(device='cuda'):
    if isinstance(device, tc.device):
        return device
    elif device == 'cuda':
        pynvml.nvmlInit()
        num_gpu = pynvml.nvmlDeviceGetCount()
        memory_gpu = tc.zeros(num_gpu)
        for index in range(num_gpu):
            handle = pynvml.nvmlDeviceGetHandleByIndex(index)
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            memory_gpu[index] = memory_info.free
        max_gpu = int(tc.sort(memory_gpu, )[1][-1])
        return tc.device('cuda:' + str(max_gpu))
    elif device == 'cpu':
        return tc.device('cpu')
    else:
        return tc.device(device)


def sort_dict(a):
    b = dict()
    dict_index = sorted(a.keys())
    for index in dict_index:
        b[index] = a[index]
    return b


def is_subdict(a, b):
    pointer = True
    # check keys
    for key in a.keys():
        if not a.get(key) == b.get(key):
            pointer = False
            break
    return pointer


def save_pr_add_data(path, file, data, names):
    mkdir(path)
    if os.path.isfile(path+file):
        tmp = load_pr(path+file)
    else:
        tmp = {}
    s = open(path + file, 'wb')
    for ii in range(0, len(names)):
        tmp[names[ii]] = data[ii]
    pickle.dump(tmp, s)
    s.close()


def save_pr_del_data(path, file, names):
    mkdir(path)
    if os.path.isfile(path+file):
        tmp = load_pr(path+file)
    else:
        tmp = {}
    s = open(path + file, 'wb')
    for ii in range(0, len(names)):
        tmp.pop(names[ii])
    pickle.dump(tmp, s)
    s.close()


# These are from BasicFunctions of Ran Shi-ju with some changes


def save_pr(path, file, data, names):
    """
    Save the data as a dict in a file located in the path
    :param path: the location of the saved file
    :param file: the name of the file
    :param data: the data to be saved
    :param names: the names of the data
    Notes: 1. Conventionally, use the suffix \'.pr\'. 2. If the folder does not exist, system will
    automatically create one. 3. use \'load_pr\' to load a .pr file
    Example:
    >>> x = 1
    >>> y = 'good'
    >>> save_pr('/test', 'ok.pr', [x, y], ['name1', 'name2'])
      You have a file '/test/ok.pr'
    >>> z = load_pr('/test/ok.pr')
      z = {'name1': 1, 'name2': 'good'}
      type(z) is dict
    """
    try:
        mkdir(path)
    except FileExistsError:
        pass
    # print(os.path.join(path, file))
    s = open(path+file, 'wb')
    tmp = dict()
    for i in range(0, len(names)):
        tmp[names[i]] = data[i]
    pickle.dump(tmp, s)
    s.close()


def load_pr(path_file, names=None):
    """
    Load the file saved by save_pr as a dict from path
    :param path_file: the path and name of the file
    :param names: the specific names of the data you want to load
    :return  the file you loaded
    Notes: the file you load should be a  \'.pr\' file.
    Example:
        >>> x = 1
        >>> y = 'good'
        >>> z = [1, 2, 3]
        >>> save_pr('.\\test', 'ok.pr', [x, y, z], ['name1', 'name2', 'name3'])
        >>> A = load_pr('.\\test\\ok.pr')
          A = {'name1': 1, 'name2': 'good'}
        >>> y, z = load_pr('\\test\\ok.pr', ['y', 'z'])
          y = 'good'
          z = [1, 2, 3]
    """
    if os.path.isfile(path_file):
        s = open(path_file, 'rb')
        if names is None:
            data = pickle.load(s)
            s.close()
            return data
        else:
            tmp = pickle.load(s)
            if type(names) is str:
                data = tmp[names]
                s.close()
                return data
            elif (type(names) is list) or (type(names) is tuple):
                nn = len(names)
                data = list(range(0, nn))
                for i in range(0, nn):
                    data[i] = tmp[names[i]]
                s.close()
                return tuple(data)
    else:
        return None


def mkdir(path):
    """
       Create a folder at your path
       :param path: the path of the folder you wish to create
       :return: the path of folder being created
       Notes: if the folder already exist, it will not create a new one.
    """
    try:
        os.makedirs(path)
    finally:
        pass

# end of Ran Shi-Ju's code


def easy_plot(x, *y):

    plt.figure(figsize=(8, 4))
    # plt.plot(np.array(x), np.array(y), 'b*')
    for nn in range(len(y)):
        # plt.plot(np.array(x), np.array(y[nn]), '*', markersize=1)
        plt.plot(np.array(x), np.array(y[nn]), label=nn)
    if len(y) == 0:
        tmp_x = np.arange(len(x))
        plt.plot(tmp_x, np.array(x), label=0)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.ylim()
    plt.title('default')
    plt.legend()
    plt.show()
    plt.close()


def easy_plot_3d(x, y, z):

    x, y = np.meshgrid(np.array(x), np.array(y))
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(x, y, np.array(z).T, rstride=1, cstride=1, cmap='rainbow')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.show()
    return fig


def compare_dict_1key(dict_list, key_com):
    pointer = True
    value = list()
    try:
        value.append(dict_list[0][key_com])
    except KeyError:
        pass
    for dict_one in dict_list:
        try:
            if dict_one[key_com] not in value:
                value.append(dict_one[key_com])
                pointer = False
        except KeyError:
            pointer = False
    return pointer, value


def seek_unique_value(a_list):
    check = []
    for xx in a_list:
        if xx not in a_list:
            check.append(xx)
    return check


if __name__ == '__main__':
    print(info_contact())
