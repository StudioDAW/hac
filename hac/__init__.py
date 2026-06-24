from typing import Any, Final
import os

content: Any

class unit:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return self.val

    def __add__(self, value):
        self.val += "+"+str(value)
        return self.val

    def __sub__(self, value):
        self.val += "-"+str(value)
        return self.val

    def __ror__(self, value):
        self.val = str(value)+self.val
        return self.val


px: unit = unit("px")
pt: unit = unit("pt")
mm: unit = unit("mm")
cm: unit = unit("cm")
em: unit = unit("em")
rem: unit = unit("rem")
vh: unit = unit("vh")
vw: unit = unit("vw")
percent: unit = unit("%")
pct: unit = unit("%")

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

class modes:
    normal: Final[str] = "normal"
    darken: Final[str] = "darken"
    multiply: Final[str] = "multiply"
    color_burn: Final[str] = "coloriburn"
    lighten: Final[str] = "lighten"
    screen: Final[str] = "screen"
    color_dodge: Final[str] = "color-dodge"
    overlay: Final[str] = "overlay"
    soft_light: Final[str] = "soft-light"
    hard_light: Final[str] = "hard-light"
    difference: Final[str] = "difference"
    exclusion: Final[str] = "exclusion"
    hue: Final[str] = "hue"
    saturation: Final[str] = "saturation"
    color: Final[str] = "color"
    luminosity: Final[str] = "luminosity"


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


class _body(node):
    _html = "body"
class body(_body):
    min_height = 100,vh
    margin = 0

class div(node):
    _html = "div"
    margin = 0

class h1(node):
    _html = "h1"

class p(node):
    _html = "p"

class code(node):
    _html = ("pre", "code")
    language = "html"

class page(div):
    width = 210,mm
    height = 297,mm
    background = "white"
    margin = 0
    stack = vertical
    position = "relative"

    class guides(div):
        enabled: bool
        position = "absolute"
        inset = 0
        z_index = 9999
        center = v,h


        class margin(div):
            enabled: bool
            outline = 2,px," solid red"
            width = "calc(100% - 20mm)"
            height = "calc(100% - 20mm)"


def tuple_value(func):
    def wrapper(value, node):
        css = {}
        if isinstance(value, tuple):
            transforms = {}
            for val in value:
                if val in units:
                    return func(value, node)
                css |= func(val, node)
            for i, c in enumerate(css):
                if c[0] == "transform":
                    transforms[i] = c[1]
            if transforms:
                for i, transform in enumerate(transforms.keys()):
                    css.pop(transform-i)
                css["transform"] = " ".join(transforms.values())

        else:
            return func(value, node)
        return css
    return wrapper


# LAYOUT


@tuple_value
def center(value, node):
    css = {"display": "flex"}
    if value in (v,vertical):
        css["justify_content"] = "center"
    elif value in (h,horizontal):
        css["align_items"] = "center"
    return css


def stack(value, node):
    css = {"display": "flex"}
    values = {h:"row",v:"column",horizontal:"row",vertical:"column"}
    if value in values:
        css["flex-direction"] = values[value]
    return css

def ratio(value, node):
    css = {"display": "flex"}
    if isinstance(value, tuple):
        value = "".join(str(v) for v in value)
    css["flex"] = value
    return css



# SHAPE


def triangle(value, node):
    css = {}
    if isinstance(value, float|int):
        value = str(value*100)+"%"
    elif isinstance(value, tuple):
        value = "".join(str(val) for val in value)
    if value.endswith("%"):
        css["clip_path"] = f"polygon(0% 100%, {value} 0%, 100% 100%)"
    return css


# TRANSFORM

@tuple_value
def flip(value, node):
    css = {}
    if value in (v,vertical):
        css["transform"] = "scaleY(-1)"
    elif value in (h,horizontal):
        css["transform"] = "scaleX(-1)"
    return css


# Visual

def blend_mode(value, node):
    return {"mix_blend_mode": value}

def background_opacity(value, node):
    """css value added before change"""
    if node.background.startswith("#"):
        if isinstance(value, float):
            value = hex(round(value * 255))
        return {"background": node.background+str(value)[2:]}
    print(node.background)
    return {}
