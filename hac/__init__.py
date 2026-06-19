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

units = [px,pt,mm,cm,em,rem,vh,vw,percent,pct]

v: Final[str] = "v"
h: Final[str] = "h"
vertical: Final[str] = "vertical"
horizontal: Final[str] = "horizontal"

down: Final[str] = "down"
up: Final[str] = "up"
upright: Final[str] = "upright"

top: Final[str] = "top"
bottom: Final[str] = "bottom"
left: Final[str] = "left"
right: Final[str] = "right"


css = []
precss = []

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

class p(node):
    _html = "p"

class code(node):
    _html = ("pre", "code")
    language = "html"

def tuple_value(func):
    def wrapper(value, node):
        css = []
        if isinstance(value, tuple):
            transforms = {}
            for val in value:
                if val in units:
                    return func(value, node)
                css += func(val, node)
            for i, c in enumerate(css):
                if c[0] == "transform":
                    transforms[i] = c[1]
            if transforms:
                for i, transform in enumerate(transforms.keys()):
                    css.pop(transform-i)
                css.append(("transform"," ".join(transforms.values())))

        else:
            return func(value, node)
        return css
    return wrapper


# LAYOUT


@tuple_value
def center(value, node):
    css = [("display", "flex")]
    if value in (v,vertical):
        css.append(("justify_content", "center"))
    elif value in (h,horizontal):
        css.append(("align_items", "center"))
    return list(dict.fromkeys(css))


def stack(value, node):
    css = [("display", "flex")]
    values = {h:"row",v:"column",horizontal:"row",vertical:"column"}
    if value in values:
        css.append(("flex-direction", values[value]))
    return css


# SHAPE


def triangle(value, node):
    css = []
    if isinstance(value, float|int):
        value = str(value*100)+"%"
    elif isinstance(value, tuple):
        value = "".join(str(val) for val in value)
    if value.endswith("%"):
        css.append(("clip_path",f"polygon(0% 100%, {value} 0%, 100% 100%)"))
    return css


# TRANSFORM

@tuple_value
def flip(value, node):
    css = []
    if value in (v,vertical):
        css.append(("transform","scaleY(-1)"))
    elif value in (h,horizontal):
        css.append(("transform","scaleX(-1)"))
    return css
