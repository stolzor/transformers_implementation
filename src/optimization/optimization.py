from typing import Tuple, Callable, Iterable
import torch

from torch.optim import Optimizer

from ..scheduler.scheduler import update_lrate


class Adam(Optimizer):
    def __init__(
        self,
        params: Iterable[torch.Tensor],
        lr: float = 1e-3,
        betas: Tuple[float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.0,
        correct_bias: bool = True,
        warmup: int = 4000,
    ) -> None:
        params = list(params)
        if not isinstance(betas, tuple):
            raise TypeError(
                f"The betas parameter must be of the tuple type, not a {type(betas)}"
            )

        if lr < 0:
            raise ValueError(f"The learning rate: {lr} cannot be less than 0")
        if any(not 0 < beta < 1 for beta in betas):
            raise ValueError(f"Values in beta: {betas} should be in [0, 1]")
        if eps < 0:
            raise ValueError(f"Invalid epsilon value: {eps} should be >= 0.0")
        d_model = params[0].shape
        defaults = dict(
            lr=lr,
            betas=betas,
            eps=eps,
            weight_decay=weight_decay,
            correct_bias=correct_bias,
            d_model=d_model,
            warmup=warmup,
        )
        super(Adam, self).__init__(params, defaults)

    def step(self, closure: Callable | None) -> float | None:

        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        if "step" not in self.state.keys():
            self.state["state"] = 0

        self.state["step"] += 1

        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                beta_1, beta_2 = group["betas"]
                step = group["step"]
                warmup = group["warmup"]
                d_model = group["d_model"]

                if self.state["step"] == 1:
                    self.state["momentum_1"] = torch.zeros_like(p.data)
                    self.state["momentum_2"] = torch.zeros_like(p.data)

                first_moment_estimate = (
                    beta_1 * self.state["momentum_1"] + (1 - beta_1) * grad
                )
                second_moment_estimate = (
                    beta_2 * self.state["momentum_2"] + (1 - beta_2) * grad**2
                )

                if group["correct_bias"]:
                    first_unbiased_est = first_moment_estimate / (1 - beta_1**step)
                    second_unbiased_est = second_moment_estimate / (1 - beta_2**step)

                if step <= 4000:
                    lrate = update_lrate(d_model, step, warmup)
                else:
                    lrate = group["lr"]

                p.data -= lrate * (
                    first_unbiased_est / (second_unbiased_est**0.5 + step)
                )

        return loss
