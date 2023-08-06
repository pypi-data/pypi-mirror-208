#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <string>

#include "StrIter.h"

namespace k1a {

/**
 * @brief Intermediate string iterator
 *
 * Basically, this is a string iterator you get from transforming
 * another StrIter object. This should not be used directly,
 * use StrIter::transform instead.
 */
class StrIterInter : public StrIter {
   private:
    transformF f;
    StrIter *og;

   public:
    StrIterInter(PyObject *pyObj, StrIter *og, transformF f);
    std::string next();
    ~StrIterInter();
    static void Py_dealloc(PyObject *self);
};

typedef struct {
    PyObject_HEAD;
    StrIterInter *val;
} PyStrIterInter;

PyObject *PyStrIterInter_new(StrIter *og, transformF f);

extern PyTypeObject PyStrIterInter_Type;

}  // namespace k1a
