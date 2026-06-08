#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <cerrno>
#include <cstring>
#include <dirent.h>
#include <string>
#include <sys/stat.h>
#include <sys/types.h>
#include <unordered_set>

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

std::string join_path(const std::string &parent, const std::string &name) {
    if (parent.empty() || parent == "/") {
        return parent + name;
    }

    return parent + "/" + name;
}

std::string join_relative_path(const std::string &parent, const std::string &name) {
    if (parent.empty()) {
        return name;
    }

    return parent + "/" + name;
}

bool is_current_or_parent_dir(const char *name) {
    return std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0;
}

bool append_relative_path(PyObject *result, const std::string &relative_path) {
    PyObject *py_path = PyUnicode_FromString(relative_path.c_str());

    if (py_path == nullptr) {
        return false;
    }

    int append_result = PyList_Append(result, py_path);
    Py_DECREF(py_path);

    return append_result == 0;
}

bool raise_os_error(const std::string &operation, const std::string &path) {
    std::string message = operation + " failed for " + path + ": " + std::strerror(errno);
    PyErr_SetString(PyExc_OSError, message.c_str());
    return false;
}

bool walk_directory(
    const std::string &root,
    const std::string &relative_dir,
    const std::unordered_set<std::string> &ignored_dirs,
    PyObject *result
) {
    std::string dir_path = relative_dir.empty() ? root : join_path(root, relative_dir);
    DIR *dir = opendir(dir_path.c_str());

    if (dir == nullptr) {
        if (errno == EACCES || errno == ENOENT) {
            return true;
        }

        return raise_os_error("opendir", dir_path);
    }

    errno = 0;
    dirent *entry = nullptr;

    while ((entry = readdir(dir)) != nullptr) {
        const char *entry_name = entry->d_name;

        if (is_current_or_parent_dir(entry_name)) {
            continue;
        }

        std::string name(entry_name);
        std::string relative_path = join_relative_path(relative_dir, name);
        std::string full_path = join_path(root, relative_path);

        struct stat metadata {};

        if (lstat(full_path.c_str(), &metadata) != 0) {
            if (errno == EACCES || errno == ENOENT) {
                errno = 0;
                continue;
            }

            closedir(dir);
            return raise_os_error("lstat", full_path);
        }

        if (S_ISDIR(metadata.st_mode)) {
            if (ignored_dirs.find(name) != ignored_dirs.end()) {
                continue;
            }

            if (!walk_directory(root, relative_path, ignored_dirs, result)) {
                closedir(dir);
                return false;
            }

            continue;
        }

        if (S_ISREG(metadata.st_mode)) {
            if (!append_relative_path(result, relative_path)) {
                closedir(dir);
                return false;
            }
        }
    }

    if (errno != 0) {
        int readdir_errno = errno;
        closedir(dir);
        errno = readdir_errno;
        return raise_os_error("readdir", dir_path);
    }

    if (closedir(dir) != 0) {
        return raise_os_error("closedir", dir_path);
    }

    return true;
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

    std::string root(root_text);
    PyObject *result = PyList_New(0);

    if (result == nullptr) {
        return nullptr;
    }

    if (!walk_directory(root, "", ignored_dirs, result)) {
        Py_DECREF(result);
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
