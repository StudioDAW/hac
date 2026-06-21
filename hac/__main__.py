import sys
import importlib.util
import time
import os
import types
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import logging
from . import fonts
from matplotlib import font_manager
import re
from . import css, precss#, guides
from . import node as NODE

# code blocks charts

module = None
font_dir = ""

def load_font(font):
    font_family, font_format = os.path.splitext(os.path.basename(fonts._paths[font]))
    precss.append([
        ("css", "@font-face"),
        ("font-family", f'"{font_family}"'),
        ("src", f'url("{fonts._paths[font]}"), format("{font_format[1:]}")')
    ])
    return f"\'{font_family}\'"
loaded_fonts = {}

# COMPILER
def addcss(node, key, value):
    if "_" in key: key = key.replace("_", "-")
    if isinstance(value, tuple):
        value = "".join(str(v) for v in value)
    css[node._cssid].append((key, value))

def parsecss(node, parent=None):
    children = []
    media_value = None
    for key, value in node.__dict__.items():
        if isinstance(value, type):
#            if value.__module__ == NODE.__module__:
#                print(key,value)
#                continue
            if isinstance(value.__mro__[-2], type(NODE)):
                heritage = [c.__qualname__.replace(".","-") for c in value.__mro__[::-1][3:]]
                if heritage:
                    value._cssid = len(css)
                    css.append([("css","."+heritage[-1])])
                    value._classname = " ".join(heritage)
                    children.append(value)
        elif not key.startswith("_") and key not in "content" and isinstance(node, type(NODE)):
            if key in node._inherited:
                if value == node._inherited[key]:
                    continue

            if key in module.__dict__:
                func = module.__dict__[key]
                if callable(func):
                    for k, v in func(value, node):
                        addcss(node,k,v)
            elif key == "font_family":
                if value not in loaded_fonts.keys():
                    loaded_fonts[value] = load_font(value)
                addcss(node,key,loaded_fonts[value])
            else:
                addcss(node,key,value)

    if isinstance(node, type(NODE)):
        css[node._cssid] = list(dict.fromkeys(css[node._cssid]))
        node._children = children
    for child in children:
        parsecss(child, node)

def render(node, depth=0):
    if hasattr(node, "enabled"):
        if node.enabled == False:
            print(node)
            return ""

    code_block = True if node.__mro__[-3].__name__ == "code" else False

    indent = "  "*depth

    inner = ""
    if node.content:
        lines = node.content if code_block else "<br>".join(node.content.splitlines())
        inner = "\n  "+ indent + lines
    for child in node._children: inner += render(child, depth+1)
    depth = 0

    if code_block:
        return f'\n{indent}<{node._html[0]} class="{node._classname}"><{node._html[1]} class="{node.language}">{inner}\n{indent}</{node._html[1]}></{node._html[0]}>'

    return f'\n{indent}<{node._html} class="{node._classname}">{inner}\n{indent}</{node._html}>'


def write(path, node):
    global module
    module = load_module(path)
    if module:
        script = """
<link href="hac/prism.css" rel="stylesheet" />
<script src="hac/prism.js"></script>
<script>
let last = null;

setInterval(async () => {
    try {
        const res = await fetch("reload.flag", { cache: "no-store" });
        const t = await res.text();

        if (last && t !== last) {
            location.reload();
        }

        last = t;
    } catch (e) {}
}, 300);
</script>
        """
        with open("index.html", "w") as f:
            parsecss(module)
            html = render(module.__dict__[node])
            style = """
@page {
    size: A4;
    margin: 0;
}

@media print {

    body {
        margin: 0;
        padding: 0;
        display: block !important;
    }

    .spread {
        width: auto !important;
        height: auto !important;
        display: block !important; 
    }

    .page {
        width: 210mm;
        height: 297mm;
        break-after: page;
        page-break-after: always;
    }

    .page:last-child {
        break-after: auto;
        page-break-after: auto;
    }

    * {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
}
"""
            for cs in precss+css:
                start = ""
                attrs = ""
                for c in cs:
                    if c[0] == "css":
                        start = c[1]+" {\n"
                        continue
                    attrs += f"\t{c[0]}:{c[1]};\n"
                style += start+attrs+"}\n\n"
            css.clear()
            f.write("<!DOCTYPE html><head>\n<style>\n"+style+"</style>\n"+script+"</head><html>"+html+"</html>")
    else:
        return


_loaded_packages = set()

def load_module(path):
    module_name = ".".join(path.split("/")[-2::])[:-3]

    project_root = os.path.dirname(os.path.dirname(path))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    package_name = module_name.split(".")[0]

    try:
        for name in list(sys.modules.keys()):
            if name == package_name or name.startswith(package_name + "."):
                del sys.modules[name]

        module = importlib.import_module(module_name)

        _loaded_packages.add(module_name)

        return module
    except Exception as e:
        print("Load failed:", e)
        return None


# WATCHDOG
class WatchHandler(FileSystemEventHandler):
    def __init__(self, path, node) -> None:
        self.path = path
        self.node = node
        self.last_run = 0
        self.debounce_time = 3

    def on_modified(self, event) -> None:
        if os.path.abspath(event.src_path) != self.path:
            return
        now = time.time()
        if now - self.last_run < self.debounce_time:
            return
        self.last_run = now
        write(self.path, self.node)
        with open("./reload.flag", "w") as f:
            f.write(str(now))

def watch(path, node, stop_event):
    handler = WatchHandler(path, node)
    observer = Observer()

    watch_dir = os.path.dirname(path)
    observer.schedule(handler, watch_dir, recursive=False)

    observer.start()
    print(f"watching: {'/'.join(path.split('/')[-2:])}")
    
    try:
        while not stop_event.is_set():
            time.sleep(.5)
    finally:
        observer.stop()
        observer.join()


# SERVER
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
class ServerHandler(SimpleHTTPRequestHandler):
    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        pass
    def log_message(self, format: str, *args) -> None:
        pass
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()


def serve(stop_event):
    server = HTTPServer(("localhost", 8000), ServerHandler)
    server.timeout = 0.5

    print("serving: http://localhost:8000")

    try:
        while not stop_event.is_set():
            server.handle_request()
    finally:
        server.server_close()


def generate_fonts():
    if hasattr(fonts, "_paths"):
        if len(getattr(fonts, "_paths")) != 0:
            return
    print("generating hac.fonts...")
    system_fonts = font_manager.findSystemFonts()

    with open(os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ), "fonts.py"), "w", encoding="utf-8") as f:
        f.write("# Auto-generated System Fonts. To regenerate remove all lines.\n\n")
        f.write("_paths = "+str(system_fonts))

        for i, font_path in enumerate(system_fonts):
            font = os.path.splitext(os.path.basename(font_path))[0]
            var_name = re.sub(r'[\s-]+', '_', re.sub(r'[^\w\s-]', '', font))

            if var_name and var_name[0].isdigit():
                var_name = f"_{var_name}"

            f.write(f'\n{var_name}:int = {i}')
        print("hac.fonts generated")
        time.sleep(1)
        os.execv(sys.executable, [sys.executable]+sys.argv)


def main():
    global font_dir

    generate_fonts()
    path = ""

    if len(sys.argv) < 2:
        path = os.getcwd()
    elif sys.argv[1] == "init":
        path = os.getcwd() if len(sys.argv) < 3 else os.path.abspath(sys.argv[2])
        if not os.path.exists(path): os.mkdir(path)
        if len(os.listdir(path)) != 0:
            print(f"To initialize please make sure the project directory '{path}' is empty.")
            quit()
        os.mkdir(os.path.join(path, "fonts"))
        os.mkdir(os.path.join(path, "images"))
        with open(os.path.join(path,"__init__.py"), "w") as f:
            f.write(
"""# __init__.py 

from hac import *
from hac import colors

class reusable_class(div):
    ratio = 1
    height = 50,pct
    stack = vertical
    center = v,h
    background = colors.ochraceous_salmon
    color = colors.black

    class text(h1):
        content = "H"
        font_size = 180,pt
""")
        with open(os.path.join(path,"design.py"), "w") as f:
            f.write(
"""# design.py

from hac import *
from hac import colors
from . import reusable_class

class main(body):
    center = vertical,horizontal
    background = colors.white

    class container(div):
        width = 80,pct
        height = 100,pct
        stack = horizontal
        center = vertical,horizontal
        gap = 30,mm

        class H(reusable_class): pass

        class A(reusable_class):
            class text(reusable_class.text):
                content = "A"

        class C(reusable_class):
            pass
        C.text.content = "C"
""")
    else:
        path = os.path.abspath(sys.argv[1])
    font_dir = os.path.join(path, "fonts")
    path = os.path.join(path, "design.py")
    write(path, "main")

    stop_event = threading.Event()

    watcher_thread = threading.Thread(
        target=watch,
        args=(path, "main", stop_event),
        daemon=True
    )

    server_thread = threading.Thread(
        target=serve,
        args=(stop_event,),
        daemon=True
    )

    watcher_thread.start()
    server_thread.start()


    try:
        watcher_thread.join()
        server_thread.join()
    except KeyboardInterrupt:
        print("\nshutting down...")
        stop_event.set()

if __name__ == "__main__":
    main()
