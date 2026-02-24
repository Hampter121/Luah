import threading
import os

def yuriinject_sound(yurilua, yurig):
    try:
        import pygame
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        yuriavail = True
    except Exception:
        yuriavail = False

    yurilock = threading.Lock()

    def yuriload(yuripath):
        if not yuriavail:
            return yurilua.table_from({"play": lambda _s: None, "stop": lambda _s: None,
                                       "loop": lambda _s: None, "volume": lambda _s, v: None,
                                       "isPlaying": lambda _s: False, "error": "pygame.mixer unavailable"})
        try:
            yurisnd = pygame.mixer.Sound(str(yuripath))
            yurichan = [None]

            def yuriplay(_s):
                with yurilock:
                    yurichan[0] = yurisnd.play()

            def yuristop(_s):
                yurisnd.stop()

            def yuriloop(_s):
                with yurilock:
                    yurichan[0] = yurisnd.play(-1)

            def yurivolume(_s, yurivol):
                yurisnd.set_volume(max(0.0, min(1.0, float(yurivol))))

            def yuriis_playing(_s):
                if yurichan[0] is None:
                    return False
                return yurichan[0].get_busy()

            return yurilua.table_from({
                "play":      yuriplay,
                "stop":      yuristop,
                "loop":      yuriloop,
                "volume":    yurivolume,
                "isPlaying": yuriis_playing,
            })
        except Exception as yuriex:
            return yurilua.table_from({
                "play": lambda _s: None, "stop": lambda _s: None,
                "loop": lambda _s: None, "volume": lambda _s, v: None,
                "isPlaying": lambda _s: False, "error": str(yuriex)
            })

    def yuribeep(yurifreq=440, yuridur=0.2, yurivol=0.5):
        if not yuriavail:
            return
        try:
            import numpy as np
            yurirate = 44100
            yurin    = int(yurirate * float(yuridur))
            yuriarr  = np.sin(2 * np.pi * float(yurifreq) * np.arange(yurin) / yurirate)
            yuriarr  = (yuriarr * 32767 * float(yurivol)).astype(np.int16)
            yuriarr  = np.column_stack([yuriarr, yuriarr])
            yurisnd  = pygame.sndarray.make_sound(yuriarr)
            yurisnd.play()
        except ImportError:
            try:
                import array as _array, math as _math
                yurirate = 22050
                yurin    = int(yurirate * float(yuridur))
                yuriarr  = _array.array("h", [
                    int(32767 * float(yurivol) * _math.sin(2 * _math.pi * float(yurifreq) * i / yurirate))
                    for i in range(yurin)
                ])
                yuribuf  = bytes(yuriarr) * 2
                yurisnd  = pygame.mixer.Sound(buffer=yuribuf)
                yurisnd.play()
            except Exception:
                pass
        except Exception:
            pass

    def yurimusic_play(yuripath, yuriloop=True):
        if not yuriavail:
            return
        try:
            pygame.mixer.music.load(str(yuripath))
            pygame.mixer.music.play(-1 if yuriloop else 0)
        except Exception:
            pass

    def yurimusic_stop():
        if not yuriavail:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def yurimusic_volume(yurivol):
        if not yuriavail:
            return
        try:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, float(yurivol))))
        except Exception:
            pass

    yurig.sound = yurilua.table_from({
        "load":         yuriload,
        "beep":         yuribeep,
        "musicPlay":    yurimusic_play,
        "musicStop":    yurimusic_stop,
        "musicVolume":  yurimusic_volume,
        "available":    yuriavail,
    })
