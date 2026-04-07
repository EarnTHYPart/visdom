#!/usr/bin/env python3

import argparse
import math
import os
import tempfile

from visdom import Visdom


def run_torch(logger, steps, seed):
    try:
        import torch
        import torch.nn as nn
    except ImportError as err:
        raise RuntimeError("PyTorch is not available") from err

    torch.manual_seed(seed)
    model = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 1))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    criterion = nn.MSELoss()

    for step in range(steps):
        x = torch.randn(64, 16)
        y = x.sum(dim=1, keepdim=True) * 0.25

        optimizer.zero_grad()
        prediction = model(x)
        loss = criterion(prediction, y)
        loss.backward()

        grad_sq = 0.0
        for parameter in model.parameters():
            if parameter.grad is not None:
                grad_sq += float(parameter.grad.norm(2).item()) ** 2

        if not logger.log(
            step=step,
            loss=float(loss.item()),
            grad_norm=math.sqrt(grad_sq),
        ):
            return False

        optimizer.step()

    return True


def run_torch_hooked(logger, steps, seed):
    try:
        import torch
        import torch.nn as nn
    except ImportError as err:
        raise RuntimeError("PyTorch is not available") from err

    torch.manual_seed(seed)
    model = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 1))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    criterion = nn.MSELoss()

    logger.attach_hooks(
        model=model,
        loss_module=criterion,
        optimizer=optimizer,
        start_step=0,
    )
    try:
        for _ in range(steps):
            x = torch.randn(64, 16)
            y = x.sum(dim=1, keepdim=True) * 0.25

            optimizer.zero_grad()
            prediction = model(x)
            loss = criterion(prediction, y)
            loss.backward()
            optimizer.step()
    finally:
        logger.detach_hooks()

    return True


def main():
    parser = argparse.ArgumentParser(description="Run Visdom auto-logger demo")
    parser.add_argument("--steps", type=int, default=60, help="Number of logging steps")
    parser.add_argument("--seed", type=int, default=7, help="Random seed")
    parser.add_argument("--env", type=str, default="main", help="Visdom environment")
    parser.add_argument("--server", type=str, default="http://localhost", help="Visdom server address")
    parser.add_argument("--port", type=int, default=8097, help="Visdom server port")
    parser.add_argument("--base_url", type=str, default="/", help="Visdom base URL")
    parser.add_argument("--offline", action="store_true", help="Run in offline mode")
    parser.add_argument("--log", type=str, default="", help="Path to visdom offline log file")
    parser.add_argument("--use_torch", action="store_true", help="Use a tiny torch training loop")
    parser.add_argument("--hook_based", action="store_true", help="Use PyTorch hooks for automatic logging")
    args = parser.parse_args()

    log_path = args.log
    if args.offline and not log_path:
        log_path = os.path.join(tempfile.gettempdir(), "visdom_autologger.log")

    viz = Visdom(
        server=args.server,
        port=args.port,
        base_url=args.base_url,
        env=args.env,
        log_to_filename=log_path if log_path else None,
        offline=args.offline,
        use_incoming_socket=False,
        raise_exceptions=True,
    )

    logger = viz.auto_logger(
        env=args.env,
        loss_title="AutoLogger Loss",
        grad_norm_title="AutoLogger Grad Norm",
    )

    if args.use_torch and args.hook_based:
        ok = run_torch_hooked(logger, steps=args.steps, seed=args.seed)
    elif args.use_torch:
        ok = run_torch(logger, steps=args.steps, seed=args.seed)
    else:
        ok = logger.run(steps=args.steps, seed=args.seed)

    if not ok:
        raise RuntimeError("Auto logger failed")

    print("Auto logger completed successfully")
    if args.offline and log_path:
        print("Offline log written to {}".format(log_path))


if __name__ == "__main__":
    main()
