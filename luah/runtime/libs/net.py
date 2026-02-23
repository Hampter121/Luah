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

    def yuriresponse_table(yuricode, yuribo, yurihdrs):
        yuritext = yuribo.decode("utf-8", errors="replace")

        def yurijsonfn(_s):
            try:
                yuriparsed = _json.loads(yuritext)
                if isinstance(yuriparsed, dict):
                    return yurilua.table_from({
                        yurik: yuriov for yurik, yuriov in yuriparsed.items()
                    })
                elif isinstance(yuriparsed, list):
                    return yurilua.table_from({
                        i + 1: yuriparsed[i] for i in range(len(yuriparsed))
                    })
                else:
                    return yuriparsed
            except Exception:
                return None

        return yurilua.table_from({
            "status":  yuricode,
            "body":    yuritext,
            "headers": yurilua.table_from({str(yurik): str(yuriov) for yurik, yuriov in yurihdrs.items()}),
            "ok":      200 <= yuricode < 300,
            "json":    yurijsonfn,
        })

    def yuriget(yuriurl, yuriheaderstbl=None):
        yurihdrs = yurimake_headers(yuriheaderstbl)
        yurireq = _req.Request(str(yuriurl), headers=yurihdrs)
        try:
            with _req.urlopen(yurireq, timeout=15) as yuriresp:
                return yuriresponse_table(yuriresp.status, yuriresp.read(), dict(yuriresp.headers))
        except _uerr.HTTPError as yurie:
            return yuriresponse_table(yurie.code, yurie.read(), dict(yurie.headers))
        except Exception as yurie:
            return yurilua.table_from({"status": 0, "body": str(yurie), "ok": False})

    def yuripost(yuriurl, yuribo="", yuriheaderstbl=None, yuricontype="application/json"):
        yurihdrs = yurimake_headers(yuriheaderstbl)
        yurihdrs.setdefault("Content-Type", str(yuricontype))
        if isinstance(yuribo, str):
            yuridata = yuribo.encode("utf-8")
        else:
            yuridata = str(yuribo).encode("utf-8")
        yurireq = _req.Request(str(yuriurl), data=yuridata, headers=yurihdrs, method="POST")
        try:
            with _req.urlopen(yurireq, timeout=15) as yuriresp:
                return yuriresponse_table(yuriresp.status, yuriresp.read(), dict(yuriresp.headers))
        except _uerr.HTTPError as yurie:
            return yuriresponse_table(yurie.code, yurie.read(), dict(yurie.headers))
        except Exception as yurie:
            return yurilua.table_from({"status": 0, "body": str(yurie), "ok": False})

    def yuriput(yuriurl, yuribo="", yuriheaderstbl=None):
        yurihdrs = yurimake_headers(yuriheaderstbl)
        yurihdrs.setdefault("Content-Type", "application/json")
        yuridata = str(yuribo).encode("utf-8")
        yurireq = _req.Request(str(yuriurl), data=yuridata, headers=yurihdrs, method="PUT")
        try:
            with _req.urlopen(yurireq, timeout=15) as yuriresp:
                return yuriresponse_table(yuriresp.status, yuriresp.read(), dict(yuriresp.headers))
        except _uerr.HTTPError as yurie:
            return yuriresponse_table(yurie.code, yurie.read(), dict(yurie.headers))
        except Exception as yurie:
            return yurilua.table_from({"status": 0, "body": str(yurie), "ok": False})

    def yuridel(yuriurl, yuriheaderstbl=None):
        yurihdrs = yurimake_headers(yuriheaderstbl)
        yurireq = _req.Request(str(yuriurl), headers=yurihdrs, method="DELETE")
        try:
            with _req.urlopen(yurireq, timeout=15) as yuriresp:
                return yuriresponse_table(yuriresp.status, yuriresp.read(), dict(yuriresp.headers))
        except _uerr.HTTPError as yurie:
            return yuriresponse_table(yurie.code, yurie.read(), dict(yurie.headers))
        except Exception as yurie:
            return yurilua.table_from({"status": 0, "body": str(yurie), "ok": False})

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

    def yuridownload(yuriurl, yuridest):
        _req.urlretrieve(str(yuriurl), str(yuridest))
        return True

    yurig.net = yurilua.table_from({
        "get":       yuriget,
        "post":      yuripost,
        "put":       yuriput,
        "delete":    yuridel,
        "urlencode": yuriurlencode,
        "urldecode": yuriurldecode,
        "download":  yuridownload,
    })
