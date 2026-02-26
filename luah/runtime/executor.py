import threading

import time as _time

import queue

import traceback

import os

import platform as _platform

import sys as _sys

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

from runtime.graphix          import GraphixManager

from runtime.libs.fs          import yuriinject_fs

from runtime.libs.json_lib    import yuriinject_json

from runtime.libs.xml_lib     import yuriinject_xml

from runtime.libs.net         import yuriinject_net

from runtime.libs.ws          import yuriinject_ws

from runtime.libs.tcp         import yuriinject_tcp

from runtime.libs.concurrent  import yuriinject_concurrent

from runtime.libs.cli         import yuriinject_cli

from runtime.libs.db          import yuriinject_db

from runtime.libs.sound       import yuriinject_sound

from runtime.libs.http_server import yuriinject_http

                                             

LUAH_VERSION = "1.2"

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

                                                               

        def yuriprintfn(*yuriargs):

            yuriparts = []

            for a in yuriargs:

                if a is None:    yuriparts.append("nil")

                elif a is True:  yuriparts.append("true")

                elif a is False: yuriparts.append("false")

                else:            yuriparts.append(str(a))

            self.output_callback("\t".join(yuriparts))

        yurig.print = yuriprintfn

                                                                      

        def yuriwaitfn(yurisecs):

            yurisecs = float(yurisecs)

            deadline = _time.perf_counter() + yurisecs

            while _time.perf_counter() < deadline:

                if yuristop.is_set():

                    raise RuntimeError("Script stopped by user.")

                yuriremaining = deadline - _time.perf_counter()

                _time.sleep(min(0.002, yuriremaining))

        yurig.wait = yuriwaitfn

        yuristart = _time.time()

        yurig.time = yurilua.table_from({

            "now":   lambda: _time.time() - yuristart,

            "clock": lambda: _time.perf_counter(),

            "sleep": yuriwaitfn,

            "stamp": lambda: _time.strftime("%Y-%m-%d %H:%M:%S"),

        })

                                            

        yurig.luah = yurilua.table_from({

            "version":  LUAH_VERSION,

            "platform": _platform.system().lower(),

            "arch":     _platform.machine(),

            "python":   _sys.version.split()[0],

        })

                                                               

        yuriloaded  = {}

        yuribasedir = os.path.dirname(os.path.abspath(yuripath)) if yuripath else os.getcwd()

        def yurirequire(yurimodname):

            yurimodname = str(yurimodname)

            if yurimodname in yuriloaded:

                return yuriloaded[yurimodname]

            for yuricandidate in [

                os.path.join(yuribasedir, yurimodname),

                os.path.join(yuribasedir, yurimodname + ".luah"),

                os.path.join(yuribasedir, yurimodname + ".lua"),

                os.path.join(os.getcwd(),  yurimodname),

                os.path.join(os.getcwd(),  yurimodname + ".luah"),

                os.path.join(os.getcwd(),  yurimodname + ".lua"),

            ]:

                if os.path.isfile(yuricandidate):

                    with open(yuricandidate, "r", encoding="utf-8") as yurif:

                        yurisrc = yurif.read()

                                                                                             

                    yuriloaded[yurimodname] = "__loading__"

                    yuriresult = yurilua.execute(yurisrc)

                    yuriloaded[yurimodname] = yuriresult                            

                    return yuriresult

            raise LuaError(f"module '{yurimodname}' not found")

        yurig.require = yurirequire

                                                               

        yurilua.execute("""
            local _orig = tostring
            tostring = function(v)
                if v == true  then return "true"
                elseif v == false then return "false"
                else return _orig(v) end
            end
        """)

                                                                                    

        yurilua.execute("math.randomseed(os.time())")

                                                               

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
            math.map   = function(v, a1, b1, a2, b2)
                return a2 + (v - a1) / (b1 - a1) * (b2 - a2)
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

                                                               

                                                      

                                             

        yurilua.execute("""
            function string.split(str, sep)
                local out, i = {}, 1
                if sep == nil or sep == "" then
                    for part in str:gmatch("%S+") do out[i] = part; i = i + 1 end
                else
                    local plain = true
                    local s = 1
                    while true do
                        local a, b = str:find(sep, s, plain)
                        if not a then
                            out[i] = str:sub(s)
                            break
                        end
                        out[i] = str:sub(s, a - 1)
                        i = i + 1
                        s = b + 1
                    end
                end
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
                local need = len - #str
                if need > 0 then
                    str = string.rep(char, math.ceil(need / #char)):sub(1, need) .. str
                end
                return str
            end
            function string.padRight(str, len, char)
                char = char or " "
                local need = len - #str
                if need > 0 then
                    str = str .. string.rep(char, math.ceil(need / #char)):sub(1, need)
                end
                return str
            end
            function string.count(str, sub)
                local n = 0
                local s = 1
                while true do
                    local a = str:find(sub, s, true)
                    if not a then break end
                    n = n + 1
                    s = a + #sub
                end
                return n
            end
            function string.replace(str, old, new, maxn)
                local out, n, s = {}, 0, 1
                while true do
                    local a, b = str:find(old, s, true)
                    if not a or (maxn and n >= maxn) then
                        table.insert(out, str:sub(s))
                        break
                    end
                    table.insert(out, str:sub(s, a-1))
                    table.insert(out, new)
                    n = n + 1
                    s = b + 1
                end
                return table.concat(out)
            end
        """)

                                                               

                                                                         

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
                for _, v in pairs(t) do if v == val then return true end end
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
            function table.find(t, fn)
                for i, v in ipairs(t) do
                    if fn(v, i) then return v, i end
                end
                return nil
            end
            function table.flatten(t, depth)
                depth = depth or 1
                local out, i = {}, 1
                for _, v in ipairs(t) do
                    if type(v) == "table" and depth > 0 then
                        for _, w in ipairs(table.flatten(v, depth-1)) do
                            out[i] = w; i = i + 1
                        end
                    else
                        out[i] = v; i = i + 1
                    end
                end
                return out
            end
            function table.count(t)
                local n = 0
                for _ in pairs(t) do n = n + 1 end
                return n
            end
            function table.reverse(t)
                local out, n = {}, #t
                for i = 1, n do out[i] = t[n - i + 1] end
                return out
            end
            function table.slice(t, from, to)
                local out, i = {}, 1
                to = to or #t
                for j = from, to do out[i] = t[j]; i = i + 1 end
                return out
            end
            function table.unique(t)
                local seen, out, i = {}, {}, 1
                for _, v in ipairs(t) do
                    if not seen[v] then seen[v] = true; out[i] = v; i = i + 1 end
                end
                return out
            end
        """)

                                                               

        def yurinewwindow(w, h, title="Luah", fullscreen=False, borderless=False):

            win = yurigraphixmgr.create_window(

                int(w), int(h), str(title), yuristop, bool(fullscreen), bool(borderless)

            )

            return win.get_lua_table(yurilua)

        yurig.graphix = yurilua.table_from({

            "newWindow": yurinewwindow,

            "version":   LUAH_VERSION,

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

        yuriinject_sound(yurilua, yurig)

        yuriinject_http(yurilua, yurig, yuristop)

    def _emit_error(self, yurimsg):

        self.error_callback(str(yurimsg))
