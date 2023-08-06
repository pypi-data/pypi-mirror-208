#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <fstream>
#include <iostream>

namespace k1a {

extern bool debug;

template <class T>
void log_print(T s) {
    std::ofstream f;
    f.open("/home/kelvin/repos/labs/k1a/logs.txt", std::ios_base::app);
    f << s;
    f.close();
}

template <class T>
void log_println(T s) {
    log_print(s);
    log_print("\n");
}

void log_clear();
PyObject *k1a_log_clear(PyObject *self, PyObject *args);
std::string demangle(const char *name);

}  // namespace k1a
