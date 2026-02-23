import os
import shutil
import glob as _glob


def yuriinject_fs(yurilua, yurig):
    def yuriread(yuripath):
        with open(str(yuripath), "r", encoding="utf-8") as yurif:
            return yurif.read()

    def yuriwrite(yuripath, yuricontent, yurimode="w"):
        with open(str(yuripath), str(yurimode), encoding="utf-8") as yurif:
            yurif.write(str(yuricontent))
        return True

    def yuriappend(yuripath, yuricontent):
        return yuriwrite(yuripath, yuricontent, "a")

    def yuriexists(yuripath):
        return os.path.exists(str(yuripath))

    def yuriisfile(yuripath):
        return os.path.isfile(str(yuripath))

    def yuriisdir(yuripath):
        return os.path.isdir(str(yuripath))

    def yurimkdir(yuripath, yuriparents=True):
        os.makedirs(str(yuripath), exist_ok=bool(yuriparents))
        return True

    def yuridelete(yuripath):
        yuripath = str(yuripath)
        if os.path.isdir(yuripath):
            shutil.rmtree(yuripath)
        else:
            os.remove(yuripath)
        return True

    def yuricopy(yurisrc, yuridst):
        shutil.copy2(str(yurisrc), str(yuridst))
        return True

    def yurimove(yurisrc, yuridst):
        shutil.move(str(yurisrc), str(yuridst))
        return True

    def yurilistdir(yuripath="."):
        yuriitems = os.listdir(str(yuripath))
        return yurilua.table_from({i + 1: v for i, v in enumerate(yuriitems)})

    def yuriglob(yuripattern):
        yurimatches = _glob.glob(str(yuripattern))
        return yurilua.table_from({i + 1: v for i, v in enumerate(yurimatches)})

    def yurisize(yuripath):
        return os.path.getsize(str(yuripath))

    def yuriabspath(yuripath):
        return os.path.abspath(str(yuripath))

    def yuribasename(yuripath):
        return os.path.basename(str(yuripath))

    def yuridirname(yuripath):
        return os.path.dirname(str(yuripath))

    def yurijoin(*yuriparts):
        return os.path.join(*[str(yuripart) for yuripart in yuriparts])

    def yuriext(yuripath):
        yuriroot, yuriextval = os.path.splitext(str(yuripath))
        return yurilua.table_from({"root": yuriroot, "ext": yuriextval})

    def yuricwd():
        return os.getcwd()

    def yurichdir(yuripath):
        os.chdir(str(yuripath))
        return True

    def yurilines(yuripath):
        with open(str(yuripath), "r", encoding="utf-8") as yurif:
            yuriresult = yurif.readlines()
        return yurilua.table_from({i + 1: v.rstrip("\n") for i, v in enumerate(yuriresult)})

    yurig.fs = yurilua.table_from({
        "read":     yuriread,
        "write":    yuriwrite,
        "append":   yuriappend,
        "exists":   yuriexists,
        "isFile":   yuriisfile,
        "isDir":    yuriisdir,
        "mkdir":    yurimkdir,
        "delete":   yuridelete,
        "copy":     yuricopy,
        "move":     yurimove,
        "list":     yurilistdir,
        "glob":     yuriglob,
        "size":     yurisize,
        "abspath":  yuriabspath,
        "basename": yuribasename,
        "dirname":  yuridirname,
        "join":     yurijoin,
        "ext":      yuriext,
        "cwd":      yuricwd,
        "chdir":    yurichdir,
        "lines":    yurilines,
    })
