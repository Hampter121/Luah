import threading
import time as _time
import queue

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

    def __init__(self, yuriwidth: int, yuriheight: int, yurititle: str, yuristopevent: threading.Event):
        self.width        = yuriwidth
        self.height       = yuriheight
        self.title        = yurititle
        self._stop        = yuristopevent
        self._open        = threading.Event()
        self._closed      = threading.Event()
        self._cmd_queue   = queue.Queue()
        self._result_q    = queue.Queue()
        self._bg_color    = (0, 0, 0)
        self._keys_down   = set()
        self._mouse_pos   = (0, 0)
        self._mouse_btn   = [False, False, False]
        self._update_fn   = None
        self._draw_fn     = None
        self._fps         = 60
        self._dt          = 0.0
        self._last_time   = _time.perf_counter()
        self._fps_actual  = 0.0
        self._fonts       = {}

        self._thread = threading.Thread(target=self._pygame_thread, daemon=True)
        self._thread.start()
        self._open.wait(timeout=5.0)

    def get_lua_table(self, yurilua):
        yuriw = self

        def yuricmd(yuriname, *yuriargs):
            if not yuriw._closed.is_set():
                yuriw._cmd_queue.put((yuriname, yuriargs))

        def clear(_s):
            yuricmd("clear")

        def set_bg(_s, yurir, yurig, yurib):
            yuriw._bg_color = (yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib))
            yuricmd("set_bg", yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib))

        def fill(_s, yurir, yurig, yurib):
            yuriw._bg_color = (yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib))
            yuricmd("set_bg", yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib))
            yuricmd("clear")

        def draw_rect(_s, yurix, yuriy, yuriw2, yurih, yurir, yurig, yurib, yuriwidth=1):
            yuricmd("draw_rect", int(yurix), int(yuriy), int(yuriw2), int(yurih),
                    yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib), max(1, int(yuriwidth)))

        def fill_rect(_s, yurix, yuriy, yuriw2, yurih, yurir, yurig, yurib):
            yuricmd("fill_rect", int(yurix), int(yuriy), int(yuriw2), int(yurih),
                    yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib))

        def draw_circle(_s, yurix, yuriy, yurirad, yurir, yurig, yurib, yuriwidth=1):
            yuricmd("draw_circle", int(yurix), int(yuriy), max(1, int(yurirad)),
                    yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib), max(1, int(yuriwidth)))

        def fill_circle(_s, yurix, yuriy, yurirad, yurir, yurig, yurib):
            yuricmd("fill_circle", int(yurix), int(yuriy), max(1, int(yurirad)),
                    yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib))

        def draw_line(_s, yurix1, yuriy1, yurix2, yuriy2, yurir, yurig, yurib, yuriwidth=1):
            yuricmd("draw_line", int(yurix1), int(yuriy1), int(yurix2), int(yuriy2),
                    yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib), max(1, int(yuriwidth)))

        def draw_text(_s, yurix, yuriy, yuritext, yurir=255, yurig=255, yurib=255, yurisize=16):
            yuricmd("draw_text", int(yurix), int(yuriy), str(yuritext),
                    yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib), max(6, int(yurisize)))

        def draw_pixel(_s, yurix, yuriy, yurir, yurig, yurib):
            yuricmd("draw_pixel", int(yurix), int(yuriy),
                    yuriclamp(yurir), yuriclamp(yurig), yuriclamp(yurib))

        def present(_s):
            yuricmd("present")

        def set_title(_s, yurit):
            yuriw.title = str(yurit)
            yuricmd("set_title", str(yurit))

        def close(_s):
            yuriw._closed.set()
            yuricmd("quit")

        def is_open(_s):
            return not yuriw._closed.is_set() and not yuriw._stop.is_set()

        def get_width(_s):    return yuriw.width
        def get_height(_s):   return yuriw.height
        def get_delta(_s):    return yuriw._dt
        def get_fps(_s):      return yuriw._fps_actual

        def is_key_down(_s, yurikey):
            yurik = yurikeymap.get(str(yurikey).lower())
            if yurik is None:
                return False
            return yurik in yuriw._keys_down

        def is_key_up(_s, yurikey):
            yurik = yurikeymap.get(str(yurikey).lower())
            if yurik is None:
                return True
            return yurik not in yuriw._keys_down

        def get_mouse_pos(_s):
            return yuriw._mouse_pos[0], yuriw._mouse_pos[1]

        def is_mouse_down(_s, yuribtn=1):
            yuriidx = max(0, int(yuribtn) - 1)
            if yuriidx >= len(yuriw._mouse_btn):
                return False
            return yuriw._mouse_btn[yuriidx]

        def on_update(_s, yurifn):
            yuriw._update_fn = yurifn

        def on_draw(_s, yurifn):
            yuriw._draw_fn = yurifn

        def run(_s, yurifps=60):
            yuriw._fps = max(1, int(yurifps))
            yuriinterval = 1.0 / yuriw._fps
            yurilast = _time.perf_counter()
            yuriframect = 0
            yurifpstimer = _time.perf_counter()

            while not yuriw._closed.is_set() and not yuriw._stop.is_set():
                yurinow = _time.perf_counter()
                yuriw._dt = yurinow - yurilast
                yurilast = yurinow

                yuriframect += 1
                if yurinow - yurifpstimer >= 1.0:
                    yuriw._fps_actual = yuriframect / (yurinow - yurifpstimer)
                    yuriframect = 0
                    yurifpstimer = yurinow

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

                yurielapsed = _time.perf_counter() - yurinow
                yurisleep = yuriinterval - yurielapsed
                if yurisleep > 0:
                    _time.sleep(yurisleep)

        yuritbl = yurilua.table_from({
            "clear":         clear,
            "setBackground": set_bg,
            "fill":          fill,
            "drawRect":      draw_rect,
            "fillRect":      fill_rect,
            "drawCircle":    draw_circle,
            "fillCircle":    fill_circle,
            "drawLine":      draw_line,
            "drawText":      draw_text,
            "drawPixel":     draw_pixel,
            "present":       present,
            "setTitle":      set_title,
            "close":         close,
            "isOpen":        is_open,
            "getWidth":      get_width,
            "getHeight":     get_height,
            "getDelta":      get_delta,
            "getFPS":        get_fps,
            "isKeyDown":     is_key_down,
            "isKeyUp":       is_key_up,
            "getMousePos":   get_mouse_pos,
            "isMouseDown":   is_mouse_down,
            "onUpdate":      on_update,
            "onDraw":        on_draw,
            "run":           run,
        })
        return yuritbl

    def _pygame_thread(self):
        yuriensure_pygame()
        yuribuildkeymap()

        yuriscreen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        yuriscreen.fill(self._bg_color)
        pygame.display.flip()
        self._open.set()

        yurirunning = True
        while yurirunning and not self._stop.is_set() and not self._closed.is_set():
            try:
                while True:
                    yuricmd, yuriargs = self._cmd_queue.get_nowait()
                    yurirunning = self._handle_cmd(yuriscreen, yuricmd, yuriargs)
                    if not yurirunning:
                        break
            except queue.Empty:
                pass

            for yurievent in pygame.event.get():
                if yurievent.type == pygame.QUIT:
                    yurirunning = False
                    self._closed.set()
                elif yurievent.type == pygame.KEYDOWN:
                    self._keys_down.add(yurievent.key)
                elif yurievent.type == pygame.KEYUP:
                    self._keys_down.discard(yurievent.key)
                elif yurievent.type == pygame.MOUSEMOTION:
                    self._mouse_pos = yurievent.pos
                elif yurievent.type == pygame.MOUSEBUTTONDOWN:
                    if 1 <= yurievent.button <= 3:
                        self._mouse_btn[yurievent.button - 1] = True
                elif yurievent.type == pygame.MOUSEBUTTONUP:
                    if 1 <= yurievent.button <= 3:
                        self._mouse_btn[yurievent.button - 1] = False

            _time.sleep(0.001)

        pygame.display.quit()
        self._closed.set()

    def _handle_cmd(self, yuriscreen, yuricmd, yuriargs):
        if yuricmd == "quit":
            return False
        elif yuricmd == "clear":
            yuriscreen.fill(self._bg_color)
        elif yuricmd == "clear_with_bg":
            yuriscreen.fill(self._bg_color)
        elif yuricmd == "set_bg":
            self._bg_color = yuriargs[:3]
        elif yuricmd == "fill_rect":
            yurix, yuriy, yuriw, yurih, yurir, yurig, yurib = yuriargs
            pygame.draw.rect(yuriscreen, (yurir, yurig, yurib), (yurix, yuriy, yuriw, yurih))
        elif yuricmd == "draw_rect":
            yurix, yuriy, yuriw, yurih, yurir, yurig, yurib, yurilw = yuriargs
            pygame.draw.rect(yuriscreen, (yurir, yurig, yurib), (yurix, yuriy, yuriw, yurih), yurilw)
        elif yuricmd == "fill_circle":
            yurix, yuriy, yurirad, yurir, yurig, yurib = yuriargs
            pygame.draw.circle(yuriscreen, (yurir, yurig, yurib), (yurix, yuriy), yurirad)
        elif yuricmd == "draw_circle":
            yurix, yuriy, yurirad, yurir, yurig, yurib, yurilw = yuriargs
            pygame.draw.circle(yuriscreen, (yurir, yurig, yurib), (yurix, yuriy), yurirad, yurilw)
        elif yuricmd == "draw_line":
            yurix1, yuriy1, yurix2, yuriy2, yurir, yurig, yurib, yurilw = yuriargs
            pygame.draw.line(yuriscreen, (yurir, yurig, yurib), (yurix1, yuriy1), (yurix2, yuriy2), yurilw)
        elif yuricmd == "draw_text":
            yurix, yuriy, yuritext, yurir, yurig, yurib, yurisize = yuriargs
            yurifont = self._get_font(yurisize)
            yurisurf = yurifont.render(str(yuritext), True, (yurir, yurig, yurib))
            yuriscreen.blit(yurisurf, (yurix, yuriy))
        elif yuricmd == "draw_pixel":
            yurix, yuriy, yurir, yurig, yurib = yuriargs
            yuriscreen.set_at((yurix, yuriy), (yurir, yurig, yurib))
        elif yuricmd == "present":
            pygame.display.flip()
        elif yuricmd == "set_title":
            pygame.display.set_caption(yuriargs[0])
        return True

    def _get_font(self, yurisize: int):
        if yurisize not in self._fonts:
            self._fonts[yurisize] = pygame.font.SysFont("monospace", yurisize)
        return self._fonts[yurisize]


def yuriclamp(yuriv) -> int:
    return max(0, min(255, int(yuriv)))


class GraphixManager:

    def __init__(self, yuristopevent: threading.Event):
        self._stop = yuristopevent
        self._wins = []
        self._lock = threading.Lock()

    def create_window(self, yuriwidth, yuriheight, yurititle, yuristopevent):
        yuriwin = GraphixWindow(yuriwidth, yuriheight, yurititle, yuristopevent)
        with self._lock:
            self._wins.append(yuriwin)
        return yuriwin

    def close_all(self):
        with self._lock:
            for yuriwin in self._wins:
                yuriwin._closed.set()
                yuriwin._cmd_queue.put(("quit", ()))
            self._wins.clear()
