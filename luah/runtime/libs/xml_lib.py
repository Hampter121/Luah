import xml.etree.ElementTree as _ET

def yuriinject_xml(yurilua, yurig):

    def yurielem_to_lua(yurielem):

        yurichildren = list(yurielem)

        return yurilua.table_from({

            "tag":         yurielem.tag,

            "text":        (yurielem.text or "").strip(),

            "tail":        (yurielem.tail or "").strip(),

            "attrs":       yurilua.table_from(dict(yurielem.attrib)),

            "children":    yurilua.table_from({i+1: yurielem_to_lua(c) for i, c in enumerate(yurichildren)}),

            "numChildren": len(yurichildren),

        })

    def yuriparse(yuritext):

        try:

            yuriroot = _ET.fromstring(str(yuritext))

            return yurielem_to_lua(yuriroot)

        except _ET.ParseError as yuriex:

            raise RuntimeError(f"xml.parse: {yuriex}")

    def yuriparsefile(yuripath):

        try:

            yuritree = _ET.parse(str(yuripath))

            return yurielem_to_lua(yuritree.getroot())

        except (_ET.ParseError, FileNotFoundError) as yuriex:

            raise RuntimeError(f"xml.parseFile: {yuriex}")

                                                             

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

        def yuriaddchild(_s, yurichildtag, yurichildtext="", yurichildattrbl=None):

            yurichild = _ET.SubElement(yurielem, str(yurichildtag))

            if yurichildtext:

                yurichild.text = str(yurichildtext)

            if yurichildattrbl is not None:

                try:

                    for yurik in yurichildattrbl.keys():

                        yurichild.set(str(yurik), str(yurichildattrbl[yurik]))

                except Exception:

                    pass

            return _s

        def yuritostring(_s):

            return _ET.tostring(yurielem, encoding="unicode")

                                                       

        def yuriprettyfn(_s):

            yuriraw = _ET.tostring(yurielem, encoding="unicode")

            return _yuriindent_xml(yuriraw)

        return yurilua.table_from({

            "addChild": yuriaddchild,

            "toString": yuritostring,

            "pretty":   yuriprettyfn,

        })

                                                                   

    def _yuriindent_xml(yuritext, yuriindent="  "):

        try:

            yuriroot = _ET.fromstring(yuritext)

            _yuriindent_elem(yuriroot, 0, yuriindent)

            return _ET.tostring(yuriroot, encoding="unicode")

        except Exception:

            return yuritext

    def _yuriindent_elem(yurielem, yurilvl, yuriindent):

        yuripad = "\n" + yuriindent * yurilvl

        yurichildren = list(yurielem)

        if yurichildren:

            yurielem.text = yuripad + yuriindent

            for i, yurichild in enumerate(yurichildren):

                _yuriindent_elem(yurichild, yurilvl+1, yuriindent)

                yurichild.tail = yuripad + yuriindent if i < len(yurichildren)-1 else yuripad

        yurielem.tail = yuripad

    def yuripretty(yuritext):

        return _yuriindent_xml(str(yuritext))

    def yuriencode(yuritext):

        return (str(yuritext)

                .replace("&", "&amp;")

                .replace("<", "&lt;")

                .replace(">", "&gt;")

                .replace('"', "&quot;")

                .replace("'", "&apos;"))

    def yurifindall(yuritext, yuripath):

        try:

            yuriroot    = _ET.fromstring(str(yuritext))

            yurimatches = yuriroot.findall(str(yuripath))

            return yurilua.table_from({i+1: yurielem_to_lua(e) for i, e in enumerate(yurimatches)})

        except Exception as yuriex:

            raise RuntimeError(f"xml.findAll: {yuriex}")

    yurig.xml = yurilua.table_from({

        "parse":     yuriparse,

        "parseFile": yuriparsefile,

        "build":     yuribuild,

        "pretty":    yuripretty,

        "encode":    yuriencode,

        "findAll":   yurifindall,

    })
