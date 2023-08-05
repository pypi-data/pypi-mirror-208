#include <pybind11/pybind11.h>

int add(int a, int b) {
    return a + b;
}

int sub(int a, int b) {
    return a - b;
}

int divide(int a, int b) {
    return a / b;
}

int multiply(int a, int b) {
    return a * b;
}

PYBIND11_MODULE(example, m)
{
    m.def("add", &add, "A function which adds two integers");
    m.def("sub", &sub, "A function which subtracte two integers");	
    m.def("Mul", &sub, "A function which Multiply two integers");
    m.def("divide", &sub, "A function which divide two integers");
}