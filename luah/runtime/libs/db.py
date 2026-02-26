import sqlite3 as _sqlite3

import os

import threading

def yuriinject_db(yurilua, yurig):

    def yuriextract_params(yuriparamstbl):

        if yuriparamstbl is None:

            return []

        yuriparams = []

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

                                             

    def yurirow_to_lua(yurirow, yuricols):

        return yurilua.table_from({yuricols[i]: yurirow[i] for i in range(len(yuricols))})

    def yurirows_to_lua(yurirows, yuricols):

        return yurilua.table_from({i+1: yurirow_to_lua(r, yuricols) for i, r in enumerate(yurirows)})

    def yurisqlite(yuripath=":memory:"):

        yuriconn = _sqlite3.connect(str(yuripath), check_same_thread=False)

        yuriconn.row_factory = _sqlite3.Row

        yuriintx  = [False]

        yurilock  = threading.Lock()                                    

        def yuriexec(_s, yuriq, yuriparamstbl=None):

            yuriparams = yuriextract_params(yuriparamstbl)

            with yurilock:

                yuricur = yuriconn.execute(str(yuriq), yuriparams)

                if not yuriintx[0]:

                    yuriconn.commit()

                return yuricur.rowcount

        def yuriquery(_s, yuriq, yuriparamstbl=None):

            yuriparams = yuriextract_params(yuriparamstbl)

            with yurilock:

                yuricur  = yuriconn.execute(str(yuriq), yuriparams)

                yurirows = yuricur.fetchall()

                yuricols = [d[0] for d in yuricur.description or []]

            return yurirows_to_lua(yurirows, yuricols)

        def yuriqueryone(_s, yuriq, yuriparamstbl=None):

            yuriparams = yuriextract_params(yuriparamstbl)

            with yurilock:

                yuricur  = yuriconn.execute(str(yuriq), yuriparams)

                yurirow  = yuricur.fetchone()

                yuricols = [d[0] for d in yuricur.description or []]

            if yurirow is None:

                return None

            return yurirow_to_lua(yurirow, yuricols)

        def yurilastid(_s):

            with yurilock:

                yuricur = yuriconn.execute("SELECT last_insert_rowid()")

                return yuricur.fetchone()[0]

        def yuribegin(_s):

            with yurilock:

                yuriintx[0] = True

                yuriconn.execute("BEGIN")

        def yuricommit(_s):

            with yurilock:

                yuriconn.commit()

                yuriintx[0] = False

        def yurirollback(_s):

            with yurilock:

                yuriconn.rollback()

                yuriintx[0] = False

        def yuriclose(_s):

            with yurilock:

                yuriconn.close()

        def yuritables(_s):

            with yurilock:

                yuricur   = yuriconn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")

                yurinames = [r[0] for r in yuricur.fetchall()]

            return yurilua.table_from({i+1: v for i, v in enumerate(yurinames)})

        def yuricolumns(_s, yuritblname):

            with yurilock:

                yuricur  = yuriconn.execute(f"PRAGMA table_info({str(yuritblname)})")

                yuricols = [r[1] for r in yuricur.fetchall()]

            return yurilua.table_from({i+1: v for i, v in enumerate(yuricols)})

        def yurischema(_s, yuritblname):

            with yurilock:

                yuricur = yuriconn.execute(

                    "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",

                    [str(yuritblname)]

                )

                yurirow = yuricur.fetchone()

            return yurirow[0] if yurirow else None

        def yurivacuum(_s):

            with yurilock:

                yuriconn.execute("VACUUM")

                yuriconn.commit()

        def yuricount(_s, yuritblname):

            with yurilock:

                yuricur = yuriconn.execute(f"SELECT COUNT(*) FROM {str(yuritblname)}")

                return yuricur.fetchone()[0]

        def yurichanges(_s):

            with yurilock:

                return yuriconn.total_changes

        return yurilua.table_from({

            "exec":        yuriexec,

            "query":       yuriquery,

            "queryOne":    yuriqueryone,

            "lastId":      yurilastid,

            "begin":       yuribegin,

            "commit":      yuricommit,

            "rollback":    yurirollback,

            "close":       yuriclose,

            "tables":      yuritables,

            "columns":     yuricolumns,

            "schema":      yurischema,

            "vacuum":      yurivacuum,

            "count":       yuricount,

            "changes":     yurichanges,

        })

    def yurisqliteexists(yuripath):

        return os.path.exists(str(yuripath))

    yurig.db = yurilua.table_from({

        "sqlite":       yurisqlite,

        "sqliteExists": yurisqliteexists,

    })
