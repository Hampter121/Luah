import tkinter as tk

from tkinter import ttk

import subprocess

import threading

import os

import sys

import queue

class LuahTerminal:

    def __init__(self, yuriparent, yuricolors, yurifontmono):

        self._yuricolors   = yuricolors

        self._yurifont     = yurifontmono

        self._yuriproc     = None

        self._yurireadq    = queue.Queue()

        self._yurirunning  = False

        self._yuribuild(yuriparent)

        self._yuristart_shell()

    def _yuribuild(self, yuriparent):

        yuriframe = tk.Frame(yuriparent, bg=self._yuricolors["surface"])

        yuriframe.pack(fill=tk.BOTH, expand=True)

        self._yuricontainer = yuriframe

        yuriheader = tk.Frame(yuriframe, bg=self._yuricolors["surface"], height=28)

        yuriheader.pack(fill=tk.X)

        yuriheader.pack_propagate(False)

        tk.Label(yuriheader, text="⬡", bg=self._yuricolors["surface"],

                 fg=self._yuricolors["accent"], font=(self._yurifont[0], 10)).pack(side=tk.LEFT, padx=(10, 4))

        tk.Label(yuriheader, text="TERMINAL", bg=self._yuricolors["surface"],

                 fg=self._yuricolors["muted"], font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT)

        self._yuristatuslbl = tk.Label(yuriheader, text="● running",

                                       bg=self._yuricolors["surface"],

                                       fg=self._yuricolors["green"],

                                       font=("Segoe UI", 8))

        self._yuristatuslbl.pack(side=tk.LEFT, padx=10)

        yurirestartbtn = tk.Button(

            yuriheader, text="↺ Restart", command=self._yurirestartshell,

            bg=self._yuricolors["surface2"], fg=self._yuricolors["muted"],

            font=("Segoe UI", 8), relief="flat", cursor="hand2",

            padx=6, pady=0,

            activebackground=self._yuricolors["border"],

        )

        yurirestartbtn.pack(side=tk.RIGHT, padx=8, pady=4)

        yuriclrbtn = tk.Button(

            yuriheader, text="⌫ Clear", command=self._yuriclear,

            bg=self._yuricolors["surface2"], fg=self._yuricolors["muted"],

            font=("Segoe UI", 8), relief="flat", cursor="hand2",

            padx=6, pady=0,

            activebackground=self._yuricolors["border"],

        )

        yuriclrbtn.pack(side=tk.RIGHT, padx=2, pady=4)

        tk.Frame(yuriframe, bg=self._yuricolors["border"], height=1).pack(fill=tk.X)

        yurioutrow = tk.Frame(yuriframe, bg="#050508")

        yurioutrow.pack(fill=tk.BOTH, expand=True)

        self._yurioutput = tk.Text(

            yurioutrow,

            bg="#050508", fg="#d4d4d4",

            font=self._yurifont,

            relief="flat", padx=10, pady=6,

            state=tk.DISABLED,

            wrap=tk.WORD,

            cursor="arrow",

        )

        self._yurioutput.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        yurisb = ttk.Scrollbar(yurioutrow, orient=tk.VERTICAL, command=self._yurioutput.yview)

        yurisb.pack(side=tk.RIGHT, fill=tk.Y)

        self._yurioutput.config(yscrollcommand=yurisb.set)

        self._yurioutput.tag_config("prompt", foreground=self._yuricolors["accent"])

        self._yurioutput.tag_config("cmd",    foreground=self._yuricolors["text"])

        self._yurioutput.tag_config("stdout", foreground="#d4d4d4")

        self._yurioutput.tag_config("stderr", foreground=self._yuricolors["red"])

        self._yurioutput.tag_config("info",   foreground=self._yuricolors["muted"])

        self._yurioutput.tag_config("success",foreground=self._yuricolors["green"])

        yuriinputrow = tk.Frame(yuriframe, bg="#050508")

        yuriinputrow.pack(fill=tk.X)

        tk.Frame(yuriinputrow, bg=self._yuricolors["border"], height=1).pack(fill=tk.X)

        yuripromptlbl = tk.Label(

            yuriinputrow, text="❯ ",

            bg="#050508", fg=self._yuricolors["accent"],

            font=self._yurifont, padx=8,

        )

        yuripromptlbl.pack(side=tk.LEFT)

        self._yuriinput = tk.Entry(

            yuriinputrow,

            bg="#050508", fg=self._yuricolors["text"],

            insertbackground=self._yuricolors["accent"],

            font=self._yurifont,

            relief="flat",

            selectbackground="#2a3050",

        )

        self._yuriinput.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=6)

        self._yuriinput.bind("<Return>", self._yurisubmit)

        self._yuriinput.bind("<Up>",     self._yurihistory_up)

        self._yuriinput.bind("<Down>",   self._yurihistory_down)

        self._yuriinput.bind("<Tab>",    self._yuritab_complete)

        self._yurihistory     = []

        self._yurihistoryidx  = -1

        self._yuricwd         = os.getcwd()

    def _yuristart_shell(self):

        self._yurirunning = True

        try:

            if sys.platform == "win32":

                yurishellcmd = ["cmd.exe"]

                yurienv = os.environ.copy()

            else:

                yurishellcmd = [os.environ.get("SHELL", "/bin/bash"), "--norc", "--noprofile"]

                yurienv = os.environ.copy()

                yurienv["TERM"] = "dumb"

                yurienv["PS1"] = ""

            self._yuriproc = subprocess.Popen(

                yurishellcmd,

                stdin=subprocess.PIPE,

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                text=True,

                bufsize=1,

                env=yurienv,

                cwd=self._yuricwd,

            )

            self._yuristdoutthread = threading.Thread(

                target=self._yuriread_stream,

                args=(self._yuriproc.stdout, "stdout"),

                daemon=True,

            )

            self._yuristderrthread = threading.Thread(

                target=self._yuriread_stream,

                args=(self._yuriproc.stderr, "stderr"),

                daemon=True,

            )

            self._yuristdoutthread.start()

            self._yuristderrthread.start()

            self._yurilog(f"Shell started. CWD: {self._yuricwd}\n", "info")

            self._yuristatuslbl.config(text="● running", fg=self._yuricolors["green"])

        except Exception as yuriex:

            self._yurilog(f"Failed to start shell: {yuriex}\n", "stderr")

            self._yurilog("Using fallback command mode.\n", "info")

            self._yuriproc = None

            self._yuristatuslbl.config(text="● fallback", fg=self._yuricolors["orange"])

        self._yurioutput.after(50, self._yuriflush_queue)

    def _yuriread_stream(self, yuristream, yuritag):

        try:

            for yuriline in yuristream:

                self._yurireadq.put((yuritag, yuriline))

        except Exception:

            pass

    def _yuriflush_queue(self):

                                                                

        try:

            for _ in range(50):

                yuritag, yuriline = self._yurireadq.get_nowait()

                self._yurilog(yuriline, yuritag)

        except queue.Empty:

            pass

        if self._yurirunning:

            self._yurioutput.after(50, self._yuriflush_queue)

    def _yurisubmit(self, yurie=None):

        yuricmd = self._yuriinput.get().strip()

        if not yuricmd:

            return

        self._yuriinput.delete(0, tk.END)

        self._yurihistory.append(yuricmd)

        self._yurihistoryidx = -1

        self._yurilog("❯ " + yuricmd + "\n", "prompt")

        if self._yuriproc and self._yuriproc.poll() is None:

            try:

                self._yuriproc.stdin.write(yuricmd + "\n")

                self._yuriproc.stdin.flush()

            except Exception as yuriex:

                self._yurilog(f"Write error: {yuriex}\n", "stderr")

        else:

            self._yurirun_fallback(yuricmd)

    def _yurirun_fallback(self, yuricmd):

        def yurirunthread():

            try:

                yuriparts = yuricmd.split()

                if not yuriparts:

                    return

                if yuriparts[0] == "cd":

                    yurinewdir = yuriparts[1] if len(yuriparts) > 1 else os.path.expanduser("~")

                    yurinewdir = os.path.expanduser(yurinewdir)

                    if not os.path.isabs(yurinewdir):

                        yurinewdir = os.path.join(self._yuricwd, yurinewdir)

                    if os.path.isdir(yurinewdir):

                        self._yuricwd = os.path.normpath(yurinewdir)

                        self._yurireadq.put(("success", f"Changed to: {self._yuricwd}\n"))

                    else:

                        self._yurireadq.put(("stderr", f"cd: no such directory: {yurinewdir}\n"))

                    return

                yuriresult = subprocess.run(

                    yuricmd, shell=True, cwd=self._yuricwd,

                    capture_output=True, text=True, timeout=30,

                )

                if yuriresult.stdout:

                    self._yurireadq.put(("stdout", yuriresult.stdout))

                if yuriresult.stderr:

                    self._yurireadq.put(("stderr", yuriresult.stderr))

                if yuriresult.returncode != 0:

                    self._yurireadq.put(("stderr", f"Exit code: {yuriresult.returncode}\n"))

                else:

                    self._yurireadq.put(("success", "✓\n"))

            except subprocess.TimeoutExpired:

                self._yurireadq.put(("stderr", "Command timed out after 30s\n"))

            except Exception as yuriex:

                self._yurireadq.put(("stderr", f"Error: {yuriex}\n"))

        threading.Thread(target=yurirunthread, daemon=True).start()

    def _yurirestartshell(self):

        self._yurilog("\n--- Restarting shell ---\n", "info")

        if self._yuriproc:

            try:

                self._yuriproc.terminate()

            except Exception:

                pass

            self._yuriproc = None

        self._yuristart_shell()

    def _yuriclear(self):

        self._yurioutput.config(state=tk.NORMAL)

        self._yurioutput.delete("1.0", "end")

        self._yurioutput.config(state=tk.DISABLED)

    def _yurilog(self, yuritext, yuritag="stdout"):

                                                                               

        self._yurioutput.config(state=tk.NORMAL)

        self._yurioutput.insert("end", yuritext, yuritag)

        self._yurioutput.see("end")

        self._yurioutput.config(state=tk.DISABLED)

    def _yurihistory_up(self, yurie):

        if not self._yurihistory:

            return "break"

        if self._yurihistoryidx == -1:

            self._yurihistoryidx = len(self._yurihistory) - 1

        elif self._yurihistoryidx > 0:

            self._yurihistoryidx -= 1

        self._yuriinput.delete(0, tk.END)

        self._yuriinput.insert(0, self._yurihistory[self._yurihistoryidx])

        return "break"

    def _yurihistory_down(self, yurie):

        if self._yurihistoryidx == -1:

            return "break"

        if self._yurihistoryidx < len(self._yurihistory) - 1:

            self._yurihistoryidx += 1

            self._yuriinput.delete(0, tk.END)

            self._yuriinput.insert(0, self._yurihistory[self._yurihistoryidx])

        else:

            self._yurihistoryidx = -1

            self._yuriinput.delete(0, tk.END)

        return "break"

    def _yuritab_complete(self, yurie):

        yuritext = self._yuriinput.get()

        if not yuritext:

            return "break"

        yuriparts = yuritext.split()

        if not yuriparts:

            return "break"

        yurilast = yuriparts[-1]

        yuridir  = os.path.dirname(yurilast) or self._yuricwd

        yuribase = os.path.basename(yurilast)

        try:

            yurimatches = [

                yurientry for yurientry in os.listdir(yuridir)

                if yurientry.startswith(yuribase)

            ]

            if len(yurimatches) == 1:

                yuricompleted = os.path.join(yuridir, yurimatches[0]) if os.path.dirname(yurilast) else yurimatches[0]

                yuriparts[-1] = yuricompleted

                self._yuriinput.delete(0, tk.END)

                self._yuriinput.insert(0, " ".join(yuriparts))

            elif yurimatches:

                self._yurilog("\n" + "  ".join(yurimatches) + "\n", "info")

        except Exception:

            pass

        return "break"

    def send_command(self, yuricmd):

        self._yuriinput.delete(0, tk.END)

        self._yuriinput.insert(0, yuricmd)

        self._yurisubmit()

    def focus_input(self):

        self._yuriinput.focus_set()

    def destroy(self):

        self._yurirunning = False

        if self._yuriproc:

            try:

                self._yuriproc.terminate()

            except Exception:

                pass
