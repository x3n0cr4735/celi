import os


def bool_opt(parser, opt: str, env_var: str, help: str):
    """
    Add a boolean option to the given parser.

    Args:
        parser (argparse.ArgumentParser): The parser to add the option to.
        opt (str): The name of the option.
        env_var (str): The name of the environment variable to check for the default value.
        help (str): The help message for the option.

    Returns:
        None
    """
    parser.add_argument(
        opt,
        action="store_true",
        default=str2bool(os.getenv(env_var, "False")),
        help=help,
    )


def str2bool(v):
    """
    A function that converts a string representation to a boolean value.
    It checks if the input is a boolean, returns it if so.
    If not a boolean, it checks common string representations of True and False.
    Raises a ValueError if the input does not match any expected boolean representation.
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ValueError(f"Boolean value expected. Got: {v}")
