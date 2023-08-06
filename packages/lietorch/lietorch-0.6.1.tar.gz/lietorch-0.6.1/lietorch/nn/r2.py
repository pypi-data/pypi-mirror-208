"""
    Functions and modules for R2 (i.e. 2D translation equivariant) neural networks.
"""

import torch
from math import sqrt
from typing import Optional, List, Tuple, Union
import torch.nn.functional as F


def morphological_kernel_r2(
    finsler_params: torch.Tensor, kernel_radius: int, alpha: float
) -> torch.Tensor:
    """
    Construct a set of Finsler functions based on circular harmonics basis functions.

    Parameters
    -----------

    finsler_params: torch.Tensor
        Tensor of shape `[... , K]`,

    kernel_radius: int
        The kernel will be sampled on a recti-linear grid of size `[2*kernel_radius+1, 2*kernel_radius+1]`.

    alpha: float
        Alpha parameter, must be >= 0.55 and <= 1.0 for stability.    

    Returns
    ---------
    A Tensor of shape `[... , 2*kernel_radius+1, 2*kernel_radius+1]`.
    """
    if torch.is_grad_enabled():
        return torch.ops.lietorch.r2_morphological_kernel(
            finsler_params, kernel_radius, alpha
        )
    else:
        return torch.ops.lietorch.r2_morphological_kernel(
            finsler_params.detach(), kernel_radius, alpha
        )


def morphological_convolution_r2(
    input: torch.Tensor, kernel: torch.Tensor
) -> torch.Tensor:
    """
    Apply morphological convolution to each channel with the corresponding kernel.

    In pseudo-code where we take liberties with tensor indices we can write:
    $$
        output[b,c,y,x] = \inf_{(y', x') ∈ ℝ²} input[b,c,y+y',x+x'] + kernel[c,y',x'].
    $$

    Parameters
    ----------
    
    input: torch.Tensor
        Tensor of shape `[B,C,H,W]`

    kernel: torch.Tensor
        Tensor of shape `[C,kH,kW]`

    Returns
    ---------
    A Tensor of shape `[B,C,H,W]`
    """
    if torch.is_grad_enabled():
        return torch.ops.lietorch.r2_morphological_convolution(input, kernel)
    else:
        return torch.ops.lietorch.r2_morphological_convolution(
            input.detach(), kernel.detach()
        )


class MorphologicalConvolutionR2(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.r2.morphological_convolution_r2`. The **kernel** tensor is part of the module's state.

    Parameters
    ------------
    channels: int
        Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,H,W]`.

    kernel_size: Tuple[int, int]
        Size of the kernel, i.e. the `kH`, `kW` in `[C,kH,kW]`. Needs to be an odd number.
    """

    channels: int
    kernel_size: Tuple[int, int]
    kernel: torch.Tensor

    def __init__(self, channels: int, kernel_size: Tuple[int, int]) -> None:
        super(MorphologicalConvolutionR2, self).__init__()

        assert (
            kernel_size[0] % 2 == 1
            and kernel_size[1] % 2 == 1
            and kernel_size[0] > 0
            and kernel_size[1] > 1
        ), "kernel sizes need to be positive odd numbers"

        self.channels = channels
        self.kernel_size = kernel_size
        self.kernel = torch.nn.Parameter(torch.Tensor(channels, *kernel_size))

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(self.kernel, a=0.0, b=1.0)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return morphological_convolution_r2(input, self.kernel)


def fractional_dilation_r2(
    input: torch.Tensor, finsler_params: torch.Tensor, kernel_radius: int, alpha: float
) -> torch.Tensor:
    """
    Apply left invariant (translation equivariant in this case) dilation to the `input` based on the Finsler functions as given by `finsler_params`.

    Parameters
    ------------
    input: torch.Tensor
        Input tensor of shape `[B,C,H,W]`.
    
    finsler_params: torch.Tensor
        Finsler parameters in a tensor of shape `[C,K]`. The Finsler function is parametrized by the `K` parameters as:
        $$
            F_{C}(x,y) = \\sqrt{x^2+y^2} \\exp{\\left( - \\sum_{k=1}^K \\textrm{finsler_params}[C, k] \\cdot B_k(x,y) \\right)},
        $$
        where B_k is the k-th circular harmonic basis function.

    kernel_radius: int
        Size `[2*kernel_radius+1, 2*kernel_radius+1]` of the grid on which the kernel will be sampled.

    alpha: float
        Alpha parameter, must be >= 0.55 and <= 1.0 for stability.

    Returns
    --------
    A tensor of shape `[B,C,H,W]`
    """
    if torch.is_grad_enabled():
        return torch.ops.lietorch.r2_fractional_dilation(
            input, finsler_params, kernel_radius, alpha
        )
    else:
        return torch.ops.lietorch.r2_fractional_dilation(
            input.detach(), finsler_params.detach(), kernel_radius, alpha
        )


class FractionalDilationR2(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.r2.fractional_dilation_r2` where the **finsler_params** tensor is part of the module's state.

    Parameters
    ------------
    channels: int
        Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,H,W]`.

    finsler_order: int
        Orders of the circular harmonics used to construct the Finsler function, i.e. the kernel will be parametrized by this number of parameters.

    kernel_radius: int
        Size of the grid where the morphological kernel will be sampled, i.e. 2*kernel_radius+1 both in height and width.

    alpha: float
        Alpha parameter, has to be >= 0.55 and <= 1.0 for stability.
    """

    channels: int
    finsler_order: int
    kernel_radius: int
    alpha: float
    finsler_params: torch.Tensor

    def __init__(
        self, channels: int, kernel_radius: int, alpha: float, finsler_order: int
    ):
        super(FractionalDilationR2, self).__init__()

        assert channels > 0, "channels needs to be strictly positive"
        assert finsler_order > 0, "finsler_order needs to be strictly positive"
        assert kernel_radius >= 0, "kernel_radius needs to be positive"
        assert alpha >= 0.55 and alpha <= 1.0, "alpha needs to be >= 0.55 and <= 1.0"

        self.channels = channels
        self.finsler_order = finsler_order
        self.kernel_radius = kernel_radius
        self.alpha = alpha
        self.finsler_params = torch.nn.Parameter(torch.Tensor(channels, finsler_order))
        self._cached_kernel = None

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(self.finsler_params, a=-1.0, b=1.0)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        if self.training:
            self._cached_kernel = None
            return fractional_dilation_r2(
                input, self.finsler_params, self.kernel_radius, self.alpha
            )

        if self._cached_kernel is None:
            self._cached_kernel = morphological_kernel_r2(
                self.finsler_params.detach(), self.kernel_radius, self.alpha
            )

        return -morphological_convolution_r2(-input, self._cached_kernel)


def fractional_erosion_r2(
    input: torch.Tensor, finsler_params: torch.Tensor, kernel_radius: int, alpha: float
) -> torch.Tensor:
    """
    Apply left invariant (translation equivariant in this case) erosion to the `input` based on the Finsler functions as given by `finsler_params`.

    Parameters
    ------------
    input: torch.Tensor
        Input tensor of shape `[B,C,H,W]`.
    
    finsler_params: torch.Tensor
        Finsler parameters in a tensor of shape `[C,K]`. The Finsler function is parametrized by the `K` parameters as:
        $$
            F_{C}(x,y) = \\sqrt{x^2+y^2} \\exp{\\left( - \\sum_{k=1}^K \\textrm{finsler_params}[C, k] \\cdot B_k(x,y) \\right)},
        $$
        where B_k is the k-th circular harmonic basis function.

    kernel_radius: int
        Size `[2*kernel_radius+1, 2*kernel_radius+1]` of the grid on which the kernel will be sampled.

    alpha: float
        Alpha parameter, must be >= 0.55 and <= 1.0 for stability.

    Returns
    --------
    A tensor of shape `[B,C,H,W]`
    """
    if torch.is_grad_enabled():
        return torch.ops.lietorch.r2_fractional_erosion(
            input, finsler_params, kernel_radius, alpha
        )
    else:
        return torch.ops.lietorch.r2_fractional_erosion(
            input.detach(), finsler_params.detach(), kernel_radius, alpha
        )


class FractionalErosionR2(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.r2.fractional_erosion_r2` where the **finsler_params** tensor is part of the module's state.

    Parameters
    ------------
    channels: int
        Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,H,W]`.

    finsler_order: int
        Orders of the circular harmonics used to construct the Finsler function, i.e. the kernel will be parametrized by this number of parameters.

    kernel_radius: int
        Size of the grid where the morphological kernel will be sampled, i.e. 2*kernel_radius+1 both in height and width.

    alpha: float
        Alpha parameter, has to be >= 0.55 and <= 1.0 for stability.
    """

    channels: int
    finsler_order: int
    kernel_radius: int
    alpha: float
    finsler_params: torch.Tensor

    def __init__(
        self, channels: int, kernel_radius: int, alpha: float, finsler_order: int
    ):
        super(FractionalErosionR2, self).__init__()

        assert channels > 0, "channels needs to be strictly positive"
        assert finsler_order > 0, "finsler_order needs to be strictly positive"
        assert kernel_radius >= 0, "kernel_radius needs to be positive"
        assert alpha >= 0.55 and alpha <= 1.0, "alpha needs to be >= 0.55 and <= 1.0"

        self.channels = channels
        self.finsler_order = finsler_order
        self.kernel_radius = kernel_radius
        self.alpha = alpha
        self.finsler_params = torch.nn.Parameter(torch.Tensor(channels, finsler_order))
        self._cached_kernel = None

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(self.finsler_params, a=-1.0, b=1.0)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        if self.training:
            self._cached_kernel = None
            return fractional_erosion_r2(
                input, self.finsler_params, self.kernel_radius, self.alpha
            )

        if self._cached_kernel is None:
            self._cached_kernel = morphological_kernel_r2(
                self.finsler_params.detach(), self.kernel_radius, self.alpha
            )

        return morphological_convolution_r2(input, self._cached_kernel)


def linear_r2(input: torch.Tensor, weight: torch.Tensor) -> torch.Tensor:
    """
    Linear combinations of R2 tensors.

    Parameters
    ------------
    input: torch.Tensor
    Tensor of shape `[B,Cin,H,W]`.

    weight: torch.Tensor
    Tensor of shape `[Cin, Cout]`.

    Returns
    --------
    Tensor of shape `[B,Cout,H,W]`.
    """
    if torch.is_grad_enabled():
        return torch.ops.lietorch.r2_linear(input, weight)
    else:
        return torch.ops.lietorch.r2_linear(input.detach(), weight.detach())


class LinearR2(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.r2.linear_r2` where the **weight** tensor is part of the module's state.

    Parameters
    -----------
    in_channels: int
    Number of input channels.

    out_channels: int
    Number of output channels.
    """

    __constants__ = ["in_channels", "out_channels"]
    in_channels: int
    out_channels: int
    weight: torch.Tensor

    def __init__(self, in_channels: int, out_channels: int) -> None:
        super(LinearR2, self).__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.weight = torch.nn.Parameter(torch.Tensor(in_channels, out_channels))

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.kaiming_uniform_(self.weight, a=sqrt(5))

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return linear_r2(input, self.weight)


def convection_r2(input: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
    """
    Translation equivariant convection of R2 tensors.

    Parameters
    ------------
    input: torch.Tensor
    Tensor of shape `[B,C,H,W]`.

    c: torch.Tensor
    Tensor of shape `[C,2]`.

    Returns
    --------
    Tensor of shape `[B,C,H,W]`.
    """
    if torch.is_grad_enabled():
        return torch.ops.lietorch.r2_convection(input, c)
    else:
        return torch.ops.lietorch.r2_convection(input.detach(), c.detach())


class ConvectionR2(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.r2.convection_r2` where the **c** tensor is part of the module's state.

    Parameters
    -----------
    channels: int
    Number of input channels.
    """

    __constants__ = ["channels"]
    channels: int
    c: torch.Tensor

    def __init__(self, channels: int) -> None:
        super(ConvectionR2, self).__init__()

        self.channels = channels
        self.c = torch.nn.Parameter(torch.Tensor(channels, 2))

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.kaiming_uniform_(self.c, a=sqrt(5))

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return convection_r2(input, self.c)


class CDEPdeLayerR2(torch.nn.Module):
    """
        Full convection/dilation/erosion layer that includes batch normalization and linear combinations.
        Solves the PDE:
        $$
            u_t = -\\mathbf{c}u + \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_1} - \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_2},
        $$
        where the convection vector \(\\mathbf{c}\) and the Riemannian metrics \( \\mathcal{G}_1 \) and \( \\mathcal{G}_2 \) are the trainable parameters. Subsequently linear combinations are taken and batch normalization (`torch.nn.BatchNorm2d`) is applied.
    """

    __constants__ = [
        "in_channels",
        "out_channels",
        "kernel_size",
        "iterations",
        "alpha",
        "bn_momentum",
    ]

    in_channels: int
    """
        Number of input channels.
    """

    out_channels: int
    """
        Number of output channels.
    """

    finsler_order: int
    """
        Orders of the circular harmonics used to construct the Finsler function for the dilation and erosion kernels, i.e. the kernel will be parametrized by this number of parameters.
    """

    kernel_size: int
    """
        Size `[kH,kW]` of the grid on which the approximative kernel that solves the dilation/erosion will be sampled. Larger grid sizes increase computational load but also allow more dilation and erosion to take place.
    """

    iterations: int
    """
        How many times the split operators are applied, defaults to 1. Higher iterations improve how well the output approximates the PDE solution but increases computational load.
    """

    alpha: float
    """
        Alpha parameter to determine the dilation and erosion's fractionality. Must be at least *0.55* and at most *1.0*, defaults to the happy compromise of *0.65*.
    """

    convection: ConvectionR2
    dilation: FractionalDilationR2
    erosion: FractionalErosionR2
    linear: LinearR2
    batch_normalization: torch.nn.BatchNorm2d

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        iterations: int = 1,
        alpha: float = 0.65,
        finsler_order: int = 5,
    ) -> None:
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.finsler_order = finsler_order
        self.kernel_size = kernel_size
        self.iterations = iterations
        self.alpha = alpha

        self.convection = ConvectionR2(in_channels)
        self.dilation = FractionalDilationR2(
            in_channels, kernel_size, alpha, finsler_order
        )
        self.erosion = FractionalErosionR2(
            in_channels, kernel_size, alpha, finsler_order
        )
        self.linear = LinearR2(in_channels, out_channels)
        self.batch_normalization = torch.nn.BatchNorm2d(
            out_channels, track_running_stats=False
        )

        self.reset_parameters()

    def reset_parameters(self) -> None:
        self.convection.reset_parameters()
        self.dilation.reset_parameters()
        self.erosion.reset_parameters()
        self.linear.reset_parameters()
        self.batch_normalization.reset_parameters()

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        x = input
        for i in range(self.iterations):
            x = self.erosion(self.dilation(self.convection(x)))
        return self.batch_normalization(self.linear(x))


class DEPdeLayerR2(torch.nn.Module):
    """
        Full convection/dilation/erosion layer that includes batch normalization and linear combinations.
        Solves the PDE:
        $$
            u_t =  + \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_1} - \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_2},
        $$
        where the Riemannian metrics \( \\mathcal{G}_1 \) and \( \\mathcal{G}_2 \) are the trainable parameters. Subsequently linear combinations are taken and batch normalization (`torch.nn.BatchNorm2d`) is applied.
    """

    __constants__ = [
        "in_channels",
        "out_channels",
        "kernel_size",
        "iterations",
        "alpha",
        "bn_momentum",
    ]

    in_channels: int
    """
        Number of input channels.
    """

    out_channels: int
    """
        Number of output channels.
    """

    finsler_order: int
    """
        Orders of the circular harmonics used to construct the Finsler function for the dilation and erosion kernels, i.e. the kernel will be parametrized by this number of parameters.
    """

    kernel_size: int
    """
        Size `[kH,kW]` of the grid on which the approximative kernel that solves the dilation/erosion will be sampled. Larger grid sizes increase computational load but also allow more dilation and erosion to take place.
    """

    iterations: int
    """
        How many times the split operators are applied, defaults to 1. Higher iterations improve how well the output approximates the PDE solution but increases computational load.
    """

    alpha: float
    """
        Alpha parameter to determine the dilation and erosion's fractionality. Must be at least *0.55* and at most *1.0*, defaults to the happy compromise of *0.65*.
    """

    dilation: FractionalDilationR2
    erosion: FractionalErosionR2
    linear: LinearR2
    batch_normalization: torch.nn.BatchNorm2d

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        iterations: int = 1,
        alpha: float = 0.65,
        finsler_order: int = 5,
    ) -> None:
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.finsler_order = finsler_order
        self.kernel_size = kernel_size
        self.iterations = iterations
        self.alpha = alpha

        self.dilation = FractionalDilationR2(
            in_channels, kernel_size, alpha, finsler_order
        )
        self.erosion = FractionalErosionR2(
            in_channels, kernel_size, alpha, finsler_order
        )
        self.linear = LinearR2(in_channels, out_channels)
        self.batch_normalization = torch.nn.BatchNorm2d(
            out_channels, track_running_stats=False
        )

        self.reset_parameters()

    def reset_parameters(self) -> None:
        self.dilation.reset_parameters()
        self.erosion.reset_parameters()
        self.linear.reset_parameters()
        self.batch_normalization.reset_parameters()

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        x = input
        for i in range(self.iterations):
            x = self.erosion(self.dilation(x))

        return self.batch_normalization(self.linear(x))


class SpatialResampleR2(torch.nn.Module):
    """

    """

    __constants__ = []

    """

    """
    size: Tuple[int, int]
    scale_factor: float
    mode: str

    def __init__(
        self,
        size: Tuple[int, int] = None,
        scale_factor: float = None,
        mode: str = "nearest",
    ) -> None:
        super(SpatialResampleR2, self).__init__()
        if size is None and scale_factor is None:
            raise ValueError("size or scale_factor needs to be specified")

        if size is not None and scale_factor is not None:
            raise ValueError("size or scale_factor needs to be specified, not both")

        self.size = size
        self.scale_factor = scale_factor
        self.mode = mode

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        ors = input.shape[2]

        if self.scale_factor is not None:
            h = floor(input.shape[2] * self.scale_factor)
            w = floor(input.shape[3] * self.scale_factor)
        else:
            h = self.size[0]
            w = self.size[1]

        return F.interpolate(input, size=(h, w), mode=self.mode)
