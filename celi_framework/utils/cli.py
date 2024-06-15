import os


def bool_opt(parser, opt: str, env_var: str, help: str):
    parser.add_argument(
        opt,
        action="store_true",
        default=str2bool(os.getenv(env_var, "False")),
        help=help,
    )


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ValueError(f"Boolean value expected. Got: {v}")
