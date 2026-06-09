white = "white"

def clone_class(cls):
    attrs = {}
    for k, v in cls.__dict__.items():
        if k in ("__dict__", "__weakref__"):
            continue
        if isinstance(v, type):
            attrs[k] = clone_class(v)
        else:
            attrs[k] = v
    return type(cls.__name__, cls.__bases__, attrs)


class node():
    content: str = ""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        bases = cls.__bases__

        for base in bases:
            if base is object:
                continue

            for k, v in base.__dict__.items():
                if k.startswith("__"):
                    continue

                if k not in cls.__dict__:
                    if isinstance(v, type):
                        setattr(cls, k, clone_class(v))
                    else:
                        setattr(cls, k, v)


class body(node):
    _html = "body"

class div(node):
    _html = "div"

class h1(node):
    _html = "h1"
class header(h1):
    pass

class p(node):
    _html = "p"


