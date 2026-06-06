#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <filesystem>
#include <string>
#include <unordered_set>

namespace fs = std::filesystem;

namespace {

bool add_ignored_dir(PyObject *item, std::unordered_set<std::string> *ignored_dirs) {
    const char *name = PyUnicode_AsUTF8(item);

    if (name == nullptr) {
        return false;
    }

    ignored_dirs->insert(name);
    return true;
}

bool collect_ignored_dirs(
    PyObject *ignored_obj,
    std::unordered_set<std::string> *ignored_dirs
) {
    PyObject *iterator = PyObject_GetIter(ignored_obj);

    if (iterator == nullptr) {
        return false;
    }

    PyObject *item = nullptr;

    while ((item = PyIter_Next(iterator)) != nullptr) {
        bool ok = add_ignored_dir(item, ignored_dirs);
        Py_DECREF(item);

        if (!ok) {
            Py_DECREF(iterator);
            return false;
        }
    }

    Py_DECREF(iterator);

    return !PyErr_Occurred();
}

bool append_relative_path(PyObject *result, const fs::path &root, const fs::path &path) {
    fs::path relative_path = fs::relative(path, root);
    std::string relative_path_text = relative_path.generic_string();
    PyObject *py_path = PyUnicode_FromString(relative_path_text.c_str());

    if (py_path == nullptr) {
        return false;
    }

    int append_result = PyList_Append(result, py_path);
    Py_DECREF(py_path);

    return append_result == 0;
}

PyObject *scan_project_files(PyObject *, PyObject *args) {
    const char *root_text = nullptr;
    PyObject *ignored_obj = nullptr;

    if (!PyArg_ParseTuple(args, "sO:scan_project_files", &root_text, &ignored_obj)) {
        return nullptr;
    }

    std::unordered_set<std::string> ignored_dirs;

    if (!collect_ignored_dirs(ignored_obj, &ignored_dirs)) {
        return nullptr;
    }

    fs::path root(root_text);
    PyObject *result = PyList_New(0);

    if (result == nullptr) {
        return nullptr;
    }

    try {
        fs::recursive_directory_iterator iterator(
            root,
            fs::directory_options::skip_permission_denied
        );
        fs::recursive_directory_iterator end;

        for (; iterator != end; ++iterator) {
            const fs::directory_entry &entry = *iterator;
            std::string filename = entry.path().filename().string();

            if (
                entry.is_directory()
                && ignored_dirs.find(filename) != ignored_dirs.end()
            ) {
                iterator.disable_recursion_pending();
                continue;
            }

            if (entry.is_regular_file()) {
                if (!append_relative_path(result, root, entry.path())) {
                    Py_DECREF(result);
                    return nullptr;
                }
            }
        }
    } catch (const fs::filesystem_error &error) {
        Py_DECREF(result);
        PyErr_SetString(PyExc_OSError, error.what());
        return nullptr;
    }

    return result;
}

PyMethodDef methods[] = {
    {
        "scan_project_files",
        scan_project_files,
        METH_VARARGS,
        "Return project file paths relative to root.",
    },
    {nullptr, nullptr, 0, nullptr},
};

PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_learning_core",
    "Native Learning Core implemented with the CPython C API.",
    -1,
    methods,
};

}  // namespace

PyMODINIT_FUNC PyInit__learning_core() {
    return PyModule_Create(&module);
}
