from hac import *
from hac.colors import *
from hac.fonts import *

Arial_Black = load_font(Arial_Black)
Arial_Narrow = load_font(Arial_Narrow)

coralred = "#FF4040"
sulpheryellow = "#CCC050"

g = "#149E40"
y = "#FBA76C"
r = "#D83550"

class page(div):
    background = white
    width = "210mm"
    height = "297mm"

class spread(div):
    display = "grid"
    grid_template_columns = "auto auto"
    gap = "10px"

class main(body):
    font_family = Arial_Black
    background = black
    display = "grid"
    place_items = "center"
    gap = "30px"

    class start_spread(spread):
        class blank(div):
            width = "210mm"
        class page1(page):
            class title(h1):
                color = black
                font_size = "58pt"
                text_align = "center"
                content = "HAC"
                padding = "10mm"
                padding_bottom = "0"
                margin_bottom = "10mm"

            class subtitle_holder(div):
                display = "grid"
                justify_content = "center"
                class subtitle(div):
                    font_size = "14pt"
                    display = "flex"
                    width = "54mm"
                    margin = "0"
                    padding = "0"

                    class html(h1):
                        flex = .5
                        color = g
                        margin = "0"
                        padding = "0"
                        font_weight = "100"
                        text_align = "center"
                        content = """H
                        T
                        M
                        L """

                    class right_side(div):
                        flex = 1
                        class columns(div):
                            display = "grid"
                            grid_template_columns = "auto auto"
                            class c2(div):
                                class text(h1):
                                    color = y
                                    margin = "0"
                                    padding = "0"
                                    font_weight = "100"
                                    text_align = "center"
                                    content = """A
                                    N
                                    D"""
                                class dot(text):
                                    color = darkgray
                                    content = "."
                            class c3(c2):
                                pass
                            c3.text.color = r
                            c3.text.content = """C
                            S
                            S"""
                        class authordiv(div):
                            display = "flex"
                            justify_content = "center"
                            class by(h1):
                                flex = .3
                                color = darkgrey
                                padding_top = "10mm"
                                text_align = "center"
                                content = "by"
                                font_size = "14pt"
                                font_weight = "300"
                            class columns(div):
                                flex = .3
                                display = "flex"
                                class d(h1):
                                    flex = .33
                                    color = darkgrey
                                    padding_top = "10mm"
                                    text_align = "center"
                                    font_size = "14pt"
                                    font_weight = "300"
                                    content = """D
                                    -
                                    -
                                    |
                                    -"""
                                class a(d): pass
                                a.content = """A
                                |
                                -
                                |
                                -"""
                                class w(d): pass
                                w.content = """W
                                |
                                -
                                -
                                |
                                |
                                -
                                -"""


    class spread2(spread):
        class page1(page):
            class e(h1):
                content = "hello"
        class page2(page):
            class e(h1):
                content = "hello"

    class spread3(spread):
        class page1(page):
            pass
        class page2(page):
            pass

    class spread4(spread):
        class page1(page):
            pass
        class page2(page):
            pass

    class spread5(spread):
        class page1(page):
            class e(h1):
                content = "hello"
        class page2(page):
            pass

    class end_spread(spread):
        class page1(page):
            pass
        class blank(div):
            width = "210mm"
