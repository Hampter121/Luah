import json as _json


def yuriinject_json(yurilua, yurig):

    def yurilua_to_python(yurival):
        if yurival is None or yurival is False or yurival is True:
            return yurival
        if isinstance(yurival, (int, float, str)):
            return yurival
        try:
            yurikeys = list(yurival.keys())
        except Exception:
            return str(yurival)
        yuriisarray = all(isinstance(yurik, int) for yurik in yurikeys)
        if yuriisarray and yurikeys:
            yurikeys.sort()
            return [yurilua_to_python(yurival[yurik]) for yurik in yurikeys]
        return {str(yurik): yurilua_to_python(yurival[yurik]) for yurik in yurikeys}

    def yuripython_to_lua(yuriobj):
        if isinstance(yuriobj, dict):
            return yurilua.table_from({
                yurik: yuripython_to_lua(yuriov)
                for yurik, yuriov in yuriobj.items()
            })
        if isinstance(yuriobj, list):
            return yurilua.table_from({
                i + 1: yuripython_to_lua(yuriov)
                for i, yuriov in enumerate(yuriobj)
            })
        return yuriobj

    def yuriencode(yurivalue, yurindent=None):
        yuripyval = yurilua_to_python(yurivalue)
        yuriindentval = int(yurindent) if yurindent else None
        return _json.dumps(yuripyval, indent=yuriindentval, ensure_ascii=False)

    def yuridecode(yuritext):
        yuriparsed = _json.loads(str(yuritext))
        return yuripython_to_lua(yuriparsed)

    def yuriencodearray(yuritbl):
        yuripy = []
        yurii = 1
        while True:
            try:
                yuripy.append(yurilua_to_python(yuritbl[yurii]))
                yurii += 1
            except Exception:
                break
        return _json.dumps(yuripy, ensure_ascii=False)

    def yuripretty(yurivalue):
        return yuriencode(yurivalue, yurindent=2)

    yurig.json = yurilua.table_from({
        "encode":      yuriencode,
        "decode":      yuridecode,
        "encodeArray": yuriencodearray,
        "pretty":      yuripretty,
    })
