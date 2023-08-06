"""
    Functions and modules for implementing geometric neural networks.
"""

import lietorch.nn.functional

from lietorch.nn.m2 import (
    LiftM2Cartesian,
    ReflectionPadM2,
    MaxProjectM2,
    ConvM2Cartesian,
    AnisotropicDilatedProjectM2,
    ConvectionM2,
    LinearConvolutionM2,
    MorphologicalConvolutionM2,
    FractionalDilationM2,
    FractionalDilationM2NonDiag,
    FractionalErosionM2,
    FractionalErosionM2NonDiag,
    LinearM2,
    ConvectionDilationPdeM2,
    ConvectionErosionPdeM2,
    CDEPdeLayerM2,
    CDEPdeLayerM2NonDiag,
    DEPdeLayerM2,
    SpatialResampleM2,
)

from lietorch.nn.r2 import (
    MorphologicalConvolutionR2,
    FractionalDilationR2,
    FractionalErosionR2,
    LinearR2,
    ConvectionR2,
    CDEPdeLayerR2,
    DEPdeLayerR2,
    SpatialResampleR2,
)

from lietorch.nn.loss import DiceLoss

