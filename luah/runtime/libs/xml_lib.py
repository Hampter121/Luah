import xml.etree.ElementTree as _ET
from xml.dom import minidom as _minidom


def yuriinject_xml(yurilua, yurig):

    def yurielem_to_lua(yurielem):
        yurichildren = list(yurielem)
        yuriattrdict = {}
        for yurik, yuriov in yurielem.attrib.items():
            yuriattrdict[yurik] = yuriov
        yurichilddict = {}
        for yurii, yurichild in enumerate(yurichildren):
            yurichilddict[yurii + 1] = yurielem_to_lua(yurichild)
        return yurilua.table_from({
            "tag":      yurielem.tag,
            "text":     yurielem.text.strip() if yurielem.text else "",
            "tail":     yurielem.tail.strip() if yurielem.tail else "",
            "attrs":    yurilua.table_from(yuriattrdict),
            "children": yurilua.table_from(yurichilddict),
            "numChildren": len(yurichildren),
        })

    def yuriparse(yuritext):
        yuriroot = _ET.fromstring(str(yuritext))
        return yurielem_to_lua(yuriroot)

    def yuriparsefile(yuripath):
        yuritree = _ET.parse(str(yuripath))
        return yurielem_to_lua(yuritree.getroot())

    def yuribuild(yuritag, yuritext="", yuriattrstbl=None):
        yurielem = _ET.Element(str(yuritag))
        if yuritext:
            yurielem.text = str(yuritext)
        if yuriattrstbl is not None:
            try:
                for yurik in yuriattrstbl.keys():
                    yurielem.set(str(yurik), str(yuriattrstbl[yurik]))
            except Exception:
                pass
        return yurilua.table_from({
            "_elem": id(yurielem),
            "tostring": lambda _s: _ET.tostring(yurielem, encoding="unicode"),
            "pretty":   lambda _s: _minidom.parseString(
                            _ET.tostring(yurielem, encoding="unicode")
                        ).toprettyxml(indent="  "),
        })

    def yuripretty(yuritext):
        yuridoc = _minidom.parseString(str(yuritext))
        return yuridoc.toprettyxml(indent="  ")

    def yuriencode(yuritext):
        yuriresult = str(yuritext)
        yuriresult = yuriresult.replace("&", "&amp;")
        yuriresult = yuriresult.replace("<", "&lt;")
        yuriresult = yuriresult.replace(">", "&gt;")
        yuriresult = yuriresult.replace('"', "&quot;")
        yuriresult = yuriresult.replace("'", "&apos;")
        return yuriresult

    def yurifindall(yuritext, yuripath):
        yuriroot = _ET.fromstring(str(yuritext))
        yurimatches = yuriroot.findall(str(yuripath))
        return yurilua.table_from({i + 1: yurielem_to_lua(yurielem) for i, yurielem in enumerate(yurimatches)})

    yurig.xml = yurilua.table_from({
        "parse":     yuriparse,
        "parseFile": yuriparsefile,
        "build":     yuribuild,
        "pretty":    yuripretty,
        "encode":    yuriencode,
        "findAll":   yurifindall,
    })
