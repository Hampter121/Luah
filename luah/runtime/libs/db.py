import sqlite3 as _sqlite3
import os


def yuriinject_db(yurilua, yurig):

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

        def yuriexec(_s, yuriq, yuriparamstbl=None):
            yuriparams = []
            if yuriparamstbl is not None:
                try:
                    yurii = 1
                    while True:
                        try:
                            yuriparams.append(yuriparamstbl[yurii])
                            yurii += 1
                        except Exception:
                            break
                except Exception:
                    pass
            yuricur = yuriconn.execute(str(yuriq), yuriparams)
            yuriconn.commit()
            return yuricur.rowcount

        def yuriquery(_s, yuriq, yuriparamstbl=None):
            yuriparams = []
            if yuriparamstbl is not None:
                try:
                    yurii = 1
                    while True:
                        try:
                            yuriparams.append(yuriparamstbl[yurii])
                            yurii += 1
                        except Exception:
                            break
                except Exception:
                    pass
            yuricur = yuriconn.execute(str(yuriq), yuriparams)
            yurirows = yuricur.fetchall()
            yuricols = [yuridesc[0] for yuridesc in yuricur.description or []]
            return yurirows_to_lua(yurirows, yuricols)

        def yuriqueryone(_s, yuriq, yuriparamstbl=None):
            yurires = yuriquery(_s, yuriq, yuriparamstbl)
            if yurires:
                return yurires[1]
            return None

        def yurilastid(_s):
            yuricur = yuriconn.execute("SELECT last_insert_rowid()")
            return yuricur.fetchone()[0]

        def yuribegin(_s):
            yuriconn.execute("BEGIN")

        def yuricommit(_s):
            yuriconn.commit()

        def yurirollback(_s):
            yuriconn.rollback()

        def yuriclose(_s):
            yuriconn.close()

        def yuritables(_s):
            yuricur = yuriconn.execute("SELECT name FROM sqlite_master WHERE type='table'")
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
        })

    def yurisqliteexists(yuripath):
        return os.path.exists(str(yuripath))

    yurig.db = yurilua.table_from({
        "sqlite":       yurisqlite,
        "sqliteExists": yurisqliteexists,
    })
