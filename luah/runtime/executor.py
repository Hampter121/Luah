import threading
import time as _time
import queue
import traceback
import os
import re as _re

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

from runtime.graphix        import GraphixManager
from runtime.libs.fs        import yuriinject_fs
from runtime.libs.json_lib  import yuriinject_json
from runtime.libs.xml_lib   import yuriinject_xml
from runtime.libs.net       import yuriinject_net
from runtime.libs.ws        import yuriinject_ws
from runtime.libs.tcp       import yuriinject_tcp
from runtime.libs.concurrent import yuriinject_concurrent
from runtime.libs.cli       import yuriinject_cli
from runtime.libs.db        import yuriinject_db
from runtime.libs.sound     import yuriinject_sound
from runtime.libs.http_server import yuriinject_http


class LuaForgeRuntime:

    def __init__(self, output_callback=None, error_callback=None):
        self.output_callback  = output_callback or print
        self.error_callback   = error_callback or print
        self._thread          = None
        self._stop_event      = threading.Event()
        self._graphix_manager = None

    def execute(self, yuricode, yuripath=None):
        if self._thread and self._thread.is_alive():
            self._emit_error("A script is already running. Stop it first.")
            return False
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run, args=(yuricode, yuripath), daemon=True
        )
        self._thread.start()
        return True

    def stop(self):
        self._stop_event.set()
        if self._graphix_manager:
            self._graphix_manager.close_all()

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def _run(self, yuricode, yuripath=None):
        try:
            yurilua = LuaRuntime(unpack_returned_tuples=True)
            self._graphix_manager = GraphixManager(self._stop_event)
            self._inject_libs(yurilua, self._graphix_manager, yuripath)
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

    def _inject_libs(self, yurilua, yurigraphixmgr, yuripath=None):
        yuristop = self._stop_event
        yurig    = yurilua.globals()

        # ── print ────────────────────────────────────────────
        def yuriprintfn(*yuriargs):
            yuriparts = []
            for a in yuriargs:
                if a is None:          yuriparts.append("nil")
                elif a is True:        yuriparts.append("true")
                elif a is False:       yuriparts.append("false")
                else:                  yuriparts.append(str(a))
            self.output_callback("\t".join(yuriparts))
        yurig.print = yuriprintfn

        # ── wait / time ──────────────────────────────────────
        def yuriwaitfn(yurisecs):
            yurisecs = float(yurisecs)
            deadline = _time.time() + yurisecs
            while _time.time() < deadline:
                if yuristop.is_set():
                    raise RuntimeError("Script stopped by user.")
                _time.sleep(0.01)
        yurig.wait = yuriwaitfn

        yuristart = _time.time()
        yurig.time = yurilua.table_from({
            "now":   lambda: _time.time() - yuristart,
            "clock": lambda: _time.perf_counter(),
            "sleep": yuriwaitfn,
            "stamp": lambda: _time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        # ── luah meta globals ────────────────────────────────
        import platform as _platform
        import sys as _sys
        yurig.luah = yurilua.table_from({
            "version":  "1.1",
            "platform": _platform.system().lower(),
            "arch":     _platform.machine(),
            "python":   _sys.version.split()[0],
        })

        # ── require (load other .luah/.lua files) ────────────
        yuriloaded = {}
        yuribasedir = os.path.dirname(os.path.abspath(yuripath)) if yuripath else os.getcwd()

        def yurirequire(yurimodname):
            yurimodname = str(yurimodname)
            if yurimodname in yuriloaded:
                return yuriloaded[yurimodname]
            yuricandidates = [
                os.path.join(yuribasedir, yurimodname),
                os.path.join(yuribasedir, yurimodname + ".luah"),
                os.path.join(yuribasedir, yurimodname + ".lua"),
                os.path.join(os.getcwd(), yurimodname),
                os.path.join(os.getcwd(), yurimodname + ".luah"),
                os.path.join(os.getcwd(), yurimodname + ".lua"),
            ]
            for yuricandidate in yuricandidates:
                if os.path.isfile(yuricandidate):
                    with open(yuricandidate, "r", encoding="utf-8") as yurif:
                        yurisrc = yurif.read()
                    yuriresult = yurilua.execute(yurisrc)
                    yuriloaded[yurimodname] = yuriresult if yuriresult is not None else True
                    return yuriloaded[yurimodname]
            raise LuaError(f"module '{yurimodname}' not found")
        yurig.require = yurirequire

        # ── tostring fix ─────────────────────────────────────
        yurilua.execute("""
            local _orig = tostring
            tostring = function(v)
                if v == true then return "true"
                elseif v == false then return "false"
                else return _orig(v) end
            end
        """)

        # ── math extras ──────────────────────────────────────
        yurilua.execute("""
            math.clamp = function(v, lo, hi)
                if v < lo then return lo elseif v > hi then return hi end return v
            end
            math.lerp  = function(a, b, t) return a + (b - a) * t end
            math.sign  = function(v)
                if v > 0 then return 1 elseif v < 0 then return -1 else return 0 end
            end
            math.round = function(v) return math.floor(v + 0.5) end
            math.dist  = function(x1, y1, x2, y2)
                return math.sqrt((x2-x1)^2 + (y2-y1)^2)
            end
            math.uuid  = function()
                local t = {"xxxxxxxx","-","xxxx","-","4xxx","-","yxxx","-","xxxxxxxxxxxx"}
                local res = ""
                for _, part in ipairs(t) do
                    res = res .. part:gsub("[xy]", function(c)
                        local v = (c == "x") and math.random(0,15) or math.random(8,11)
                        return string.format("%x", v)
                    end)
                end
                return res
            end
        """)

        # ── string extras ────────────────────────────────────
        yurilua.execute("""
            function string.split(str, sep)
                local out, i = {}, 1
                local pat = sep and ("[^"..sep.."]+") or "%S+"
                for part in str:gmatch(pat) do out[i] = part; i = i + 1 end
                return out
            end
            function string.trim(str)
                return str:match("^%s*(.-)%s*$")
            end
            function string.startsWith(str, prefix)
                return str:sub(1, #prefix) == prefix
            end
            function string.endsWith(str, suffix)
                return suffix == "" or str:sub(-#suffix) == suffix
            end
            function string.contains(str, sub)
                return str:find(sub, 1, true) ~= nil
            end
            function string.padLeft(str, len, char)
                char = char or " "
                while #str < len do str = char .. str end
                return str
            end
            function string.padRight(str, len, char)
                char = char or " "
                while #str < len do str = str .. char end
                return str
            end
        """)

        # ── table extras ─────────────────────────────────────
        yurilua.execute("""
            function table.map(t, fn)
                local out = {}
                for i, v in ipairs(t) do out[i] = fn(v, i) end
                return out
            end
            function table.filter(t, fn)
                local out, j = {}, 1
                for i, v in ipairs(t) do
                    if fn(v, i) then out[j] = v; j = j + 1 end
                end
                return out
            end
            function table.reduce(t, fn, init)
                local acc = init
                for i, v in ipairs(t) do acc = fn(acc, v, i) end
                return acc
            end
            function table.contains(t, val)
                for _, v in ipairs(t) do if v == val then return true end end
                return false
            end
            function table.keys(t)
                local out, i = {}, 1
                for k in pairs(t) do out[i] = k; i = i + 1 end
                return out
            end
            function table.values(t)
                local out, i = {}, 1
                for _, v in pairs(t) do out[i] = v; i = i + 1 end
                return out
            end
            function table.clone(t)
                local out = {}
                for k, v in pairs(t) do out[k] = v end
                return out
            end
            function table.merge(a, b)
                local out = table.clone(a)
                for k, v in pairs(b) do out[k] = v end
                return out
            end
        """)

        # ── graphix ──────────────────────────────────────────
        def yurinewwindow(w, h, title="Luah"):
            win = yurigraphixmgr.create_window(int(w), int(h), str(title), yuristop)
            return win.get_lua_table(yurilua)

        yurig.graphix = yurilua.table_from({
            "newWindow": yurinewwindow,
            "version":   "1.1",
        })

        # ── all libs ─────────────────────────────────────────
        yuriinject_fs(yurilua, yurig)
        yuriinject_json(yurilua, yurig)
        yuriinject_xml(yurilua, yurig)
        yuriinject_net(yurilua, yurig)
        yuriinject_ws(yurilua, yurig, yuristop)
        yuriinject_tcp(yurilua, yurig, yuristop)
        yuriinject_concurrent(yurilua, yurig, yuristop)
        yuriinject_cli(yurilua, yurig)
        yuriinject_db(yurilua, yurig)
        yuriinject_sound(yurilua, yurig)
        yuriinject_http(yurilua, yurig, yuristop)

    def _emit_error(self, yurimsg):
        self.error_callback(str(yurimsg))
