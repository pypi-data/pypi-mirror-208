"""
    Functions and modules for M2 (i.e. 2D roto-translation equivariant) neural networks.
"""

import torch
import torch.nn.functional as F
from lietorch.padding import pad_reflect, pad_periodic
from math import pi, ceil, floor, sqrt
import lietorch.bspline
from typing import Optional, List, Tuple, Union


###
###
### Functional interface
###
###


def lift_m2_bspline(
    x, nodes, scales, weights, orientations=8, grid_size=None, spline_order=2
):
    """
        Lift 2 dimensional data to the 3 dimensional M2 domain with trainable kernels that are represented by (non-uniform) B-splines.

        Parameters
        ----------------
        x : torch.Tensor
            Input tensor of shape `[B, Cin, H, W]`.

        nodes : torch.Tensor
            Spline centers with shape `[Cout, Cin, Spl, 2]`.

        scales : torch.Tensor
            Spline scales with shape  `[Cout, Cin, Spl]`.

        weights : torch.Tensor
            Spline weights with shape `[Cout, Cin, Spl]`.

        orientations : int
            Number of orientations to output, defaults to 8.

        grid_size : None or int or (int, int)
            The size of the sampling grid to use to realize the B-spline kernel, this would equate to the kernel size (y_size, x_size) in a conventional spatial setting. The grid will always center on (0,0).
            
            When specifying a single int the kernel will be sampled on a grid of grid_size x grid_size.

            When specifying `None` (the default) the grid size will be infered from the coordinates given by `nodes` so that all nodes are included in the grid.

        spline_order : int
            Order of the B-splines used to realize the kernel, default to 2.

        Returns
        ---------
        A tensor of shape `[B, Cout, Or, H-grid_size[0]+1, W-grid_size[1]+1]`. Observe that if you do not specify `grid_size` the exact shape of the output will depend on `nodes` and is not known a priori, if a predictable output shape is required you will need to specify `grid_size`.
    """

    assert (
        len(x.shape) == 4
    ), f"Expecting x to have shape [B, Cin, H, W] but got {x.shape}."
    assert (
        len(nodes.shape) == 4 and nodes.shape[-1] == 2
    ), f"Expecting nodes to have shape [Cout, Cin, Spl, 2] but got {nodes.shape}."
    assert (
        len(scales.shape) == 3
    ), f"Expecting scales to have shape [Cout, Cin, Spl] but got {scales.shape}."
    assert (
        x.shape[1] == nodes.shape[1] == scales.shape[1] == weights.shape[1]
    ), f"Cout dimensions do not match."
    assert (
        nodes.shape[0] == scales.shape[0] == weights.shape[0]
    ), f"Cout dimensions do not match."
    assert (
        nodes.shape[2] == scales.shape[2] == weights.shape[2]
    ), f"Spline dimensions do not match."

    if type(grid_size) is int:
        y_size, x_size = grid_size, grid_size
    elif (
        type(grid_size) is tuple
        and len(grid_size) == 2
        and type(grid_size[0]) is type(grid_size[1]) is int
    ):
        y_size, x_size = grid_size
    elif grid_size is None:
        x_size = 2 * nodes[..., 0].abs().max().ceil().int().item() + 1
        y_size = 2 * nodes[..., 1].abs().max().ceil().int().item() + 1
    else:
        raise TypeError(f"Argument grid_size should be type None, int or (int, int).")

    grid_stack = _r2_rotated_cartesian_grid_stack(x_size, y_size, orientations).to(
        weights.device
    )

    return _lift_m2_grid_stack(x, nodes, scales, weights, grid_stack, spline_order)


def lift_m2_cartesian(x, weights, orientations=8, spline_order=2):
    """
        Lift 2 dimensional data to the 3 dimensional M2 domain with trainable kernels that are represented by uniform B-splines on a Cartesian grid.

        Parameters
        ----------------
        x : torch.Tensor
            Input tensor of shape `[B, Cin, H, W]`.

        weights : torch.Tensor
            Kernel tensor of shape `[Cout, Cin, KH, KW]`

        orientations : int
            Number of orientations (dimension `Or`) to output.

        spline_order : int
            Order of the B-splines used to realize the kernel.

        Returns
        ---------
        A tensor of shape `[B, Cout, Or, H-KH+1, W-KW+1]`
    """
    x_size = weights.shape[-1]
    y_size = weights.shape[-2]
    x_offset = float(x_size - 1) / 2.0
    y_offset = float(y_size - 1) / 2.0
    xs = torch.linspace(-x_offset, x_offset, x_size)
    ys = torch.linspace(-y_offset, y_offset, y_size)
    y_grid, x_grid = torch.meshgrid(ys, xs)

    weights = weights.reshape(*weights.shape[:-2], -1)

    nodes = torch.stack((y_grid, x_grid), dim=-1).reshape(-1, 2).to(weights.device)
    nodes, _ = torch.broadcast_tensors(nodes, weights[..., None])
    scales = torch.ones(weights.shape, dtype=torch.float32).to(weights.device)

    return lift_m2_bspline(
        x, nodes, scales, weights, orientations, (y_size, x_size), spline_order
    )


def reflection_pad_m2(x, padding):
    """
        Pad the M2 volume via reflections along the spatial dimensions.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape `[B, C, Or, H, W]`.

        padding : int
            Amount of padding on each side.

        Returns
        -------
        A tensor of shape 
        `[B, C, Or, H + 2*padding, W + 2*padding]`
    """
    output = pad_reflect(x, dim=-1, padding=padding)
    output = pad_reflect(output, dim=-2, padding=padding)
    return output


def conv_m2_bspline(x, nodes, scales, weights, grid_size=None, spline_order=2):
    """
        Apply group convolution in M2 with a B-spline kernel.
    """

    assert (
        len(x.shape) == 5
    ), f"Expecting x to have shape [B, Cin, Or, H, W] but got {x.shape}."
    assert (
        len(nodes.shape) == 4 and nodes.shape[-1] == 3
    ), f"Expecting nodes to have shape [Cout, Cin, Spl, 3] but got {nodes.shape}."
    assert (
        len(scales.shape) == 3
    ), f"Expecting scales to have shape [Cout, Cin, Spl] but got {scales.shape}."
    assert (
        x.shape[1] == nodes.shape[1] == scales.shape[1] == weights.shape[1]
    ), f"Cin dimensions do not match."
    assert (
        nodes.shape[0] == scales.shape[0] == weights.shape[0]
    ), f"Cout dimensions do not match."
    assert (
        nodes.shape[2] == scales.shape[2] == weights.shape[2]
    ), f"Spline dimensions do not match."

    if type(grid_size) is int:
        or_size, y_size, x_size = grid_size, grid_size, grid_size
    elif (
        type(grid_size) is tuple
        and len(grid_size) == 3
        and type(grid_size[0]) is type(grid_size[1]) is type(grid_size[2]) is int
    ):
        or_size, y_size, x_size = grid_size
    elif grid_size is None:
        x_size = 2 * nodes[..., 0].abs().max().ceil().int().item() + 1
        y_size = 2 * nodes[..., 1].abs().max().ceil().int().item() + 1
        or_size = 2 * nodes[..., 2].abs().max().ceil().int().item() + 1
    else:
        raise TypeError(
            f"Argument grid_size should be type None, int or (int, int, int)."
        )

    grid_stack = _m2_rotated_cartesian_grid_stack(
        x_size, y_size, or_size, orientations=x.shape[2]
    )

    return _conv_m2_grid_stack_conv3d(
        x, nodes, scales, weights, grid_stack, spline_order
    )


def conv_m2_cartesian(x, weights, spline_order=2):
    """
        Apply group convolution in M2 with a kernel on a Cartesian grid.

        Parameters
        ----------
        x : torch.Tensor
            Input of shape `[B, Cin, Or, H, W]`.

        weights : torch.Tensor
            Weights tensor of shape `[Cout, Cin, KOr, KH, KW]`.


        Returns
        -------
        Tensor of shape `[B, Cout, Or, H-KH+1, W-KW+1]`
    """
    cout, cin, kor, kh, kw = weights.shape[-3:]

    x_size = weights.shape[-1]
    y_size = weights.shape[-2]
    or_size = weights.shape[-3]
    x_offset = float(x_size - 1) / 2.0
    y_offset = float(y_size - 1) / 2.0
    or_offset = float(or_size - 1) / 2.0
    xs = torch.linspace(-x_offset, x_offset, x_size)
    ys = torch.linspace(-y_offset, y_offset, y_size)
    ors = torch.linspace(-or_offset, or_offset, or_size)
    or_grid, y_grid, x_grid = torch.meshgrid(ors, ys, xs)

    weights = weights.reshape(*weights.shape[:-3], -1)

    nodes = (
        torch.stack((or_grid, y_grid, x_grid), dim=-1).reshape(-1, 3).to(weights.device)
    )
    nodes, _ = torch.broadcast_tensors(nodes, weights[..., None])
    scales = torch.ones(weights.shape, dtype=torch.float32).to(weights.device)

    return conv_m2_bspline(
        x,
        nodes,
        scales,
        weights,
        grid_size=(or_size, y_size, x_size),
        spline_order=spline_order,
    )


def max_project_m2(x):
    """
        Applies a maximum projection over the orientation dimension.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape `[B, C, Or, H, W]`.

        Returns
        -------
        A tensor of shape `[B, C, H, W]`.
    """
    return torch.max(x, dim=2)[0]


def anisotropic_dilated_project_m2(x, longitudinal, lateral, alpha):
    """
         Applies a anisotropic dilated projection over the orientation dimension.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape `[B, C, Or, H, W]`.

        longitudinal : float
            longitudinal kernel size

        lateral : float
            lateral kernel size

        alpha : float > 1/2 and <= 1

        Returns
        -------
        A tensor of shape `[B, C, H, W]`.
    """
    return torch.ops.lietorch.m2_anisotropic_dilated_project(
        x, longitudinal, lateral, alpha, 1.0
    )


###
###
### Modular interface
###
###


class LiftM2Cartesian(torch.nn.Module):
    """
        Lift 2 dimensional data to the 3 dimensional M2 domain with trainable kernels that are represented by uniform B-splines on a Cartesian grid.

        Parameters
        ----------
        in_channels : int
            Number of input channels the module expects.

        out_channels : int
            Number of output channels the module will produce.

        orientations : int
            Number of orientations the module will produce.

        kernel_size : int
            Spatial size of the lifting kernel will be `(kernel_size, kernel_size)`.


        Shape
        -----
        Input :
            Tensor of shape `[Batch, Cout, Y, X]`.

        Output :
            Tensor of shape `[Batch,[Cout, orientations, Y, X]`
    """

    def __init__(
        self, in_channels, out_channels, orientations, kernel_size, spline_order=2
    ):
        super(LiftM2Cartesian, self).__init__()
        self._in_channels = in_channels
        self._out_channels = out_channels
        self._orientations = orientations
        self._kernel_size = kernel_size
        self._spline_order = spline_order

        # assert (
        #     orientations >= kernel_size
        # ), f"kernel_size ({kernel_size}) is required to be smaller or equal to orientations ({orientations})."

        offset = float(kernel_size - 1) / 2.0
        xs = torch.linspace(-offset, offset, kernel_size)
        y_grid, x_grid = torch.meshgrid(xs, xs)
        nodes = torch.stack([y_grid, x_grid], dim=-1).reshape(-1, 2)

        nodes = nodes.repeat(out_channels, in_channels, 1, 1)
        self.register_buffer("_nodes", nodes)

        scales = torch.ones_like(self._nodes[..., 0])
        self.register_buffer("_scales", scales)

        grid_stack = _r2_rotated_cartesian_grid_stack(
            kernel_size, kernel_size, orientations
        )
        self.register_buffer("_grid_stack", grid_stack)

        self._weights = torch.nn.Parameter(
            torch.empty(out_channels, in_channels, kernel_size ** 2)
        )

        self.reset_parameters()

    def reset_parameters(self):
        torch.nn.init.xavier_normal_(
            self._weights, gain=torch.nn.init.calculate_gain("relu")
        )

    @property
    def in_channels(self):
        return self._in_channels

    @property
    def out_channels(self):
        return self._out_channels

    @property
    def orientations(self):
        return self._orientations

    @property
    def kernel_size(self):
        return self._kernel_size

    @property
    def weights(self):
        return self._weights.view(
            *self._weights.shape[:-1], self._kernel_size, self._kernel_size
        )

    @weights.setter
    def weights(self, w):
        self._weights = torch.nn.Parameter(w.view(*w.shape[:-2], -1))

    def forward(self, x):
        return _lift_m2_grid_stack(
            x,
            self._buffers["_nodes"],
            self._buffers["_scales"],
            self._weights,
            self._buffers["_grid_stack"],
            self._spline_order,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self._in_channels}, {self._out_channels}, orientations={self._orientations}, kernel_size={self._kernel_size}, spline_order={self._spline_order})"


class ReflectionPadM2(torch.nn.Module):
    """
        Pad the M2 volume via reflections along the spatial dimensions.

        Parameters
        ----------
        padding : int
            The amount of padding to apply on all spatial sides.


        Shape
        -----
        Input :
            Tensor of shape `[Batch, Channel, Orientation, Y, X]`.

        Output :
            Tensor of shape
            `[Batch, Channel, Orientation, Y + 2*padding, X + 2*padding]`

    """

    def __init__(self, padding):
        super(ReflectionPadM2, self).__init__()
        self._padding = padding

    @property
    def padding(self):
        return self._padding

    def forward(self, x):
        return reflection_pad_m2(x, padding=self._padding)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._padding})"


class ConvM2Cartesian(torch.nn.Module):
    """

    """

    def __init__(
        self, in_channels, out_channels, orientations, kernel_size, spline_order=2
    ):
        super(ConvM2Cartesian, self).__init__()
        self._in_channels = in_channels
        self._out_channels = out_channels
        self._orientations = orientations
        self._kernel_size = kernel_size
        self._spline_order = spline_order

        assert (
            orientations >= kernel_size
        ), f"kernel_size ({kernel_size}) is required to be smaller or equal to orientations ({orientations})."

        offset = float(kernel_size - 1) / 2.0
        xs = torch.linspace(-offset, offset, kernel_size)
        or_grid, y_grid, x_grid = torch.meshgrid(xs, xs, xs)
        nodes = torch.stack([or_grid, y_grid, x_grid], dim=-1).reshape(-1, 3)

        nodes = nodes.repeat(out_channels, in_channels, 1, 1)
        self.register_buffer("_nodes", nodes)

        scales = torch.ones_like(self._nodes[..., 0])
        self.register_buffer("_scales", scales)

        grid_stack = _m2_rotated_cartesian_grid_stack(
            kernel_size, kernel_size, kernel_size, orientations
        )
        self.register_buffer("_grid_stack", grid_stack)

        self._weights = torch.nn.Parameter(
            torch.empty(out_channels, in_channels, kernel_size ** 3)
        )

        self.reset_parameters()

    def reset_parameters(self):
        torch.nn.init.xavier_normal_(
            self._weights, gain=torch.nn.init.calculate_gain("relu")
        )

    @property
    def in_channels(self):
        return self._in_channels

    @property
    def out_channels(self):
        return self._out_channels

    @property
    def orientations(self):
        return self._orientations

    @property
    def kernel_size(self):
        return self._kernel_size

    @property
    def weights(self):
        return self._weights.view(
            *self._weights.shape[:-1],
            self._kernel_size,
            self._kernel_size,
            self._kernel_size,
        )

    @weights.setter
    def weights(self, w):
        self._weights = torch.nn.Parameter(w.view(*w.shape[:-3], -1))

    def forward(self, x):
        return _conv_m2_grid_stack_conv3d(
            x,
            self._buffers["_nodes"],
            self._buffers["_scales"],
            self._weights,
            self._buffers["_grid_stack"],
            spline_order=self._spline_order,
        )

    def __repr__(self):
        f"{self.__class__.__name__}({self._in_channels}, {self._out_channels}, orientations={self._orientations}, kernel_size={self._kernel_size})"


class MaxProjectM2(torch.nn.Module):
    """
        Maximum projection over the orientation dimension. Input is required to have shape `[Batch, Channel, Orientation, Y, X]` which will produce output of the shape `[Batch, Channel, Y, X]`.
    """

    def __init__(self):
        super(MaxProjectM2, self).__init__()

    def forward(self, x):
        return max_project_m2(x)

    def __repr__(self):
        f"{self.__class__.__name__}()"


class AnisotropicDilatedProjectM2(torch.nn.Module):
    """
        Anisotropic Dilated Maximum projection over the orientation dimension. Input is required to have shape `[Batch, Channel, Orientation, Y, X]` which will produce output of the shape `[Batch, Channel, Y, X]`.
    """

    def __init__(self, longitudinal=5, lateral=2.5, alpha=2.0 / 3.0):
        super(AnisotropicDilatedProjectM2, self).__init__()
        self._longitudinal = longitudinal
        self._lateral = lateral
        self._alpha = alpha

    def forward(self, x):
        return anisotropic_dilated_project_m2(
            x, self._longitudinal, self._lateral, self._alpha
        )

    def __repr__(self):
        f"{self.__class__.__name__}\
            ({self._longitudinal}, {self._lateral}, {self._alpha})"


###
###
### Internal functions
###
###


def _r2_rotated_cartesian_grid_stack(
    x_size: int, y_size: int, orientations: int
) -> torch.Tensor:
    """
        Produce a set of rotated 2D Cartesian grids. 

        Returns
        -------
        Tensor of shape `[orientations, y_size, x_size, 2]`.
    """
    x_offset = float(x_size - 1) / 2.0
    y_offset = float(y_size - 1) / 2.0
    xs = torch.linspace(-x_offset, x_offset, x_size)
    ys = torch.linspace(-y_offset, y_offset, y_size)
    y_base_grid, x_base_grid = torch.meshgrid(ys, xs)

    angles = -torch.arange(0.0, 2 * pi, 2 * pi / orientations)[:, None, None]
    x_grid = x_base_grid * angles.cos() + y_base_grid * angles.sin()
    y_grid = -x_base_grid * angles.sin() + y_base_grid * angles.cos()

    return torch.stack((y_grid, x_grid), dim=-1)


def _m2_rotated_cartesian_grid_stack(
    x_size: int, y_size: int, or_size: int, orientations: int
) -> torch.Tensor:
    """
        Produce a set of rotated M2 Cartesian grids.

        Returns
        -------
        Tensor of shape `[orientations, or_size, y_size, x_size]`.
    """
    x_offset = float(x_size - 1) / 2.0
    y_offset = float(y_size - 1) / 2.0
    or_offset = float(or_size - 1) / 2.0
    xs = torch.linspace(-x_offset, x_offset, x_size)
    ys = torch.linspace(-y_offset, y_offset, y_size)
    ors = torch.linspace(-or_offset, or_offset, or_size)
    or_base_grid, y_base_grid, x_base_grid = torch.meshgrid(ors, ys, xs)

    angles = -torch.arange(0.0, 2 * pi, 2 * pi / orientations)[:, None, None, None]
    x_grid = x_base_grid * angles.cos() + y_base_grid * angles.sin()
    y_grid = -x_base_grid * angles.sin() + y_base_grid * angles.cos()
    or_grid = or_base_grid.expand_as(x_grid)

    return torch.stack((or_grid, y_grid, x_grid), dim=-1)


def _lift_m2_grid_stack(
    x: torch.Tensor,
    nodes: torch.Tensor,
    scales: torch.Tensor,
    weights: torch.Tensor,
    grid_stack: torch.Tensor,
    spline_order: int = 2,
) -> torch.Tensor:
    """
        Perform lifting by convolution with the B-spline kernel given by `(nodes,scales,weights)` sampled by the pre-computed `grid_stack`.
    """
    orientations = grid_stack.shape[0]
    kernel_stack = lietorch.bspline.sample(
        nodes, scales, weights, grid_stack, order=spline_order
    )
    kernel_stack = kernel_stack.transpose(1, 2)
    out_channels = kernel_stack.shape[0]
    kernel_stack = kernel_stack.reshape(-1, *kernel_stack.shape[2:])

    y = F.conv2d(x, kernel_stack)
    y = y.view(y.shape[0], out_channels, orientations, *y.shape[2:])

    return y


def _conv_m2_grid_stack_conv3d(
    x: torch.Tensor,
    nodes: torch.Tensor,
    scales: torch.Tensor,
    weights: torch.Tensor,
    grid_stack: torch.Tensor,
    spline_order: int = 2,
) -> torch.Tensor:
    """
        Perform M2 group convolution with the B-spline kernel given by `(nodes,scales,weights)` sampled by the pre-computed `grid_stack`. This backend relies on the `torch.nn.functional.conv3d` function.
    """
    orientations, kor, kh, kw, _ = grid_stack.shape
    out_shape = (
        x.shape[0],
        nodes.shape[0],
        x.shape[2],
        x.shape[3] - kh + 1,
        x.shape[4] - kw + 1,
    )
    out = torch.empty(out_shape, device=x.device)

    pad_bottom, pad_top = int(ceil((kor - 1) / 2)), int(floor((kor - 1) / 2))
    x = lietorch.padding.pad_periodic(x, dim=2, padding=(pad_bottom, pad_top))

    kernel_stack = lietorch.bspline.sample(
        nodes, scales, weights, grid_stack, order=spline_order
    )

    for i in range(orientations):
        out[:, :, i : i + 1, ...] = F.conv3d(
            x[:, :, i : i + kor, ...], kernel_stack[:, :, i, ...]
        )

    return out


###
###
### PDE Operators
###
###


def convection_m2(input: torch.Tensor, g0: torch.Tensor) -> torch.Tensor:
    """

       Apply convection to each channel of the **input** orientation score according to the corresponding group element specified in **g0**.
        

        Mathematically, convection of an initial condition \(U_0\) on \(\mathbb{M}_2\)  after a fixed amount of time T is solved by:
        $$
            U_{T}(p) = U_{0} \\left( g_p g_0^{-1}.p_0\\right)
        $$
        for a \(g_p\) so that \(g_p.p_0=p\) and particular choice of \( g_0 \). The element \( g_0 \) represented by the triple \( (x_0,y_0,\\theta_0) \) is what we are looking to train for each channel.

        In pseudo-code where we take liberties with tensor indices we can write:
        $$
            output[b,c,(\\theta,y,x)]=input[b,c,(\\theta,y,x) ⋅ g0[c]^{-1} ].
        $$
        


        Inputs
        ----------

        **input**: Tensor of shape `[B,C,Or,H,W]`


        **g0**: Tensor of shape `[C,3]`



        Returns
        -------
        A Tensor of shape `[B,C,Or,H,W]`

    """
    return torch.ops.lietorch.m2_convection(input, g0)


class ConvectionM2(torch.nn.Module):
    """
        Modular interface to `lietorch.nn.m2.convection_m2`. The **g0** tensor here is part of the module's state.

        Parameters
        ------------
        channels: int
            Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,Or,H,W]`.

        parameter_dtype: dtype
            Specifies which dtype is used by **g0** for coordinate calculations, currently supports `torch.float32` (the default) and `torch.float64`.
    """

    channels: int
    parameter_dtype: torch.dtype
    g0: torch.Tensor

    def __init__(
        self, channels: int, parameter_dtype: torch.dtype = torch.float32
    ) -> None:
        super(ConvectionM2, self).__init__()

        self.channels = channels
        self.parameter_dtype = parameter_dtype
        self.g0 = torch.nn.Parameter(torch.zeros(channels, 3, dtype=parameter_dtype))

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.constant_(self.g0, 0.0)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return convection_m2(input, self.g0)


def linear_convolution_m2(
    input: torch.Tensor, kernel: torch.Tensor
) -> torch.Tensor:
    """
        Apply linear convolution to each channel with the corresponding kernel.

        In pseudo-code where we take liberties with tensor indices we can write:
        $$
            output[b,c,θ,y,x] = \sum_{g ∈ SE(2)} input[b,c, g ⋅ (θ,y,x)] * kernel[c,g ⋅ (0,0,0)].
        $$
        This is implemented internally as the following equivalent formulation:
        $$
            output[b,c,θ,y,x] = \sum_{θ', y', x'} input[b,c,θ+θ',y+y',x+x']
            * kernel[c,θ', R_θ (y',x')].
        $$
        Meaning the input tensor is evaluated exactly on its grid points, the kernel is sampled using nearest-neighbour interpolation.

        Inputs
        --------
        
        **input**: Tensor of shape `[B,C,Or,H,W]`

        **kernel**: Tensor of shape `[C,kOr,kH,kW]`

        Returns
        ---------
        A Tensor of shape `[B,C,Or,H,W]`
    """
    return torch.ops.lietorch.m2_linear_convolution(input, kernel)

class LinearConvolutionM2(torch.nn.Module):
    """
        Modular interface to `lietorch.nn.m2.linear_convolution_m2`. The **kernel** tensor is part of the module's state.

        Parameters
        ------------
        channels: int
            Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,Or,H,W]`.

        kernel_size: Tuple[int, int, int]
            Size of the kernel, i.e. the `kOr`, `kH`, `kW` in `[C,kOr,kH,kW]`.
    """

    channels: int
    kernel_size: Tuple[int, int, int]
    kernel: torch.Tensor

    def __init__(self, channels: int, kernel_size: Tuple[int, int, int]) -> None:
        super(LinearConvolutionM2, self).__init__()

        self.channels = channels
        self.kernel_size = kernel_size
        self.kernel = torch.nn.Parameter(torch.Tensor(channels, *kernel_size))

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(self.kernel, a=-1.0, b=1.0)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return linear_convolution_m2(input, self.kernel)


def morphological_convolution_m2(
    input: torch.Tensor, kernel: torch.Tensor
) -> torch.Tensor:
    """
        Apply morphological convolution to each channel with the corresponding kernel.

        In pseudo-code where we take liberties with tensor indices we can write:
        $$
            output[b,c,θ,y,x] = \inf_{g ∈ SE(2)} input[b,c, g ⋅ (0,0,0)] + kernel[c, (θ,y,x)^{-1} ⋅ g].
        $$
        This is implemented internally as the following equivalent formulation:
        $$
            output[b,c,θ,y,x] = \inf_{θ', y', x'} input[b,c,θ',y',x']
            + kernel[c,θ'-θ, R_θ^{-1} (y',x')].
        $$
        Meaning the input tensor is evaluated exactly on its grid points, the kernel is sampled using nearest-neighbour interpolation.

        Inputs
        --------
        
        **input**: Tensor of shape `[B,C,Or,H,W]`

        **kernel**: Tensor of shape `[C,kOr,kH,kW]`

        Returns
        ---------
        A Tensor of shape `[B,C,Or,H,W]`
    """
    return torch.ops.lietorch.m2_morphological_convolution(input, kernel)


class MorphologicalConvolutionM2(torch.nn.Module):
    """
        Modular interface to `lietorch.nn.m2.morphological_convolution_m2`. The **kernel** tensor is part of the module's state.

        Parameters
        ------------
        channels: int
            Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,Or,H,W]`.

        kernel_size: Tuple[int, int, int]
            Size of the kernel, i.e. the `kOr`, `kH`, `kW` in `[C,kOr,kH,kW]`.
    """

    channels: int
    kernel_size: Tuple[int, int, int]
    kernel: torch.Tensor

    def __init__(self, channels: int, kernel_size: Tuple[int, int, int]) -> None:
        super(MorphologicalConvolutionM2, self).__init__()

        self.channels = channels
        self.kernel_size = kernel_size
        self.kernel = torch.nn.Parameter(torch.Tensor(channels, *kernel_size))

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(self.kernel, a=0.0, b=1.0)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return morphological_convolution_m2(input, self.kernel)


def fractional_dilation_m2(
    input: torch.Tensor,
    metric_params: torch.Tensor,
    kernel_size: Tuple[int, int, int],
    alpha: float = 0.65,
) -> torch.Tensor:
    """
    Apply left invariant dilation to the `input` based on the Riemannian metric as given by `metric_params`.

    Parameters
    ------------
    input: torch.Tensor
        Input tensor of shape `[B,C,Or,H,W]`.
    
    metric_params: torch.Tensor
        Riemannian metric parameters in a tensor of shape `[C,3]`, each triple contains the parameters `[dMain,dLat,dAng]`, note the order is chosen to match the index order.

    kernel_size: Tuple[int, int, int]
        Size `[kOr,kH,kW]` of the grid on which the kernel will be sampled.

    alpha: float
        Alpha parameter, must be >= 0.55 and <= 1.0 for stability.

    Returns
    --------
    A tensor of shape `[B,C,Or,H,W]`
    """
    return torch.ops.lietorch.m2_fractional_dilation(
        input, metric_params, kernel_size, alpha
    )

class FractionalDilationM2(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.m2.fractional_dilation_m2` where the **metric_params** tensor is part of the module's state.

    Parameters
    ------------
    channels: int
        Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,Or,H,W]`.

    kernel_size: Tuple[int, int, int]
        Size of the grid where the morphological kernel will be sampled, i.e. the `kOr`, `kH`, `kW` in `[C,kOr,kH,kW]`.

    alpha: float
        Alpha parameter has to be >= 0.55 and <= 1.0 for stability.
    """

    channels: int
    metric_params: torch.Tensor
    kernel_size: Tuple[int, int, int]
    alpha: float

    def __init__(
        self, channels: int, kernel_size: Tuple[int, int, int], alpha: float = 0.65
    ) -> None:
        super(FractionalDilationM2, self).__init__()

        self.channels = channels
        self.kernel_size = kernel_size
        self.metric_params = torch.nn.Parameter(torch.Tensor(channels, 3))
        if alpha < 0.55 or alpha > 1.0:
            raise ValueError("alpha should be >= 0.55 and <= 1.0")
        self.alpha = alpha

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(
            self.metric_params,
            a=1.4 / max(self.kernel_size),
            b=0.7 * min(self.kernel_size),
        )

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return fractional_dilation_m2(
            input, self.metric_params, self.kernel_size, self.alpha
        )

def fractional_dilation_m2_nondiag(
    input: torch.Tensor,
    metric_params: torch.Tensor,
    kernel_size: Tuple[int, int, int],
    alpha: float = 0.65,
) -> torch.Tensor:
    """
    Apply left invariant dilation to the `input` based on the Riemannian metric as given by `metric_params`.

    Parameters
    ------------
    input: torch.Tensor
        Input tensor of shape `[B,C,Or,H,W]`.
    
    metric_params: torch.Tensor
        Riemannian metric parameters in a tensor of shape `[C,3,3]`.

    kernel_size: Tuple[int, int, int]
        Size `[kOr,kH,kW]` of the grid on which the kernel will be sampled.

    alpha: float
        Alpha parameter, must be >= 0.55 and <= 1.0 for stability.

    Returns
    --------
    A tensor of shape `[B,C,Or,H,W]`
    """
    return torch.ops.lietorch.m2_fractional_dilation_nondiag(
        input, metric_params, kernel_size, alpha
    )

class FractionalDilationM2NonDiag(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.m2.fractional_dilation_m2` where the **metric_params** tensor is part of the module's state.

    Parameters
    ------------
    channels: int
        Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,Or,H,W]`.

    kernel_size: Tuple[int, int, int]
        Size of the grid where the morphological kernel will be sampled, i.e. the `kOr`, `kH`, `kW` in `[C,kOr,kH,kW]`.

    alpha: float
        Alpha parameter has to be >= 0.55 and <= 1.0 for stability.
    """

    channels: int
    metric_params: torch.Tensor
    kernel_size: Tuple[int, int, int]
    alpha: float

    def __init__(
        self, channels: int, kernel_size: Tuple[int, int, int], alpha: float = 0.65
    ) -> None:
        super(FractionalDilationM2NonDiag, self).__init__()

        self.channels = channels
        self.kernel_size = kernel_size
        self.metric_params = torch.nn.Parameter(torch.Tensor(channels, 3, 3))
        if alpha < 0.55 or alpha > 1.0:
            raise ValueError("alpha should be >= 0.55 and <= 1.0")
        self.alpha = alpha

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(
            self.metric_params,
            a=1.4 / max(self.kernel_size),
            b=0.7 * min(self.kernel_size),
        )

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return fractional_dilation_m2_nondiag(
            input, self.metric_params, self.kernel_size, self.alpha
        )

def fractional_erosion_m2(
    input: torch.Tensor,
    metric_params: torch.Tensor,
    kernel_size: Tuple[int, int, int],
    alpha: float = 0.65,
) -> torch.Tensor:
    """
    Apply left invariant erosion to the `input` based on the Riemannian metric as given by `metric_params`.

    Parameters
    ------------
    input: torch.Tensor
        Input tensor of shape `[B,C,Or,H,W]`.
    
    metric_params: torch.Tensor
        Riemannian metric parameters in a tensor of shape `[C,3]`, each triple contains the parameters `[dMain,dLat,dAng]`, note the order is chosen to match the index order.

    kernel_size: Tuple[int, int, int]
        Size `[kOr,kH,kW]` of the grid on which the kernel will be sampled.

    alpha: float
        Alpha parameter, must be >= 0.55 and <= 1.0 for stability.

    Returns
    --------
    A tensor of shape `[B,C,Or,H,W]`
    """
    return torch.ops.lietorch.m2_fractional_erosion(
        input, metric_params, kernel_size, alpha
    )


class FractionalErosionM2(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.m2.fractional_erosion_m2` where the **metric_params** tensor is part of the module's state.

    Parameters
    ------------
    channels: int
        Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,Or,H,W]`.

    kernel_size: Tuple[int, int, int]
        Size of the grid where the morphological kernel will be sampled, i.e. the `kOr`, `kH`, `kW` in `[C,kOr,kH,kW]`.

    alpha: float
        Alpha parameter has to be >= 0.55 and <= 1.0 for stability.
    """

    channels: int
    metric_params: torch.Tensor
    kernel_size: Tuple[int, int, int]
    alpha: float

    def __init__(
        self, channels: int, kernel_size: Tuple[int, int, int], alpha: float = 0.65
    ) -> None:
        super(FractionalErosionM2, self).__init__()

        self.channels = channels
        self.kernel_size = kernel_size
        self.metric_params = torch.nn.Parameter(torch.Tensor(channels, 3))
        if alpha < 0.55 or alpha > 1.0:
            raise ValueError("alpha should be >= 0.55 and <= 1.0")
        self.alpha = alpha

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(
            self.metric_params,
            a=1.4 / max(self.kernel_size),
            b=0.7 * min(self.kernel_size),
        )

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return fractional_erosion_m2(
            input, self.metric_params, self.kernel_size, self.alpha
        )

def fractional_erosion_m2_nondiag(
    input: torch.Tensor,
    metric_params: torch.Tensor,
    kernel_size: Tuple[int, int, int],
    alpha: float = 0.65,
) -> torch.Tensor:
    """
    Apply left invariant erosion to the `input` based on the Riemannian metric as given by `metric_params`.

    Parameters
    ------------
    input: torch.Tensor
        Input tensor of shape `[B,C,Or,H,W]`.
    
    metric_params: torch.Tensor
        Riemannian metric parameters in a tensor of shape `[C,3,3]`, each triple contains the parameters `[dMain,dLat,dAng]`, note the order is chosen to match the index order.

    kernel_size: Tuple[int, int, int]
        Size `[kOr,kH,kW]` of the grid on which the kernel will be sampled.

    alpha: float
        Alpha parameter, must be >= 0.55 and <= 1.0 for stability.

    Returns
    --------
    A tensor of shape `[B,C,Or,H,W]`
    """
    return torch.ops.lietorch.m2_fractional_erosion_nondiag(
        input, metric_params, kernel_size, alpha
    )

class FractionalErosionM2NonDiag(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.m2.fractional_erosion_m2` where the **metric_params** tensor is part of the module's state.

    Parameters
    ------------
    channels: int
        Number of channels the input tensor is expected to have, i.e. the `C` in `[B,C,Or,H,W]`.

    kernel_size: Tuple[int, int, int]
        Size of the grid where the morphological kernel will be sampled, i.e. the `kOr`, `kH`, `kW` in `[C,kOr,kH,kW]`.

    alpha: float
        Alpha parameter has to be >= 0.55 and <= 1.0 for stability.
    """

    channels: int
    metric_params: torch.Tensor
    kernel_size: Tuple[int, int, int]
    alpha: float

    def __init__(
        self, channels: int, kernel_size: Tuple[int, int, int], alpha: float = 0.65
    ) -> None:
        super(FractionalErosionM2NonDiag, self).__init__()

        self.channels = channels
        self.kernel_size = kernel_size
        self.metric_params = torch.nn.Parameter(torch.Tensor(channels, 3, 3))
        if alpha < 0.55 or alpha > 1.0:
            raise ValueError("alpha should be >= 0.55 and <= 1.0")
        self.alpha = alpha

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.uniform_(
            self.metric_params,
            a=1.4 / max(self.kernel_size),
            b=0.7 * min(self.kernel_size),
        )

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return fractional_erosion_m2_nondiag(
            input, self.metric_params, self.kernel_size, self.alpha
        )

def linear_m2(input: torch.Tensor, weight: torch.Tensor) -> torch.Tensor:
    """
    Linear combinations of M2 tensors.

    Parameters
    ------------
    input: torch.Tensor
    Tensor of shape `[B,Cin,Or,H,W]`.

    weight: torch.Tensor
    Tensor of shape `[Cin, Cout]`.

    Returns
    --------
    Tensor of shape `[B,Cout,Or,H,W]`.

    """
    return torch.ops.lietorch.m2_linear(input, weight)


class LinearM2(torch.nn.Module):
    """
    Modular interface to `lietorch.nn.m2.linear_m2` where the **weight** tensor is part of the module's state.

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
        super(LinearM2, self).__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.weight = torch.nn.Parameter(torch.Tensor(in_channels, out_channels))

        self.reset_parameters()

    def reset_parameters(self) -> None:
        torch.nn.init.kaiming_uniform_(self.weight, a=sqrt(5))

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return linear_m2(input, self.weight)


class ConvectionDilationPdeM2(torch.nn.Module):
    """
    Convection dilation PDE module, gives an approximative solution to the evolution PDE:
    $$
        u_t = -\\mathbf{c}u + \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}}
    $$
    where the inputs are the initial conditions and the ouputs the solutions at a fixed time. The convection vector \( \\mathbf{c} \) (3 parameters per channel) and Riemannian metric \( \\mathcal{G} \) (3 parameters per channel) are the trainable parameters.
    """

    __constants__ = [
        "channels",
        "kernel_size",
        "iterations",
        "alpha_dilation",
    ]
    channels: int
    """
        Number of channels
    """

    kernel_size: Tuple[int, int, int]
    """
        Size `[kOr,kH,kW]` of the grid on which the approximative kernel that solves the dilation will be sampled. Larger grid sizes increase computational load but also allow more dilation to take place.
    """

    iterations: int
    """
        How many times the split operators are applied, defaults to 1. Higher iterations improve how well the output approximates the PDE solution but increases computational load.
    """

    alpha_dilation: float
    """
        Alpha parameter to determine the dilation's fractionality. Must be at least *0.55* and at most *1.0*, defaults to the happy medium of *0.65*.
    """

    convection: ConvectionM2
    dilation: FractionalDilationM2

    def __init__(
        self,
        channels: int,
        kernel_size: Tuple[int, int, int],
        alpha_dilation: float = 0.65,
        iterations: int = 1,
    ) -> None:
        super(ConvectionDilationPdeM2, self).__init__()

        self.channels = channels
        self.kernel_size = kernel_size
        self.alpha_dilation = alpha_dilation
        self.iterations = iterations

        self.convection = ConvectionM2(channels)
        self.dilation = FractionalDilationM2(channels, kernel_size, alpha_dilation)

        self.reset_parameters()

    def reset_parameters(self) -> None:
        self.convection.reset_parameters()
        self.dilation.reset_parameters()

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        out = input
        for i in range(self.iterations):
            out = self.dilation(self.convection(out))

        return out


class ConvectionErosionPdeM2(torch.nn.Module):
    """
    Convection erosion PDE module, gives an approximative solution to the evolution PDE:
    $$
        u_t = -\\mathbf{c}u - \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}}
    $$
    where the inputs are the initial conditions and the ouputs the solutions at a fixed time. The convection vector \( \\mathbf{c} \) (3 parameters per channel) and Riemannian metric \( \\mathcal{G} \) (3 parameters per channel) are the trainable parameters.
    """

    __constants__ = [
        "channels",
        "kernel_size",
        "iterations",
        "alpha_erosion",
    ]

    channels: int
    """
        Number of channels
    """

    kernel_size: Tuple[int, int, int]
    """
        Size `[kOr,kH,kW]` of the grid on which the approximative kernel that solves the erosion will be sampled. Larger grid sizes increase computational load but also allow more erosion to take place.
    """

    iterations: int
    """
        How many times the split operators are applied, defaults to 1. Higher iterations improve how well the output approximates the PDE solution but increases computational load.
    """

    alpha_erosion: float
    """
        Alpha parameter to determine the erosion's fractionality. Must be at least *0.55* and at most *1.0*, defaults to the happy medium of *0.65*.
    """

    convection: ConvectionM2
    erosion: FractionalErosionM2

    def __init__(
        self,
        channels: int,
        kernel_size: Tuple[int, int, int],
        alpha_erosion: float = 0.65,
        iterations: int = 1,
    ) -> None:
        super(ConvectionErosionPdeM2, self).__init__()

        self.channels = channels
        self.kernel_size = kernel_size
        self.alpha_erosion = alpha_erosion
        self.iterations = iterations

        self.convection = ConvectionM2(channels)
        self.erosion = FractionalErosionM2(channels, kernel_size, alpha_erosion)

        self.reset_parameters()

    def reset_parameters(self) -> None:
        self.convection.reset_parameters()
        self.erosion.reset_parameters()

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        out = input
        for i in range(self.iterations):
            out = self.erosion(self.convection(out))

        return out


class CDEPdeLayerM2(torch.nn.Module):
    """
        Full convection/dilation/erosion layer that includes batch normalization and linear combinations.
        Solves the PDE:
        $$
            u_t = -\\mathbf{c}u + \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_1} - \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_2},
        $$
        where the convection vector \(\\mathbf{c}\) and the Riemannian metrics \( \\mathcal{G}_1 \) and \( \\mathcal{G}_2 \) are the trainable parameters. Subsequently linear combinations are taken and batch normalization (`torch.nn.BatchNorm3d`) is applied.
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

    kernel_size: Tuple[int, int, int]
    """
        Size `[kOr,kH,kW]` of the grid on which the approximative kernel that solves the dilation/erosion will be sampled. Larger grid sizes increase computational load but also allow more dilation and erosion to take place.
    """

    iterations: int
    """
        How many times the split operators are applied, defaults to 1. Higher iterations improve how well the output approximates the PDE solution but increases computational load.
    """

    alpha: float
    """
        Alpha parameter to determine the dilation and erosion's fractionality. Must be at least *0.55* and at most *1.0*, defaults to the happy medium of *0.65*.
    """

    convection: ConvectionM2
    dilation: FractionalDilationM2
    erosion: FractionalErosionM2
    linear: LinearM2
    batch_normalization: torch.nn.BatchNorm3d

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: Tuple[int, int, int],
        iterations: int = 1,
        alpha: float = 0.65,
    ) -> None:
        super(CDEPdeLayerM2, self).__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.iterations = iterations
        self.alpha = alpha

        self.convection = ConvectionM2(in_channels)
        self.dilation = FractionalDilationM2(in_channels, kernel_size, alpha)
        self.erosion = FractionalErosionM2(in_channels, kernel_size, alpha)
        self.linear = LinearM2(in_channels, out_channels)
        self.batch_normalization = torch.nn.BatchNorm3d(
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

class CDEPdeLayerM2NonDiag(torch.nn.Module):
    """
        Full convection/dilation/erosion layer that includes batch normalization and linear combinations.
        Solves the PDE:
        $$
            u_t = -\\mathbf{c}u + \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_1} - \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_2},
        $$
        where the convection vector \(\\mathbf{c}\) and the Riemannian metrics \( \\mathcal{G}_1 \) and \( \\mathcal{G}_2 \) are the trainable parameters. 
        Subsequently linear combinations are taken and batch normalization (`torch.nn.BatchNorm3d`) is applied.
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

    kernel_size: Tuple[int, int, int]
    """
        Size `[kOr,kH,kW]` of the grid on which the approximative kernel that solves the dilation/erosion will be sampled. Larger grid sizes increase computational load but also allow more dilation and erosion to take place.
    """

    iterations: int
    """
        How many times the split operators are applied, defaults to 1. Higher iterations improve how well the output approximates the PDE solution but increases computational load.
    """

    alpha: float
    """
        Alpha parameter to determine the dilation and erosion's fractionality. Must be at least *0.55* and at most *1.0*, defaults to the happy medium of *0.65*.
    """

    convection: ConvectionM2
    dilation: FractionalDilationM2NonDiag
    erosion: FractionalErosionM2NonDiag
    linear: LinearM2
    batch_normalization: torch.nn.BatchNorm3d

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: Tuple[int, int, int],
        iterations: int = 1,
        alpha: float = 0.65,
    ) -> None:
        super(CDEPdeLayerM2NonDiag, self).__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.iterations = iterations
        self.alpha = alpha

        self.convection = ConvectionM2(in_channels)
        self.dilation = FractionalDilationM2NonDiag(in_channels, kernel_size, alpha)
        self.erosion = FractionalErosionM2NonDiag(in_channels, kernel_size, alpha)
        self.linear = LinearM2(in_channels, out_channels)
        self.batch_normalization = torch.nn.BatchNorm3d(
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

class DEPdeLayerM2(torch.nn.Module):
    """
        Full dilation/erosion layer that includes batch normalization and linear combinations.
        Solves the PDE:
        $$
            u_t =  \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_1} - \\left\\| \\nabla u \\right\\|^{2\\alpha}_{\\mathcal{G}_2},
        $$
        where the Riemannian metrics \( \\mathcal{G}_1 \) and \( \\mathcal{G}_2 \) are the trainable parameters. Subsequently linear combinations are taken and batch normalization (`torch.nn.BatchNorm3d`) is applied.
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

    kernel_size: Tuple[int, int, int]
    """
        Size `[kOr,kH,kW]` of the grid on which the approximative kernel that solves the dilation/erosion will be sampled. Larger grid sizes increase computational load but also allow more dilation and erosion to take place.
    """

    iterations: int
    """
        How many times the split operators are applied, defaults to 1. Higher iterations improve how well the output approximates the PDE solution but increases computational load.
    """

    alpha: float
    """
        Alpha parameter to determine the dilation and erosion's fractionality. Must be at least *0.55* and at most *1.0*, defaults to the happy medium of *0.65*.
    """

    dilation: FractionalDilationM2
    erosion: FractionalErosionM2
    linear: LinearM2
    batch_normalization: torch.nn.BatchNorm3d

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: Tuple[int, int, int],
        iterations: int = 1,
        alpha: float = 0.65,
    ) -> None:
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.iterations = iterations
        self.alpha = alpha

        self.dilation = FractionalDilationM2(in_channels, kernel_size, alpha)
        self.erosion = FractionalErosionM2(in_channels, kernel_size, alpha)
        self.linear = LinearM2(in_channels, out_channels)
        self.batch_normalization = torch.nn.BatchNorm3d(
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


class SpatialResampleM2(torch.nn.Module):
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
        super(SpatialResampleM2, self).__init__()
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
            h = floor(input.shape[3] * self.scale_factor)
            w = floor(input.shape[4] * self.scale_factor)
        else:
            h = self.size[0]
            w = self.size[1]

        return F.interpolate(input, size=(ors, h, w), mode=self.mode)

