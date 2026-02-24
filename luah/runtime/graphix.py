import threading
import time as _time
import queue
import os

try:
    import pygame
except ImportError:
    raise ImportError("pygame is required: pip install pygame")

yuripygameinited = False
yuripygamelock   = threading.Lock()

def yuriensure_pygame():
    global yuripygameinited
    with yuripygamelock:
        if not yuripygameinited:
            pygame.init()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            yuripygameinited = True

yurikeymap = {}

def yuribuildkeymap():
    for yurichar in "abcdefghijklmnopqrstuvwxyz":
        yurikeymap[yurichar] = getattr(pygame, f"K_{yurichar}", None)
    for yuridigit in range(10):
        yurikeymap[str(yuridigit)] = getattr(pygame, f"K_{yuridigit}", None)
    yurispecials = {
        "space": pygame.K_SPACE, "return": pygame.K_RETURN,
        "enter": pygame.K_RETURN, "escape": pygame.K_ESCAPE,
        "esc": pygame.K_ESCAPE, "backspace": pygame.K_BACKSPACE,
        "tab": pygame.K_TAB, "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT, "up": pygame.K_UP,
        "down": pygame.K_DOWN, "lshift": pygame.K_LSHIFT,
        "rshift": pygame.K_RSHIFT, "shift": pygame.K_LSHIFT,
        "lctrl": pygame.K_LCTRL, "rctrl": pygame.K_RCTRL,
        "ctrl": pygame.K_LCTRL, "lalt": pygame.K_LALT,
        "ralt": pygame.K_RALT, "alt": pygame.K_LALT,
        "f1": pygame.K_F1, "f2": pygame.K_F2, "f3": pygame.K_F3,
        "f4": pygame.K_F4, "f5": pygame.K_F5, "f6": pygame.K_F6,
        "f7": pygame.K_F7, "f8": pygame.K_F8, "f9": pygame.K_F9,
        "f10": pygame.K_F10, "f11": pygame.K_F11, "f12": pygame.K_F12,
        "delete": pygame.K_DELETE, "insert": pygame.K_INSERT,
        "home": pygame.K_HOME, "end": pygame.K_END,
        "pageup": pygame.K_PAGEUP, "pagedown": pygame.K_PAGEDOWN,
    }
    yurikeymap.update(yurispecials)


class GraphixWindow:

    def __init__(self, yuriwidth, yuriheight, yurititle, yuristopevent):
        self.width         = yuriwidth
        self.height        = yuriheight
        self.title         = yurititle
        self._stop         = yuristopevent
        self._open         = threading.Event()
        self._closed       = threading.Event()
        self._cmd_queue    = queue.Queue(maxsize=4000)
        self._frame_ready  = threading.Event()
        self._frame_done   = threading.Event()
        self._frame_done.set()  # initially ready
        self._pending_cbs  = queue.Queue()  # cross-thread callback delivery
        self._bg_color     = (0, 0, 0)
        self._keys_down    = set()
        self._mouse_pos    = (0, 0)
        self._mouse_btn    = [False, False, False]
        self._scroll_delta = 0
        self._update_fn    = None
        self._draw_fn      = None
        self._keydown_fn   = None
        self._keyup_fn     = None
        self._mousedown_fn = None
        self._mouseup_fn   = None
        self._scroll_fn    = None
        self._fps          = 60
        self._dt           = 0.0
        self._fps_actual   = 0.0
        self._fonts        = {}
        self._images       = {}
        self._typed_chars  = []
        self._key_events   = []
        self._scroll_events= []
        self._input_lock   = threading.Lock()
        self._alpha        = 255

        self._thread = threading.Thread(target=self._pygame_thread, daemon=True)
        self._thread.start()
        self._open.wait(timeout=5.0)

    def get_lua_table(self, yurilua):
        yuriw = self

        def yuricmd(yuriname, *yuriargs):
            if not yuriw._closed.is_set():
                try:
                    yuriw._cmd_queue.put_nowait((yuriname, yuriargs))
                except queue.Full:
                    pass  # drop command rather than block/crash

        def clear(_s):                      yuricmd("clear")
        def present(_s):                    yuricmd("present")
        def get_width(_s):                  return yuriw.width
        def get_height(_s):                 return yuriw.height
        def get_delta(_s):                  return yuriw._dt
        def get_fps(_s):                    return yuriw._fps_actual

        def set_bg(_s, r, g, b):
            yuriw._bg_color = (yuriclamp(r), yuriclamp(g), yuriclamp(b))
            yuricmd("set_bg", yuriclamp(r), yuriclamp(g), yuriclamp(b))

        def fill(_s, r, g, b):
            yuriw._bg_color = (yuriclamp(r), yuriclamp(g), yuriclamp(b))
            yuricmd("set_bg", yuriclamp(r), yuriclamp(g), yuriclamp(b))
            yuricmd("clear")

        def set_title(_s, t):
            yuriw.title = str(t)
            yuricmd("set_title", str(t))

        def close(_s):
            yuriw._closed.set()
            yuricmd("quit")

        def is_open(_s):
            return not yuriw._closed.is_set() and not yuriw._stop.is_set()

        # ── drawing primitives ──────────────────────────────
        def fill_rect(_s, x, y, w, h, r, g, b):
            yuricmd("fill_rect", int(x), int(y), int(w), int(h),
                    yuriclamp(r), yuriclamp(g), yuriclamp(b), yuriw._alpha)

        def draw_rect(_s, x, y, w, h, r, g, b, lw=1):
            yuricmd("draw_rect", int(x), int(y), int(w), int(h),
                    yuriclamp(r), yuriclamp(g), yuriclamp(b), max(1, int(lw)), yuriw._alpha)

        def fill_circle(_s, x, y, rad, r, g, b):
            yuricmd("fill_circle", int(x), int(y), max(1, int(rad)),
                    yuriclamp(r), yuriclamp(g), yuriclamp(b), yuriw._alpha)

        def draw_circle(_s, x, y, rad, r, g, b, lw=1):
            yuricmd("draw_circle", int(x), int(y), max(1, int(rad)),
                    yuriclamp(r), yuriclamp(g), yuriclamp(b), max(1, int(lw)), yuriw._alpha)

        def draw_line(_s, x1, y1, x2, y2, r, g, b, lw=1):
            yuricmd("draw_line", int(x1), int(y1), int(x2), int(y2),
                    yuriclamp(r), yuriclamp(g), yuriclamp(b), max(1, int(lw)), yuriw._alpha)

        def draw_text(_s, x, y, text, r=255, g=255, b=255, size=16):
            yuricmd("draw_text", int(x), int(y), str(text),
                    yuriclamp(r), yuriclamp(g), yuriclamp(b), max(6, int(size)), yuriw._alpha)

        def draw_pixel(_s, x, y, r, g, b):
            yuricmd("draw_pixel", int(x), int(y),
                    yuriclamp(r), yuriclamp(g), yuriclamp(b))

        # ── NEW: rounded rect ───────────────────────────────
        def fill_round_rect(_s, x, y, w, h, radius, r, g, b):
            yuricmd("fill_round_rect", int(x), int(y), int(w), int(h),
                    max(0, int(radius)), yuriclamp(r), yuriclamp(g), yuriclamp(b), yuriw._alpha)

        def draw_round_rect(_s, x, y, w, h, radius, r, g, b, lw=1):
            yuricmd("draw_round_rect", int(x), int(y), int(w), int(h),
                    max(0, int(radius)), yuriclamp(r), yuriclamp(g), yuriclamp(b), max(1, int(lw)), yuriw._alpha)

        # ── NEW: polygon ────────────────────────────────────
        def fill_polygon(_s, points_tbl, r, g, b):
            yuripts = []
            for i in range(1, len(points_tbl) + 1):
                yuript = points_tbl[i]
                if yuript:
                    yuripts.append((int(yuript[1]), int(yuript[2])))
            if len(yuripts) >= 3:
                yuricmd("fill_polygon", yuripts, yuriclamp(r), yuriclamp(g), yuriclamp(b), yuriw._alpha)

        def draw_polygon(_s, points_tbl, r, g, b, lw=1):
            yuripts = []
            for i in range(1, len(points_tbl) + 1):
                yuript = points_tbl[i]
                if yuript:
                    yuripts.append((int(yuript[1]), int(yuript[2])))
            if len(yuripts) >= 3:
                yuricmd("draw_polygon", yuripts, yuriclamp(r), yuriclamp(g), yuriclamp(b), max(1, int(lw)), yuriw._alpha)

        # ── NEW: image loading ──────────────────────────────
        def load_image(_s, path):
            yurikey = str(path)
            if yurikey not in yuriw._images:
                yuricmd("load_image", yurikey)
                yuriw._images[yurikey] = True
            return yurilua.table_from({
                "_path": yurikey,
                "draw":  lambda imgself, x, y, w=None, h=None: _draw_image(imgself, x, y, w, h),
            })

        def _draw_image(imgself, x, y, w=None, h=None):
            yuripath = imgself["_path"]
            yuricmd("draw_image", str(yuripath), int(x), int(y),
                    int(w) if w is not None else -1,
                    int(h) if h is not None else -1,
                    yuriw._alpha)

        def draw_image(_s, path, x, y, w=None, h=None):
            yuricmd("draw_image", str(path), int(x), int(y),
                    int(w) if w is not None else -1,
                    int(h) if h is not None else -1,
                    yuriw._alpha)

        # ── NEW: text measurement ───────────────────────────
        def get_text_width(_s, text, size=16):
            yurifont = pygame.font.SysFont("monospace", max(6, int(size)))
            return yurifont.size(str(text))[0]

        def get_text_height(_s, size=16):
            yurifont = pygame.font.SysFont("monospace", max(6, int(size)))
            return yurifont.get_height()

        # ── NEW: opacity ────────────────────────────────────
        def set_opacity(_s, yuriopa):
            yuriw._alpha = yuriclamp(int(float(yuriopa) * 255))

        def reset_opacity(_s):
            yuriw._alpha = 255

        # ── input ───────────────────────────────────────────
        def is_key_down(_s, key):
            k = yurikeymap.get(str(key).lower())
            return False if k is None else k in yuriw._keys_down

        def is_key_up(_s, key):
            k = yurikeymap.get(str(key).lower())
            return True if k is None else k not in yuriw._keys_down

        def get_mouse_pos(_s):
            return yuriw._mouse_pos[0], yuriw._mouse_pos[1]

        def is_mouse_down(_s, btn=1):
            idx = max(0, int(btn) - 1)
            return yuriw._mouse_btn[idx] if idx < len(yuriw._mouse_btn) else False

        def get_scroll(_s):
            with yuriw._input_lock:
                yurid = yuriw._scroll_delta
                yuriw._scroll_delta = 0
            return yurid

        # ── NEW: event callbacks ────────────────────────────
        def on_key_down(_s, fn):  yuriw._keydown_fn   = fn
        def on_key_up(_s, fn):    yuriw._keyup_fn     = fn
        def on_mouse_down(_s, fn):yuriw._mousedown_fn = fn
        def on_mouse_up(_s, fn):  yuriw._mouseup_fn   = fn
        def on_scroll(_s, fn):    yuriw._scroll_fn    = fn
        def on_update(_s, fn):    yuriw._update_fn    = fn
        def on_draw(_s, fn):      yuriw._draw_fn      = fn

        def get_typed_chars(_s):
            with yuriw._input_lock:
                yuriresult = list(yuriw._typed_chars)
                yuriw._typed_chars.clear()
            return yurilua.table_from({i+1: v for i,v in enumerate(yuriresult)})

        def get_key_events(_s):
            with yuriw._input_lock:
                yuriresult = list(yuriw._key_events)
                yuriw._key_events.clear()
            return yurilua.table_from({
                i+1: yurilua.table_from({
                    "key": ev["key"], "char": ev["char"],
                    "ctrl": ev["ctrl"], "shift": ev["shift"], "alt": ev["alt"],
                })
                for i, ev in enumerate(yuriresult)
            })

        def get_scroll_events(_s):
            with yuriw._input_lock:
                yuriresult = list(yuriw._scroll_events)
                yuriw._scroll_events.clear()
            return yurilua.table_from({i+1: v for i,v in enumerate(yuriresult)})

        def run(_s, fps=60):
            yuriw._fps = max(1, int(fps))
            yuriinterval = 1.0 / yuriw._fps
            yurilast     = _time.perf_counter()
            yuriframect  = 0
            yurifpstimer = _time.perf_counter()

            while not yuriw._closed.is_set() and not yuriw._stop.is_set():
                yurinow      = _time.perf_counter()
                yuriw._dt    = yurinow - yurilast
                yurilast     = yurinow
                yuriframect += 1
                if yurinow - yurifpstimer >= 1.0:
                    yuriw._fps_actual = yuriframect / (yurinow - yurifpstimer)
                    yuriframect  = 0
                    yurifpstimer = yurinow

                try:
                    # drain cross-thread callbacks safely on the Lua thread
                    while True:
                        cb = yuriw._pending_cbs.get_nowait()
                        try:
                            kind = cb[0]
                            if kind == "keydown"   and yuriw._keydown_fn:
                                yuriw._keydown_fn(cb[1], cb[2])
                            elif kind == "keyup"   and yuriw._keyup_fn:
                                yuriw._keyup_fn(cb[1])
                            elif kind == "mousedown" and yuriw._mousedown_fn:
                                yuriw._mousedown_fn(cb[1], cb[2], cb[3])
                            elif kind == "mouseup"  and yuriw._mouseup_fn:
                                yuriw._mouseup_fn(cb[1], cb[2], cb[3])
                            elif kind == "scroll"   and yuriw._scroll_fn:
                                yuriw._scroll_fn(cb[1])
                        except Exception:
                            if not yuriw._stop.is_set():
                                raise
                except queue.Empty:
                    pass

                try:
                    if yuriw._update_fn:
                        yuriw._update_fn(yuriw._dt)
                    yuricmd("clear_with_bg")
                    if yuriw._draw_fn:
                        yuriw._draw_fn()
                    yuricmd("present")
                except Exception:
                    if not yuriw._stop.is_set():
                        raise

                # wait for pygame to finish this frame before queuing next
                yuriw._frame_done.wait(timeout=0.1)
                yuriw._frame_done.clear()

                yurielapsed = _time.perf_counter() - yurinow
                yurisleep   = yuriinterval - yurielapsed
                if yurisleep > 0:
                    _time.sleep(yurisleep)

        return yurilua.table_from({
            "clear":           clear,
            "present":         present,
            "setBackground":   set_bg,
            "fill":            fill,
            "setTitle":        set_title,
            "close":           close,
            "isOpen":          is_open,
            "getWidth":        get_width,
            "getHeight":       get_height,
            "getDelta":        get_delta,
            "getFPS":          get_fps,
            "fillRect":        fill_rect,
            "drawRect":        draw_rect,
            "fillCircle":      fill_circle,
            "drawCircle":      draw_circle,
            "drawLine":        draw_line,
            "drawText":        draw_text,
            "drawPixel":       draw_pixel,
            "fillRoundRect":   fill_round_rect,
            "drawRoundRect":   draw_round_rect,
            "fillPolygon":     fill_polygon,
            "drawPolygon":     draw_polygon,
            "loadImage":       load_image,
            "drawImage":       draw_image,
            "getTextWidth":    get_text_width,
            "getTextHeight":   get_text_height,
            "setOpacity":      set_opacity,
            "resetOpacity":    reset_opacity,
            "isKeyDown":       is_key_down,
            "isKeyUp":         is_key_up,
            "getMousePos":     get_mouse_pos,
            "isMouseDown":     is_mouse_down,
            "getScroll":       get_scroll,
            "onKeyDown":       on_key_down,
            "onKeyUp":         on_key_up,
            "onMouseDown":     on_mouse_down,
            "onMouseUp":       on_mouse_up,
            "onScroll":        on_scroll,
            "onUpdate":        on_update,
            "onDraw":          on_draw,
            "getTypedChars":   get_typed_chars,
            "getKeyEvents":    get_key_events,
            "getScrollEvents": get_scroll_events,
            "run":             run,
        })

    def _pygame_thread(self):
        yuriensure_pygame()
        yuribuildkeymap()

        yuriscreen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        yuriscreen.fill(self._bg_color)
        pygame.display.flip()
        self._open.set()

        yuriimages = {}
        yurirunning = True

        while yurirunning and not self._stop.is_set() and not self._closed.is_set():
            try:
                while True:
                    yuricmd, yuriargs = self._cmd_queue.get_nowait()
                    yurirunning = self._handle_cmd(yuriscreen, yuricmd, yuriargs, yuriimages)
                    if not yurirunning:
                        break
            except queue.Empty:
                pass

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    yurirunning = False
                    self._closed.set()

                elif ev.type == pygame.KEYDOWN:
                    self._keys_down.add(ev.key)
                    mods   = pygame.key.get_mods()
                    ctrl   = bool(mods & pygame.KMOD_CTRL)
                    shift  = bool(mods & pygame.KMOD_SHIFT)
                    alt    = bool(mods & pygame.KMOD_ALT)
                    name   = pygame.key.name(ev.key)
                    char   = ev.unicode if ev.unicode else ""
                    with self._input_lock:
                        if char and not ctrl and not alt:
                            self._typed_chars.append(char)
                        self._key_events.append({
                            "key": name, "char": char,
                            "ctrl": ctrl, "shift": shift, "alt": alt,
                        })
                    if self._keydown_fn:
                        try:
                            self._pending_cbs.put_nowait(("keydown", name, char))
                        except queue.Full:
                            pass

                elif ev.type == pygame.KEYUP:
                    self._keys_down.discard(ev.key)
                    if self._keyup_fn:
                        try:
                            self._pending_cbs.put_nowait(("keyup", pygame.key.name(ev.key)))
                        except queue.Full:
                            pass

                elif ev.type == pygame.MOUSEMOTION:
                    self._mouse_pos = ev.pos

                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    if 1 <= ev.button <= 3:
                        self._mouse_btn[ev.button - 1] = True
                    if self._mousedown_fn:
                        try:
                            self._pending_cbs.put_nowait(("mousedown", ev.pos[0], ev.pos[1], ev.button))
                        except queue.Full:
                            pass

                elif ev.type == pygame.MOUSEBUTTONUP:
                    if 1 <= ev.button <= 3:
                        self._mouse_btn[ev.button - 1] = False
                    if self._mouseup_fn:
                        try:
                            self._pending_cbs.put_nowait(("mouseup", ev.pos[0], ev.pos[1], ev.button))
                        except queue.Full:
                            pass

                elif ev.type == pygame.MOUSEWHEEL:
                    with self._input_lock:
                        self._scroll_delta += ev.y
                        self._scroll_events.append(ev.y)
                    if self._scroll_fn:
                        try:
                            self._pending_cbs.put_nowait(("scroll", ev.y))
                        except queue.Full:
                            pass

            _time.sleep(0.001)

        pygame.display.quit()
        self._closed.set()

    def _handle_cmd(self, screen, cmd, args, images):
        if cmd == "quit":
            return False
        elif cmd in ("clear", "clear_with_bg"):
            screen.fill(self._bg_color)
        elif cmd == "set_bg":
            self._bg_color = args[:3]
        elif cmd == "present":
            pygame.display.flip()
            self._frame_done.set()
        elif cmd == "set_title":
            pygame.display.set_caption(args[0])

        elif cmd == "fill_rect":
            x, y, w, h, r, g, b, a = args
            if a >= 255:
                pygame.draw.rect(screen, (r, g, b), (x, y, w, h))
            else:
                yurisurf = pygame.Surface((max(1,w), max(1,h)), pygame.SRCALPHA)
                yurisurf.fill((r, g, b, a))
                screen.blit(yurisurf, (x, y))

        elif cmd == "draw_rect":
            x, y, w, h, r, g, b, lw, a = args
            if a >= 255:
                pygame.draw.rect(screen, (r, g, b), (x, y, w, h), lw)
            else:
                yurisurf = pygame.Surface((max(1,w), max(1,h)), pygame.SRCALPHA)
                pygame.draw.rect(yurisurf, (r, g, b, a), (0, 0, w, h), lw)
                screen.blit(yurisurf, (x, y))

        elif cmd == "fill_circle":
            x, y, rad, r, g, b, a = args
            if a >= 255:
                pygame.draw.circle(screen, (r, g, b), (x, y), rad)
            else:
                yurisurf = pygame.Surface((rad*2+1, rad*2+1), pygame.SRCALPHA)
                pygame.draw.circle(yurisurf, (r, g, b, a), (rad, rad), rad)
                screen.blit(yurisurf, (x - rad, y - rad))

        elif cmd == "draw_circle":
            x, y, rad, r, g, b, lw, a = args
            if a >= 255:
                pygame.draw.circle(screen, (r, g, b), (x, y), rad, lw)
            else:
                yurisurf = pygame.Surface((rad*2+lw+1, rad*2+lw+1), pygame.SRCALPHA)
                pygame.draw.circle(yurisurf, (r, g, b, a), (rad+lw//2, rad+lw//2), rad, lw)
                screen.blit(yurisurf, (x - rad, y - rad))

        elif cmd == "draw_line":
            x1, y1, x2, y2, r, g, b, lw, a = args
            pygame.draw.line(screen, (r, g, b), (x1, y1), (x2, y2), lw)

        elif cmd == "draw_text":
            x, y, text, r, g, b, size, a = args
            font = self._get_font(size)
            surf = font.render(str(text), True, (r, g, b))
            if a < 255:
                surf.set_alpha(a)
            screen.blit(surf, (x, y))

        elif cmd == "draw_pixel":
            x, y, r, g, b = args
            screen.set_at((x, y), (r, g, b))

        elif cmd == "fill_round_rect":
            x, y, w, h, radius, r, g, b, a = args
            radius = min(radius, w // 2, h // 2)
            if a >= 255:
                pygame.draw.rect(screen, (r, g, b), (x, y, w, h), border_radius=radius)
            else:
                yurisurf = pygame.Surface((max(1,w), max(1,h)), pygame.SRCALPHA)
                pygame.draw.rect(yurisurf, (r, g, b, a), (0, 0, w, h), border_radius=radius)
                screen.blit(yurisurf, (x, y))

        elif cmd == "draw_round_rect":
            x, y, w, h, radius, r, g, b, lw, a = args
            radius = min(radius, w // 2, h // 2)
            if a >= 255:
                pygame.draw.rect(screen, (r, g, b), (x, y, w, h), lw, border_radius=radius)
            else:
                yurisurf = pygame.Surface((max(1,w), max(1,h)), pygame.SRCALPHA)
                pygame.draw.rect(yurisurf, (r, g, b, a), (0, 0, w, h), lw, border_radius=radius)
                screen.blit(yurisurf, (x, y))

        elif cmd == "fill_polygon":
            pts, r, g, b, a = args
            if a >= 255:
                pygame.draw.polygon(screen, (r, g, b), pts)
            else:
                sw, sh = screen.get_size()
                yurisurf = pygame.Surface((sw, sh), pygame.SRCALPHA)
                pygame.draw.polygon(yurisurf, (r, g, b, a), pts)
                screen.blit(yurisurf, (0, 0))

        elif cmd == "draw_polygon":
            pts, r, g, b, lw, a = args
            pygame.draw.polygon(screen, (r, g, b), pts, lw)

        elif cmd == "load_image":
            path = args[0]
            if path not in images:
                try:
                    images[path] = pygame.image.load(path).convert_alpha()
                except Exception:
                    images[path] = None

        elif cmd == "draw_image":
            path, x, y, w, h, a = args
            if path not in images:
                try:
                    images[path] = pygame.image.load(path).convert_alpha()
                except Exception:
                    images[path] = None
            img = images.get(path)
            if img:
                if w > 0 and h > 0:
                    img = pygame.transform.scale(img, (w, h))
                if a < 255:
                    img = img.copy()
                    img.set_alpha(a)
                screen.blit(img, (x, y))

        return True

    def _get_font(self, size):
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont("monospace", size)
        return self._fonts[size]


def yuriclamp(v):
    return max(0, min(255, int(v)))


class GraphixManager:

    def __init__(self, yuristopevent):
        self._stop = yuristopevent
        self._wins = []
        self._lock = threading.Lock()

    def create_window(self, w, h, title, stop):
        win = GraphixWindow(w, h, title, stop)
        with self._lock:
            self._wins.append(win)
        return win

    def close_all(self):
        with self._lock:
            for win in self._wins:
                win._closed.set()
                win._cmd_queue.put(("quit", ()))
            self._wins.clear()
