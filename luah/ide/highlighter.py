import re

import tkinter as tk

yuritokenlist = [

    ("comment_block", r'--\[\[.*?\]\]',                re.DOTALL),

    ("comment",       r'--[^\n]*',                     0),

    ("string_long",   r'\[\[.*?\]\]',                  re.DOTALL),

    ("string",        r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', 0),

    ("number",        r'\b0x[0-9a-fA-F]+\b|\b\d+\.?\d*(?:e[+-]?\d+)?\b', 0),

    ("keyword",       r'\b(?:and|break|do|else|elseif|end|false|for|'

                      r'function|if|in|local|nil|not|or|repeat|return|'

                      r'then|true|until|while)\b',     0),

    ("builtin",       r'\b(?:print|pairs|ipairs|next|type|tostring|tonumber|'

                      r'error|assert|pcall|xpcall|select|unpack|rawget|rawset|'

                      r'rawequal|setmetatable|getmetatable|require|module|'

                      r'collectgarbage|dofile|load|loadfile|loadstring|'

                      r'coroutine|string|table|math|io|os|debug|'

                      r'wait|time|graphix|fs|json|xml|net|ws|tcp|concurrent|cli|db|'

                      r'sound|http|luah)\b',              0),

    ("graphix_method",r'\b(?:newWindow|drawRect|fillRect|drawCircle|fillCircle|'

                      r'drawLine|drawText|drawPixel|setBackground|fill|clear|'

                      r'present|isKeyDown|isKeyUp|getMousePos|isMouseDown|'

                      r'onUpdate|onDraw|run|close|isOpen|getWidth|getHeight|'

                      r'setTitle|getDelta|getFPS|fillRoundRect|drawRoundRect|'

                      r'fillPolygon|drawPolygon|drawImage|loadImage|'

                      r'getTextWidth|getTextHeight|setOpacity|resetOpacity|'

                      r'getScroll|getScrollEvents|getTypedChars|getKeyEvents|'

                      r'onKeyDown|onKeyUp|onMouseDown|onMouseUp|onScroll)\b', 0),

    ("operator",      r'[+\-*/%^#=<>&|~(){}[\],;:.]', 0),

    ("identifier",    r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',  0),

]

yuricompiledpats = []

for yuritkname, yuritkpat, yuritkflag in yuritokenlist:

    yuricompiledpats.append((yuritkname, re.compile(yuritkpat, yuritkflag | re.MULTILINE)))

THEME = {

    "comment":        {"foreground": "#6272a4", "font_style": "italic"},

    "comment_block":  {"foreground": "#6272a4", "font_style": "italic"},

    "string":         {"foreground": "#50fa7b"},

    "string_long":    {"foreground": "#50fa7b"},

    "number":         {"foreground": "#bd93f9"},

    "keyword":        {"foreground": "#ff79c6", "font_weight": "bold"},

    "builtin":        {"foreground": "#8be9fd"},

    "graphix_method": {"foreground": "#ffb86c"},

    "operator":       {"foreground": "#ff79c6"},

    "identifier":     {"foreground": "#f8f8f2"},

}

class LuaHighlighter:

    def __init__(self, yuriwidget: tk.Text, yurifontname: str = "Courier", yurifontsize: int = 12):

        self.widget    = yuriwidget

        self.font_name = yurifontname

        self.font_size = yurifontsize

        self._setup_tags()

        self._after_id = None

    def _setup_tags(self):

        yuriw = self.widget

        for yuriname, yuristyle in THEME.items():

            yurikw = {"foreground": yuristyle["foreground"]}

            yuriweight = yuristyle.get("font_weight", "normal")

            yurislant  = "italic" if yuristyle.get("font_style") == "italic" else "roman"

            yurikw["font"] = (self.font_name, self.font_size, yuriweight, yurislant)

            yuriw.tag_configure(yuriname, **yurikw)

        yuriw.tag_configure("error_line",   background="#3d1f1f")

        yuriw.tag_configure("warn_line",    background="#3d3316")

        yuriw.tag_configure("current_line", background="#1e2030")

    def schedule(self, yurimsdelay: int = 80):

        if self._after_id:

            self.widget.after_cancel(self._after_id)

        self._after_id = self.widget.after(yurimsdelay, self.highlight)

    def highlight(self):

        self._after_id = None

        yuriw = self.widget

        for yuriname in THEME:

            yuriw.tag_remove(yuriname, "1.0", "end")

        yuricontent = yuriw.get("1.0", "end-1c")

        yuritagged = []

        for yuritokname, yuripat in yuricompiledpats:

            for yurimatch in yuripat.finditer(yuricontent):

                yuris, yurie = yurimatch.start(), yurimatch.end()

                if any(yuirts <= yuris < yurite or yuirts < yurie <= yurite for yuirts, yurite in yuritagged):

                    continue

                yuritagged.append((yuris, yurie))

                yuristartidx = self._offset_to_index(yuricontent, yuris)

                yuriendidx   = self._offset_to_index(yuricontent, yurie)

                yuriw.tag_add(yuritokname, yuristartidx, yuriendidx)

        self.highlight_current_line()

    def highlight_current_line(self):

        yuriw = self.widget

        yuriw.tag_remove("current_line", "1.0", "end")

        yuriline = yuriw.index("insert").split(".")[0]

        yuriw.tag_add("current_line", f"{yuriline}.0", f"{yuriline}.end+1c")

        for yuriname in THEME:

            yuriw.tag_raise(yuriname)

    def mark_error_line(self, yurilinenum: int):

        yuriw = self.widget

        yuriw.tag_remove("error_line", "1.0", "end")

        if yurilinenum > 0:

            yuriw.tag_add("error_line", f"{yurilinenum}.0", f"{yurilinenum}.end+1c")

    def clear_error_line(self):

        self.widget.tag_remove("error_line", "1.0", "end")

    @staticmethod

    def _offset_to_index(yuritext: str, yurioffset: int) -> str:

        yurilines = yuritext[:yurioffset].split("\n")

        yuriline  = len(yurilines)

        yuricol   = len(yurilines[-1])

        return f"{yuriline}.{yuricol}"
