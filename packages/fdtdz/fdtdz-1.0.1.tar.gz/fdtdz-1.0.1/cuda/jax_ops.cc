#include <pybind11/pybind11.h>
#include <string>

#include "kernel_jax.h"
#include "pybind11_kernel_helpers.h"
#include "shapedefs.h"

namespace {

using defs::RunShape;
using defs::UV;
using defs::XY;

pybind11::dict Registrations() {
  pybind11::dict dict;
  dict["kernel_f32"] =
      pybind11_kernel_helpers::EncapsulateFunction(kernel_jax::kernel_f32);
  dict["kernel_f16"] =
      pybind11_kernel_helpers::EncapsulateFunction(kernel_jax::kernel_f16);
  return dict;
}

PYBIND11_MODULE(gpu_ops, m) {
  m.def("registrations", &Registrations);
  m.def(
      "build_kernel_descriptor",
      [](float hmat, int capability, bool withglobal, bool withshared,
         bool withupdate, int blocku, int blockv, int gridu, int gridv,
         int blockspacing, int domainx, int domainy, int npml, int zshift,
         int srctype, int srcpos, int outstart, int outinterval, int outnum,
         std::string dirname) {
        return pybind11::bytes(
            kernel_jax::KernelDescriptor::ToString(kernel_jax::KernelDescriptor(
                std::string(dirname), capability, hmat,
                RunShape(UV(blocku, blockv), UV(gridu, gridv), blockspacing,
                         XY(domainx, domainy), RunShape::Pml(npml, zshift),
                         RunShape::Src(
                             static_cast<RunShape::Src::Type>(srctype), srcpos),
                         RunShape::Out(outstart, outinterval, outnum)),
                withglobal, withshared, withupdate)));
      });
}

} // namespace
