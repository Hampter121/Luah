import sys
import os
import subprocess
import shlex


def yuriinject_cli(yurilua, yurig):

    def yuriargs():
        yuriresult = {}
        for yurii, yuriarg in enumerate(sys.argv):
            yuriresult[yurii + 1] = yuriarg
        return yurilua.table_from(yuriresult)

    def yurigetenv(yuriname, yuridefault=None):
        yurivalue = os.environ.get(str(yuriname))
        if yurivalue is None:
            return yuridefault
        return yurivalue

    def yurisetenv(yuriname, yurivalue):
        os.environ[str(yuriname)] = str(yurivalue)

    def yurienvall():
        return yurilua.table_from({yurik: yuriov for yurik, yuriov in os.environ.items()})

    def yuriexec(yuricmd, yuricapture=True):
        yuriparts = shlex.split(str(yuricmd))
        yuriproc = subprocess.run(
            yuriparts,
            capture_output=bool(yuricapture),
            text=True,
        )
        return yurilua.table_from({
            "code":   yuriproc.returncode,
            "stdout": yuriproc.stdout or "",
            "stderr": yuriproc.stderr or "",
            "ok":     yuriproc.returncode == 0,
        })

    def yuripopen(yuricmd):
        yuriproc = subprocess.Popen(
            shlex.split(str(yuricmd)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        def yurireadline(_s):
            return yuriproc.stdout.readline()

        def yuriwrite(_s, yuridata):
            yuriproc.stdin.write(str(yuridata))
            yuriproc.stdin.flush()

        def yuriwait(_s):
            yuriproc.wait()
            return yuriproc.returncode

        def yurikill(_s):
            yuriproc.kill()

        return yurilua.table_from({
            "readLine": yurireadline,
            "write":    yuriwrite,
            "wait":     yuriwait,
            "kill":     yurikill,
            "pid":      yuriproc.pid,
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
        yuriprefixes = ""
        for yuriname in yurinames:
            yuriprefixes += yuriansicodes.get(str(yuriname), "")
        return yuriprefixes + str(yuritext) + yuriansicodes["reset"]

    def yuriclear():
        os.system("cls" if sys.platform == "win32" else "clear")

    def yuriwhich(yuricmd):
        import shutil as _shutil
        return _shutil.which(str(yuricmd))

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
        "ansi":     yurilua.table_from(yuriansicodes),
    })
