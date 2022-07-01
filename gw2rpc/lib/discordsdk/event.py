import ctypes
import typing as t


def bind_events(structure: ctypes.Structure, *methods: t.List[t.Callable[..., None]]):
    contents = structure()
    for index, (name, func) in enumerate(structure._fields_):
        setattr(contents, name, func(methods[index]))

    pointer = ctypes.pointer(contents)
    return pointer
