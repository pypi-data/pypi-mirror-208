#ifndef TEST_ADD_CPU_HPP
#define TEST_ADD_CPU_HPP
#include <cstddef>

void add_one_cpu_cpp(int * data, size_t N);
void add_one_cpu_cpp_mp(int * data, size_t N);
float sum_sin_cpu_cpp_mp(float * data, size_t N);
float sum_sin_cpu_cpp(float * data, size_t N);

#endif