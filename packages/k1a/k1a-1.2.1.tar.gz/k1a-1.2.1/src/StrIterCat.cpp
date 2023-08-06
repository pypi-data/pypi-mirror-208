#define PY_SSIZE_T_CLEAN
#include "StrIterCat.h"

#include <Python.h>
#include <structmember.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "utils.h"

namespace k1a {

StrIterCat::StrIterCat(PyObject *pyObj, std::string fileName, long sB, long eB) : StrIter(pyObj) {
    this->fileName = new std::string(fileName);
    this->fp = new std::ifstream(fileName);
    this->sB = sB;
    this->eB = eB;
    this->seekPos = sB;
    this->fp->seekg(sB);
};

std::string StrIterCat::next() {
    std::string line;
    if (eB >= 0 && seekPos > eB) done = true;
    if (std::getline(*fp, line)) {
        seekPos += line.size() + 1;  // plus 1 to account for newline
        if (eB >= 0 && seekPos > eB) return line.substr(0, line.size() - (seekPos - eB) + 1);
        return line;
    } else {
        done = true;
        return "";
    }
};

/**
 * @brief Creates a new PyStrIterCat object
 *
 * @param fileName
 * @return PyObject*
 */
PyObject *PyStrIterCat_new(std::string fileName, long sB, long eB) {
    if (debug) log_println("PyStrIterCat_new");
    PyStrIterCat *res = PyObject_New(PyStrIterCat, &PyStrIterCat_Type);
    res->val = new StrIterCat((PyObject *)res, fileName, sB, eB);
    return (PyObject *)res;
}

PyObject *PyStrIterCat_new(std::string fileName) {
    if (debug) log_println("PyStrIterCat_new2");
    return PyStrIterCat_new(fileName, 0L, -1L);
}

PyObject *PyStrIterCat_new(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    PyStrIterCat *return_value = PyObject_New(PyStrIterCat, type);
    char *fileName;
    long sB = 0, eB = -1;
    PyArg_ParseTuple(args, "s|ll", &fileName, &sB, &eB);
    return PyStrIterCat_new(std::string(fileName), sB, eB);
}

StrIterCat::~StrIterCat() {
    fp->close();
    delete fileName;
}

PyObject *PyStrIterCat_conjugate(PyStrIterCat *self, PyObject *Py_UNUSED(ignored)) {
    return PyUnicode_FromString("str_iter_conjugate");
};

PyMethodDef PyStrIterCat_methods[] = {
    {"conjugate", (PyCFunction)PyStrIterCat_conjugate, METH_NOARGS, "conjugate docs"},
    {NULL, NULL}};

PyTypeObject PyStrIterCat_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0) "StrIterCat",
    sizeof(PyStrIterCat),
    0,
    (destructor)StrIter::Py_dealloc<PyStrIterCat>, /* tp_dealloc (destructor)str_iter_dealloc */
    0,                                             /* tp_vectorcall_offset */
    0,                                             /* tp_getattr */
    0,                                             /* tp_setattr */
    0,                                             /* tp_as_async */
    (reprfunc)StrIter::Py_repr<PyStrIterCat>,      /* tp_repr */
    0,                                             /* tp_as_number */
    StrIter::Py_as_sequence<PyStrIterCat>(),       /* tp_as_sequence */
    0,                                             /* tp_as_mapping */
    0,                                             /* tp_hash */
    0,                                             /* tp_call */
    0,                                             /* tp_str */
    PyObject_GenericGetAttr,                       /* tp_getattro */
    0,                                             /* tp_setattro */
    0,                                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                            /* tp_flags */
    "StrIterCat(filename, sB, eB)",                /* tp_doc */
    0,                                             /* tp_traverse */
    0,                                             /* tp_clear */
    0,                                             /* tp_richcompare */
    0,                                             /* tp_weaklistoffset */
    PyObject_SelfIter,                             /* tp_iter */
    (iternextfunc)StrIter::Py_next<PyStrIterCat>,  /* tp_iternext */
    PyStrIterCat_methods,                          /* tp_methods */
    0,                                             /* tp_members */
    0,                                             /* tp_getset */
    0,                                             /* tp_base */
    0,                                             /* tp_dict */
    0,                                             /* tp_descr_get */
    0,                                             /* tp_descr_set */
    0,                                             /* tp_dictoffset */
    0,                                             /* tp_init */
    PyType_GenericAlloc,                           /* tp_alloc */
    PyStrIterCat_new,                              /* tp_new */
    PyObject_Del,                                  /* tp_free PyObject_Del */
};

}  // namespace k1a
