#define PY_SSIZE_T_CLEAN
#include "StrIter.h"

#include <Python.h>

#include <string>
#include <vector>

#include "StrIterInter.h"
#include "utils.h"

namespace k1a {

StrIter::StrIter() {
    done = false;
    this->pyObj = NULL;
};

StrIter::StrIter(PyObject *pyObj) {
    done = false;
    this->pyObj = pyObj;
};

/**
 * @brief Transforms StrIter into other iterators
 *
 * This passes ownership of the associated Python object to you.
 * However, you don't own intermediary StrIter objects as those
 * are cleaned automatically for you.
 *
 * If this StrIter is internal only, and is not returned to Python,
 * then you can set `decref` to true, just for convenience.
 *
 * @param fs Vector of transform functions
 * @param decref Whether to take ownership of this StrIter
 * @return StrIter*
 */
StrIter *StrIter::transform(std::vector<transformF> fs, bool decref) {
    if (debug) log_println("StrIter::transform");
    StrIter *answer = this;
    PyObject *lastPyObj = NULL;
    for (auto f : fs) {
        answer = ((PyStrIterInter *)PyStrIterInter_new(answer, f))->val;
        Py_XDECREF(lastPyObj);
        lastPyObj = answer->pyObj;
    }
    if (decref) Py_XDECREF(pyObj);
    return answer;
}

std::string StrIter::next() {
    if (debug) log_println("StrIter::next");
    return "";
}

long StrIter::length() {
    int count = 0;
    while (true) {
        next();
        if (done) break;
        count += 1;
    }
    return count;
}

StrIter::~StrIter(){};

}  // namespace k1a
