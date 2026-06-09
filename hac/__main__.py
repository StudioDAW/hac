import sys
import importlib.util
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
from .server import serve 
import logging


# COMPILER
def render(node):
    css = ""
    children = []
    for key, value in node.__dict__.items():
        if type(value) == type:
            if type(value.__mro__[-2]) == type(node):
                children.append(value)
        elif key not in ("__module__","__doc__","content","_html"):
            if "_" in key: key = key.replace("_", "-")
            css += f"{key}:{value};"

    inner = "<br>".join(node.content.splitlines())+ "".join(render(c) for c in children)

    return f'<{node._html} style="{css}">{inner}</{node._html}>'

def write(node):
    module = safe_load(path)
    if module:
        script = """
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
        }, 1000);
        </script>
        """

        with open("index.html", "w") as f:
            f.write("<!DOCTYPE html><head>"+script+"</head><html>"+render(module.__dict__[node])+"</html>")
    else:
        return

def load_module_from_path(path):
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
        write(self.node)
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


if __name__ == "__main__":
    path = sys.argv[1]
    node = sys.argv[2]

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
