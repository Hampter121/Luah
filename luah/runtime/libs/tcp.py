import socket as _socket

import threading

import queue as _queue

import io as _io

def yuriinject_tcp(yurilua, yurig, yuristop):

                                                                    

    def yurimake_recvline(yurisock):

        yuribuf = _io.BytesIO()

        def yurirecvline_fn():

            while True:

                try:

                    yurichunk = yurisock.recv(4096)

                except OSError:

                    break

                if not yurichunk:

                    break

                yuribuf.write(yurichunk)

                yuridata = yuribuf.getvalue()

                yurinl   = yuridata.find(b"\n")

                if yurinl != -1:

                    yuriline = yuridata[:yurinl]

                    yuribuf  = _io.BytesIO()

                    yuribuf.write(yuridata[yurinl+1:])

                    return yuriline.decode("utf-8", errors="replace").rstrip("\r")

            return yuribuf.getvalue().decode("utf-8", errors="replace").rstrip("\r\n")

        return yurirecvline_fn

    def yurimake_client_table(yurisock):

        yurirecvline_fn = yurimake_recvline(yurisock)

        def yurisend(_s, yuridata):

            if isinstance(yuridata, str):

                yuridata = yuridata.encode("utf-8")

            yurisock.sendall(yuridata)

        def yurirecv(_s, yuribufsize=4096):

            yuriraw = yurisock.recv(int(yuribufsize))

            return yuriraw.decode("utf-8", errors="replace")

        def yurirecvall(_s, yuribufsize=65536):

            yuriparts = []

            while True:

                yurichunk = yurisock.recv(int(yuribufsize))

                if not yurichunk:

                    break

                yuriparts.append(yurichunk)

            return b"".join(yuriparts).decode("utf-8", errors="replace")

        def yurirecvline(_s):

            return yurirecvline_fn()

        def yurisendline(_s, yuridata):

            yurisock.sendall((str(yuridata) + "\n").encode("utf-8"))

        def yuriclose(_s):

            try:

                yurisock.shutdown(_socket.SHUT_RDWR)

            except OSError:

                pass

            yurisock.close()

        def yurisetimeout(_s, yurisecs):

            yurisock.settimeout(float(yurisecs) if yurisecs else None)

        def yuriis_connected(_s):

            try:

                yurisock.getpeername()

                return True

            except OSError:

                return False

        return yurilua.table_from({

            "send":        yurisend,

            "recv":        yurirecv,

            "recvAll":     yurirecvall,

            "recvLine":    yurirecvline,

            "sendLine":    yurisendline,

            "close":       yuriclose,

            "setTimeout":  yurisetimeout,

            "isConnected": yuriis_connected,

        })

    def yuriconnect(yurihost, yuriport, yuritimeout=10):

        yurisock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)

                                                                  

        yurisock.setsockopt(_socket.SOL_SOCKET, _socket.SO_KEEPALIVE, 1)

        yurisock.settimeout(float(yuritimeout))

        yurisock.connect((str(yurihost), int(yuriport)))

        yurisock.settimeout(None)

        return yurimake_client_table(yurisock)

    def yurilisten(yuriport, yurihost="0.0.0.0", yuribacklog=5):

        yuriserver = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)

        yuriserver.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)

        yuriserver.bind((str(yurihost), int(yuriport)))

        yuriserver.listen(int(yuribacklog))

        yuriserver.settimeout(0.5)                                                

        yuriopen = [True]

        def yuriaccept(_s):

            while not yuristop.is_set() and yuriopen[0]:

                try:

                    yuricsock, yuriaddr = yuriserver.accept()

                                                               

                    yuricsock.setsockopt(_socket.SOL_SOCKET, _socket.SO_KEEPALIVE, 1)

                    yuriclient = yurimake_client_table(yuricsock)

                                         

                    return yurilua.table_from(dict(

                        list({"address": yuriaddr[0], "port": yuriaddr[1]}.items()) +

                        [(k, yuriclient[k]) for k in

                         ["send","recv","recvAll","recvLine","sendLine","close","setTimeout","isConnected"]]

                    ))

                except _socket.timeout:

                    continue

                except OSError:

                    break

            return None

        def yuriclose_srv(_s):

            yuriopen[0] = False

            try:

                yuriserver.close()

            except OSError:

                pass

        return yurilua.table_from({

            "accept": yuriaccept,

            "close":  yuriclose_srv,

            "port":   int(yuriport),

        })

                                                        

    def yuriudp():

        yurisock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)

        def yurisend(_s, yurihost, yuriport, yuridata):

            yurisock.sendto(str(yuridata).encode("utf-8"), (str(yurihost), int(yuriport)))

        def yuribind(_s, yuriport, yurihost="0.0.0.0"):

            yurisock.bind((str(yurihost), int(yuriport)))

        def yurirecv(_s, yuribufsize=4096, yuritimeout=None):

            if yuritimeout is not None:

                yurisock.settimeout(float(yuritimeout))

            try:

                yuridata, yuriaddr = yurisock.recvfrom(int(yuribufsize))

                return yurilua.table_from({

                    "data":    yuridata.decode("utf-8", errors="replace"),

                    "address": yuriaddr[0],

                    "port":    yuriaddr[1],

                })

            except _socket.timeout:

                return None

            finally:

                yurisock.settimeout(None)

        def yuriclose(_s):

            yurisock.close()

        return yurilua.table_from({

            "send":  yurisend,

            "bind":  yuribind,

            "recv":  yurirecv,

            "close": yuriclose,

        })

                                     

    def yuriudpsend(yurihost, yuriport, yuridata):

        yurisock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)

        yurisock.sendto(str(yuridata).encode("utf-8"), (str(yurihost), int(yuriport)))

        yurisock.close()

    yurig.tcp = yurilua.table_from({

        "connect": yuriconnect,

        "listen":  yurilisten,

        "udp":     yuriudp,                                   

        "udpSend": yuriudpsend,                             

    })
