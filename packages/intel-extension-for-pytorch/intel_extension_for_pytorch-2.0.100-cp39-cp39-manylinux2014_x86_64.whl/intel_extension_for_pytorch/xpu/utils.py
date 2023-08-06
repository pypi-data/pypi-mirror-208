import torch
from .. import _C
from enum import Enum
from .. import frontend
import intel_extension_for_pytorch  # noqa
from enum import IntEnum
import intel_extension_for_pytorch._C as core

from ._utils import _dummy_type

if not hasattr(core, 'XPUBackend'):
    # Define dummy base Enum classes
    core.__dict__['XPUBackend'] = _dummy_type('XPUBackend')
    setattr(core.XPUBackend, 'GPU', 0)
    setattr(core.XPUBackend, 'CPU', 1)
    setattr(core.XPUBackend, 'AUTO', 2)

def to_channels_last_1d(t):
    if isinstance(t, torch.nn.Module):
        for m in t.modules():
            for param in m.parameters():
                if isinstance(m, (torch.nn.Conv1d, torch.nn.BatchNorm1d, torch.nn.MaxPool1d)):
                    if 3 == param.data.dim():
                        if 1 == param.data.size(0):
                            param.data = param.data.transpose(1, -1).contiguous().transpose(1, -1)
                        elif 1 == param.data.size(1):
                            param.data = param.data.as_strided(
                                param.data.size(), (param.data.size(1) * param.data.size(-1), 1, param.data.size(1)))
                        else:
                            param.data = param.data.view(
                                param.data.size(0), param.data.size(1), 1, param.data.size(2))
                            param.data = param.data.to(
                                memory_format=torch.channels_last)
                            param.data = param.data.view(
                                param.data.size(0), param.data.size(1), param.data.size(3))
        return t

    if 3 == t.dim():
        if 1 == t.size(0):
            t = t.transpose(1, -1).contiguous().transpose(1, -1)
        elif 1 == t.size(1):
            t = t.as_strided(t.size(), (t.size(1) * t.size(-1), 1, t.size(1)))
        else:
            t = t.view(t.size(0), t.size(1), 1, t.size(2))
            t = t.to(memory_format=torch.channels_last)
            t = t.view(t.size(0), t.size(1), t.size(3))
    return t


def is_contiguous_channels_last_1d(input):
    if 3 != input.dim():
        return False

    tmpTen = input.view(input.size(0), input.size(1), 1, input.size(2))
    if tmpTen.is_contiguous(memory_format=torch.channels_last):
        return True
    else:
        return False


def has_onemkl():
    return _C._is_onemkl_enabled()


def has_channels_last_1d():
    return _C._is_channels_last_1d_enabled()

def has_fp64_dtype(device: int = -1) -> bool:
    r"""Returns a bool indicating if the current XPU device supports dtype float64"""
    return _C._get_device_properties(device).support_fp64


# Basic OnOff
class OnOff():
    def __init__(self, checker, enable, disable):
        self._init_status = checker()
        self._enabled = True
        self._disabled = False
        self._enable_fn = enable
        self._disable_fn = disable

    def __enter__(self):
        if self._init_status == self._disabled:
            self._enable_fn()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._init_status == self._disabled:
            self._disable_fn()
        return False


class EnumBase(Enum):
    @classmethod
    def convert(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, str) and value.isdecimal():
            value = int(value)
        if isinstance(value, int) and cls.has_value(value):
            return cls(value)
        raise RuntimeError("Unexpected {} value {}!".format(cls, value))

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def get_value(cls, get_func):
        return cls(get_func())

    @classmethod
    def set_value(cls, set_func, value):
        return set_func(cls.convert(value).value)


# Verbose Level
class VerbLevel(EnumBase):
    OFF = 0
    ON = 1


def get_verbose_level():
    return VerbLevel.get_value(_C._get_verbose_level)


def set_verbose_level(level):
    VerbLevel.set_value(_C._set_verbose_level, level)


# oneDNN Verbose
class OnednnVerbLevel(EnumBase):
    OFF = 0
    ON = 1
    ON_DETAIL = 2


def set_onednn_verbose(level):
    st = OnednnVerbLevel.set_value(_C._set_onednn_verbose, level)
    assert bool(st), "WARNING: Failed to turn on oneDNN verbose!"


class onednn_verbose(object):
    def __init__(self, level):
        self.level = OnednnVerbLevel.convert(level)

    def __enter__(self):
        if self.level != OnednnVerbLevel.OFF:
            set_onednn_verbose(self.level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_onednn_verbose(OnednnVerbLevel.OFF)
        return False


# oneMKL Verbose
class OnemklVerbLevel(EnumBase):
    OFF = 0
    ON = 1
    ON_SYNC = 2


def set_onemkl_verbose(level):
    st = OnemklVerbLevel.set_value(_C._set_onemkl_verbose, level)
    assert bool(st), "WARNING: Failed to turn on oneMKL verbose!"


class onemkl_verbose(object):
    def __init__(self, level):
        self.level = OnemklVerbLevel.convert(level)

    def __enter__(self):
        if self.level != OnemklVerbLevel.OFF:
            set_onemkl_verbose(self.level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_onemkl_verbose(OnemklVerbLevel.OFF)
        return False


def optimize(model, dtype=None, optimizer=None, level="O1",
             inplace=False, conv_bn_folding=None, linear_bn_folding=None,
             weights_prepack=None, replace_dropout_with_identity=None,
             optimize_lstm=None, split_master_weight_for_bf16=None,
             fuse_update_step=None, auto_kernel_selection=None,
             sample_input=None, graph_mode=None):
    r"""
    torch.xpu.optimize is an alternative of optimize API in Intel® Extension for
    PyTorch*, to provide identical usage for XPU device only. The motivation of
    adding this alias is to unify the coding style in user scripts base on torch.xpu
    modular.

    TODO: When finish merge frontend code, add other aurgments describtion here.
    Args (Specific default values for XPU device):
        inplace (bool): Default set false to save valuable XPU device memory.
        weights_prepack (bool): Disabled for XPU device.
        sample_input (tuple or torch.Tensor): Disabled for XPU device.

    Examples:
        >>> # bfloat16 inference case.
        >>> model = ...
        >>> model.load_state_dict(torch.load(PATH))
        >>> model.eval()
        >>> optimized_model = torch.xpu.optimize(model, dtype=torch.bfloat16)
        >>> # running evaluation step.
        >>> # bfloat16 training case.
        >>> optimizer = ...
        >>> model.train()
        >>> optimized_model, optimized_optimizer = torch.xpu.optimize(model, dtype=torch.bfloat16, optimizer=optimizer)
        >>> # running training step.
    """
    return frontend.optimize(model, dtype, optimizer, level,
                             inplace, conv_bn_folding, linear_bn_folding,
                             weights_prepack, replace_dropout_with_identity,
                             optimize_lstm, split_master_weight_for_bf16,
                             fuse_update_step, auto_kernel_selection,
                             sample_input, graph_mode)


class FP32MathMode(EnumBase):
    FP32 = int(core.FP32MathMode.FP32)
    TF32 = int(core.FP32MathMode.TF32)
    BF32 = int(core.FP32MathMode.BF32)


def get_fp32_math_mode():
    return FP32MathMode.get_value(core._get_fp32_math_mode)


def set_fp32_math_mode(mode):
    st = FP32MathMode.set_value(core._set_fp32_math_mode, mode)
    assert bool(st), "WARNING: Failed to set FP32 math mode!"


class fp32_math_mode(object):
    def __init__(self, mode):
        self.mode = FP32MathMode.convert(mode)

    def __enter__(self):
        current_math_mode = get_fp32_math_mode()
        if self.mode != current_math_mode:
            set_fp32_math_mode(self.mode)
            self.mode = current_math_mode
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_fp32_math_mode(self.mode)
        return False


# Basic OnOff
class OnOff():
    def __init__(self, checker, enable, disable):
        self._init_status = checker()
        self._enabled = True
        self._disabled = False
        self._enable_fn = enable
        self._disable_fn = disable

    def __enter__(self):
        if self._init_status == self._disabled:
            self._enable_fn()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._init_status == self._disabled:
            self._disable_fn()
        return False


# Sync Execution Mode
def using_sync_mode():
    return _C._is_sync_mode()


def enable_sync_mode():
    _C._enable_sync_mode()


def disable_sync_mode():
    _C._disable_sync_mode()


class sync_mode(OnOff):
    def __init__(self):
        super().__init__(using_sync_mode, enable_sync_mode, disable_sync_mode)


# Tile Partition As Device
def using_tile_as_device():
    return _C._is_tile_as_device_enabled()

# Only work before lazy init
def enable_tile_as_device():
    _C._enable_tile_as_device()


# Only work before lazy init
def disable_tile_as_device():
    _C._disable_tile_as_device()


# XPU Backend
# NOTE: XPU Backend is not available yet.
class Backend(EnumBase):
    GPU = int(_C.XPUBackend.GPU)
    CPU = int(_C.XPUBackend.CPU)
    AUTO = int(_C.XPUBackend.AUTO)


def get_backend():
    return Backend.get_value(_C._get_backend)


def set_backend(backend):
    st = Backend.set_value(_C._set_backend, backend)
    assert bool(st), "WARNING: Failed to set XPU backend!"


################################################################
# EXPERIMENTAL options:
# NOTE: Below options are under experimental.
#       They are instable, and may be removed without notice!
################################################################

def has_jit_quantization_save():
    return _C._is_jit_quantization_save_enabled()


# oneDNN Layout
def using_onednn_layout():
    return _C._is_onednn_layout_enabled()


def enable_onednn_layout():
    _C._enable_onednn_layout()


def disable_onednn_layout():
    _C._disable_onednn_layout()


class onednn_layout(OnOff):
    def __init__(self):
        super().__init__(using_onednn_layout, enable_onednn_layout, disable_onednn_layout)


# force oneDNN primivite
def using_force_onednn_primitive():
    r"""
    Get the current force onednn primitive setting.

    Return:
        Force onednn primitive mode
        The value will be ``ON`` or ``OFF``.
        ``ON`` means enabled force onednn primitive mode;
        ``OFF`` means disabled force onednn primitive mode;

    Supported operator list:
        GRU
    """
    return _C._is_force_onednn_primitive_enabled()


def enable_force_onednn_primitive():
    _C._enable_force_onednn_primitive()


def disable_force_onednn_primitive():
    _C._disable_force_onednn_primitive()


class force_onednn_primitive(OnOff):
    def __init__(self):
        super().__init__(using_force_onednn_primitive, enable_force_onednn_primitive, disable_force_onednn_primitive)


# Simple Trace
def using_simple_trace():
    return _C._is_simple_trace_enabled()


def enable_simple_trace():
    _C._enable_simple_trace()


def disable_simple_trace():
    _C._disable_simple_trace()


class simple_trace(OnOff):
    def __init__(self):
        super().__init__(using_simple_trace, enable_simple_trace, disable_simple_trace)
