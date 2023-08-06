#include <test_add_kernel.cu>
#include <test_add.hh>
#include <assert.h>
#include <iostream>

void kernel_add_one_host(int * data_host, int N){
    int size = N*sizeof(int);

    int * data_device;

    cudaError_t err = cudaMalloc((void**) &data_device, size);
    assert(err == 0);
    err = cudaMemcpy(data_device, data_host, size, cudaMemcpyHostToDevice);
    assert(err == 0);


    kernel_add_one<<<64, 64>>>(data_device, N);
    err = cudaGetLastError();
    assert(err == 0);


    err = cudaMemcpy(data_host, data_device, size, cudaMemcpyDeviceToHost);
    assert(err == 0);

    cudaFree(data_device);
}

float kernel_sum_sin_host(float * data_host, int N){
    int size = N*sizeof(float);

    float res_sum = 0;

    float * data_device;
    float * res_sum_device;

    cudaError_t err;

    err = cudaMalloc((void**) &data_device, size);
    assert(err == 0);
    err = cudaMalloc((void**) &res_sum_device, sizeof(float));
    assert(err == 0);
    
    err = cudaMemcpy(data_device, data_host, size, cudaMemcpyHostToDevice);
    assert(err == 0);
    err = cudaMemcpy(res_sum_device, &res_sum, sizeof(float), cudaMemcpyHostToDevice);
    assert(err == 0);

    kernel_sum_sin<<<64, 64>>>(data_device, N, res_sum_device);
    err = cudaGetLastError();
    assert(err == 0);

    err = cudaMemcpy(&res_sum, res_sum_device, sizeof(float), cudaMemcpyDeviceToHost);
    assert(err == 0);

    cudaFree(res_sum_device);
    cudaFree(data_device);

    return res_sum;
}