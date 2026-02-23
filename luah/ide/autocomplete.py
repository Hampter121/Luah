import tkinter as tk
import re

yuricompletions = {
    "graphix": ["newWindow(w, h, title)"],

    "win": [
        "clear()",
        "setBackground(r, g, b)",
        "fill(r, g, b)",
        "fillRect(x, y, w, h, r, g, b)",
        "drawRect(x, y, w, h, r, g, b)",
        "fillCircle(x, y, radius, r, g, b)",
        "drawCircle(x, y, radius, r, g, b)",
        "drawLine(x1, y1, x2, y2, r, g, b)",
        "drawText(x, y, text, r, g, b, size)",
        "drawPixel(x, y, r, g, b)",
        "present()",
        "setTitle(title)",
        "close()",
        "isOpen()",
        "getWidth()",
        "getHeight()",
        "getDelta()",
        "getFPS()",
        "isKeyDown(key)",
        "isKeyUp(key)",
        "getMousePos()",
        "isMouseDown(btn)",
        "onUpdate(function(dt) end)",
        "onDraw(function() end)",
        "run(fps)",
    ],

    "math": [
        "abs(x)", "ceil(x)", "floor(x)", "sqrt(x)", "sin(x)", "cos(x)",
        "tan(x)", "max(a, b)", "min(a, b)", "random()", "random(m, n)",
        "randomseed(x)", "pi", "huge", "clamp(v, lo, hi)", "lerp(a, b, t)",
        "sign(v)", "round(v)", "pow(x, y)", "log(x)", "exp(x)",
        "fmod(x, y)", "modf(x)",
    ],

    "string": [
        "format(fmt, ...)", "len(s)", "sub(s, i, j)", "rep(s, n)",
        "reverse(s)", "upper(s)", "lower(s)", "find(s, pattern)",
        "match(s, pattern)", "gmatch(s, pattern)", "gsub(s, pattern, repl)",
        "byte(s, i)", "char(...)",
    ],

    "table": [
        "insert(t, value)", "insert(t, pos, value)", "remove(t, pos)",
        "sort(t)", "sort(t, comp)", "concat(t, sep)", "unpack(t)",
    ],

    "time": ["now()", "clock()", "sleep(seconds)"],

    "fs": [
        "read(path)",
        "write(path, content)",
        "append(path, content)",
        "lines(path)",
        "exists(path)",
        "isFile(path)",
        "isDir(path)",
        "mkdir(path)",
        "delete(path)",
        "copy(src, dst)",
        "move(src, dst)",
        "list(path)",
        "glob(pattern)",
        "size(path)",
        "abspath(path)",
        "basename(path)",
        "dirname(path)",
        "join(a, b)",
        "ext(path)",
        "cwd()",
        "chdir(path)",
    ],

    "json": [
        "encode(value)",
        "decode(text)",
        "pretty(value)",
        "encodeArray(tbl)",
    ],

    "xml": [
        "parse(text)",
        "parseFile(path)",
        "build(tag, text, attrs)",
        "pretty(text)",
        "encode(text)",
        "findAll(text, path)",
    ],

    "net": [
        "get(url)",
        "get(url, headers)",
        "post(url, body)",
        "post(url, body, headers)",
        "put(url, body)",
        "delete(url)",
        "urlencode(params)",
        "urldecode(text)",
        "download(url, dest)",
    ],

    "ws": [
        "connect(url)",
    ],

    "tcp": [
        "connect(host, port)",
        "listen(port)",
        "udpSend(host, port, data)",
    ],

    "concurrent": [
        "thread(fn, ...)",
        "channel()",
        "channel(maxSize)",
        "mutex()",
        "event()",
        "sleep(seconds)",
    ],

    "cli": [
        "args()",
        "getEnv(name)",
        "getEnv(name, default)",
        "setEnv(name, value)",
        "envAll()",
        "exec(cmd)",
        "popen(cmd)",
        "platform()",
        "input(prompt)",
        "color(text, ...colors)",
        "clear()",
        "which(cmd)",
    ],

    "db": [
        "sqlite()",
        "sqlite(path)",
        "sqliteExists(path)",
    ],

    "io": [
        "read()", "write(s)", "lines(filename)",
        "open(filename, mode)", "close(file)",
    ],

    "os": [
        "time()", "clock()", "date(format)", "exit()",
        "getenv(name)",
    ],

    "coroutine": [
        "create(f)", "resume(co, ...)", "yield(...)",
        "status(co)", "wrap(f)", "running()",
    ],
}

yuriglobal_keywords = [
    "print(", "pairs(", "ipairs(", "next(", "type(", "tostring(", "tonumber(",
    "error(", "assert(", "pcall(", "xpcall(", "select(", "unpack(",
    "rawget(", "rawset(", "rawequal(", "setmetatable(", "getmetatable(",
    "require(", "dofile(", "loadstring(", "collectgarbage(",
    "wait(", "graphix", "math", "string", "table", "time", "io", "os", "coroutine",
    "fs", "json", "xml", "net", "ws", "tcp", "concurrent", "cli", "db",
    "local ", "function ", "return ", "if ", "then", "else", "elseif ",
    "end", "do", "while ", "for ", "repeat", "until ", "in ", "not ", "and ", "or ",
    "true", "false", "nil",
]


class LuahAutocomplete:

    def __init__(self, yuriparent, yurieditor: tk.Text, yuricolorsdict: dict, yurifont):
        self._yurieditor   = yurieditor
        self._yuricolors   = yuricolorsdict
        self._yurifont     = yurifont
        self._yuripopup    = None
        self._yurilistbox  = None
        self._yurimatches  = []
        self._yuriactive   = False
        self._yuriafterid  = None
        self._yuriparent   = yuriparent

        yurieditor.bind("<KeyRelease>",  self._yurionkey)
        yurieditor.bind("<Escape>",      lambda yurie: self.yuridismiss())
        yurieditor.bind("<Up>",          self._yurinavigate_up,   add="+")
        yurieditor.bind("<Down>",        self._yurinavigate_down, add="+")
        yurieditor.bind("<Return>",      self._yuriaccept,        add="+")
        yurieditor.bind("<Tab>",         self._yuriaccept,        add="+")
        yurieditor.bind("<FocusOut>",    lambda yurie: self.yuridismiss())
        yurieditor.bind("<ButtonPress>", lambda yurie: self.yuridismiss())

    def _yurionkey(self, yurie):
        yurikeysym = yurie.keysym
        if yurikeysym in ("Escape", "Return", "Up", "Down", "Tab", "Left", "Right"):
            return
        if self._yuriafterid:
            self._yurieditor.after_cancel(self._yuriafterid)
        self._yuriafterid = self._yurieditor.after(120, self._yuritrigger)

    def _yuritrigger(self):
        yuricontext, yuriprefix = self._yuriget_context()
        if yuricontext is None and len(yuriprefix) < 1:
            self.yuridismiss()
            return
        yurimatches = self._yuriget_matches(yuricontext, yuriprefix)
        if not yurimatches:
            self.yuridismiss()
            return
        self._yurimatches = yurimatches
        self._yurishow_popup(yurimatches, yuriprefix)

    def _yuriget_context(self):
        yurieditor = self._yurieditor
        yurilinestart = yurieditor.index("insert linestart")
        yuricipos     = yurieditor.index("insert")
        yuriline      = yurieditor.get(yurilinestart, yuricipos)

        yuridotmatch = re.search(r'(\w+)[.:](\w*)$', yuriline)
        if yuridotmatch:
            return yuridotmatch.group(1), yuridotmatch.group(2)

        yuriwordmatch = re.search(r'(\w+)$', yuriline)
        if yuriwordmatch and len(yuriwordmatch.group(1)) >= 1:
            return None, yuriwordmatch.group(1)

        return None, ""

    def _yuriget_matches(self, yuricontext, yuriprefix):
        yurimatches = []
        if yuricontext is not None:
            yurilookup = yuricompletions.get(yuricontext, [])
            for yuriitem in yurilookup:
                if yuriitem.lower().startswith(yuriprefix.lower()):
                    yurimatches.append(yuriitem)
        else:
            for yurikw in yuriglobal_keywords:
                yuribase = yurikw.rstrip("( ")
                if yuribase.lower().startswith(yuriprefix.lower()):
                    yurimatches.append(yurikw)
            for yurikey in yuricompletions:
                if yurikey.lower().startswith(yuriprefix.lower()) and yurikey not in [m.rstrip("( ") for m in yurimatches]:
                    yurimatches.append(yurikey)
        return yurimatches[:12]

    def _yurishow_popup(self, yurimatches, yuriprefix):
        self.yuridismiss()

        yuribbox = self._yurieditor.bbox("insert")
        if not yuribbox:
            return
        yuribx, yuriby, yuribw, yuribh = yuribbox

        yuriex  = self._yurieditor.winfo_rootx() + yuribx
        yuriey  = self._yurieditor.winfo_rooty() + yuriby + yuribh + 2

        self._yuripopup = tk.Toplevel(self._yurieditor)
        self._yuripopup.wm_overrideredirect(True)
        self._yuripopup.wm_geometry(f"+{yuriex}+{yuriey}")
        self._yuripopup.configure(bg=self._yuricolors["border"])
        self._yuripopup.attributes("-topmost", True)

        yuriframe = tk.Frame(self._yuripopup, bg=self._yuricolors["border"], padx=1, pady=1)
        yuriframe.pack(fill=tk.BOTH, expand=True)

        yurimaxw = max(len(yurim) for yurim in yurimatches)
        yuriwidth = min(max(yurimaxw + 2, 24), 50)

        self._yurilistbox = tk.Listbox(
            yuriframe,
            bg=self._yuricolors["surface"],
            fg=self._yuricolors["text"],
            selectbackground=self._yuricolors["accent2"],
            selectforeground="#000000",
            font=self._yurifont,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            width=yuriwidth,
            height=min(len(yurimatches), 10),
            activestyle="none",
            exportselection=False,
        )
        self._yurilistbox.pack(fill=tk.BOTH, expand=True)

        for yuriitem in yurimatches:
            self._yurilistbox.insert(tk.END, "  " + yuriitem)

        self._yurilistbox.select_set(0)
        self._yurilistbox.bind("<Double-Button-1>", self._yuriaccept)
        self._yurilistbox.bind("<Return>",          self._yuriaccept)

        self._yuriactive = True

    def _yurinavigate_up(self, yurie):
        if not self._yuriactive or not self._yurilistbox:
            return
        yuricur = self._yurilistbox.curselection()
        if yuricur:
            yurinext = max(0, yuricur[0] - 1)
            self._yurilistbox.select_clear(0, tk.END)
            self._yurilistbox.select_set(yurinext)
            self._yurilistbox.see(yurinext)
        return "break"

    def _yurinavigate_down(self, yurie):
        if not self._yuriactive or not self._yurilistbox:
            return
        yuricur = self._yurilistbox.curselection()
        if yuricur:
            yurinext = min(self._yurilistbox.size() - 1, yuricur[0] + 1)
            self._yurilistbox.select_clear(0, tk.END)
            self._yurilistbox.select_set(yurinext)
            self._yurilistbox.see(yurinext)
        return "break"

    def _yuriaccept(self, yurie=None):
        if not self._yuriactive or not self._yurilistbox:
            return
        yurisel = self._yurilistbox.curselection()
        if not yurisel:
            self.yuridismiss()
            return
        yuriraw = self._yurilistbox.get(yurisel[0]).strip()
        self._yuriinsert_completion(yuriraw)
        self.yuridismiss()
        return "break"

    def _yuriinsert_completion(self, yuricompletion: str):
        yurieditor  = self._yurieditor
        yurilinestart = yurieditor.index("insert linestart")
        yuriinsert    = yurieditor.index("insert")
        yuriline      = yurieditor.get(yurilinestart, yuriinsert)

        yuridotmatch = re.search(r'(\w+)[.:](\w*)$', yuriline)
        if yuridotmatch:
            yuriprefix = yuridotmatch.group(2)
        else:
            yuriwordmatch = re.search(r'(\w*)$', yuriline)
            yuriprefix = yuriwordmatch.group(1) if yuriwordmatch else ""

        if yuriprefix:
            yuristart = f"insert-{len(yuriprefix)}c"
            yurieditor.delete(yuristart, "insert")

        yuriname = yuricompletion.split("(")[0].rstrip()

        if "(" in yuricompletion:
            yuriargs = yuricompletion[yuricompletion.index("("):]
            yurieditor.insert("insert", yuriname + yuriargs)
            yuriarglen = len(yuriargs)
            yurieditor.mark_set("insert", f"insert-{yuriarglen - 1}c")
        else:
            yurieditor.insert("insert", yuriname)

    def yuridismiss(self):
        self._yuriactive = False
        if self._yuripopup:
            try:
                self._yuripopup.destroy()
            except Exception:
                pass
            self._yuripopup  = None
            self._yurilistbox = None
