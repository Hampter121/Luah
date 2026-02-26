import threading

import queue as _queue

import time as _time

def yuriinject_concurrent(yurilua, yurig, yuristop):

                                                                     

    def yurithread(yurifn, *yuriargs):

        yuriresultq  = _queue.Queue()

        yuridoneflag = threading.Event()

        yuriresult_cache = [None, False]                                                         

        def yurirun():

            try:

                yuriresult = yurifn(*yuriargs)

                yuriresultq.put(("ok", yuriresult))

            except Exception as yuriex:

                if not yuristop.is_set():

                    yuriresultq.put(("err", str(yuriex)))

            finally:

                yuridoneflag.set()

        yurit = threading.Thread(target=yurirun, daemon=True)

        yurit.start()

        def yurijoin(_s, yuritimeout=None):

            yuridoneflag.wait(timeout=float(yuritimeout) if yuritimeout else None)

            if not yuriresult_cache[1] and not yuriresultq.empty():

                yuristatus, yurivalue = yuriresultq.get()

                yuriresult_cache[0] = (yuristatus, yurivalue)

                yuriresult_cache[1] = True

            if yuriresult_cache[1]:

                yuristatus, yurivalue = yuriresult_cache[0]

                return yuristatus == "ok", yurivalue

            return False, None

        def yuriisdone(_s):

            return yuridoneflag.is_set()

                                              

        def yuriresultfn(_s):

            if not yuriresult_cache[1] and not yuriresultq.empty():

                yuristatus, yurivalue = yuriresultq.get()

                yuriresult_cache[0] = (yuristatus, yurivalue)

                yuriresult_cache[1] = True

            if yuriresult_cache[1]:

                return yuriresult_cache[0][1]

            return None

        return yurilua.table_from({

            "join":   yurijoin,

            "isDone": yuriisdone,

            "result": yuriresultfn,

        })

    def yurichannel(yurimaxsize=0):

        yuriq = _queue.Queue(maxsize=int(yurimaxsize))

        def yurisend(_s, yurivalue, yuritimeout=None):

            try:

                yuriq.put(yurivalue, timeout=float(yuritimeout) if yuritimeout else None)

                return True

            except _queue.Full:

                return False

        def yurirecv(_s, yuritimeout=None):

            try:

                return yuriq.get(timeout=float(yuritimeout) if yuritimeout else None)

            except _queue.Empty:

                return None

        def yuriisempty(_s):

            return yuriq.empty()

        def yurisize(_s):

            return yuriq.qsize()

        def yuriclear(_s):

            while not yuriq.empty():

                try:

                    yuriq.get_nowait()

                except _queue.Empty:

                    break

        return yurilua.table_from({

            "send":    yurisend,

            "recv":    yurirecv,

            "isEmpty": yuriisempty,

            "size":    yurisize,

            "clear":   yuriclear,

        })

    def yurimutex():

        yurilock = threading.Lock()

        def yuriaquire(_s, yuritimeout=None):

            return yurilock.acquire(timeout=float(yuritimeout) if yuritimeout else -1)

        def yurirelease(_s):

            try:

                yurilock.release()

            except RuntimeError:

                pass                    

        def yuriis_locked(_s):

            yuracquired = yurilock.acquire(blocking=False)

            if yuracquired:

                yurilock.release()

                return False

            return True

        return yurilua.table_from({

            "lock":     yuriaquire,

            "unlock":   yurirelease,

            "isLocked": yuriis_locked,

        })

    def yurievent():

        yuriflg = threading.Event()

        def yuriset(_s):   yuriflg.set()

        def yuriclear(_s): yuriflg.clear()

        def yuriwait(_s, yuritimeout=None):

            return yuriflg.wait(timeout=float(yuritimeout) if yuritimeout else None)

        def yuriisset(_s): return yuriflg.is_set()

        return yurilua.table_from({

            "set":   yuriset,

            "clear": yuriclear,

            "wait":  yuriwait,

            "isSet": yuriisset,

        })

    def yurisleep(yurisecs):

        yuriend = _time.time() + float(yurisecs)

        while _time.time() < yuriend:

            if yuristop.is_set():

                return

            _time.sleep(0.005)

    def yuriall(yurilist_tbl):

        """Wait for all threads to finish, return table of results."""

        yuriresults = {}

        yurii = 1

        while True:

            yurit = yurilist_tbl[yurii]

            if yurit is None:

                break

            yuriok, yurivalue = yurit.join()

            yuriresults[yurii] = yurivalue

            yurii += 1

        return yurilua.table_from(yuriresults)

    yurig.concurrent = yurilua.table_from({

        "thread":  yurithread,

        "channel": yurichannel,

        "mutex":   yurimutex,

        "event":   yurievent,

        "sleep":   yurisleep,

        "all":     yuriall,

    })
