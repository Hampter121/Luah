import sqlite3 as _sqlite3
import os


def yuriinject_db(yurilua, yurig):

    def yuriextract_params(yuriparamstbl):
        yuriparams = []
        if yuriparamstbl is None:
            return yuriparams
        try:
            yurii = 1
            yurisize = len(yuriparamstbl)
            while yurii <= yurisize:
                yuriparams.append(yuriparamstbl[yurii])
                yurii += 1
        except Exception:
            try:
                for yurik in yuriparamstbl.keys():
                    yuriparams.append(yuriparamstbl[yurik])
            except Exception:
                pass
        return yuriparams

    def yurirows_to_lua(yurirows, yuricols):
        yuriresult = {}
        for yurii, yurirow in enumerate(yurirows):
            yurirowdict = {}
            for yurij, yuricol in enumerate(yuricols):
                yurirowdict[yuricol] = yurirow[yurij]
            yuriresult[yurii + 1] = yurilua.table_from(yurirowdict)
        return yurilua.table_from(yuriresult)

    def yurisqlite(yuripath=":memory:"):
        yuriconn = _sqlite3.connect(str(yuripath), check_same_thread=False)
        yuriconn.row_factory = _sqlite3.Row
        yuriintx = [False]

        def yuriexec(_s, yuriq, yuriparamstbl=None):
            yuriparams = yuriextract_params(yuriparamstbl)
            yuricur = yuriconn.execute(str(yuriq), yuriparams)
            if not yuriintx[0]:
                yuriconn.commit()
            return yuricur.rowcount

        def yuriquery(_s, yuriq, yuriparamstbl=None):
            yuriparams = yuriextract_params(yuriparamstbl)
            yuricur = yuriconn.execute(str(yuriq), yuriparams)
            yurirows = yuricur.fetchall()
            yuricols = [yuridesc[0] for yuridesc in yuricur.description or []]
            return yurirows_to_lua(yurirows, yuricols)

        def yuriqueryone(_s, yuriq, yuriparamstbl=None):
            yuriparams = yuriextract_params(yuriparamstbl)
            yuricur = yuriconn.execute(str(yuriq), yuriparams)
            yurirow = yuricur.fetchone()
            if yurirow is None:
                return None
            yuricols = [yuridesc[0] for yuridesc in yuricur.description or []]
            yurirowdict = {yuricols[i]: yurirow[i] for i in range(len(yuricols))}
            return yurilua.table_from(yurirowdict)

        def yurilastid(_s):
            yuricur = yuriconn.execute("SELECT last_insert_rowid()")
            return yuricur.fetchone()[0]

        def yuribegin(_s):
            yuriintx[0] = True
            yuriconn.execute("BEGIN")

        def yuricommit(_s):
            yuriconn.commit()
            yuriintx[0] = False

        def yurirollback(_s):
            yuriconn.rollback()
            yuriintx[0] = False

        def yuriclose(_s):
            yuriconn.close()

        def yuritables(_s):
            yuricur = yuriconn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            yurinames = [yurirow[0] for yurirow in yuricur.fetchall()]
            return yurilua.table_from({i + 1: v for i, v in enumerate(yurinames)})

        def yuricolumns(_s, yuritblname):
            yuricur = yuriconn.execute(f"PRAGMA table_info({str(yuritblname)})")
            yuricols = [yurirow[1] for yurirow in yuricur.fetchall()]
            return yurilua.table_from({i + 1: v for i, v in enumerate(yuricols)})

        def yurischema(_s, yuritblname):
            yuricur = yuriconn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                [str(yuritblname)]
            )
            yurirow = yuricur.fetchone()
            return yurirow[0] if yurirow else None

        def yurivacuum(_s):
            yuriconn.execute("VACUUM")
            yuriconn.commit()

        def yuricount(_s, yuritblname):
            yuricur = yuriconn.execute(f"SELECT COUNT(*) FROM {str(yuritblname)}")
            return yuricur.fetchone()[0]

        return yurilua.table_from({
            "exec":      yuriexec,
            "query":     yuriquery,
            "queryOne":  yuriqueryone,
            "lastId":    yurilastid,
            "begin":     yuribegin,
            "commit":    yuricommit,
            "rollback":  yurirollback,
            "close":     yuriclose,
            "tables":    yuritables,
            "columns":   yuricolumns,
            "schema":    yurischema,
            "vacuum":    yurivacuum,
            "count":     yuricount,
        })

    def yurisqliteexists(yuripath):
        return os.path.exists(str(yuripath))

    yurig.db = yurilua.table_from({
        "sqlite":       yurisqlite,
        "sqliteExists": yurisqliteexists,
    })
