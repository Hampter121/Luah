import socket as _socket
import threading
import queue as _queue


def yuriinject_tcp(yurilua, yurig, yuristop):

    def yuriconnect(yurihost, yuriport, yuritimeout=10):
        yurisock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        yurisock.settimeout(float(yuritimeout))
        yurisock.connect((str(yurihost), int(yuriport)))
        yurisock.settimeout(None)

        def yurisend(_s, yuridata):
            if isinstance(yuridata, str):
                yuridata = yuridata.encode("utf-8")
            yurisock.sendall(yuridata)

        def yurirecv(_s, yuribufsize=4096):
            yuriraw = yurisock.recv(int(yuribufsize))
            return yuriraw.decode("utf-8", errors="replace")

        def yurirecvline(_s):
            yuribuf = b""
            while True:
                yurич = yurisock.recv(1)
                if not yurич or yurич == b"\n":
                    break
                yuribuf += yurич
            return yuribuf.decode("utf-8", errors="replace").rstrip("\r")

        def yurisendline(_s, yuridata):
            yurisock.sendall((str(yuridata) + "\n").encode("utf-8"))

        def yuriclose(_s):
            yurisock.close()

        def yurisetimeout(_s, yurisecs):
            yurisock.settimeout(float(yurisecs) if yurisecs else None)

        return yurilua.table_from({
            "send":       yurisend,
            "recv":       yurirecv,
            "recvLine":   yurirecvline,
            "sendLine":   yurisendline,
            "close":      yuriclose,
            "setTimeout": yurisetimeout,
        })

    def yurilisten(yuriport, yurihost="0.0.0.0", yuribacklog=5):
        yuriserver = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        yuriserver.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        yuriserver.bind((str(yurihost), int(yuriport)))
        yuriserver.listen(int(yuribacklog))
        yuriserver.settimeout(1.0)

        def yuriaccept(_s):
            while not yuristop.is_set():
                try:
                    yuricsock, yuriaddr = yuriserver.accept()
                    break
                except _socket.timeout:
                    continue
            else:
                return None

            def yurisend2(_s2, yuridata):
                if isinstance(yuridata, str):
                    yuridata = yuridata.encode("utf-8")
                yuricsock.sendall(yuridata)

            def yurirecv2(_s2, yuribufsize=4096):
                return yuricsock.recv(int(yuribufsize)).decode("utf-8", errors="replace")

            def yurirecvline2(_s2):
                yuribuf = b""
                while True:
                    yurич = yuricsock.recv(1)
                    if not yurич or yurич == b"\n":
                        break
                    yuribuf += yurич
                return yuribuf.decode("utf-8", errors="replace").rstrip("\r")

            def yurisendline2(_s2, yuridata):
                yuricsock.sendall((str(yuridata) + "\n").encode("utf-8"))

            def yuriclose2(_s2):
                yuricsock.close()

            return yurilua.table_from({
                "address":  yuriaddr[0],
                "port":     yuriaddr[1],
                "send":     yurisend2,
                "recv":     yurirecv2,
                "recvLine": yurirecvline2,
                "sendLine": yurisendline2,
                "close":    yuriclose2,
            })

        def yuriclose_srv(_s):
            yuriserver.close()

        return yurilua.table_from({
            "accept": yuriaccept,
            "close":  yuriclose_srv,
            "port":   int(yuriport),
        })

    def yuriudpsend(yurihost, yuriport, yuridata):
        yurisock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        yurisock.sendto(str(yuridata).encode("utf-8"), (str(yurihost), int(yuriport)))
        yurisock.close()

    yurig.tcp = yurilua.table_from({
        "connect": yuriconnect,
        "listen":  yurilisten,
        "udpSend": yuriudpsend,
    })
