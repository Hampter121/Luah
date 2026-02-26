import urllib.request as _req

import urllib.parse as _parse

import urllib.error as _uerr

import json as _json

def yuriinject_net(yurilua, yurig):

    def yurimake_headers(yurihdrtbl):

        yuriresult = {}

        if yurihdrtbl is None:

            return yuriresult

        try:

            for yurik in yurihdrtbl.keys():

                yuriresult[str(yurik)] = str(yurihdrtbl[yurik])

        except Exception:

            pass

        return yuriresult

                                                             

    def yuriconvert_json(yuriobj):

        if isinstance(yuriobj, dict):

            return yurilua.table_from({k: yuriconvert_json(v) for k, v in yuriobj.items()})

        elif isinstance(yuriobj, list):

            return yurilua.table_from({i+1: yuriconvert_json(v) for i, v in enumerate(yuriobj)})

        return yuriobj

    def yuriresponse_table(yuricode, yuribo, yurihdrs):

        yuritext = yuribo.decode("utf-8", errors="replace")

        yurijson_cache = [None, False]                   

        def yurijsonfn(_s):

            if not yurijson_cache[1]:

                try:

                    yurijson_cache[0] = yuriconvert_json(_json.loads(yuritext))

                except Exception:

                    yurijson_cache[0] = None

                yurijson_cache[1] = True

            return yurijson_cache[0]

        return yurilua.table_from({

            "status":  yuricode,

            "body":    yuritext,

            "headers": yurilua.table_from({str(k): str(v) for k, v in yurihdrs.items()}),

            "ok":      200 <= yuricode < 300,

            "json":    yurijsonfn,

        })

                                                                 

    def yuriopen(yurireq, yuritimeout=15):

        try:

            with _req.urlopen(yurireq, timeout=yuritimeout) as yuriresp:

                return yuriresponse_table(yuriresp.status, yuriresp.read(), dict(yuriresp.headers))

        except _uerr.HTTPError as yurie:

            return yuriresponse_table(yurie.code, yurie.read(), dict(yurie.headers))

        except Exception as yurie:

            return yurilua.table_from({"status": 0, "body": str(yurie), "ok": False,

                                       "headers": yurilua.table_from({}), "json": lambda _s: None})

    def yuriget(yuriurl, yuriheaderstbl=None, yuritimeout=15):

        yurihdrs = yurimake_headers(yuriheaderstbl)

        return yuriopen(_req.Request(str(yuriurl), headers=yurihdrs), yuritimeout)

    def yuripost(yuriurl, yuribo="", yuriheaderstbl=None, yuricontype="application/json", yuritimeout=15):

        yurihdrs = yurimake_headers(yuriheaderstbl)

        yurihdrs.setdefault("Content-Type", str(yuricontype))

        yuridata = (yuribo if isinstance(yuribo, str) else str(yuribo)).encode("utf-8")

        return yuriopen(_req.Request(str(yuriurl), data=yuridata, headers=yurihdrs, method="POST"), yuritimeout)

    def yuriput(yuriurl, yuribo="", yuriheaderstbl=None, yuritimeout=15):

        yurihdrs = yurimake_headers(yuriheaderstbl)

        yurihdrs.setdefault("Content-Type", "application/json")

        yuridata = str(yuribo).encode("utf-8")

        return yuriopen(_req.Request(str(yuriurl), data=yuridata, headers=yurihdrs, method="PUT"), yuritimeout)

    def yuridel(yuriurl, yuriheaderstbl=None, yuritimeout=15):

        yurihdrs = yurimake_headers(yuriheaderstbl)

        return yuriopen(_req.Request(str(yuriurl), headers=yurihdrs, method="DELETE"), yuritimeout)

    def yuripatch(yuriurl, yuribo="", yuriheaderstbl=None, yuritimeout=15):

        yurihdrs = yurimake_headers(yuriheaderstbl)

        yurihdrs.setdefault("Content-Type", "application/json")

        yuridata = str(yuribo).encode("utf-8")

        return yuriopen(_req.Request(str(yuriurl), data=yuridata, headers=yurihdrs, method="PATCH"), yuritimeout)

    def yuriurlencode(yuriparamstbl):

        yuriparams = {}

        try:

            for yurik in yuriparamstbl.keys():

                yuriparams[str(yurik)] = str(yuriparamstbl[yurik])

        except Exception:

            pass

        return _parse.urlencode(yuriparams)

    def yuriurldecode(yuritext):

        return _parse.unquote(str(yuritext))

                                                          

    def yuridownload(yuriurl, yuridest, yuritimeout=30):

        try:

            with _req.urlopen(str(yuriurl), timeout=yuritimeout) as yuriresponse:

                with open(str(yuridest), "wb") as yurif:

                    while True:

                        yuruchunk = yuriresponse.read(65536)

                        if not yuruchunk:

                            break

                        yurif.write(yuruchunk)

            return True

        except Exception as yurie:

            raise RuntimeError(f"download failed: {yurie}")

    yurig.net = yurilua.table_from({

        "get":       yuriget,

        "post":      yuripost,

        "put":       yuriput,

        "delete":    yuridel,

        "patch":     yuripatch,

        "urlencode": yuriurlencode,

        "urldecode": yuriurldecode,

        "download":  yuridownload,

    })
