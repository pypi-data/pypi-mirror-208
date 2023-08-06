#define PY_SSIZE_T_CLEAN
#include "StrIterInter.h"

#include <Python.h>

#include <string>

#include "utils.h"

namespace k1a {

StrIterInter::StrIterInter(PyObject *pyObj, StrIter *og, transformF f) : StrIter(pyObj) {
    this->f = f;
    this->og = og;
    Py_XINCREF(og->pyObj);
}

PyObject *PyStrIterInter_new(StrIter *og, transformF f) {
    PyStrIterInter *pyObj = PyObject_New(PyStrIterInter, &PyStrIterInter_Type);
    char *fileName;
    if (debug) log_println("PyStrIterInter_new");
    pyObj->val = new StrIterInter((PyObject *)pyObj, og, f);
    return (PyObject *)pyObj;
}

std::string StrIterInter::next() {
    std::string res = og->next();
    if (og->done) {
        done = true;
        return "";
    } else
        return f(res);
}

StrIterInter::~StrIterInter() {
    Py_XDECREF(og->pyObj);
}

PyTypeObject PyStrIterInter_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0) "StrIterInter",
    sizeof(PyStrIterInter),
    0,
    (destructor)StrIter::Py_dealloc<PyStrIterInter>, /* tp_dealloc (destructor)str_iter_dealloc */
    0,                                               /* tp_vectorcall_offset */
    0,                                               /* tp_getattr */
    0,                                               /* tp_setattr */
    0,                                               /* tp_as_async */
    (reprfunc)StrIter::Py_repr<PyStrIterInter>,      /* tp_repr */
    0,                                               /* tp_as_number */
    StrIter::Py_as_sequence<PyStrIterInter>(),       /* tp_as_sequence */
    0,                                               /* tp_as_mapping */
    0,                                               /* tp_hash */
    0,                                               /* tp_call */
    0,                                               /* tp_str */
    PyObject_GenericGetAttr,                         /* tp_getattro */
    0,                                               /* tp_setattro */
    0,                                               /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                              /* tp_flags */
    "StrIterInter, intermediate object",             /* tp_doc */
    0,                                               /* tp_traverse */
    0,                                               /* tp_clear */
    0,                                               /* tp_richcompare */
    0,                                               /* tp_weaklistoffset */
    PyObject_SelfIter,                               /* tp_iter */
    (iternextfunc)StrIter::Py_next<PyStrIterInter>,  /* tp_iternext */
    0,                                               /* tp_methods */
    0,                                               /* tp_members */
    0,                                               /* tp_getset */
    0,                                               /* tp_base */
    0,                                               /* tp_dict */
    0,                                               /* tp_descr_get */
    0,                                               /* tp_descr_set */
    0,                                               /* tp_dictoffset */
    0,                                               /* tp_init */
    PyType_GenericAlloc,                             /* tp_alloc */
    0,                                               /* tp_new */
    PyObject_Del,                                    /* tp_free PyObject_Del */
};

}  // namespace k1a
