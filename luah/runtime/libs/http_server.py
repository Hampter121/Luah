import threading
import json as _json
import re as _re
from http.server import HTTPServer, BaseHTTPRequestHandler

def yuriinject_http(yurilua, yurig, yuristop):

    yuriactive_servers = []

    def yurimake_server(yuriport, yurihandler_fn):
        yuriport = int(yuriport)
        yuriresponce_data = {}

        class YuriHandler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                pass

            def _read_body(self):
                yuriln = self.headers.get("Content-Length")
                if yuriln:
                    return self.rfile.read(int(yuriln)).decode("utf-8", errors="replace")
                return ""

            def _make_req(self):
                yuriqs = ""
                yuripath = self.path
                if "?" in yuripath:
                    yuripath, yuriqs = yuripath.split("?", 1)
                yuribody = self._read_body()
                yurireq = yurilua.table_from({
                    "method":  self.command,
                    "path":    yuripath,
                    "query":   yuriqs,
                    "body":    yuribody,
                    "headers": yurilua.table_from({
                        str(k): str(v) for k, v in self.headers.items()
                    }),
                })
                return yurireq

            def _handle(self):
                try:
                    yurireq = self._make_req()
                    yuriresptbl = yurihandler_fn(yurireq)
                    yuristatus  = int(yuriresptbl["status"] if yuriresptbl and yuriresptbl["status"] else 200)
                    yuribody2   = str(yuriresptbl["body"]   if yuriresptbl and yuriresptbl["body"]   else "")
                    yurictype   = str(yuriresptbl["type"]   if yuriresptbl and yuriresptbl["type"]   else "text/plain")
                    self.send_response(yuristatus)
                    self.send_header("Content-Type", yurictype)
                    self.send_header("Content-Length", str(len(yuribody2.encode("utf-8"))))
                    self.end_headers()
                    self.wfile.write(yuribody2.encode("utf-8"))
                except Exception as yuriex:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(yuriex).encode())

            def do_GET(self):    self._handle()
            def do_POST(self):   self._handle()
            def do_PUT(self):    self._handle()
            def do_DELETE(self): self._handle()
            def do_PATCH(self):  self._handle()
            def do_HEAD(self):   self._handle()

        yurihttpd = HTTPServer(("", yuriport), YuriHandler)
        yurihttpd.timeout = 0.5
        yuriactive_servers.append(yurihttpd)

        def yurirun():
            while not yuristop.is_set():
                yurihttpd.handle_request()
            yurihttpd.server_close()

        yurithread = threading.Thread(target=yurirun, daemon=True)
        yurithread.start()

        def yuristopfn(_s):
            yurihttpd.server_close()
            if yurihttpd in yuriactive_servers:
                yuriactive_servers.remove(yurihttpd)

        return yurilua.table_from({
            "port":  yuriport,
            "stop":  yuristopfn,
        })

    def yuriresponse(yuribody="", yuristatus=200, yuritype="text/plain"):
        return yurilua.table_from({
            "body":   str(yuribody),
            "status": int(yuristatus),
            "type":   str(yuritype),
        })

    def yurijson_response(yuridata_tbl, yuristatus=200):
        def yuriconvert(yuriv):
            if yuriv is None:              return None
            if isinstance(yuriv, bool):    return yuriv
            if isinstance(yuriv, (int, float)): return yuriv
            if isinstance(yuriv, str):     return yuriv
            try:
                yuriout = {}
                for yurik in yuriv.keys():
                    yuriout[str(yurik)] = yuriconvert(yuriv[yurik])
                return yuriout
            except Exception:
                return str(yuriv)
        try:
            yuriobj = yuriconvert(yuridata_tbl)
            yuribody2 = _json.dumps(yuriobj)
        except Exception as yuriex:
            yuribody2 = '{"error":"' + str(yuriex) + '"}'
        return yurilua.table_from({
            "body":   yuribody2,
            "status": int(yuristatus),
            "type":   "application/json",
        })

    yurig.http = yurilua.table_from({
        "serve":        yurimake_server,
        "response":     yuriresponse,
        "jsonResponse": yurijson_response,
    })
