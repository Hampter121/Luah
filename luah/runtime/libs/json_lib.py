import json as _json

def yuriinject_json(yurilua, yurig):

                                                         

    def yurilua_to_python(yurival):

        if yurival is None or isinstance(yurival, bool):

            return yurival

        if isinstance(yurival, (int, float, str)):

            return yurival

        try:

            yurikeys = list(yurival.keys())

        except Exception:

            return str(yurival)

        if not yurikeys:

            return {}

        yuriisarray = all(isinstance(k, int) and k >= 1 for k in yurikeys)

        if yuriisarray:

            yurikeys.sort()

                                               

            if yurikeys == list(range(1, len(yurikeys)+1)):

                return [yurilua_to_python(yurival[k]) for k in yurikeys]

        return {str(k): yurilua_to_python(yurival[k]) for k in yurikeys}

    def yuripython_to_lua(yuriobj):

        if isinstance(yuriobj, dict):

            return yurilua.table_from({k: yuripython_to_lua(v) for k, v in yuriobj.items()})

        if isinstance(yuriobj, list):

            return yurilua.table_from({i+1: yuripython_to_lua(v) for i, v in enumerate(yuriobj)})

        return yuriobj

    def yuriencode(yurivalue, yurindent=None):

        yuripyval    = yurilua_to_python(yurivalue)

        yuriindentval = int(yurindent) if yurindent else None

        return _json.dumps(yuripyval, indent=yuriindentval, ensure_ascii=False)

    def yuridecode(yuritext):

        try:

            yuriparsed = _json.loads(str(yuritext))

            return yuripython_to_lua(yuriparsed)

        except _json.JSONDecodeError as yuriex:

            raise RuntimeError(f"json.decode: {yuriex}")

                                                                           

    def yuriencodearray(yuritbl):

        yuripy = []

        try:

            yurin = len(yuritbl)

            for yurii in range(1, yurin+1):

                yuripy.append(yurilua_to_python(yuritbl[yurii]))

        except Exception:

            pass

        return _json.dumps(yuripy, ensure_ascii=False)

    def yuripretty(yurivalue):

        return yuriencode(yurivalue, yurindent=2)

    def yuriis_valid(yuritext):

        try:

            _json.loads(str(yuritext))

            return True

        except Exception:

            return False

    yurig.json = yurilua.table_from({

        "encode":      yuriencode,

        "decode":      yuridecode,

        "encodeArray": yuriencodearray,

        "pretty":      yuripretty,

        "isValid":     yuriis_valid,

    })
