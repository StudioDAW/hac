import sys
import importlib.util
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import logging
from . import fonts
from matplotlib import font_manager
import re
from . import css, precss
from . import node as NODE


# code blocks charts

module = None

def load_font(font):
    font_family, font_format = os.path.splitext(os.path.basename(fonts._paths[font]))
    precss.append([
        ("css", "@font-face"),
        ("font-family", f'"{font_family}"'),
        ("src", f'url("{fonts._paths[font]}"), format("{font_format[1:]}")')
    ])
    print(font_family)
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
            if value.__module__ == NODE.__module__: continue
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
                print(loaded_fonts, value)
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
    module = safe_load(path)
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

def load_module_from_path(path):
    global module
    module_name = path.split("/")[-1].split(".")[0]

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module

def safe_load(path):
    module_name = path.split("/")[-1].split(".")[0]

    sys.modules.pop(module_name, None)

    try:
        return load_module_from_path(path)
    except Exception as e:
        print("Load failed:", e)
        return None

# WATCHDOG
class WatchHandler(FileSystemEventHandler):
    def __init__(self, path, node) -> None:
        self.path = os.path.abspath(path)
        self.node = node
        self.last_run = 0
        self.debounce_time = 0.1

    def on_modified(self, event) -> None:
        if os.path.abspath(event.src_path) != self.path:
            return
        now = time.time()
        write(self.path, self.node)
        with open("./reload.flag", "w") as f:
            f.write(str(now))

def watch(path, node, stop_event):
    handler = WatchHandler(path, node)
    observer = Observer()

    watch_dir = os.path.dirname(os.path.abspath(path))
    observer.schedule(handler, watch_dir, recursive=False)

    observer.start()
    print(f"watching: {path}")
    
    try:
        while not stop_event.is_set():
            time.sleep(.1)
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
    if len(fonts.__dict__) < 11:
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

                f.write(f'\n{var_name}:int|str = {i}')


def main():
    generate_fonts()

    path = sys.argv[1]
    node = sys.argv[2]
    write(path, node)

    stop_event = threading.Event()

    watcher_thread = threading.Thread(
        target=watch,
        args=(path, node, stop_event),
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
