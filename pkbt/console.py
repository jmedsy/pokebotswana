def for_console(value) -> str:
    """The Windows console encoding cannot print the male or female sign."""
    return str(value).replace("♂", "-M").replace("♀", "-F")
