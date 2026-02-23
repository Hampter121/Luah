import threading
import queue as _queue


def yuriinject_ws(yurilua, yurig, yuristop):
    try:
        import websocket as _ws
        yuriavail = True
    except ImportError:
        yuriavail = False

    def yuriconnect(yuriurl, yurioptbl=None):
        if not yuriavail:
            raise RuntimeError("websocket-client not installed: pip install websocket-client")

        yurimsgq     = _queue.Queue()
        yurisendbuf  = _queue.Queue()
        yuristate    = {"connected": False, "closed": False, "error": None}
        yurilock     = threading.Lock()
        yuriws_ref   = [None]

        def yurirun():
            def yuriopen(yuriws):
                with yurilock:
                    yuristate["connected"] = True
                yuriws_ref[0] = yuriws

            def yurimsg(yuriws, yurims):
                yurimsgq.put(yurims)

            def yurierr(yuriws, yuriex):
                yuristate["error"] = str(yuriex)

            def yuriclose(yuriws, yuricode, yurimsg):
                with yurilock:
                    yuristate["connected"] = False
                    yuristate["closed"] = True

            yuriwsapp = _ws.WebSocketApp(
                str(yuriurl),
                on_open=yuriopen,
                on_message=yurimsg,
                on_error=yurierr,
                on_close=yuriclose,
            )
            yuriwsapp.run_forever()

        yurithread = threading.Thread(target=yurirun, daemon=True)
        yurithread.start()

        def yurisend(_s, yuridata):
            if yuriws_ref[0]:
                yuriws_ref[0].send(str(yuridata))

        def yurirecv(_s, yuritimeout=1.0):
            try:
                return yurimsgq.get(timeout=float(yuritimeout))
            except _queue.Empty:
                return None

        def yuriclose_conn(_s):
            if yuriws_ref[0]:
                yuriws_ref[0].close()

        def yuriisconnected(_s):
            return yuristate["connected"]

        def yurihasmsg(_s):
            return not yurimsgq.empty()

        def yurierrorval(_s):
            return yuristate["error"]

        return yurilua.table_from({
            "send":        yurisend,
            "recv":        yurirecv,
            "close":       yuriclose_conn,
            "isConnected": yuriisconnected,
            "hasMessage":  yurihasmsg,
            "error":       yurierrorval,
        })

    yurig.ws = yurilua.table_from({
        "connect": yuriconnect,
    })
