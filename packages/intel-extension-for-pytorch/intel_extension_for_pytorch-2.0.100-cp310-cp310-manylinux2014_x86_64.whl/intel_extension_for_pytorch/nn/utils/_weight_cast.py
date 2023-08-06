import torch
import torch.nn as nn
import sys
from intel_extension_for_pytorch.optim import _optimizer_utils, _lamb
import types
from ._model_convert import _LSTM
from intel_extension_for_pytorch.nn.modules import MergedEmbeddingBag as MergedEmbeddingBag

# IPEX does not cast all module parameters for acc reason, such as BN
IPEX_WEIGHT_CAST_MODULE = {
    # align with auto cast white list
    torch.nn.Linear,
    torch.nn.Conv1d,
    torch.nn.Conv2d,
    torch.nn.Conv3d,
    torch.nn.ConvTranspose1d,
    torch.nn.ConvTranspose2d,
    torch.nn.ConvTranspose3d,
    # ipex support
    torch.nn.EmbeddingBag,
    torch.nn.Embedding,
    _LSTM,
    MergedEmbeddingBag,
}

def _save_to_state_dict(self, destination, prefix, keep_vars):
    param_dict = {}
    for name, para in self.named_parameters():
        if not hasattr(self, name):
            continue
        temp = para
        param_dict.update({name: para})
        if hasattr(self, name + '_trail'):
            temp_para = torch.nn.Parameter(
                torch.ops.torch_ipex.cat_bfloat16_float(para.data, getattr(self, name + '_trail')),
                requires_grad=temp.requires_grad)
            setattr(self, name, temp_para)
        elif hasattr(self, 'master_' + name):
            temp_para = torch.nn.Parameter(
                getattr(self, 'master_' + name),
                requires_grad=temp.requires_grad)
            setattr(self, name, temp_para)
    super(type(self), self)._save_to_state_dict(destination, prefix, keep_vars)
    for p in param_dict:
        origin_param = param_dict[p]
        setattr(self, p, origin_param)

def _load_from_state_dict(self, state_dict, prefix, local_metadata, strict,
                            missing_keys, unexpected_keys, error_msgs):
    for name, para in self.named_parameters():
        if not hasattr(self, name):
            continue
        para_name = prefix + name
        with torch.no_grad():
            if para_name in state_dict:
                fp32_param = state_dict[para_name]
                if hasattr(self, 'master_' + name):
                    getattr(self, 'master_' + name).copy_(fp32_param)
                    getattr(self, name).copy_(fp32_param.bfloat16())
                elif hasattr(self, name + '_trail'):
                    top, bot = torch.ops.torch_ipex.split_float_bfloat16(fp32_param)
                    getattr(self, name).copy_(top)
                    getattr(self, name + '_trail').copy_(bot)

def weight_dtype_convert_with_ipex(module, optimizer, params_attr, master_weight_split, convert_dtype=torch.bfloat16):
    
    def cast_attr(m, attr, master_weight_split, params_attr, optimizer):
        # cast weight/bias for BF16 or FP16 dtype
        float_param = getattr(m, attr)
        params_attr[float_param] = {}
        if master_weight_split:
            if not hasattr(m, attr + '_trail'):
                assert convert_dtype == torch.bfloat16, "master_weight_split is only support for bf16 now"
                top_half, bot_half = torch.ops.torch_ipex.split_float_bfloat16(float_param.data)
                setattr(m, attr + '_trail', bot_half)
                setattr(m, attr, nn.Parameter(top_half.detach(), requires_grad=float_param.requires_grad))
                params_attr[float_param]['trail'] = getattr(m, attr + '_trail')
        else:
            if not hasattr(m, 'master_' + attr):
                assert float_param.dtype == torch.float32, "The original " + attr + " of the " + str(m) \
                + " should be kept float and the associated float master " + attr + " will be created for you"
                setattr(m, 'master_' + attr, float_param.data)
                if convert_dtype == torch.bfloat16:
                    setattr(m, attr, nn.Parameter(float_param.detach().bfloat16(), requires_grad=float_param.requires_grad))
                    params_attr[float_param]['bf16_param'] = getattr(m, attr)
                else:
                    assert convert_dtype == torch.half, "Only bf16 and fp16 are supported"
                    setattr(m, attr, nn.Parameter(float_param.detach().half(), requires_grad=float_param.requires_grad))
                    params_attr[float_param]['fp16_param'] = getattr(m, attr)
        # update attr entry, always use params in optimzer as "key"
        # while master weight split, key is m.weight/bias, if not split, key is m.master_weight/master_bias
        attr_name = attr if master_weight_split else 'master_' + attr
        params_attr[getattr(m, attr_name)] = params_attr.pop(float_param)
        _optimizer_utils.refresh_optimizer_params_after_cast(m, attr, float_param, master_weight_split, optimizer) 

    def convert(m):
        if type(m) in IPEX_WEIGHT_CAST_MODULE:
            if not hasattr(m, 'master_weight_split'):
                setattr(m, 'master_weight_split', master_weight_split)
                # replace weight/bias
                for name, para in m.named_parameters():
                    if hasattr(m, name):
                        cast_attr(m, name, master_weight_split, params_attr, optimizer)
                # for resume training reason, we always save float tensors
                # replace module method to ensure return float params while call "state_dict()"
                setattr(m, '_save_to_state_dict', types.MethodType(_save_to_state_dict, m))
                setattr(m, '_load_from_state_dict', types.MethodType(_load_from_state_dict, m))
                for name, sub_m in m.named_children():
                    if isinstance(sub_m, torch.nn.ParameterList):
                        setattr(sub_m, 'master_weight_split', master_weight_split)
                        setattr(sub_m, '_save_to_state_dict', types.MethodType(_save_to_state_dict, sub_m))
                        setattr(sub_m, '_load_from_state_dict', types.MethodType(_load_from_state_dict, sub_m))
                        for name, para in sub_m.named_parameters():
                            cast_attr(sub_m, name, master_weight_split, params_attr, optimizer)
        return m

    def isCLIPTextEmbeddings(m):
        mod = 'transformers.models.clip.modeling_clip'
        return mod in sys.modules and hasattr(sys.modules[mod], 'CLIPTextEmbeddings') and isinstance(m, sys.modules[mod].CLIPTextEmbeddings)

    def convert_rec(m):
        new_m = convert(m)
        for name, sub_m in m.named_children():
            if not isCLIPTextEmbeddings(sub_m):
                setattr(new_m, name, convert_rec(sub_m))
        return new_m

    casted_model, casted_optimizer, params_attr = convert_rec(module), optimizer, params_attr

    if optimizer is not None:
        _optimizer_utils.patch_load_state_dict(casted_optimizer)
        if not hasattr(casted_optimizer, 'params_attr'):
            setattr(casted_optimizer, 'params_attr', params_attr)
        if not master_weight_split:
            _optimizer_utils.patch_step_for_master_weight_training(casted_optimizer)
            _optimizer_utils.patch_zero_grad_for_master_weight_training(casted_optimizer)

    return casted_model, casted_optimizer, params_attr
