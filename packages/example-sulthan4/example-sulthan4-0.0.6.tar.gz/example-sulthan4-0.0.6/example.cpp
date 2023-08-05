#include <Python.h>

int add(int a, int b) 
{
	printf("Add function called");
    return a + b;
}

static PyObject* add(PyObject* self, PyObject* args) 
{
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
	printf("Add function called a + b");
    return PyLong_FromLong(a * b);
}

static PyMethodDef module_methods[] = {
    {"add", add, METH_VARARGS, "A function which adds two integers"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef examplemodule = {
    PyModuleDef_HEAD_INIT,
    "example",
    "Example module using Python C API",
    -1,
    module_methods
};

PyMODINIT_FUNC PyInit_example(void) 
{
	printf("PyModule_Create");
    return PyModule_Create(&examplemodule);
}
