from hac import *
from hac.colors import *

class page(div):
    background = darkgray
    width = "210mm"
    height = "297mm"

class spread(div):
    display = "grid"
    grid_template_columns = "auto auto"
    gap = "10px"

class main(body):
    background = black
    display = "grid"
    place_items = "center"
    gap = "30px"

    class start_spread(spread):
        class blank(div):
            width = "210mm"
        class page1(page):
            class title(h1):
                font_size = "60pt"
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
                    display = "grid"
                    width = "54mm"
                    margin = "0"
                    padding = "0"
                    grid_template_columns = "auto auto auto"

                    class html(h1):
                        margin = "0"
                        padding = "0"
                        font_weight = "100"
                        text_align = "center"
                        content = """H
T
M
L """
                    class and_(html):
                        content = """A
N
D
."""
                    class css(html):
                        content = """C
S
S
."""
                class author(h1):
                    padding_right = "5mm"
                    padding_top = "10mm"
                    text_align = "right"
                    content = "by DAW"
                    font_size = "14pt"
                    font_weight = "300"


    class spread2(spread):
        class page1(page):
            pass
        class page2(page):
            pass

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
            pass
        class page2(page):
            pass

    class end_spread(spread):
        class page1(page):
            pass
        class blank(div):
            width = "210mm"
