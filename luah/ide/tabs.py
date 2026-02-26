import tkinter as tk

from tkinter import ttk, filedialog, messagebox

import os

from ide.highlighter import LuaHighlighter

from ide.autocomplete import LuahAutocomplete

class LuahTab:

    def __init__(self, yuritabid, yuripath=None):

        self.yuritabid      = yuritabid

        self.yuripath       = yuripath

        self.yuridirty      = False

        self.yuriframe      = None

        self.yurieditor     = None

        self.yurilinenumsw  = None

        self.yurihighlighter= None

        self.yuriautocomplete = None

    @property

    def yuridisplayname(self):

        yuribase = os.path.basename(self.yuripath) if self.yuripath else "untitled.luah"

        return ("• " if self.yuridirty else "") + yuribase

class LuahTabBar:

    def __init__(self, yuriparent, yuricolors, yurifontmono, yurifontmonos, yurifontui,

                 yuriontabchange, yuriontabclose):

        self._yuricolors      = yuricolors

        self._yurifontmono    = yurifontmono

        self._yurifontmonos   = yurifontmonos

        self._yurifontui      = yurifontui

        self._yuriontabchange = yuriontabchange

        self._yuriontabclose  = yuriontabclose

        self._yuritabs        = []

        self._yuriactiveidx   = -1

        self._yuritabidctr    = 0

        self._yuriframe = tk.Frame(yuriparent, bg=yuricolors["surface"], height=34)

        self._yuriframe.pack(fill=tk.X, side=tk.TOP)

        self._yuriframe.pack_propagate(False)

        self._yuritabrow = tk.Frame(self._yuriframe, bg=yuricolors["surface"])

        self._yuritabrow.pack(side=tk.LEFT, fill=tk.Y)

        self._yurinewbtn = tk.Button(

            self._yuriframe, text=" + ", command=self._yurinew_tab,

            bg=yuricolors["surface"], fg=yuricolors["muted"],

            font=yurifontui, relief="flat", cursor="hand2",

            activebackground=yuricolors["border"], activeforeground=yuricolors["text"],

            padx=6, pady=0,

        )

        self._yurinewbtn.pack(side=tk.LEFT, padx=(2, 0))

        self._yurieditorframe = tk.Frame(yuriparent, bg=yuricolors["bg"])

        self._yurieditorframe.pack(fill=tk.BOTH, expand=True)

    def _yurinew_tab(self, yuripath=None, yuricode=None):

        self._yuritabidctr += 1

        yurittab = LuahTab(self._yuritabidctr, yuripath)

        yuriframe = tk.Frame(self._yurieditorframe, bg=self._yuricolors["bg"])

        yurilinenumsw = tk.Text(

            yuriframe,

            width=4, state=tk.DISABLED,

            bg=self._yuricolors["surface"], fg=self._yuricolors["muted"],

            font=self._yurifontmono, relief="flat",

            padx=8, pady=14,

            cursor="arrow",

            selectbackground=self._yuricolors["surface"],

        )

        yurilinenumsw.pack(side=tk.LEFT, fill=tk.Y)

        tk.Frame(yuriframe, bg=self._yuricolors["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)

        yurieditor = tk.Text(

            yuriframe,

            bg=self._yuricolors["bg"], fg=self._yuricolors["text"],

            insertbackground=self._yuricolors["accent"],

            font=self._yurifontmono,

            relief="flat", padx=14, pady=14,

            undo=True,

            selectbackground="#2a3050",

            selectforeground=self._yuricolors["text"],

            wrap=tk.NONE,

            tabs=("    "),

        )

        yurieditor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        yurivscroll = ttk.Scrollbar(yuriframe, orient=tk.VERTICAL)

        yurivscroll.pack(side=tk.RIGHT, fill=tk.Y)

        def yurivscmd(*yuriargs):

            yurieditor.yview(*yuriargs)

            yurilinenumsw.yview(*yuriargs)

        yurivscroll.config(command=yurivscmd)

        def yuriyscroll_set(*yuriargs):

            yurivscroll.set(*yuriargs)

            yurilinenumsw.yview_moveto(yuriargs[0])

        yurieditor.config(yscrollcommand=yuriyscroll_set)

        yurihscroll = ttk.Scrollbar(yuriframe, orient=tk.HORIZONTAL, command=yurieditor.xview)

        yurihscroll.pack(fill=tk.X, side=tk.BOTTOM)

        yurieditor.config(xscrollcommand=yurihscroll.set)

        yurihighlighter = LuaHighlighter(yurieditor,

                                         yurifontname=self._yurifontmono[0],

                                         yurifontsize=self._yurifontmono[1])

        yuriautocomplete = LuahAutocomplete(

            yuriframe, yurieditor, self._yuricolors,

            (self._yurifontmono[0], self._yurifontmono[1] - 1)

        )

        yurittab.yuriframe        = yuriframe

        yurittab.yurieditor       = yurieditor

        yurittab.yurilinenumsw    = yurilinenumsw

        yurittab.yurihighlighter  = yurihighlighter

        yurittab.yuriautocomplete = yuriautocomplete

        if yuricode:

            yurieditor.insert("1.0", yuricode)

        elif yuripath and os.path.exists(yuripath):

            with open(yuripath, "r", encoding="utf-8") as yurif:

                yurieditor.insert("1.0", yurif.read())

        def yurionedit(yurie=None):

            self._yuriupdate_linenums(yurittab)

            yurihighlighter.schedule()

            self._yurimark_dirty(yurittab)

        def yuriauto_indent(yurie):

            import re

            yuriedloc = yurieditor

            yuriline  = yuriedloc.get("insert linestart", "insert lineend")

            yuriindent = len(yuriline) - len(yuriline.lstrip())

            yuristripped = yuriline.rstrip()

            if re.search(r'\b(function|do|then|else|repeat|elseif)\b', yuristripped):

                yuriindent += 4

            yuriedloc.insert("insert", "\n" + " " * yuriindent)

            yurionedit()

            return "break"

        def yurihandle_tab(yurie):

            if yuriautocomplete._yuriactive:

                return

            yurieditor.insert("insert", "    ")

            yurionedit()

            return "break"

        def yurihandle_bs(yurie):

            yuriln = yurieditor.get("insert linestart", "insert")

            if yuriln and yuriln == " " * len(yuriln) and len(yuriln) % 4 == 0:

                yurieditor.delete("insert-4c", "insert")

                yurionedit()

                return "break"

        yurieditor.bind("<KeyRelease>",    yurionedit)

        yurieditor.bind("<ButtonRelease>", yurionedit)

        yurieditor.bind("<Return>",        yuriauto_indent)

        yurieditor.bind("<Tab>",           yurihandle_tab)

        yurieditor.bind("<BackSpace>",     yurihandle_bs)

        self._yuritabs.append(yurittab)

        self._yurirebuild_tabrow()

        self._yuriswitch_to(len(self._yuritabs) - 1)

        self._yuriupdate_linenums(yurittab)

        yurihighlighter.highlight()

        yurittab.yuridirty = False

        self._yurirebuild_tabrow()

        return yurittab

    def _yurirebuild_tabrow(self):

        for yuriw in self._yuritabrow.winfo_children():

            yuriw.destroy()

        for yurii, yurittab in enumerate(self._yuritabs):

            yuriisactive = yurii == self._yuriactiveidx

            yuritabframe = tk.Frame(

                self._yuritabrow,

                bg=self._yuricolors["bg"] if yuriisactive else self._yuricolors["surface"],

                padx=0, pady=0,

            )

            yuritabframe.pack(side=tk.LEFT, fill=tk.Y, padx=(1, 0))

            if yuriisactive:

                tk.Frame(yuritabframe, bg=self._yuricolors["accent"], height=2).pack(fill=tk.X, side=tk.TOP)

            yuriinner = tk.Frame(yuritabframe,

                                 bg=self._yuricolors["bg"] if yuriisactive else self._yuricolors["surface"])

            yuriinner.pack(fill=tk.BOTH, expand=True, padx=2)

            yurilbl = tk.Label(

                yuriinner,

                text=yurittab.yuridisplayname,

                bg=self._yuricolors["bg"] if yuriisactive else self._yuricolors["surface"],

                fg=self._yuricolors["text"] if yuriisactive else self._yuricolors["muted"],

                font=self._yurifontmonos,

                padx=8, pady=6, cursor="hand2",

            )

            yurilbl.pack(side=tk.LEFT)

            yuriidx = yurii

            yurilbl.bind("<Button-1>", lambda yurie, yurii=yuriidx: self._yuriswitch_to(yurii))

            yuritabframe.bind("<Button-1>", lambda yurie, yurii=yuriidx: self._yuriswitch_to(yurii))

            yuriclosebtn = tk.Label(

                yuriinner, text="×",

                bg=self._yuricolors["bg"] if yuriisactive else self._yuricolors["surface"],

                fg=self._yuricolors["muted"],

                font=(self._yurifontui[0], 11), padx=4, cursor="hand2",

            )

            yuriclosebtn.pack(side=tk.LEFT, padx=(0, 4))

            yuriclosebtn.bind("<Button-1>", lambda yurie, yurii=yuriidx: self._yuriclose_tab(yurii))

            yuriclosebtn.bind("<Enter>",    lambda yurie, yuriw=yuriclosebtn: yuriw.config(fg=self._yuricolors["red"]))

            yuriclosebtn.bind("<Leave>",    lambda yurie, yuriw=yuriclosebtn: yuriw.config(fg=self._yuricolors["muted"]))

    def _yuriswitch_to(self, yuriidx):

        if self._yuriactiveidx >= 0 and self._yuriactiveidx < len(self._yuritabs):

            self._yuritabs[self._yuriactiveidx].yuriframe.pack_forget()

        self._yuriactiveidx = yuriidx

        yurittab = self._yuritabs[yuriidx]

        yurittab.yuriframe.pack(fill=tk.BOTH, expand=True)

        yurittab.yurieditor.focus_set()

        self._yurirebuild_tabrow()

        self._yuriontabchange(yurittab)

    def _yuriclose_tab(self, yuriidx):

        yurittab = self._yuritabs[yuriidx]

        if yurittab.yuridirty:

            yuriname = yurittab.yuridisplayname.lstrip("• ")

            yurians = messagebox.askyesnocancel("Unsaved changes",

                f"'{yuriname}' has unsaved changes. Save before closing?")

            if yurians is None:

                return

            if yurians:

                self.save_tab(yurittab)

        yurittab.yuriframe.destroy()

        self._yuritabs.pop(yuriidx)

        self._yuriontabclose(yurittab)

        if not self._yuritabs:

            self._yurinew_tab()

            return

        self._yuriactiveidx = min(yuriidx, len(self._yuritabs) - 1)

        self._yuriswitch_to(self._yuriactiveidx)

    def _yurimark_dirty(self, yurittab):

        yurittab.yuridirty = True

        self._yurirebuild_tabrow()

    def _yuriupdate_linenums(self, yurittab):

        yurieditor = yurittab.yurieditor

        yurilinenumsw = yurittab.yurilinenumsw

        yuricount = int(yurieditor.index("end-1c").split(".")[0])

        yurilinenumsw.config(state=tk.NORMAL)

        yurilinenumsw.delete("1.0", "end")

        for yurii in range(1, yuricount + 1):

            yurilinenumsw.insert("end", f"{yurii}\n")

        yurilinenumsw.config(state=tk.DISABLED)

    def active_tab(self):

        if 0 <= self._yuriactiveidx < len(self._yuritabs):

            return self._yuritabs[self._yuriactiveidx]

        return None

    def new_tab(self, yuripath=None, yuricode=None):

        return self._yurinew_tab(yuripath, yuricode)

    def save_tab(self, yurittab=None):

        if yurittab is None:

            yurittab = self.active_tab()

        if yurittab is None:

            return False

        if yurittab.yuripath:

            with open(yurittab.yuripath, "w", encoding="utf-8") as yurif:

                yurif.write(yurittab.yurieditor.get("1.0", "end-1c"))

            yurittab.yuridirty = False

            self._yurirebuild_tabrow()

            return True

        return self.save_tab_as(yurittab)

    def save_tab_as(self, yurittab=None):

        if yurittab is None:

            yurittab = self.active_tab()

        if yurittab is None:

            return False

        yuripath = filedialog.asksaveasfilename(

            defaultextension=".luah",

            filetypes=[("Luah files", "*.luah"), ("All files", "*.*")])

        if not yuripath:

            return False

        yurittab.yuripath = yuripath

        return self.save_tab(yurittab)

    def open_file(self):

        yuripath = filedialog.askopenfilename(

            filetypes=[("Luah files", "*.luah"), ("All files", "*.*")])

        if not yuripath:

            return None

        for yurii, yurittab in enumerate(self._yuritabs):

            if yurittab.yuripath == yuripath:

                self._yuriswitch_to(yurii)

                return yurittab

        return self._yurinew_tab(yuripath=yuripath)

    def mark_error_line(self, yurilinenum):

        yurittab = self.active_tab()

        if yurittab:

            yurittab.yurihighlighter.mark_error_line(yurilinenum)

    def clear_error_line(self):

        yurittab = self.active_tab()

        if yurittab:

            yurittab.yurihighlighter.clear_error_line()

    def get_code(self):

        yurittab = self.active_tab()

        if yurittab:

            return yurittab.yurieditor.get("1.0", "end-1c")

        return ""

    def insert_snippet(self, yuricode):

        yurittab = self.active_tab()

        if yurittab:

            yurittab.yurieditor.delete("1.0", "end")

            yurittab.yurieditor.insert("1.0", yuricode)

            self._yuriupdate_linenums(yurittab)

            yurittab.yurihighlighter.highlight()

            yurittab.yuridirty = False

            self._yurirebuild_tabrow()

    def all_tabs(self):

        return list(self._yuritabs)
