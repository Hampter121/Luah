import threading

def yuriinject_sound(yurilua, yurig):

                                                            

    try:

        import pygame

        if not pygame.mixer.get_init():

            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        yuriavail = True

    except Exception:

        yuriavail = False

    yurilock       = threading.Lock()

                                                                  

    yuribeep_cache = {}

    def yuriload(yuripath):

        if not yuriavail:

            return yurilua.table_from({

                "play": lambda _s: None, "stop": lambda _s: None,

                "loop": lambda _s: None, "volume": lambda _s, v: None,

                "isPlaying": lambda _s: False, "error": "pygame.mixer unavailable",

            })

        try:

            yurisnd  = pygame.mixer.Sound(str(yuripath))

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

                return yurichan[0].get_busy() if yurichan[0] else False

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

                "isPlaying": lambda _s: False, "error": str(yuriex),

            })

    def yuribeep(yurifreq=440, yuridur=0.2, yurivol=0.5):

        if not yuriavail:

            return

        yurifreq = float(yurifreq)

        yuridur  = float(yuridur)

        yurivol  = float(yurivol)

        yurikey  = (round(yurifreq), round(yuridur * 100), round(yurivol * 100))

        with yurilock:

            if yurikey not in yuribeep_cache:

                try:

                    import numpy as np

                    yurirate = 44100

                    yurin    = int(yurirate * yuridur)

                    yuriarr  = np.sin(2 * np.pi * yurifreq * np.arange(yurin) / yurirate)

                    yuriarr  = (yuriarr * 32767 * yurivol).astype(np.int16)

                    yuriarr  = np.column_stack([yuriarr, yuriarr])

                    yuribeep_cache[yurikey] = pygame.sndarray.make_sound(yuriarr)

                except ImportError:

                    try:

                        import array as _array, math as _math

                        yurirate = 22050

                        yurin    = int(yurirate * yuridur)

                        yuriarr  = _array.array("h", [

                            int(32767 * yurivol * _math.sin(2 * _math.pi * yurifreq * i / yurirate))

                            for i in range(yurin)

                        ])

                        yuribuf  = bytes(yuriarr) * 2

                        yuribeep_cache[yurikey] = pygame.mixer.Sound(buffer=yuribuf)

                    except Exception:

                        yuribeep_cache[yurikey] = None

                except Exception:

                    yuribeep_cache[yurikey] = None

            yurisnd = yuribeep_cache[yurikey]

        if yurisnd:

            yurisnd.play()

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

    def yurimusic_pause():

        if not yuriavail:

            return

        try:

            pygame.mixer.music.pause()

        except Exception:

            pass

    def yurimusic_resume():

        if not yuriavail:

            return

        try:

            pygame.mixer.music.unpause()

        except Exception:

            pass

    yurig.sound = yurilua.table_from({

        "load":         yuriload,

        "beep":         yuribeep,

        "musicPlay":    yurimusic_play,

        "musicStop":    yurimusic_stop,

        "musicVolume":  yurimusic_volume,

        "musicPause":   yurimusic_pause,

        "musicResume":  yurimusic_resume,

        "available":    yuriavail,

    })
