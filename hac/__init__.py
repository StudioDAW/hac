from typing import Any, Final
from .fonts import _paths
import os

content: Any

px: Final[str] = "px"
pt: Final[str] = "pt"
mm: Final[str] = "mm"
cm: Final[str] = "cm"
em: Final[str] = "em"
rem: Final[str] = "rem"
vh: Final[str] = "vh"
vw: Final[str] = "vw"
percent: Final[str] = "%"
pct: Final[str] = "%"

v: Final[str] = "v"
h: Final[str] = "h"
vertical: Final[str] = "vertical"
horizontal: Final[str] = "horizontal"

css = []

def load_font(font):
    font_family, font_format = os.path.splitext(os.path.basename(_paths[font]))
    css.append([
        ("css", "@font-face"),
        ("font-family", f'"{font_family}"'),
        ("src", f'url("{_paths[font]}"), format("{font_format}")')
    ])
    return f"\'{font_family}\'"

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

class NodeMeta(type):
    _inherited: dict = {}
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        ns = {
            "_inherited": {},
            "_children": [],
            "_cssid": 0,
            "_classname": "",
            "content": "",
        }

        # inject inherited values BEFORE class body runs
        for base in bases:
            if base is object:
                continue

            for k, v in base.__dict__.items():
                if k.startswith("__"):
                    continue

                if isinstance(v, type):
                    ns[k] = clone_class(v)
                else:
                    ns[k] = v

        return ns

    def __new__(mcls, name, bases, ns, **kwargs):
        cls = super().__new__(mcls, name, bases, dict(ns))

        cls._inherited = {}

        for base in bases:
            if base is object:
                continue

            for k, v in base.__dict__.items():
                if k.startswith("__"):
                    continue

                if not k.startswith("_"):
                    cls._inherited[k] = v

        return cls


class node(metaclass=NodeMeta):
    _inherited: dict
    _children: list
    _cssid: int
    _classname: str
    content: str
#class node():
#    def __init_subclass__(cls, **kwargs):
#        super().__init_subclass__(**kwargs)
#
#        cls._inherited = {}
#        cls._children: list = []
#        cls._cssid:int = 0
#        cls._classname: str = ""
#        cls.content: str = ""
#
#        bases = cls.__bases__
#
#        for base in bases:
#            if base is object:
#                continue
#
#            for k, v in base.__dict__.items():
#                if k.startswith("__"):
#                    continue
#
#                if k not in cls.__dict__:
#                    if isinstance(v, type):
#                        setattr(cls, k, clone_class(v))
#                    else:
#                        if not k.startswith("_"):
#                            cls._inherited[k] = v
#                            setattr(cls, k, v)


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


