from stacks.stack import Stack

reader_registry = {}
writer_registry = {}


def register_reader(ext):
    def wrapper(cls):
        reader_registry[ext] = cls()
        return cls

    return wrapper


def register_writer(ext):
    def wrapper(cls):
        writer_registry[ext] = cls()
        return cls

    return wrapper


def load_stack_from_file(path: str) -> Stack:
    ext = path.split(".")[-1]
    reader = reader_registry.get(ext)
    if not reader:
        raise ValueError(f"Unsupported input format: .{ext}")
    with open(path, encoding="utf-8") as f:
        return reader.read(f)


def write_stack_to_file(stack: Stack, path: str):
    ext = path.split(".")[-1]
    writer = writer_registry.get(ext)
    if not writer:
        raise ValueError(f"Unsupported output format: .{ext}")
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer.write(stack, f)
