#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <string>
#include <typeinfo>
#include <vector>

#include "utils.h"

namespace k1a {

typedef std::string (*transformF)(std::string);

/**
 * @brief String iterator
 *
 * Basically just a base string iterator class.
 *
 * For an overview of how memory is managed, check out this diagram:
 *
 * ```
 *  A--ref--|   B
 * val      |--val
 * ```
 *
 * A, B, and C are Python objects that has an associated StrIter at `A->val`.
 *
 * Let's assume that `A` is a string iterator that reads from a file, and `B`
 * is a string iterator that adds some suffix text to every line of `A`. Then
 * `A` owns `A->val`, `B->val` owns `A`, `B` owns `B->val`. Which means if `B`
 * is deleted by Python, then it would trigger deletion of `B->val`, which would
 * decrease Python's reference count of `A`, which can trigger deletion of `A`,
 * which would trigger deletion of `A->val`.
 *
 * Let's check out a chain with 3 StrIters:
 *
 * ```
 *  A--ref--|   B--ref--|   C
 * val      |--val      |--val
 * ```
 *
 * Again, assume `A` is reading from a file, `B` is adding a suffix and `C` is
 * adding a prefix. Let's also assume that only `A` and `C` are exposed to Python.
 * For the user, the flow looks like this:
 *
 * - Creates `A` and `A->val` using Python
 * - Runs a function that tries to create `C`
 * - The function creates `B` and `B->val`
 * - `B->val` obtains a reference to `A`. Now, `A` will not be deleted unless `B->val` is deleted
 * - The function creates `C` and `C->val`
 * - `C->val` obtains a reference to `B`. Now, `B` will not be deleted unless `C->val` is deleted
 * - `C` is returned to the user
 *
 * After this, reference count for al of them should be:
 *
 * - `A`: 2, from Python and from `B->val`
 * - `B`: 1, from `C->val`
 * - `C`: 1, from Python
 *
 * Assuming the user no longer uses `A` and `C`, this is what would happen:
 * - Python DECREF `C`
 * - `C` counter goes to 0, thus Python deletes it
 * - That triggers `C->val` deletion, which DECREF `B`
 * - `B` counter goes to 0, thus Python deletes it
 * - That triggers `B->val` deletion, which DECREF `A`
 * - `A` counter is 1
 * - Python DECREF `A`
 * - `A` counter goes to 0, thus Python deletes it
 * - That triggers `A->val` deletion
 *
 * So the convention is, the StrIter objects should not be deleted
 * outside of the associated Python object's dealloc method.
 *
 * When subclassing this, you should implement StrIter::next. If there
 * are no more elements, you should set StrIter::done to true, and
 * return an empty string.
 */
class StrIter {
   public:
    PyObject *pyObj;  ///< Associated python object
    bool done;        ///< Whether the iterator has any elements left

    StrIter();
    StrIter(PyObject *pyObj);
    virtual std::string next();
    StrIter *transform(std::vector<transformF> fs, bool decref = false);
    long length();
    ~StrIter();

    template <class T>
    static PyObject *Py_next(PyObject *self);
    template <class T>
    static PyObject *Py_repr(PyObject *self);
    template <class T>
    static Py_ssize_t Py_length(PyObject *self);
    template <class T>
    static void Py_dealloc(PyObject *self);
    template <class T>
    static PySequenceMethods *Py_as_sequence();
};

/**
 * @brief Default `tp_as_sequence` method generator.
 *
 * Example:
 * ```
 * PyTypeObject PyStrIterCat_Type = {
 *     PyVarObject_HEAD_INIT(&PyType_Type, 0) "StrIterCat",
 *     StrIter::Py_as_sequence<PyStrIterCat>(),
 * }
 * ```
 *
 * @tparam T
 * @return PySequenceMethods*
 */
template <class T>
PySequenceMethods *StrIter::Py_as_sequence() {
    PySequenceMethods *answer = new PySequenceMethods();
    *answer = {
        0, /* sq_length */  // (lenfunc)StrIter::Py_length<T>
        0,                  /* sq_concat */
        0,                  /* sq_repeat */
        0,                  /* sq_item */
        0,                  /* sq_slice */
        0,                  /* sq_ass_item */
        0,                  /* sq_ass_slice */
        0,                  /* sq_contains */
        0,                  /* sq_inplace_concat */
        0,                  /* sq_inplace_repeat */
    };
    return answer;
}

/**
 * @brief Default `__next__` function
 *
 * Example:
 * ```
 * PyTypeObject PyStrIterCat_Type = {
 *     PyVarObject_HEAD_INIT(&PyType_Type, 0) "StrIterCat",
 *     (iternextfunc)StrIter::Py_next<PyStrIterCat>,
 * }
 * ```
 *
 * @tparam T
 * @param self
 * @return PyObject*
 */
template <class T>
PyObject *StrIter::Py_next(PyObject *self) {
    T *it = (T *)self;
    if (debug) log_println(std::string("StrIter::Py_next - ") + demangle(typeid(T).name()));
    std::string res = it->val->next();
    if (it->val->done)
        return NULL;
    else
        return PyUnicode_FromString(res.c_str());
}

/**
 * @brief Default `__repr__` function
 *
 * Example:
 * ```
 * PyTypeObject PyStrIterCat_Type = {
 *     PyVarObject_HEAD_INIT(&PyType_Type, 0) "StrIterCat",
 *     (reprfunc)StrIter::Py_next<PyStrIterCat>,
 * }
 * ```
 *
 * @tparam T
 * @param self
 * @return PyObject*
 */
template <class T>
PyObject *StrIter::Py_repr(PyObject *self) {
    return PyUnicode_FromString(std::string("<").append(demangle(typeid(T).name())).append(" object>").c_str());
}

template <class T>
Py_ssize_t StrIter::Py_length(PyObject *self) {
    return ((T *)self)->val->length();
}

/**
 * @brief Default dealloc function
 *
 * Example:
 * ```
 * PyTypeObject PyStrIterCat_Type = {
 *     PyVarObject_HEAD_INIT(&PyType_Type, 0) "StrIterCat",
 *     (destructor)StrIter::Py_dealloc<PyStrIterCat>,
 * }
 * ```
 *
 * @tparam T
 * @param self
 * @return PyObject*
 */
template <class T>
void StrIter::Py_dealloc(PyObject *self) {
    if (debug) log_println(std::string("StrIter::Py_dealloc - ") + demangle(typeid(T).name()));
    T *_self = (T *)self;
    delete _self->val;
    Py_TYPE(_self)->tp_free(self);
}
}  // namespace k1a
