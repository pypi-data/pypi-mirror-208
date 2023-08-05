// Compares the simulation kernel with the reference implementation.

#ifndef _VERIFICATION_H_
#define _VERIFICATION_H_

#include "buffer.h"
#include "defs.h"
#include "diamond.h"
#include "field.h"
#include "kernel.h"
#include "kernel_precompiled.h"
#include "slice.h"
#include "testutils.h"

namespace verification {

using defs::kWarpSize;
using defs::One;
using defs::RunShape;
using defs::UV;
using defs::XY;
using defs::Zero;
using diamond::E;
using diamond::H;
using diamond::Node;
using diamond::Nz;
using diamond::Xyz;

template <typename T, typename T1> void MatCopy(T1 *src, T1 *dst, RunShape rs) {
  for (int i = 0; i < cbuf::ExternalElems<T>(rs.domain, rs.pml.n); ++i)
    dst[i] = src[i];
}

template <typename T, typename T1>
void ZCoeffCopy(reference::ZCoeff<T1> *src, T1 *dst, RunShape rs) {
  for (int k = 0; k < diamond::ExtZz<T>(rs.pml.n); ++k) {
    reference::ZCoeff<T1> zc = src[k];
    dst[zcoeff::ExternalIndex(k, E, zcoeff::ExternalType::A)] = zc.epa;
    dst[zcoeff::ExternalIndex(k, E, zcoeff::ExternalType::B)] = zc.epb;
    dst[zcoeff::ExternalIndex(k, E, zcoeff::ExternalType::Z)] = zc.edz;
    dst[zcoeff::ExternalIndex(k, H, zcoeff::ExternalType::A)] = zc.hpa;
    dst[zcoeff::ExternalIndex(k, H, zcoeff::ExternalType::B)] = zc.hpb;
    dst[zcoeff::ExternalIndex(k, H, zcoeff::ExternalType::Z)] = zc.hdz;
  }
}

template <typename T> void AbsLayerCopy(T *src, T *dst, RunShape rs) {
  for (int i = 0; i < slice::ZMask<T>::ExternalElems(rs.domain); ++i)
    dst[i] = src[i];
}

template <typename T>
void ZSrcLayerCopy(T *src0, T *src1, T *dst, RunShape rs) {
  for (int i = 0; i < rs.domain.x; ++i)
    for (int j = 0; j < rs.domain.y; ++j)
      for (Xyz xyz : {diamond::X, diamond::Y}) {
        int srcindex = reference::FieldIndex(Node(i, j, 0, E, xyz), rs.domain.x,
                                             rs.domain.y);
        dst[slice::ZSrc<T>::ExternalIndex(XY(i, j), xyz, /*channel=*/0,
                                          rs.domain)] = src0[srcindex];
        dst[slice::ZSrc<T>::ExternalIndex(XY(i, j), xyz, /*channel=*/1,
                                          rs.domain)] = src1[srcindex];
      }
}

template <typename T, typename T1>
void SrcLayerInit(T1 *dst, Node srcnode, RunShape rs) {
  if (rs.src.type == RunShape::Src::ZSLICE) {
    XY pos(srcnode.i, srcnode.j);
    dst[slice::ZSrc<T>::ExternalIndex(pos, srcnode.xyz, /*channel=*/0,
                                      rs.domain)] = One<T1>();
    dst[slice::ZSrc<T>::ExternalIndex(pos, srcnode.xyz, /*channel=*/1,
                                      rs.domain)] = One<T1>();
  } else { // rs.srctype == RunShape::SourceType::YSLICE.
    dst[slice::YSrc<T>::ExternalIndex(srcnode.i, srcnode.k, srcnode.xyz,
                                      rs.pml.n)] = One<T1>();
  }
}

template <typename T> void WfToWaveform(T *src0, T *src1, T *dst, int n) {
  for (int i = 0; i < n; ++i) {
    dst[2 * i + 0] = src0[i];
    dst[2 * i + 1] = src1[i];
  }
}

template <typename T, typename T1, int Npml>
void RunKernel(RunShape rs, T1 *outptr, reference::SimParams<T1> sp, int nlo,
               int nhi) {
  // Ensure that the sizes of the reference and GPU-based simulation match.
  ASSERT_EQ(XY(sp.x, sp.y), rs.domain);
  ASSERT_EQ(sp.z, diamond::ExtZz<T>(Npml));
  ASSERT_EQ(sp.z + nlo + nhi, kWarpSize * diamond::EffNz<T>());

  // void *kernel = (void *)kernel::SimulationKernel<T, T1, Npml>;

  kernel::KernelAlloc<T, T1> alloc(rs, /*hmat=*/sp.hmat);
  kernel::KernelArgs<T, T1> args = alloc.Args();

  // Convert inputs.
  MatCopy<T, T1>(sp.mat, args.inputs.cbuffer, rs);
  ZCoeffCopy<T, T1>(sp.zcoeff, args.inputs.zcoeff, rs);
  AbsLayerCopy<T1>(sp.abs, args.inputs.abslayer, rs);
  SrcLayerInit<T, T1>(args.inputs.srclayer, sp.srcnode, rs);
  WfToWaveform(sp.wf0, sp.wf1, args.inputs.waveform,
               defs::NumTimeSteps(rs.out));

  // Execute kernel.
  kernel_precompiled::RunKernel<T, T1>(
      kernel_precompiled::MakePreCompiledKernelType<T>(
          /*capability=*/"75",
          /*npml=*/Npml),
      args);
  cudaDeviceSynchronize(); // TODO: Better error checking.

  // Copy output.
  for (int i = 0; i < field::ExternalElems<T>(rs.domain, /*nout=*/1, rs.pml.n);
       ++i)
    outptr[i] = args.output[i];
}

} // namespace verification

#endif // _VERIFICATION_H_
