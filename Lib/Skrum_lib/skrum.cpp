
#include "../pybind11/include/pybind11/pybind11.h"
#include "../pybind11/include/pybind11/stl_bind.h"
#include "../pybind11/include/pybind11/stl.h"

#include <vector>

#include "skrum_aby.h"


namespace py = pybind11;
using namespace std;


typedef uint32_t uInt32;

PYBIND11_MAKE_OPAQUE(std::vector<uInt32>);

PYBIND11_MODULE(SKRUM, m) {

    py::bind_vector<std::vector<uInt32>>(m, "VectoruInt32", py::buffer_protocol());

    m.doc() = "C++ module for KD_lib";

    m.def("init_skrum_aby", &init_skrum_aby, "init_skrum_aby");

    m.def("shutdown_skrum_aby", &shutdown_skrum_aby, "shutdown_skrum_aby");

    m.def("skrum_mul", &skrum_mul, "skrum_mul");
    m.def("skrum_secp", &skrum_secp, "skrum_secp");
}
