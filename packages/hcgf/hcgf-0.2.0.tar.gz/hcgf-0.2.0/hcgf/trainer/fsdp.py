"""
Referenced from: 
https://pytorch.org/blog/introducing-pytorch-fully-sharded-data-parallel-api/
https://pytorch.org/tutorials/intermediate/FSDP_tutorial.html
https://pytorch.org/tutorials/intermediate/FSDP_adavnced_tutorial.html
https://github.com/HamidShojanazeri/examples/blob/FSDP_example/FSDP/T5_training.py
https://pytorch.org/docs/stable/fsdp.html
"""
import os
import functools
from typing import Callable, Optional

from looseversion import LooseVersion

import torch
import torch.nn as nn

import torch.distributed as dist
from torch.distributed.fsdp import (
    MixedPrecision,
    ShardingStrategy,
)
from torch.distributed.fsdp.wrap import (
    transformer_auto_wrap_policy,
    lambda_auto_wrap_policy,
    _or_policy,
)

from hcgf.utils import get_module_class_from_name


fpSixteen = MixedPrecision(
    param_dtype=torch.float16,
    # Gradient communication precision.
    reduce_dtype=torch.float16,
    # Buffer precision.
    buffer_dtype=torch.float16,
)

bfSixteen = MixedPrecision(
    param_dtype=torch.bfloat16,
    # Gradient communication precision.
    reduce_dtype=torch.bfloat16,
    # Buffer precision.
    buffer_dtype=torch.bfloat16,
)

fp32_policy = MixedPrecision(
    param_dtype=torch.float32,
    reduce_dtype=torch.float32,
    buffer_dtype=torch.float32,
)


def setup(rank, world_size):
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12356"
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    dist.destroy_process_group()


def get_mp_policy() -> Optional[MixedPrecision]:
    bf16_ready = (
        torch.version.cuda
        and torch.cuda.is_bf16_supported()
        and LooseVersion(torch.version.cuda) >= "11.0"
        and dist.is_nccl_available()
        and torch.cuda.nccl.version() >= (2, 10)
    )

    if bf16_ready:
        mp_policy = bfSixteen
    else:
        mp_policy = None # defaults to fp32
    return mp_policy


def get_transformer_wrap_policy(model: nn.Module, module_name: str) -> Callable:
    def lambda_policy_fn(module: nn.Module):
        # From HuggingFace
        if (
            len(list(module.named_children())) == 0
            and getattr(module, "weight", None) is not None
            and module.weight.requires_grad
        ):
            return True
        return False

    lambda_policy = functools.partial(
        lambda_auto_wrap_policy, lambda_fn=lambda_policy_fn
    )
    transformer_cls_to_wrap = set()
    tf_cls = get_module_class_from_name(model, module_name)
    transformer_cls_to_wrap.add(tf_cls)
    tf_wrap_policy = functools.partial(
        transformer_auto_wrap_policy, transformer_layer_cls=transformer_cls_to_wrap
    )
    auto_wrap_policy = functools.partial(
        _or_policy, policies=[lambda_policy, tf_wrap_policy]
    )
    return auto_wrap_policy


def get_sharding_strategy(strategy: str) -> ShardingStrategy:
    if "zero2" in strategy:
        return ShardingStrategy.SHARD_GRAD_OP
    elif "zero3" in strategy:
        return ShardingStrategy.FULL_SHARD
    elif "mpdp" in strategy:
        return ShardingStrategy.NO_SHARD
    else:
        msg = f"{__file__}: unsupported strategy: {strategy}"
        raise ValueError(msg)