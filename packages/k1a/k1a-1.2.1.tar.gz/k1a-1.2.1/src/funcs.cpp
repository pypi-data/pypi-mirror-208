/**
 * @file funcs.cpp
 * @brief Independent functions
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <string>

#include "StrIterCat.h"
#include "StrIterInter.h"
#include "utils.h"

namespace k1a {

PyObject *k1a_system(PyObject *self, PyObject *args) {
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command)) return NULL;
    sts = system(command);
    if (sts < 0) {
        // TODO: add exception string
        return NULL;
    }
    return PyLong_FromLong(sts);
}

PyObject *k1a_test(PyObject *self, PyObject *args) {
    const char *str;
    if (!PyArg_ParseTuple(args, "s", &str)) return NULL;
    const std::string a = str;
    auto b = (PyStrIterCat *)PyStrIterCat_new(a);
    auto f1 = [](std::string x) { return x + " |end"; };
    auto f2 = [](std::string x) { return "begin| " + x; };
    return b->val->transform(std::vector<transformF>{f1, f2}, true)->pyObj;
    //  return PyUnicode_FromString("def");
    //  return PyUnicode_FromString((a + "end").c_str());
}

/**
 * @brief Splits a string up into multiple pieces, respecting quotation marks
 *
 * Example:
 *
 * ```python
 * # returns ['ab', "c'd.e'f"]
 * k1a.str_split("ab.c'd.e'f", ".")
 * ```
 */
PyObject *k1a_str_split(PyObject *self, PyObject *args) {
    char *_str, *_delim, *str, *begin;
    if (!PyArg_ParseTuple(args, "ss", &_str, &_delim)) return NULL;
    char delim = _delim[0], quoteChar = '"';

    begin = str = (char *)malloc((strlen(_str) + 1) * sizeof(char));
    strcpy(str, _str);
    PyObject *plist = PyList_New(0);

    int i = 0;
    bool inBlock = false;

    while (str[i] != NULL) {
        char a = str[i];
        if (a == delim && !inBlock) {
            str[i] = NULL;
            PyList_Append(plist, PyUnicode_FromString(begin));
            begin = str + (i + 1);
        } else if (!inBlock && (a == '"' || a == '\'')) {  // new block
            inBlock = true;
            quoteChar = a;
        } else if (inBlock && a == quoteChar)
            inBlock = false;  // exiting block
        i++;
    }
    PyList_Append(plist, PyUnicode_FromString(begin));
    free(str);
    return plist;
}

/**
 * @brief Gets rid of special characters and only retain alpha numeric characters
 *
 * Example:
 *
 * ```python
 * # returns "abg 8 86"
 * k1a.str_alpha_numeric("abg$%^8,;86")
 * ```
 */
PyObject *k1a_str_alpha_numeric(PyObject *self, PyObject *args) {
    char *_str, *str;
    if (!PyArg_ParseTuple(args, "s", &_str)) return NULL;
    str = (char *)malloc((strlen(_str) + 1) * sizeof(char));
    int i = 0, j = 0;
    bool stillSpecial = false;

    while (_str[i] != NULL) {
        unsigned int a = _str[i];
        if ((65 <= a && a <= 90) || (97 <= a && a <= 122) || (48 <= a && a <= 57)) {  // legit characters
            str[j] = a;
            j++;
            stillSpecial = false;
        } else {
            if (!stillSpecial) {
                str[j] = ' ';
                j++;
            }
            stillSpecial = true;
        }
        i++;
    }
    str[j] = '\0';
    auto res = PyUnicode_FromString(str);
    free(str);
    return res;
}

/**
 * @brief Returns all k-mers for the given string
 *
 * Example:
 *
 * ```python
 * # returns ['012', '123', '234', '345', '456']
 * k1a.str_kmers("0123456", 3)
 * ```
 */
PyObject *k1a_str_kmers(PyObject *self, PyObject *args) {
    char *str;
    int k;
    if (!PyArg_ParseTuple(args, "si", &str, &k)) return NULL;
    PyObject *plist = PyList_New(0);

    bool inBlock = false;
    int n = strlen(str);
    if (n < k) return plist;

    for (int i = 0; i < n - (k - 1); i++) {
        char tmp = str[i + k];
        str[i + k] = '\0';
        PyList_Append(plist, PyUnicode_FromString(str + i));
        str[i + k] = tmp;
    }
    return plist;
}

/**
 * @brief Returns whether the string has any numeric characters inside them.
 *
 * Example:
 *
 * ```python
 * # returns True
 * k1a.str_has_number("gh365")
 * # returns False
 * k1a.str_has_number("ghj")
 * ```
 */
PyObject *k1a_str_has_number(PyObject *self, PyObject *args) {
    char *str;
    if (!PyArg_ParseTuple(args, "s", &str)) return NULL;
    int i = 0;
    while (str[i] != NULL) {
        unsigned int a = str[i];
        if (48 <= a && a <= 57) {
            Py_INCREF(Py_True);
            return Py_True;
        }
        i++;
    }
    Py_INCREF(Py_False);
    return Py_False;
}

PyMethodDef K1aMethods[] = {
    {"system", k1a_system, METH_VARARGS, "Execute a shell command."},
    {"test", k1a_test, METH_VARARGS,
     "Test function for developing the library"},
    {"clear", k1a_log_clear, METH_VARARGS, "Clear logs"},
    {"str_split", k1a_str_split, METH_VARARGS,
     "str_split(s, ch). Splits string into multiple fragments using a delimiter, respecting quotes."
     "\n\nExample: k1a.str_split(\"'ab'cdb3\", \"b\") == [\"'ab'cd\", \"3\"]"},
    {"str_alpha_numeric", k1a_str_alpha_numeric, METH_VARARGS, "str_alpha_numeric(s). Replaces characters that are not alpha numeric with white spaces. \n\nExample: str_alpha_numeric(\"4,.53-45ag\") == \"4 53 45ag\""},
    {"str_kmers", k1a_str_kmers, METH_VARARGS, "str_kmers(s, k). Gets a string's k-mers. \n\nExample: k1a.str_kmers(\"abcde\", 2) == ['ab', 'bc', 'cd', 'de']"},
    {"str_has_number", k1a_str_has_number, METH_VARARGS, "str_has_number(s). Returns whether the string has any numeric characters inside them."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

struct PyModuleDef k1amodule = {
    PyModuleDef_HEAD_INIT, "k1a", /* name of module */
    NULL,                         /* module documentation, may be NULL */
    -1,                           /* size of per-interpreter state of the module,
                                     or -1 if the module keeps state in global variables. */
    K1aMethods};

}  // namespace k1a
