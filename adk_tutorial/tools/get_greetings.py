from typing import Optional


def say_hello(name: Optional[str] = None) -> str:
    """
    Provides a simple greeting. If name is provided, it will be used

    Args:
        name (str, optional): The name of the person to greet. Defaults to a generic greeting if not provided.

    Returns:
        str: A friendly greeting message.
    """
    if name:
        return f"Hello, {name}!"

    return "Hello! It's great to meet you."


def say_goodbye(name: Optional[str] = None) -> str:
    """
    Provides a simple goodbye message. If name is provided, it will be used
    """
    if name:
        return f"Goodbye, {name}!"

    return "Goodbye! It was great to meet you."
