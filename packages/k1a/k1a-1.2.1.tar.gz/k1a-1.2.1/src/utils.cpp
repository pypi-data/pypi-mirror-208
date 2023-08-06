#include "utils.h"

#ifndef _WIN32
#include <cxxabi.h>
#endif

#include <fstream>
#include <iostream>
#include <memory>
#include <string>

namespace k1a {

bool debug = false;

void log_clear() {
    std::ofstream f;
    f.open("/home/kelvin/repos/labs/k1a/logs.txt");
    f << "";
    f.close();
}

PyObject *k1a_log_clear(PyObject *self, PyObject *args) {
    log_clear();
    Py_RETURN_NONE;
}

/**
 * @brief Demangles C++ signatures
 *
 * @param name
 * @return std::string
 */
#ifdef _WIN32
std::string demangle(const char *name) {
    return std::string(name);
}
#else
std::string demangle(const char *name) {
    int status = -4;  // some arbitrary value to eliminate the compiler warning

    // enable c++11 by passing the flag -std=c++11 to g++
    std::unique_ptr<char, void (*)(void *)> res{
        abi::__cxa_demangle(name, NULL, NULL, &status),
        std::free};

    return (status == 0) ? res.get() : name;
}
#endif

}  // namespace k1a
