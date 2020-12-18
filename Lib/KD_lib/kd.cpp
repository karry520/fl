
#include "../pybind11/include/pybind11/pybind11.h"
#include "../pybind11/include/pybind11/stl_bind.h"
#include "../pybind11/include/pybind11/stl.h"

#include <vector>

#include "kd_aby.h"


namespace py = pybind11;
using namespace std;

typedef uint8_t uInt;
typedef int8_t Int;
typedef uint32_t uInt32;

PYBIND11_MAKE_OPAQUE(std::vector<Int>);
PYBIND11_MAKE_OPAQUE(std::vector<uInt>);
PYBIND11_MAKE_OPAQUE(std::vector<uInt32>);

PYBIND11_MODULE(KD, m) {

    py::bind_vector<std::vector<Int>>(m, "VectorInt", py::buffer_protocol());
    py::bind_vector<std::vector<uInt>>(m, "VectoruInt", py::buffer_protocol());
    py::bind_vector<std::vector<uInt32>>(m, "VectoruInt32", py::buffer_protocol());

    m.doc() = "C++ module for KD_lib";

    m.def("init_sru_aby", &init_sru_aby, "init_sru_aby");
    m.def("init_kd_aby", &init_kd_aby, "init_kd_aby");

    m.def("shutdown_sru_aby", &shutdown_sru_aby, "shutdown_sru_aby");
    m.def("shutdown_kd_aby", &shutdown_kd_aby, "shutdown_kd_aby");

    m.def("kd_sru", &kd_sru, "kd_sru");
    m.def("kd_top", &kd_top, "kd_top");

}
