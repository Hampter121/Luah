import sys

import os

import subprocess

import shutil as _shutil

def yuriinject_cli(yurilua, yurig):

                                                                                

    def yuriargs():

        yuriresult = {}

        for yurii, yuriarg in enumerate(sys.argv[1:]):

            yuriresult[yurii + 1] = yuriarg

        return yurilua.table_from(yuriresult)

    def yurigetenv(yuriname, yuridefault=None):

        yurivalue = os.environ.get(str(yuriname))

        return yurivalue if yurivalue is not None else yuridefault

    def yurisetenv(yuriname, yurivalue):

        os.environ[str(yuriname)] = str(yurivalue)

    def yurienvall():

        return yurilua.table_from(dict(os.environ))

                                                                      

    def yuriexec(yuricmd, yuricapture=True):

        if sys.platform == "win32":

            yuriparts = str(yuricmd)

            yurishell = True

        else:

            import shlex

            yuriparts = shlex.split(str(yuricmd))

            yurishell = False

        yuriproc = subprocess.run(

            yuriparts,

            capture_output=bool(yuricapture),

            text=True,

            shell=yurishell,

        )

        return yurilua.table_from({

            "code":   yuriproc.returncode,

            "stdout": yuriproc.stdout or "",

            "stderr": yuriproc.stderr or "",

            "ok":     yuriproc.returncode == 0,

        })

                                                                              

    def yuripopen(yuricmd):

        if sys.platform == "win32":

            yuriparts = str(yuricmd)

            yurishell = True

        else:

            import shlex

            yuriparts = shlex.split(str(yuricmd))

            yurishell = False

        yuriproc = subprocess.Popen(

            yuriparts,

            stdin=subprocess.PIPE,                                  

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            shell=yurishell,

        )

        def yurireadline(_s):

            return yuriproc.stdout.readline()

        def yurireadall(_s):

            return yuriproc.stdout.read()

        def yuriwrite(_s, yuridata):

            yuriproc.stdin.write(str(yuridata))

            yuriproc.stdin.flush()

        def yuriwait(_s):

            yuriproc.wait()

            return yuriproc.returncode

        def yurikill(_s):

            yuriproc.kill()

        def yuriis_running(_s):

            return yuriproc.poll() is None

        return yurilua.table_from({

            "readLine":  yurireadline,

            "readAll":   yurireadall,

            "write":     yuriwrite,

            "wait":      yuriwait,

            "kill":      yurikill,

            "isRunning": yuriis_running,

            "pid":       yuriproc.pid,

        })

    def yuriplatform():

        return sys.platform

    def yuriinput(yuriprompt=""):

        return input(str(yuriprompt))

    yuriansicodes = {

        "reset":     "\033[0m",

        "bold":      "\033[1m",

        "dim":       "\033[2m",

        "underline": "\033[4m",

        "black":     "\033[30m",

        "red":       "\033[31m",

        "green":     "\033[32m",

        "yellow":    "\033[33m",

        "blue":      "\033[34m",

        "magenta":   "\033[35m",

        "cyan":      "\033[36m",

        "white":     "\033[37m",

        "bgBlack":   "\033[40m",

        "bgRed":     "\033[41m",

        "bgGreen":   "\033[42m",

        "bgYellow":  "\033[43m",

        "bgBlue":    "\033[44m",

        "bgMagenta": "\033[45m",

        "bgCyan":    "\033[46m",

        "bgWhite":   "\033[47m",

    }

    def yuricolor(yuritext, *yurinames):

        yuriprefixes = "".join(yuriansicodes.get(str(n), "") for n in yurinames)

        return yuriprefixes + str(yuritext) + yuriansicodes["reset"]

    def yuriclear():

        os.system("cls" if sys.platform == "win32" else "clear")

                                         

    def yuriwhich(yuricmd):

        return _shutil.which(str(yuricmd))

    def yuriexit(yuricode=0):

        sys.exit(int(yuricode))

    yurig.cli = yurilua.table_from({

        "args":     yuriargs,

        "getEnv":   yurigetenv,

        "setEnv":   yurisetenv,

        "envAll":   yurienvall,

        "exec":     yuriexec,

        "popen":    yuripopen,

        "platform": yuriplatform,

        "input":    yuriinput,

        "color":    yuricolor,

        "clear":    yuriclear,

        "which":    yuriwhich,

        "exit":     yuriexit,

        "ansi":     yurilua.table_from(yuriansicodes),

    })
