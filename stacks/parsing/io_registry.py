"""Registry for file readers and writers with automatic source tracking."""

from pathlib import Path

from stacks.stack import Stack

reader_registry = {}
writer_registry = {}


def register_reader(ext: str):
    """Register a reader for a file extension.

    Args:
        ext: File extension to register.

    Returns:
        Decorator function.

    """

    def wrapper(cls):
        """Wrap the class and register it."""
        reader_registry[ext] = cls()
        return cls

    return wrapper


def register_writer(ext: str):
    """Register a writer for a file extension.

    Args:
        ext: File extension to register.

    Returns:
        Decorator function.

    """

    def wrapper(cls):
        """Wrap the class and register it."""
        writer_registry[ext] = cls()
        return cls

    return wrapper


def load_stack_from_file(path: str) -> Stack:
    """Load a stack from a file with automatic source tracking.

    Args:
        path: Path to the file to load.

    Returns:
        Stack with cards having their source property set.

    Raises:
        ValueError: If the file format is not supported.

    """
    path_obj = Path(path)
    # Remove the leading dot or use full name if no extension
    ext = path_obj.suffix[1:] if path_obj.suffix else path_obj.name
    reader = reader_registry.get(ext)
    if not reader:
        msg = f"Unsupported input format: .{ext}"
        raise ValueError(msg)
    with path_obj.open(encoding="utf-8") as f:
        return reader.read_with_source(f, path_obj)


def write_stack_to_file(stack: Stack, path: str) -> None:
    """Write a stack to a file.

    Args:
        stack: Stack to write.
        path: Path to write to.

    Raises:
        ValueError: If the file format is not supported.

    """
    path_obj = Path(path)
    # Remove the leading dot or use full name if no extension
    ext = path_obj.suffix[1:] if path_obj.suffix else path_obj.name
    writer = writer_registry.get(ext)
    if not writer:
        msg = f"Unsupported output format: .{ext}"
        raise ValueError(msg)
    with path_obj.open("w", encoding="utf-8", newline="") as f:
        writer.write(stack, f)
