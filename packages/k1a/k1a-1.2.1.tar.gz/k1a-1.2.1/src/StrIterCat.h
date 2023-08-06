#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "StrIter.h"

namespace k1a {

/**
 * @brief Line iterator from file
 *
 * Basically a k1a.StrIter, but iterates through lines in a specific file.
 * Constructor: k1a::PyStrIterCat_new. Example:
 *
 * ```
 * PyObject *a = PyStrIterCat_new("file.txt");
 * ```
 */
class StrIterCat : public StrIter {
   public:
    std::string *fileName;
    long sB;
    long eB;
    long seekPos;
    StrIterCat(PyObject *pyObj, std::string fileName, long sB, long eB);
    std::string next();
    ~StrIterCat();

   private:
    std::ifstream *fp;
};

typedef struct {
    PyObject_HEAD;
    StrIterCat *val;
} PyStrIterCat;

PyObject *PyStrIterCat_new(std::string fileName);
PyObject *PyStrIterCat_new(PyTypeObject *type, PyObject *args, PyObject *kwargs);
extern PyTypeObject PyStrIterCat_Type;

}  // namespace k1a
