import cython
import numpy as np
cimport numpy as np
from libcpp.vector cimport vector

cdef extern from "./src/test_add.hh":
    void kernel_add_one_host(int * data_host, int N)
    float kernel_sum_sin_host(float * data_host, int N)

cdef extern from "./src/test_add_cpu.hpp":
    void add_one_cpu_cpp(int * data, size_t N)
    void add_one_cpu_cpp_mp(int * data, size_t N)
    float sum_sin_cpu_cpp(float * data, size_t N)
    float sum_sin_cpu_cpp_mp(float * data, size_t N)

def add_one(np.ndarray[np.int32_t, ndim=1, mode='c'] input):
    cdef int * _input = <int *>input.data
    
    kernel_add_one_host(_input, input.shape[0])

    return input

def add_one_cpu(np.ndarray[np.int32_t, ndim=1, mode='c'] input):
    cdef int * _input = <int*> input.data

    add_one_cpu_cpp(_input, input.shape[0])

    return input

def add_one_cpu_mp(np.ndarray[np.int32_t, ndim=1, mode='c'] input):
    cdef int * _input = <int*> input.data

    add_one_cpu_cpp_mp(_input, input.shape[0])

    return input

def sum_sin_cpu(np.ndarray[np.float32_t, ndim=1, mode='c'] input):
    cdef float * _input = <float*> input.data

    return sum_sin_cpu_cpp(_input, input.shape[0])

def sum_sin_cpu_mp(np.ndarray[np.float32_t, ndim=1, mode='c'] input):
    cdef float * _input = <float*> input.data

    return sum_sin_cpu_cpp_mp(_input, input.shape[0])

def sum_sin_gpu(np.ndarray[np.float32_t, ndim=1, mode='c'] input):
    cdef float * _input = <float*> input.data

    return kernel_sum_sin_host(_input, input.shape[0])
