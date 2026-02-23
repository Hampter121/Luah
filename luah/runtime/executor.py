import threading
import time as _time
import queue
import traceback

try:
    try:
        from lupa.lua54 import LuaRuntime, LuaError
    except ImportError:
        try:
            from lupa.lua51 import LuaRuntime, LuaError
        except ImportError:
            from lupa import LuaRuntime, LuaError
except ImportError:
    raise ImportError("lupa is required: pip install lupa")

from runtime.graphix import GraphixManager
from runtime.libs.fs         import yuriinject_fs
from runtime.libs.json_lib   import yuriinject_json
from runtime.libs.xml_lib    import yuriinject_xml
from runtime.libs.net        import yuriinject_net
from runtime.libs.ws         import yuriinject_ws
from runtime.libs.tcp        import yuriinject_tcp
from runtime.libs.concurrent import yuriinject_concurrent
from runtime.libs.cli        import yuriinject_cli
from runtime.libs.db         import yuriinject_db


class LuaForgeRuntime:

    def __init__(self, output_callback=None, error_callback=None):
        self.output_callback  = output_callback or print
        self.error_callback   = error_callback or print
        self._thread          = None
        self._stop_event      = threading.Event()
        self._graphix_manager = None

    def execute(self, yuricode: str):
        if self._thread and self._thread.is_alive():
            self._emit_error("A script is already running. Stop it first.")
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run, args=(yuricode,), daemon=True
        )
        self._thread.start()
        return True

    def stop(self):
        self._stop_event.set()
        if self._graphix_manager:
            self._graphix_manager.close_all()

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def _run(self, yuricode: str):
        try:
            yurilua = LuaRuntime(unpack_returned_tuples=True)
            self._graphix_manager = GraphixManager(self._stop_event)
            self._inject_libs(yurilua, self._graphix_manager)
            yurilua.execute(yuricode)
        except LuaError as yuriex:
            yurimsg = str(yuriex)
            if "LuaError:" in yurimsg:
                yurimsg = yurimsg.split("LuaError:")[-1].strip()
            self._emit_error(yurimsg)
        except Exception as yuriex:
            if not self._stop_event.is_set():
                self._emit_error(traceback.format_exc())
        finally:
            if self._graphix_manager:
                self._graphix_manager.close_all()
            self._graphix_manager = None

    def _inject_libs(self, yurilua: LuaRuntime, yurigraphixmgr):
        yuristop = self._stop_event

        def yuriprintfn(*yuriargs):
            yuriparts = []
            for yuriarg in yuriargs:
                if yuriarg is None:
                    yuriparts.append("nil")
                elif yuriarg is True:
                    yuriparts.append("true")
                elif yuriarg is False:
                    yuriparts.append("false")
                else:
                    yuriparts.append(str(yuriarg))
            self.output_callback("\t".join(yuriparts))

        yurilua.globals().print = yuriprintfn

        def yuriwaitfn(yuriseconds):
            yuriseconds = float(yuriseconds)
            yurideadline = _time.time() + yuriseconds
            while _time.time() < yurideadline:
                if yuristop.is_set():
                    raise RuntimeError("Script stopped by user.")
                _time.sleep(0.01)

        yurilua.globals().wait = yuriwaitfn

        yurilua.execute("""
            local _orig_tostring = tostring
            tostring = function(v)
                if v == true then return "true"
                elseif v == false then return "false"
                else return _orig_tostring(v) end
            end
        """)

        yurilua.execute("time = {}")
        yurig = yurilua.globals()

        class YuriTimeClass:
            pass

        yuritmobj = YuriTimeClass()
        yuristart = _time.time()
        yuritmobj.now   = lambda: _time.time() - yuristart
        yuritmobj.clock = lambda: _time.perf_counter()
        yuritmobj.sleep = yuriwaitfn

        yurig.time = yurilua.table_from({
            "now":   yuritmobj.now,
            "clock": yuritmobj.clock,
            "sleep": yuritmobj.sleep,
        })

        yurilua.execute("""
            math.clamp = function(v, lo, hi)
                if v < lo then return lo end
                if v > hi then return hi end
                return v
            end
            math.lerp = function(a, b, t)
                return a + (b - a) * t
            end
            math.sign = function(v)
                if v > 0 then return 1
                elseif v < 0 then return -1
                else return 0 end
            end
            math.round = function(v)
                return math.floor(v + 0.5)
            end
        """)

        def yurinewwindow(yuriwidth, yuriheight, yurititle="graphix"):
            yuriwidth, yuriheight = int(yuriwidth), int(yuriheight)
            yuriwin = yurigraphixmgr.create_window(yuriwidth, yuriheight, str(yurititle), yuristop)
            return yuriwin.get_lua_table(yurilua)

        yurig.graphix = yurilua.table_from({
            "newWindow": yurinewwindow,
            "version":   "1.0",
        })

        yuriinject_fs(yurilua, yurig)
        yuriinject_json(yurilua, yurig)
        yuriinject_xml(yurilua, yurig)
        yuriinject_net(yurilua, yurig)
        yuriinject_ws(yurilua, yurig, yuristop)
        yuriinject_tcp(yurilua, yurig, yuristop)
        yuriinject_concurrent(yurilua, yurig, yuristop)
        yuriinject_cli(yurilua, yurig)
        yuriinject_db(yurilua, yurig)

    def _emit_error(self, yurimsg: str):
        self.error_callback(str(yurimsg))
