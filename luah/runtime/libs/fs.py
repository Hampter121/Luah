import os

import shutil

import glob as _glob

import tempfile as _tempfile

def yuriinject_fs(yurilua, yurig):

                                                                     

    def yuriread(yuripath):

        yuripath = str(yuripath)

        if not os.path.exists(yuripath):

            raise RuntimeError(f"fs.read: file not found: {yuripath}")

        with open(yuripath, "r", encoding="utf-8") as yurif:

            return yurif.read()

    def yuriread_bytes(yuripath):

        yuripath = str(yuripath)

        if not os.path.exists(yuripath):

            raise RuntimeError(f"fs.readBytes: file not found: {yuripath}")

        with open(yuripath, "rb") as yurif:

            yuridata = yurif.read()

        return yurilua.table_from({i+1: b for i, b in enumerate(yuridata)})

    def yuriwrite(yuripath, yuricontent, yurimode="w"):

        yuripath = str(yuripath)

        yuridir  = os.path.dirname(yuripath)

        if yuridir:

            os.makedirs(yuridir, exist_ok=True)

        with open(yuripath, str(yurimode), encoding="utf-8") as yurif:

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

        if not os.path.exists(yuripath):

            raise RuntimeError(f"fs.delete: path not found: {yuripath}")

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

        try:

            yuriitems = os.listdir(str(yuripath))

        except FileNotFoundError:

            raise RuntimeError(f"fs.list: directory not found: {yuripath}")

        return yurilua.table_from({i+1: v for i, v in enumerate(yuriitems)})

    def yuriglob(yuripattern):

        yurimatches = _glob.glob(str(yuripattern))

        return yurilua.table_from({i+1: v for i, v in enumerate(yurimatches)})

    def yurisize(yuripath):

        yuripath = str(yuripath)

        if not os.path.exists(yuripath):

            raise RuntimeError(f"fs.size: path not found: {yuripath}")

        return os.path.getsize(yuripath)

    def yuriabspath(yuripath):

        return os.path.abspath(str(yuripath))

    def yuribasename(yuripath):

        return os.path.basename(str(yuripath))

    def yuridirname(yuripath):

        return os.path.dirname(str(yuripath))

    def yurijoin(*yuriparts):

        return os.path.join(*[str(p) for p in yuriparts])

    def yuriext(yuripath):

        yuriroot, yuriextval = os.path.splitext(str(yuripath))

        return yurilua.table_from({"root": yuriroot, "ext": yuriextval})

    def yuricwd():

        return os.getcwd()

    def yurichdir(yuripath):

        os.chdir(str(yuripath))

        return True

                                                                   

    def yurilines(yuripath):

        yuripath = str(yuripath)

        if not os.path.exists(yuripath):

            raise RuntimeError(f"fs.lines: file not found: {yuripath}")

        with open(yuripath, "r", encoding="utf-8") as yurif:

            yuriresult = yurif.readlines()

        return yurilua.table_from({i+1: v.rstrip("\r\n") for i, v in enumerate(yuriresult)})

                                    

    def yuritemp_file(yurisuffix=""):

        yurif = _tempfile.NamedTemporaryFile(delete=False, suffix=str(yurisuffix))

        yurif.close()

        return yurif.name

    def yuritemp_dir():

        return _tempfile.mkdtemp()

    def yuristat(yuripath):

        yuripath = str(yuripath)

        if not os.path.exists(yuripath):

            raise RuntimeError(f"fs.stat: path not found: {yuripath}")

        yuris = os.stat(yuripath)

        return yurilua.table_from({

            "size":    yuris.st_size,

            "mtime":   yuris.st_mtime,

            "ctime":   yuris.st_ctime,

            "isFile":  os.path.isfile(yuripath),

            "isDir":   os.path.isdir(yuripath),

        })

    yurig.fs = yurilua.table_from({

        "read":      yuriread,

        "readBytes": yuriread_bytes,

        "write":     yuriwrite,

        "append":    yuriappend,

        "exists":    yuriexists,

        "isFile":    yuriisfile,

        "isDir":     yuriisdir,

        "mkdir":     yurimkdir,

        "delete":    yuridelete,

        "copy":      yuricopy,

        "move":      yurimove,

        "list":      yurilistdir,

        "glob":      yuriglob,

        "size":      yurisize,

        "abspath":   yuriabspath,

        "basename":  yuribasename,

        "dirname":   yuridirname,

        "join":      yurijoin,

        "ext":       yuriext,

        "cwd":       yuricwd,

        "chdir":     yurichdir,

        "lines":     yurilines,

        "tempFile":  yuritemp_file,

        "tempDir":   yuritemp_dir,

        "stat":      yuristat,

    })
