#include <cstddef>
#include <cmath>
#include "test_add_cpu.hpp"

void add_one_cpu_cpp(int * data, size_t N){
    for(size_t i = 0; i < N; i++)
        data[i] += 1;
}

void add_one_cpu_cpp_mp(int * data, size_t N){
    #pragma omp parallel for
        for(size_t i = 0; i < N; i++)
            data[i] += 1;
}

float sum_sin_cpu_cpp(float * data, size_t N){
    float sum(0);
    for(size_t i = 0; i < N; i++)
        sum = sum + sinf(data[i]);
    return sum;
}

float sum_sin_cpu_cpp_mp(float * data, size_t N){
    float sum(0);

    #pragma omp parallel for reduction(+ : sum)
    for(size_t i = 0; i < N; i++){
        sum = sum + sinf(data[i]);
    }
    return sum;
}