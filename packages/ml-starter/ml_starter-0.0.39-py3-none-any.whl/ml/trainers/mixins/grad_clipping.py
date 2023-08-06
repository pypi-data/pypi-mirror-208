"""Defines a trainer mixin for supporting gradient clipping.

Gradient clipping occurs after the gradients are computed and before the
optimizer step. It is done in-place, so the gradients are modified. There
are basically three types of gradient clipping:

1. Norm-based clipping
2. Value-based clipping
3. Global norm-based clipping

Norm-based clipping is the most common type of gradient clipping. It
clips the norm of each gradient to a maximum value, by dividing by the norm
if the norm is greater than some threshold.

Value-based clipping clips each gradient value to a maximum value, by
clamping the gradient value to the maximum value.

Global norm-based clipping clips the norm of all gradients to a maximum
value, by dividing all gradients by the total norm if the total norm is
greater than some threshold.
"""

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

import torch
from torch import Tensor, nn
from torch.distributed.fsdp.fully_sharded_data_parallel import FullyShardedDataParallel as FSDP
from torch.optim import Optimizer

from ml.core.config import conf_field
from ml.trainers.base import BaseTrainer, BaseTrainerConfig, ModelT, TaskT
from ml.trainers.mixins.mixed_precision import (
    MixedPrecisionTrainerConfig,
    MixedPrecisionTrainerMixin,
)


@dataclass
class GradientClipping:
    clip_grad_norm: float | None = conf_field(None, help="What to clip the gradient norm to")
    norm_type: Any = conf_field(2, help="Type of norm to use")
    clip_grad_value: float | None = conf_field(None, help="What to clip the gradient value to")
    clip_global_grad_norm: float | None = conf_field(None, help="What to clip global gradient norm to")
    global_norm_type: Any = conf_field(2, help="Type of global norm to use")
    log_grad: bool = conf_field(False, help="Whether to log the gradient norm")


@dataclass
class GradientClippingConfig(MixedPrecisionTrainerConfig, BaseTrainerConfig):
    grad_clipping: GradientClipping = conf_field(GradientClipping(), help="Gradient clipping configuration")


GradientClippingConfigT = TypeVar("GradientClippingConfigT", bound=GradientClippingConfig)


def get_clip_grad_func(clip_value: float) -> Callable[[Tensor], Tensor]:
    def func(grad: Tensor) -> Tensor:
        return grad.clamp(-clip_value, clip_value)

    return func


def get_clip_norm_func(clip_value: float, norm_type: Any) -> Callable[[Tensor], Tensor]:
    def func(grad: Tensor) -> Tensor:
        grad_norm = torch.norm(grad, p=norm_type)
        return grad * (grad_norm.clamp_max(clip_value) / grad_norm)

    return func


class GradientClippingTrainerMixin(
    MixedPrecisionTrainerMixin[GradientClippingConfigT, ModelT, TaskT],
    BaseTrainer[GradientClippingConfigT, ModelT, TaskT],
):
    """Defines a trainer mixin for doing gradient clipping."""

    def maybe_add_grad_clipping(self, model: nn.Module) -> None:
        clip_value = self.config.grad_clipping.clip_grad_value
        clip_norm = self.config.grad_clipping.clip_grad_norm
        if clip_value is not None:
            for p in model.parameters():
                if p.requires_grad:
                    p.register_hook(get_clip_grad_func(clip_value))
        if clip_norm is not None:
            for p in model.parameters():
                if p.requires_grad:
                    p.register_hook(get_clip_norm_func(clip_norm, self.config.grad_clipping.norm_type))

    def clip_grads(self, model: nn.Module, optim: Optimizer) -> None:
        clip_norm = self.config.grad_clipping.clip_global_grad_norm
        norm_type = self.config.grad_clipping.global_norm_type
        if clip_norm is not None:
            if isinstance(model, FSDP):
                total_norm = model.clip_grad_norm_(clip_norm, norm_type)
            else:
                self.unscale_mixed_precision(optim)
                total_norm = nn.utils.clip_grad.clip_grad_norm_(model.parameters(), clip_norm, norm_type)
            self.logger.log_scalar("total_norm", total_norm.item(), namespace="optim")
            if self.config.grad_clipping.log_grad:
                self.unscale_mixed_precision(optim)
                total_grad = sum(
                    param.grad.norm(self.config.grad_clipping.norm_type) ** 2
                    for param in model.parameters()
                    if param.grad is not None
                )
                self.logger.log_scalar("total_grad", total_grad.item(), namespace="optim")
