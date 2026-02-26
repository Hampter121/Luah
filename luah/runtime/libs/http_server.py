import threading

import json as _json

import queue as _queue

from http.server import HTTPServer, BaseHTTPRequestHandler

def yuriinject_http(yurilua, yurig, yuristop):

    yuriactive_servers = []

    def yurimake_server(yuriport, yurihandler_fn):

        yuriport   = int(yuriport)

                                                                                         

        yurireq_q  = _queue.Queue()

        yuriresp_q = _queue.Queue()

        class YuriHandler(BaseHTTPRequestHandler):

            def log_message(self, fmt, *args):

                pass

            def _read_body(self):

                yuriln = self.headers.get("Content-Length")

                if yuriln:

                    try:

                        return self.rfile.read(int(yuriln)).decode("utf-8", errors="replace")

                    except Exception:

                        return ""

                return ""

            def _handle(self):

                try:

                    yuriqs   = ""

                    yuripath = self.path

                    if "?" in yuripath:

                        yuripath, yuriqs = yuripath.split("?", 1)

                    yuribody = self._read_body()

                                                                                               

                    yurireq_q.put({

                        "method":  self.command,

                        "path":    yuripath,

                        "query":   yuriqs,

                        "body":    yuribody,

                        "headers": {str(k): str(v) for k, v in self.headers.items()},

                    })

                                                         

                    yuriresptuple = yuriresp_q.get(timeout=10)

                    yuristatus = yuriresptuple[0]

                    yurirbody  = yuriresptuple[1]

                    yurictype  = yuriresptuple[2]

                    yuriencoded = yurirbody.encode("utf-8")

                    self.send_response(yuristatus)

                    self.send_header("Content-Type", yurictype)

                    self.send_header("Content-Length", str(len(yuriencoded)))

                    self.end_headers()

                    self.wfile.write(yuriencoded)

                except Exception as yuriex:

                    try:

                        self.send_response(500)

                        self.end_headers()

                        self.wfile.write(str(yuriex).encode())

                    except Exception:

                        pass

            do_GET    = _handle

            do_POST   = _handle

            do_PUT    = _handle

            do_DELETE = _handle

            do_PATCH  = _handle

            do_HEAD   = _handle

                                                                                    

        from http.server import ThreadingHTTPServer

        yurihttpd         = ThreadingHTTPServer(("", yuriport), YuriHandler)

        yurihttpd.timeout = 0.5

        yuriactive_servers.append(yurihttpd)

        yurirunning = [True]

        def yurihttp_thread():

            while yurirunning[0] and not yuristop.is_set():

                yurihttpd.handle_request()

            yurihttpd.server_close()

        threading.Thread(target=yurihttp_thread, daemon=True).start()

                                                                                 

        def yuripump(_s):

            try:

                yuripyreq = yurireq_q.get_nowait()

                yurireq_lua = yurilua.table_from({

                    "method":  yuripyreq["method"],

                    "path":    yuripyreq["path"],

                    "query":   yuripyreq["query"],

                    "body":    yuripyreq["body"],

                    "headers": yurilua.table_from(yuripyreq["headers"]),

                })

                yuriresptbl = yurihandler_fn(yurireq_lua)

                yuristatus  = int(yuriresptbl["status"] if yuriresptbl and yuriresptbl["status"] else 200)

                yurirbody   = str(yuriresptbl["body"]   if yuriresptbl and yuriresptbl["body"]   else "")

                yurictype   = str(yuriresptbl["type"]   if yuriresptbl and yuriresptbl["type"]   else "text/plain")

                yuriresp_q.put((yuristatus, yurirbody, yurictype))

                return True

            except _queue.Empty:

                return False

        def yuristopfn(_s):

            yurirunning[0] = False

            yurihttpd.server_close()

            if yurihttpd in yuriactive_servers:

                yuriactive_servers.remove(yurihttpd)

        def yurihas_request(_s):

            return not yurireq_q.empty()

        return yurilua.table_from({

            "port":       yuriport,

            "stop":       yuristopfn,

            "pump":       yuripump,

            "hasRequest": yurihas_request,

        })

    def yuriresponse(yuribody="", yuristatus=200, yuritype="text/plain"):

        return yurilua.table_from({

            "body":   str(yuribody),

            "status": int(yuristatus),

            "type":   str(yuritype),

        })

    def yurijson_response(yuridata_tbl, yuristatus=200):

        def yuriconvert(yuriv):

            if yuriv is None:                   return None

            if isinstance(yuriv, bool):         return yuriv

            if isinstance(yuriv, (int, float)): return yuriv

            if isinstance(yuriv, str):          return yuriv

            try:

                yuriout = {}

                for yurik in yuriv.keys():

                    yuriout[str(yurik)] = yuriconvert(yuriv[yurik])

                return yuriout

            except Exception:

                return str(yuriv)

        try:

            yuriobj   = yuriconvert(yuridata_tbl)

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
