#!/usr/bin/env python
"""A small svg module."""
import math
import os
import re
import subprocess
import uuid
import xml.dom.minidom

from pysvg_cl3.matrix import Matrix
from pysvg_cl3.matrix import Point

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
SODIPODY_NS = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"

SVG_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
'''
SVG_FOOTER = '</svg>'
END_TAG_LINE = '>\n'

twopi = 2.0*math.pi


class SingleTone(object):
    """Singleton class."""
    __instance = None

    def __new__(cls, val):
        if SingleTone.__instance is None:
            SingleTone.__instance = object.__new__(cls)
        SingleTone.__instance.val = val
        return SingleTone.__instance


def get_temp_name(folder=None, prefix=None, suffix=None):
    """Get a temporary name."""
    s = uuid.uuid1().urn.split(':')[2]
    if not folder:
        folder = "/tmp"

    if not prefix:
        prefix = ''

    if not suffix:
        suffix = ''

    name = os.path.join(folder, prefix+s+suffix)
    return name


def find_inkspape():
    """Returns the path of inkscape."""
    folders = ('/usr/bin',
               '/usr/local/bin',
               '/Applications/Inkscape.app/Contents/Resources/bin')
    inkscape = None
    for p in folders:
        inkscape = os.path.join(p, "inkscape")
        if os.path.exists(inkscape):
            break

    if not inkscape:
        raise Exception("Could not find Inkscape")

    return inkscape


def svg2pdf(fin, fout):
    """Convert a svg to a pdf."""
    inkscape = find_inkspape()
    try:
        subprocess.check_output([inkscape, '-z', '-A', fout, fin],
                                stderr=subprocess.STDOUT,
                                shell=False)
    except subprocess.CalledProcessError as xx:
        print("svg2pdf: error rc=%d.\n%s" % (xx.returncode, xx.output))


def svg2png(fin, fout, density=300):
    """Converts a SVG fila into a png."""
#    rc = os.spawnlp(os.P_WAIT,
#                    'convert','convert',
#                    '-units', 'PixelsPerInch',
#                    '-density', '%d' % density, '-background',
#                    'transparent', fin, fout)
    inkscape = find_inkspape()
    try:
        subprocess.check_output([inkscape, '-z', '-d', '%d' % density, '-e', fout, fin],
                                stderr=subprocess.STDOUT,
                                shell=False)
    except subprocess.CalledProcessError as xx:
        print("svg2png: error rc=%d.\n%s" % (xx.returncode, xx.output))


def find_element_by_id(node, element_id):
    """Find element in SVG document by id."""
    for child in node.childNodes:
        if child.hasAttribute('id') and child.getAttribute('id') == element_id:
            return child
        else:
            rc = find_element_by_id(child, element_id)
            if rc:
                return rc

    return None


def bezier_quadratic(t, x0, x1, x2):
    """Evaluates a quadratic bezier."""
    t1 = (1.0-t)
    return t1*t1*x0 + 2.0*t1*t*x1 + t*t*x2


def BezierQuadratic(P0, P1, P2, npts=30):
    """Return npts points that belong to a quadratic bezier."""
    step = 1.0/float(npts)
    for i in range(0, npts+1):
        t = i*step
        P = Point(bezier_quadratic(t, P0.x, P1.x, P2.x),
                  bezier_quadratic(t, P0.y, P1.y, P2.y))
        yield P


def bezier_cubic(t, x0, x1, x2, x3):
    """Evaluates a cubic Bezier."""
    t1 = (1.0-t)
    return t1*t1*t1*x0 + 3.0*t1*t1*t*x1 + 3.0*t1*t*t*x2 + t*t*t*x3


def BezierCubic(P0, P1, P2, P3, npts=30):
    """Returns a list with npts Points in a Cubic Bezier."""
    step = 1.0/float(npts)
    for i in range(0, npts+1):
        t = i*step
        P = Point(bezier_cubic(t, P0.x, P1.x, P2.x, P3.x),
                  bezier_cubic(t, P0.y, P1.y, P2.y, P3.y))
        yield P


def EvalEllipse(xc, yc, rx, ry, npts=30):
    """Evaluates an ellipse.

    Args:
    ----
        xc (float): X coordinate of center
        yc (float): Y coordinate of center
        rx (float): X radius
        ry (float): Y radius
        npts (int, optional): Number of points to evaluate. Defaults to 30.

    Returns
    -------
        Point:  The next point

    Yields
    ------
        Point: The points generated

    """
    ellipse_matrix = Matrix().translate(Point(xc, yc))

    def ellipse(x):
        """Closure for the parametric shape."""
        point = Point(rx*math.cos(x), ry*math.sin(x))
        point = ellipse_matrix.transform(point)
        return point

    step = 1.0/float(npts)
    for i in range(0, npts+1):
        t = i*step
        P = ellipse(2.0*math.pi*t)
        yield P


def EvalArc(rx, ry, phi, fa, fs, p0, p1, npts=30):
    """Evaluates points in an Arc.

    NOTE: this implementation follows Standard SVG 1.1 implementation guidelines
          for elliptical arc curves. See Appendix F.6.
    """
    sin_rot_angle = math.sin(phi)
    cos_rot_angle = math.cos(phi)

    d = p0 - p1
    m = Matrix([cos_rot_angle, -sin_rot_angle,
                sin_rot_angle, cos_rot_angle, 0.0, 0.0])
    p = m.transform(0.5*d)
    rx2 = rx*rx
    ry2 = ry*ry
    rxpy = rx*p.y
    rypx = ry*p.x
    rx2py2 = rxpy*rxpy
    ry2px2 = rypx*rypx
    num = rx2*ry2
    den = rx2py2 + ry2px2
    if den == 0.0:
        print("Cannot compute ellipse")
        return

    rad = num / den
    c = Point()
    if rad > 1.0:
        rad = rad - 1.0
        rad = math.sqrt(rad)

        if fa == fs:
            rad = -rad

        c = rad * Point(rxpy/ry, -rypx/rx)
        m[1] = -m[1]
        m[2] = -m[2]

        center = m.transform(c) + 0.5*(p0 + p1)
    elif rad == 1.0:
        center = 0.5*(p0 + p1)
    elif rad > 0.0:
        lmd = math.sqrt(1.0/rad)
        rx *= lmd
        ry *= lmd
        center = 0.5 * (p0+p1)
    else:
        print("There is no ellipse that satisfies the given constrains")

    sp = Point((p.x - c.x)/rx, (p.y - c.y)/ry)
    ep = Point((-p.x - c.x)/rx, (-p.y-c.y)/ry)
    v = Point(1.0, 0.0)
    start_angle = v.angle(sp)
    sweep_angle = sp.angle(ep)

    if fs == 0.0 and sweep_angle > 0.0:
        sweep_angle -= twopi

    if fs and sweep_angle < 0.0:
        sweep_angle += twopi

    if start_angle < 0.0:
        start_angle += twopi

    ellipse_matrix = Matrix().rotate(phi).translate(center)

    def ellipse(t):
        """Closure for the parametric shape."""
        x = start_angle + t * sweep_angle
        point = Point(rx*math.cos(x), ry*math.sin(x))
        point = ellipse_matrix.transform(point)
        return point

    step = 1.0/float(npts)
    for i in range(0, npts+1):
        t = i*step
        P = ellipse(t)
        yield P


def lexPath(d):
    """Path parser.

    Return an iterator that breaks path data identifies
    command and parameter tokens
    """
    offset = 0
    length = len(d)
    wps = re.compile(r'[ \t\r\n,]+')
    command = re.compile(r'[MLHVCSQTAZmlhvcsqtaz]')
    parameter = re.compile(r'(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)')
    while 1:
        m = wps.match(d, offset)
        if m:
            offset = m.end()
        if offset >= length:
            break
        m = command.match(d, offset)
        if m:
            yield [d[offset:m.end()], True]
            offset = m.end()
            continue
        m = parameter.match(d, offset)
        if m:
            yield [d[offset:m.end()], False]
            offset = m.end()
            continue
        # TODO: create new exception
        raise Exception('Invalid path data! '+d)


'''
pathdefs = {commandfamily:
    [
    implicitnext,
    #params,
    [casts,cast,cast],
    [coord type,x,y,0]
    ]}
'''
pathdefs = {
    'M': ['L', 2, [float, float], ['x', 'y']],
    'L': ['L', 2, [float, float], ['x', 'y']],
    'H': ['H', 1, [float], ['x']],
    'V': ['V', 1, [float], ['y']],
    'C': ['C', 6, [float, float, float, float, float, float], ['x', 'y', 'x', 'y', 'x', 'y']],
    'S': ['S', 4, [float, float, float, float], ['x', 'y', 'x', 'y']],
    'Q': ['Q', 4, [float, float, float, float], ['x', 'y', 'x', 'y']],
    'T': ['T', 2, [float, float], ['x', 'y']],
    'A': ['A', 7, [float, float, float, int, int, float, float], [0, 0, 0, 0, 0, 'x', 'y']],
    'Z': ['L', 0, [], []]
}


def parsePath(d):
    """Parse SVG path and return an array of segments.

    Removes all shorthand notation.
    Converts coordinates to absolute.
    """
    retval = []
    lexer = lexPath(d)

    pen = (0.0, 0.0)
    subPathStart = pen
    lastControl = pen
    lastCommand = ''
    moveTo = 0

    while 1:
        try:
            token, isCommand = next(lexer)
        except StopIteration:
            break
        params = []
        needParam = True
        if isCommand:
            if not lastCommand and token.upper() != 'M':
                raise Exception('Invalid path, must begin with moveto.')
            else:
                command = token
                if command in ('M', 'm'):
                    moveTo = command
                else:
                    moveTo = 0
        else:
            # command was omited
            # use last command's implicit next command
            needParam = False
            if lastCommand:
                if token.isupper():
                    command = pathdefs[lastCommand.upper()][0]
                else:
                    command = pathdefs[lastCommand.upper()][0].lower()
                    if moveTo == 'M' and command == 'l':
                        command = 'L'
            else:
                raise Exception('Invalid path, no initial command.')
        numParams = pathdefs[command.upper()][1]
        while numParams > 0:
            if needParam:
                try:
                    token, isCommand = next(lexer)
                    if isCommand:
                        raise Exception('Invalid number of parameters')
                except StopIteration:
                    raise Exception('Unexpected end of path')
            cast = pathdefs[command.upper()][2][-numParams]
            param = cast(token)
            if command.islower():
                if pathdefs[command.upper()][3][-numParams] == 'x':
                    param += pen[0]
                elif pathdefs[command.upper()][3][-numParams] == 'y':
                    param += pen[1]
            params.append(param)
            needParam = True
            numParams -= 1
        # segment is now absolute so
        outputCommand = command.upper()

        # Flesh out shortcut notation
        if outputCommand in ('H', 'V'):
            if outputCommand == 'H':
                params.append(pen[1])
            if outputCommand == 'V':
                params.insert(0, pen[0])
            outputCommand = 'L'
        if outputCommand in ('S', 'T'):
            params.insert(0, pen[1]+(pen[1]-lastControl[1]))
            params.insert(0, pen[0]+(pen[0]-lastControl[0]))
            if outputCommand == 'S':
                outputCommand = 'C'
            if outputCommand == 'T':
                outputCommand = 'Q'

        # current values become "last" values
        if outputCommand == 'M':
            subPathStart = tuple(params[0:2])
        if outputCommand == 'Z':
            pen = subPathStart
        else:
            pen = tuple(params[-2:])

        if outputCommand in ('Q', 'C'):
            lastControl = tuple(params[-4:-2])
        else:
            lastControl = pen
        lastCommand = command

        retval.append([outputCommand, params])
    return retval


def formatPath(a):
    """Format SVG path data from an array."""
    return "".join([cmd + " ".join([str(p) for p in params]) for cmd, params in a])


def translatePath(p, x, y):
    """Translates a path."""
    for cmd, params in p:
        defs = pathdefs[cmd]
        for i in range(defs[1]):
            if defs[3][i] == 'x':
                params[i] += x
            elif defs[3][i] == 'y':
                params[i] += y


def scalePath(p, x, y):
    """Scales a path."""
    for cmd, params in p:
        defs = pathdefs[cmd]
        for i in range(defs[1]):
            if defs[3][i] == 'x':
                params[i] *= x
            elif defs[3][i] == 'y':
                params[i] *= y


def rotatePath(p, a, cx=0, cy=0):
    """Rotates a path."""
    if a == 0:
        return p
    for cmd, params in p:
        defs = pathdefs[cmd]
        for i in range(defs[1]):
            if defs[3][i] == 'x':
                x = params[i] - cx
                y = params[i + 1] - cy
                r = math.sqrt((x**2) + (y**2))
                if r != 0:
                    theta = math.atan2(y, x) + a
                    params[i] = (r * math.cos(theta)) + cx
                    params[i + 1] = (r * math.sin(theta)) + cy


class Units(object):
    """Stores conversions among units.

    Base Unit is px=1
    """

    px = 1.0
    inch = 90.0
    pt = 1.25
    mm = 3.5433070866
    cm = 35.433070866
    um = mm/1000.
    pc = 15.0
    degree = 57.295779513082323
    radian = 0.017453292519943295

    units = {"px": px, "in": inch, "pt": pt, "mm": mm, "cm": cm}
    default_unit = None

    @staticmethod
    def set_default_unit(val):
        """Sets the default unit."""
        Units.default_unit = val

    @staticmethod
    def get_factor(unit_name):
        """Get conversion factor to default units."""
        if Units.default_unit is None:
            return 1.0

        else:
            val = Units.units.get(unit_name, 1.0)
            return 1.0/val

    @staticmethod
    def get_value(val):
        """Return a string representation of the value with units."""
        if Units.default_unit is None:
            return str(val)

        else:
            rc = val * Units.get_factor(Units.default_unit)
            return "%f%s" % (rc, Units.default_unit)


class BoundingBox(object):
    """Bounding box object."""

    MAX_VALUE = 1.e20
    MIN_VALUE = -MAX_VALUE

    def __init__(self, llx, lly, urx, ury):
        """Initialization."""
        self.bb = [llx, lly, urx, ury]

    def __str__(self):
        """String represetnation."""
        return "%s - center %s" % (self.bb, self.center())

    def width(self):
        """Return width."""
        return abs(self.bb[2] - self.bb[0])

    def height(self):
        """Return height."""
        return abs(self.bb[3] - self.bb[1])

    def center(self):
        """Return the center of the Bounding Box."""
        return 0.5*(self.bb[0]+self.bb[2]), 0.5*(self.bb[1]+self.bb[3])

    def pos(self):
        """Return position of BB."""
        return self.bb[0], self.bb[1]

    def get_ll(self):
        """Get Lower Left corner."""
        return self.bb[0], self.bb[1]

    def get_ur(self):
        """Return Upper Right corner."""
        return self.bb[2], self.bb[2]

    def get_llx(self):
        """Get X of lower left corner."""
        return self.bb[0]

    def get_lly(self):
        """Get Y of lower left corner."""
        return self.bb[1]

    def get_urx(self):
        """Get X of upper right corner."""
        return self.bb[2]

    def get_ury(self):
        """Get Y of upper right corner."""
        return self.bb[3]

    def set_ll(self, x, y):
        """Set value of lower left corner."""
        self.bb[0] = x
        self.bb[1] = y

    def set_ur(self, x, y):
        """Set value of upper right corner."""
        self.bb[2] = x
        self.bb[3] = y

    def set_bb(self, llx, lly, urx, ury):
        """Set values of upper righ and lower left corners."""
        self.bb = [llx, lly, urx, ury]

    def get_points(self):
        """Generate all the bb points."""
        for x in range(0, 2):
            for y in range(0, 2):
                yield self.bb[2*x], self.bb[2*y+1]

    def union(self, bb):
        """Sets the bounding box to the union of the two."""
        for i in range(0, 2):
            self.bb[i] = min(self.bb[i], bb.bb[i])

        for j in range(2, 4):
            self.bb[j] = max(self.bb[j], bb.bb[j])

    def union_point(self, bb):
        """Sets the bounding box to the union of a Point and a BB."""
        for i in range(0, 2):
            self.bb[i] = min(self.bb[i], bb[i])

        for j in range(0, 2):
            self.bb[j+2] = max(self.bb[j+2], bb[j])

    def convert(self, unit):
        """Convert to given units."""
        try:
            conv = getattr(Units, unit)
            self.bb = [x/conv for x in self.bb]
        except AttributeError:
            print('Unknown unit', unit)


def bounding_box():
    """Create a bounding box instance."""
    return BoundingBox(BoundingBox.MAX_VALUE, BoundingBox.MAX_VALUE,
                       BoundingBox.MIN_VALUE, BoundingBox.MIN_VALUE)


def convertTupleArrayToPoints(arrayOfPointTuples):
    """Method used to convert an array of tuples (x,y) into a string.

    Suitable for createPolygon or createPolyline

    Args:
    ----
        arrayOfPointTuples (list): An array containing tuples
                                   eg.[(x1,y1),(x2,y2)]
                                   needed to create the shape

    Return:
    ------
        A string in the form 'x1,y1 x2,y2 x3,y3'.

    """
    points = ""
    for tple in arrayOfPointTuples:
        points += str(tple[0]) + "," + str(tple[1]) + " "

    return points


#
# We define a global xml.dom.minidom.Document instance that we will use
# to create the different elements
#
NAMESPACES = {
    "svg": SVG_NS,
    "xmlns:xlink": XLINK_NS,
    "xmlns:inkscape": INKSCAPE_NS,
    "xmlns:sodipodi": SODIPODY_NS
}
DOC = xml.dom.minidom.getDOMImplementation().createDocument(None, "svg", None)
# for __key, __val in list(NAMESPACES.items()):
#     DOC.documentElement.setAttribute(__key, __val)


def addNamespace(key, uri):
    """Add given namespace."""
    tag = "xmlns:"+key
    if tag not in NAMESPACES:
        NAMESPACES[tag] = uri


def getNSUri(key):
    """Get the URL of a given namespace key."""
    tag = "xmlns:"+key
    return NAMESPACES.get(tag, None)


# ------------new
G__object_library = {}


def addGlobalDefition(name, obj):
    global G__object_library
    if name in G__object_library:
        pass  # print("Object ", name, "already exists. Ignoring")
    else:
        G__object_library[name] = obj


class SVG(object):
    """Base class for a SVG document."""

    def __init__(self, title="svg", description="",
                 height=None, width=None, default_unit=None, viewBox=None, adjust=False):
        """Initialization.

        Args:
        ----
            title (str, optional): Title of the document. Defaults to "svg".
            description (str, optional): Description of the document.
            height ([type], optional): Height of the document.
            width ([type], optional): Width of the document.
            default_unit ([type], optional): Default unit.
            viewBox ([type], optional): [description].
            adjust (bool, optional): [description].

        """
        self.adjust = adjust
        self.height = height
        self.width = width
        if self.height is None:
            if self.width is None:
                self.height = 100
                self.width = 100

            else:
                self.height = self.width

        if self.width is None:
            if self.height is None:
                self.height = 100
                self.width = 100

            else:
                self.width = self.height

        self.view = {}
        self.default_unit = default_unit
        if self.default_unit is None:
            self.default_unit = ""

        impl = xml.dom.minidom.getDOMImplementation()
        svgDOCTYPE = impl.createDocumentType("svg",
                                             "-//W3C//DTD SVG 1.0//EN",
                                             "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd")
        self.doc = impl.createDocument("http://www.w3.org/2000/svg", "svg", None)
        # self.doc = xml.dom.minidom.Document()getDOMImplementation().createDocument(SVG_NS, "svg", None)

        self.doc.documentElement.setAttribute("width", "%f%s" % (self.width, self.default_unit))
        self.doc.documentElement.setAttribute("height", "%f%s" % (self.height, self.default_unit))
        if viewBox is None:
            self.doc.documentElement.setAttribute("viewBox", "0 0 %f %f" % (self.width, self.height))
        else:
            self.doc.documentElement.setAttribute("viewBox", "%f %f %f %f" % viewBox)

        svg = self.doc.documentElement
        for key, val in list(NAMESPACES.items()):
            self.doc.documentElement.setAttribute(key, val)

        self.namedview = self.doc.createElement("sodipodi:namedview")
        svg.appendChild(self.namedview)
        self.namedview.setAttribute("id", "base")
        self.__description = None

        self.main_defs = Defs()
        self.addElement(self.main_defs)

    def add_namespace(self, ns, uri):
        """Add given namespace."""
        self.doc.documentElement.setAttribute("xmlns:"+ns, uri)

    def get_top(self):
        """Get the top element."""
        return self.doc.documentElement

    def getXML(self):
        """Return a XML representation of the current SVG document.

        This function can be used for debugging purposes.

        Return:
        ------
            the representation of the current SVG as an xml string.

        """
        return self.doc.toprettyxml("   ")

    def bounding_box(self):
        """Get the bounding box of the whole picture."""
        bb = bounding_box()
        for node in self.doc.documentElement.childNodes:
            try:
                bb.union(node.object.bounding_box())
            except AttributeError:
                pass

        return bb

    def add_defs(self):
        """Add dangling defs."""
        global G__object_library

        # Get existing definitions
        already_there = {}
        for node in self.main_defs.element.childNodes:
            try:
                already_there[node.id] = node
            except AttributeError:
                pass

        for name, obj in G__object_library.items():
            if name in already_there:
                pass
            else:
                self.main_defs.addElement(obj)

    def saveSVG(self, filename):
        """Save the current SVG document into a file.

        Args:
        ----
            filename: file to store the svg in (complete path+filename+extension)

        """
        f = open(filename, 'w')
        if len(self.view) > 0:
            for key, val in list(self.view.items()):
                self.namedview.setAttribute(key, str(val))

        if self.adjust:
            self.adjust_to_window()

        bb = self.bounding_box()

        if self.adjust:
            self.width = bb.width()
            self.height = bb.height()
            self.doc.documentElement.setAttribute("width", "%f%s" % (self.width, self.default_unit))
            self.doc.documentElement.setAttribute("height", "%fpx%s" % (self.height, self.default_unit))

        for node in self.doc.documentElement.childNodes:
            try:
                node.object.update()
            except AttributeError:
                pass

        # Add dangling defs
        self.add_defs()

        self.doc.writexml(f, indent="\t", addindent="\t",
                          newl='\n', encoding='UTF-8')
        f.flush()
        f.close()

    def show(self):
        """Shows the SVG file."""
        fsvg = get_temp_name(folder="/tmp", prefix="svg_", suffix=".svg")
        fpng = get_temp_name(folder="/tmp", prefix="svg_", suffix=".png")

        self.saveSVG(fsvg)
        try:
            svg2png(fsvg, fpng, 72)
        except OSError as e:
            print(e)
            return

        rc = os.spawnlp(os.P_WAIT, 'xdg-open', 'xdg-open', fpng)
        if rc:
            print("Could not show the svg file")

    def set_document_units(self, units):
        """Set the document units."""
        self.view['inkscape:document-units'] = units

    def set_snap(self, do_snap):
        """Set the snap option of the document."""
        if do_snap:
            self.view['inkscape:object-paths'] = "true"
            self.view['inkscape:object-nodes'] = "true"
            self.view['inkscape:snap-center'] = "true"
            self.view['guidetolerance'] = "100"
            self.view['objecttolerance'] = "100"
            self.view['gridtolerance'] = "100"

        else:
            del self.view['inkscape:object-paths']
            del self.view['inkscape:object-nodes']
            del self.view['inkscape:snap-center']
            del self.view['guidetolerance']
            del self.view['objecttolerance']
            del self.view['gridtolerance']

    def addElement(self, element):
        """Generic method to add any element to the document.

        Args:
        ----
            element: Object that contains a getXML method (circle, line, text, polyline, etc....)

        """
        self.doc.documentElement.appendChild(element.element)

    def createComment(self, txt):
        """Create a comment."""
        E = DOC.createComment(txt)
        self.doc.documentElement.appendChild(E)

    def addTextElement(self, ns, tag, txt):
        """Add a text element."""
        E = DOC.createElementNS(ns, tag)
        E.appendChild(DOC.createTextNode(txt))
        self.doc.documentElement.appendChild(E)

    def adjust_to_window(self):
        """Adjust the overall image to the page size."""
        bb = self.bounding_box()
        translation = Point(self.width/2.0, self.height/2.0) - Point(bb.center())
        for node in self.doc.documentElement.childNodes:
            try:
                if node.tagName.find("sodipodi") < 0:
                    T = TransformHelper()
                    T.setTranslation(translation.x, translation.y)
                    if node.object.transform_dict:
                        node.object.transform_dict.insert(0, T.getTransformDict()[0])
                    else:
                        node.object.transform_dict = T.getTransformDict()

            except AttributeError:
                pass

    def add_guide(self, name, direction, position):
        """Add a guide to the document."""
        view = self.namedview
        guide = DOC.createElement("sodipodi:guide")
        view.appendChild(guide)

        guide.setAttribute("id", name)
        guide.setAttribute("orientation", "%d,%d" % (direction[0], direction[1]))
        guide.setAttribute("position", "%f,%f" % (position[0], position[1]))

    def set_description(self, text):
        """Set the document description."""
        if self.__description is None:
            desc = DOC.createElement("desc")
            self.__description = desc
            self.doc.documentElement.appendChild(desc)
        else:
            desc = self.__description

        tt = DOC.createTextNode(text)
        desc.appendChild(tt)

    def add_private_description(self, ns, tag, txt):
        """Add a private description."""
        if self.__description is None:
            desc = DOC.createElement("desc")
            self.__description = desc
            self.doc.documentElement.appendChild(desc)
        else:
            desc = self.__description

        E = DOC.createElementNS(ns, tag)
        E.appendChild(DOC.createTextNode(txt))
        desc.appendChild(E)

        return E


class BaseElement(object):
    """Base class for all svg elements like elipses, texts, lines etc."""

    def __init__(self, style_dict=None, transform_dict=None, tag=None):
        """Initialization.

        Args:
        ----
            style_dict (dct, optional): The style dictionary.
            transform_dict (dict, optional): The transform dict.
            tag (string, optional): The xml tag of the object.

        """
        if not tag:
            tag = self.__class__.__name__
        self.__element = DOC.createElement(tag)
        self.__element.object = self
        self.__description = None
        self.style_dict = style_dict
        if not self.style_dict:
            self.style_dict = {}

        self.transform_dict = transform_dict
        if not self.transform_dict:
            self.transform_dict = {}

        self.attr_with_units = []
        self.xlink_href = None
        self.description = None
        self.bb = BoundingBox(0, 0, 0, 0)

    def set_id(self, iid):
        """Sets the element id."""
        self.setAttribute("id", iid)

    def get_id(self):
        """Return the element id."""
        iid = self.getAttribute("id")
        return iid

    id = property(get_id, set_id, None, "Object id")

    def addElement(self, element):
        """Generic method to add any element to the container.

        Args:
        ----
            element(Element): the element to add to the container.

        """
        self.__element.appendChild(element.element)

    def set_description(self, txt):
        """Add a description of the object."""
        self.description = txt
        if self.__description is None:
            desc = DOC.createElement("desc")
            self.__description = desc
            self.__element.appendChild(desc)
            tt = DOC.createTextNode(self.description)
        else:
            desc = self.__description

        desc.appendChild(tt)

    def add_private_description(self, ns, tag, txt):
        """Add a private description."""
        if self.__description is None:
            desc = DOC.createElement("desc")
            self.__description = desc
            self.__element.appendChild(desc)
        else:
            desc = self.__description

        E = DOC.createElementNS(ns, tag)
        E.appendChild(DOC.createTextNode(txt))
        desc.appendChild(E)

        return E

    def setAttribute(self, attr, val):
        """Sets an attribute value."""
        if val is None:
            return

        if attr in self.attr_with_units:
            sval = Units.get_value(val)
        else:
            sval = str(val)

        self.__element.setAttribute(attr, sval)

    def setAttributeNS(self, attr, val, ns):
        """Set the NS sttribute."""
        uri = getNSUri(ns)
        self.__element.setAttributeNS(uri, attr, str(val))

    def getAttribute(self, attr):
        """Get an attribute value."""
        return self.__element.getAttribute(attr)

    def extra_tags(self):
        """Called right before passing the xml.dom element.

        This method should be implemented by each of the Elements derived
        from this class.
        """
        pass

    def add_clipPath(self, clip_path):
        """Add a clip path to the object."""
        self.setAttribute("clip-path", "url(#{})".format(clip_path.id))

    def addTransform(self, transform, append=True):
        """Adds a new transform.

        If append is True it will be appended (that is,
        the very first transform, otherwise it is inserted
        at the beginning (the very last transform)
        """
        if not self.transform_dict:
            self.transform_dict = [transform]
        else:
            if append:
                self.transform_dict.append(transform)
            else:
                self.transform_dict.insert(0, transform)

    def bounding_box(self, M=None):
        """Computes the bounding box."""
        if not M:
            M = Matrix()

        if self.transform_dict:
            m = Matrix()
            m.parse(self.getXMLFromTransform())
            M = M * m

        self.bb = bounding_box()
        for node in self.element.childNodes:
            try:
                oobb = node.object.bounding_box(M)
                self.bb.union(oobb)
            except AttributeError:
                pass

        return self.bb

    def update_values(self):
        """Transfers the object values to the svg element."""
        if self.style_dict:
            self.__element.setAttribute("style", self.getXMLFromStyle())

        if self.transform_dict:
            self.__element.setAttribute("transform", self.getXMLFromTransform())

        if self.xlink_href:
            self.__element.setAttribute("xlink:href", self.xlink_href)

        if hasattr(self, "id") and getattr(self, "id"):
            eid = getattr(self, "id")
            try:
                aid = self.__element.getAttribute("id")
                if aid != eid:
                    self.__element.setAttribute("id", eid)

            except xml.dom.NotFoundErr:
                self.__element.setAttribute("id", eid)

        self.extra_tags()

    def update(self):
        """Update own values and those of the children."""
        self.update_values()
        for node in self.__element.childNodes:
            try:
                node.object.update_values()
            except AttributeError:
                pass

    def _get_xml(self):
        """Get the xml element."""
        return self.__element

    xml = property(_get_xml)

    def get_element(self):
        """Get the xml alement."""
        self.update()
        return self.__element

    element = property(get_element)

    def getXMLFromStyle(self):
        """Convert style dict to SVG undestandable string.

        This method converts the information in the style
        dictionary into svg syntax for the style attribute

        Return:
        ------
            the representation of the current style as an xml_string string.

        """
        count = 0
        xml_string = ""
        for key in list(self.style_dict.keys()):
            if self.style_dict.get(key) == "":
                continue
            if count > 0:
                xml_string += '; '

            xml_string += '%s:%s' % (key, self.style_dict.get(key))
            count += 1

        if len(xml_string) > 0:
            return xml_string
        else:  # empty style
            return ""

    def getXMLFromTransform(self):
        """Convert transform dict to SVG understandable string.

        This method converts the information in the transform
        dictionary into svg syntax for the transform attribute

        Return:
        ------
            the representation of the current transformations as an xml_string string.

        """
        return ''.join([s+' ' for s in self.transform_dict])

    def show(self):
        """Show the element."""
        doc = SVG("s", "test", adjust=True)
        doc.addElement(self)
        doc.show()


class Group(BaseElement):
    """SVG Group.

    Base class for a container element. Different shapes, paths and
    text can be put together inside a container sharing the same style.
    """

    def __init__(self, idname=None, style_dict=None, transform_dict=None):
        """Initialization."""
        super(Group, self).__init__(tag="g",
                                    style_dict=style_dict,
                                    transform_dict=transform_dict)
        if idname:
            self.id = idname

        self.layer_name = False

    def extra_tags(self):
        """Set the attributes."""
        if self.layer_name:
            self.setAttribute("inkscape:groupmode", "layer")
            self.setAttribute("inkscape:label", self.layer_name)
        else:
            try:
                self.xml.removeAttribute("inkscape:groupmode")
                self.xml.removeAttribute("inkscape:label")
            except xml.dom.NotFoundErr:
                pass

    def asLayer(self, name):
        """Inkscape specific. Makes this group an Inkscape layer.

        The input is the layer name. If None, it stops being a layer
        """
        self.layer_name = name
        self.set_id(name)


class Defs(BaseElement):
    """Packs all definitions."""

    def __init__(self):
        """Initialization."""
        super(Defs, self).__init__(tag="defs")

    def addDefinition(self, definition):
        """Add a new definition."""
        global G__object_library
        self.addElement(definition)
        if definition.id:
            G__object_library[definition.id] = definition

    def removeDefinition(self, def_id):
        """Remove an existing definition."""
        for node in self.element.getElementsByTagName('*'):
            if node.hasAttribute("id"):
                if node.getAttribute("id") == def_id:
                    self.element.removeChild(node)
                    break


class clipPath(BaseElement):
    """clipPath element.

    Should go into the defs section
    """
    def __init__(self, idname, style_dict=None, transform_dict=None):
        super(clipPath, self).__init__(tag="clipPath",
                                       style_dict=style_dict,
                                       transform_dict=transform_dict)

        global G__object_library
        if idname in G__object_library:
            print("Tere is already an object wit hthis name:", idname)

        self.id = idname
        G__object_library[self.id] = self


class Mask(BaseElement):
    """A mask element

    Different shapes, paths and text can be put together inside a
    container sharing the same style.
    """

    def __init__(self, idname=None, style_dict=None, transform_dict=None):
        """Initialization."""
        super(Mask, self).__init__(tag="mask",
                                   style_dict=style_dict,
                                   transform_dict=transform_dict)
        if idname:
            self.id = idname


class Stop(BaseElement):
    """Stop element."""

    def __init__(self, offset, stopcolor):
        """Offset and stop color should be string."""
        super(Stop, self).__init__(tag="stop")
        self.offset = offset
        self.stopcolor = stopcolor

    def extra_tags(self):
        """Add the attributes."""
        self.setAttribute("offset", str(self.offset))
        self.setAttribute("stop-color", self.stopcolor)


class LinearGradient(BaseElement):
    """Implements a linear gradient."""

    def __init__(self, grad_id, x1, y1, x2, y2):
        """Initialization."""
        super(LinearGradient, self).__init__(tag="linearGradient")
        self.id = grad_id
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def extra_tags(self):
        """Set the attributes."""
        self.setAttribute("id", self.id)
        self.setAttribute("x1", "%.4f" % self.x1)
        self.setAttribute("y1", "%.4f" % self.y1)
        self.setAttribute("x2", "%.4f" % self.x2)
        self.setAttribute("y2", "%.4f" % self.y2)

    def addStop(self, offset, color):
        """A new stop element."""
        s = Stop(offset, color)
        self.addElement(s.element)


class Use(BaseElement):
    """A use element."""

    def __init__(self, cloneof, x=None, y=None):
        """Initialization."""
        super(Use, self).__init__(tag="use")
        self.cloneof = cloneof
        self.x = x
        self.y = y

    def extra_tags(self):
        """Set the attributes."""
        if self.x is not None:
            self.setAttribute("x", "%.4f" % self.x)

        if self.y is not None:
            self.setAttribute("y", "%.4f" % self.y)

        self.setAttribute("xlink:href", "#%s" % self.cloneof)

    def bounding_box(self, M=None):
        """Return the Bounding box."""
        global G__object_library
        self.bb = bounding_box()
        if not M:
            M = Matrix()

        if self.transform_dict:
            m = Matrix()
            m.parse(self.getXMLFromTransform())
            M = M * m

        try:
            original = G__object_library[self.cloneof]

        except Exception:
            top = self.element

            while top.parentNode:
                top = top.parentNode

            original = find_element_by_id(top, self.cloneof)

        if not original:
            pass
            # print("Could not find original element:", self.cloneof)

        else:
            original.object.bounding_box(M)
            self.bb = original.object.bb

        return self.bb


class line(BaseElement):
    """The line element of an svg doc.

    Note that this element is NOT painted VISIBLY by default UNLESS you provide
    a style including STROKE and STROKE-WIDTH
    """

    def __init__(self, x1=None, y1=None, x2=None, y2=None, style_dict=None):
        """Create a line.

        Args:
        ----
            x1:  starting x-coordinate
            y1:  starting y-coordinate
            x2:  ending x-coordinate
            y2:  ending y-coordinate
            style_dict:  style(s) to use for this element

        """
        super(line, self).__init__(style_dict=style_dict)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def extra_tags(self):
        """Set the attributes."""
        self.setAttribute("x1", "%.4f" % self.x1)
        self.setAttribute("y1", "%.4f" % self.y1)
        self.setAttribute("x2", "%.4f" % self.x2)
        self.setAttribute("y2", "%.4f" % self.y2)

    def bounding_box(self, M=None):
        """Return the bounding box."""
        if not M:
            M = Matrix()

        if self.transform_dict:
            m = Matrix()
            m.parse(self.getXMLFromTransform())
            M = M * m

        stroke = 1.0
        if 'stroke-width' in self.style_dict:
            stroke = float(self.style_dict['stroke-width'])

        stroke = stroke/2.0
        ll = Point(min(self.x1-stroke, self.x2-stroke),
                   min(self.y1-stroke, self.y2-stroke))
        ur = Point(max(self.x1+stroke, self.x2+stroke),
                   max(self.y1+stroke, self.y2+stroke))

        ll = M*ll
        ur = M*ur
        self.bb = BoundingBox(min(ll.x, ur.x), min(ll.y, ur.y),
                              max(ll.x, ur.x), max(ll.y, ll.x))

        return self.bb


class ellipse(BaseElement):
    """The ellipse element of an svg doc."""

    def __init__(self, cx=None, cy=None, rx=None, ry=None, style_dict=None):
        super(ellipse, self).__init__(style_dict=style_dict)
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry

    def bounding_box(self, M=None):
        """ Not implemented """

        if not M:
            M = Matrix()

        if self.transform_dict:
            m = Matrix()
            m.parse(self.getXMLFromTransform())
            M = M * m

        bb = bounding_box()
        for P in EvalEllipse(self.cx, self.cy, self.rx, self.ry):
            bb.union_point(P)

        self.bb = bb
        return self.bb

    def extra_tags(self):
        """ Set the attributes
        """
        self.setAttribute("cx", "%.4f" % self.cx)
        self.setAttribute("cy", "%.4f" % self.cy)
        self.setAttribute("rx", "%.4f" % self.rx)
        self.setAttribute("ry", "%.4f" % self.ry)


class rect(BaseElement):
    """
    Class representing the rect element of an svg doc.
    """

    def __init__(self, x=0.0, y=0.0,
                 width=None, height=None,
                 rx=None, ry=None,
                 style_dict=None):

        super(rect, self).__init__(style_dict=style_dict)
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.rx = rx
        self.ry = ry

    def extra_tags(self):
        """ Set the attributes
        """
        for name in ["x", "y", "width", "height", "rx", "ry"]:
            val = getattr(self, name)
            if val is not None:
                self.setAttribute(name, "%.4f" % val)

    def bounding_box(self, M=None):
        if not M:
            M = Matrix()

        if self.transform_dict:
            m = Matrix()
            m.parse(self.getXMLFromTransform())
            M = M * m

        stroke = 1.0
        if 'stroke-width' in self.style_dict:
            stroke = float(self.style_dict['stroke-width'])

        stroke = stroke/2.0
        points = (Point(self.x-stroke, self.y-stroke),
                  Point(self.x-stroke, self.y+self.height+stroke),
                  Point(self.x+self.width+stroke, self.y+self.height+stroke),
                  Point(self.x+self.width+stroke, self.y-stroke)
                  )

        self.bb = bounding_box()
        for P in points:
            self.bb.union_point(M.transform(P))

        return self.bb


class circle(BaseElement):
    """
    Class representing the cirle element of an svg doc.
    """

    def __init__(self, cx=None, cy=None, r=None,
                 style_dict=None, focusable=None):

        super(circle, self).__init__(style_dict=style_dict)
        self.cx = cx
        self.cy = cy
        self.r = r

    def extra_tags(self):
        """ Set the attributes
        """
        self.setAttribute("cx", "%.4f" % self.cx)
        self.setAttribute("cy", "%.4f" % self.cy)
        self.setAttribute("r", "%.4f" % self.r)

    def bounding_box(self, M=None):
        if not M:
            M = Matrix()

        if self.transform_dict:
            m = Matrix()
            m.parse(self.getXMLFromTransform())
            M = M * m

        stroke = 1.0
        if 'stroke-width' in self.style_dict:
            stroke = float(self.style_dict['stroke-width'])

        stroke = stroke/2.0

        bb = bounding_box()
        for P in EvalEllipse(self.cx, self.cy, self.r+stroke, self.r+stroke):
            bb.union_point(P)

        self.bb = bb
        return self.bb

# todo: BaseElement wont work here ...
#        make this class seperate of the hirarchie or try
#        to make it work ?


class polygon(BaseElement):
    """ Draws a polygon
    """

    def __init__(self, points=None, style_dict=None, transform_dict=None):
        super(polygon, self).__init__(style_dict=style_dict, transform_dict=transform_dict)
        self.points = None
        self.set_points(points)

    def set_points(self, point_list):
        """ Sets the points
        """
        if isinstance(point_list, list) or isinstance(point_list, tuple):
            self.points = convertTupleArrayToPoints(point_list)
        else:
            self.points = point_list

    def extra_tags(self):
        """ Set the attributes
        """
        self.setAttribute("points", self.points)

    def bounding_box(self, M=None):
        p = re.compile(r"""(?P<x>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)+? # X
                           \s*,\s*                                          # separator
                           (?P<y>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)+? # Y
                           """,
                       re.VERBOSE)

        stroke = 1.0
        if 'stroke-width' in self.style_dict:
            stroke = float(self.style_dict['stroke-width'])

        stroke = stroke/2.0
        if not M:
            M = Matrix()

        if self.transform_dict:
            m = Matrix()
            m.parse(self.getXMLFromTransform())
            M = M * m

        self.bb = bounding_box()
        for m in p.finditer(self.points):
            x = float(m.group('x'))
            y = float(m.group('y'))

            self.bb.union_point(M.transform(Point(x, y)))

        return self.bb


class polyline(polygon):
    """
    Class representing the polyline element of an svg doc.
    """

    def __init__(self, points=None, style_dict=None, transform_dict=None):
        super(polyline, self).__init__(points, style_dict, transform_dict)


class text(BaseElement):
    """
    Class representing the text element of an svg doc.
    @type  content: string
    @param content:  the text to display
    @type  x: int
    @param x:  x-coordinate for the text
    @type  y: int
    @param y:  y-coordinate for the text
    @type  rotate: int
    @param rotate:  rotation in degrees (negative means counterclockwise)
    """

    def __init__(self, content, x, y, rotate=None,
                 style_dict=None, transform_dict=None, editable=None, focusable=None):

        super(text, self).__init__(style_dict=style_dict, transform_dict=transform_dict)
        self.x = x
        self.y = y
        self.rotate = rotate
        self.editable = editable
        self.content = content
        self.text = None

    def extra_tags(self):
        """ Set the attributes
        """
        self.setAttribute("x", "%.4f" % self.x)
        self.setAttribute("y", "%.4f" % self.y)
        if not self.text:
            self.text = DOC.createTextNode(self.content)
            self.get_element().appendChild(self.text)

        self.text.data = self.content
        if self.rotate:
            self.setAttribute("rotate", self.rotate)

        if self.editable:
            self.setAttribute("editable", self.editable)

    def bounding_box(self, M=None):
        """ Bounding box of text
        """
        if not M:
            M = Matrix()

        m = Matrix()
        if self.rotate:
            m.rotate(self.rotate)
        M = M * m

        lines = self.content.split('\n')
        mxlen = -99999
        for line in lines:
            ln = len(line)
            if ln > mxlen:
                mxlen = ln

        if 'font-size' in self.style_dict:
            font_size = int(self.style_dict['font-size'])
        else:
            font_size = 20

        width = mxlen * font_size
        height = 1.5*len(lines)*font_size
        points = (Point(self.x, self.y), Point(self.x, self.y+height),
                  Point(self.x+width, self.y+height), Point(self.x+width, self.y+height)
                  )

        self.bb = bounding_box()
        for P in points:
            self.bb.union_point(M.transform(P))

        return self.bb


class path(BaseElement):
    """ Inserts a path
    """

    def __init__(self, pathData="", pathLength=None,
                 style_dict=None, transform_dict=None):

        super(path, self).__init__(style_dict=style_dict, transform_dict=transform_dict)
        if pathData != '' and not pathData.endswith(' '):
            pathData += ' '
        self.d = pathData
        self.pathLength = pathLength

    def __append__(self, command, params, relative=True):
        if relative is True:
            self.d += command.lower()
        else:
            self.d += command.upper()
        for param in params:
            self.d += ' %s ' % (param)

    def appendPointList(self, points, closed=False, relative=False):
        """Append the points as a part of the path

        Args:
            points ([array of points]): the points
        """
        P0 = points[0]
        self.appendMoveToPath(P0.x, P0.y, relative)
        for P in points[1:]:
            self.appendLineToPath(P.x, P.y, relative)

        if closed:
            self.appendCloseCurve()

    def appendLineToPath(self, endx, endy, relative=True):
        """line to path."""
        self.__append__('l', [endx, endy], relative)

    def appendHorizontalLineToPath(self, endx, relative=True):
        """horizontal line to path."""
        self.__append__('h', [endx], relative)

    def appendVerticalLineToPath(self, endy, relative=True):
        """vertical line to path."""
        self.__append__('v', [endy], relative)

    def appendMoveToPath(self, endx, endy, relative=True):
        """move to path."""
        self.__append__('m', [endx, endy], relative)

    def appendCloseCurve(self):
        """close curve."""
        self.d += "z"

    def appendCubicCurveToPath(self, controlstartx, controlstarty, controlendx, controlendy, endx, endy, relative=True):
        """Cubic curve to path."""
        self.__append__('c', [controlstartx, controlstarty, controlendx, controlendy, endx, endy], relative)

    def appendCubicShorthandCurveToPath(self, controlendx, controlendy, endx, endy, relative=True):
        """  x
        """
        self.__append__('s', [controlendx, controlendy, endx, endy], relative)

    def appendQuadraticCurveToPath(self, controlx, controly, endx, endy, relative=True):
        """  x
        """
        self.__append__('q', [controlx, controly, endx, endy], relative)

    def appendQuadraticShorthandCurveToPath(self, endx, endy, relative=True):
        """  x
        """
        self.__append__('t', [endx, endy], relative)

    def appendArcToPath(self, rx, ry, x, y, x_axis_rotation=0, large_arc_flag=0, sweep_flag=1, relative=True):
        """  x
        """
        param = "%f,%f %f %d %d %f,%f" % (rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y)
        self.__append__('a', [param, ], relative)

    def extra_tags(self):
        """ Set the attributes
        """
        self.setAttribute("d", self.d)
        if self.pathLength:
            self.setAttribute("pathLength", str(self.pathLength))

    def bounding_box(self, M=None):
        """
        """
        if not M:
            M = Matrix()

        if self.transform_dict:
            m = Matrix()
            m.parse(self.getXMLFromTransform())
            M = M * m

        bb = bounding_box()
        cp = None
        ret = parsePath(self.d)
        for cmd, args in ret:
            if cmd == 'M':
                cp = Point(args[0], args[1])
                bb.union_point(M*cp)
                np = len(args)-2
                for i in range(0, np, 2):
                    cp = Point(args[2*(i+1)], args[2*(i+1)+1])
                    bb.union_point(M*cp)

            elif cmd == 'L' or cmd == 'Z':
                np = len(args)
                for i in range(0, np, 2):
                    cp = Point(args[2*i], args[2*i+1])
                    bb.union_point(M*cp)

            elif cmd == 'C':
                np = len(args)
                for i in range(0, np, 6):
                    p0 = cp
                    p1 = Point(args[6*i], args[6*i+1])
                    p2 = Point(args[6*i+2], args[6*i+3])
                    p3 = Point(args[6*i+4], args[6*i+5])
                    cp = p3
                    for p in BezierCubic(p0, p1, p2, p3):
                        bb.union_point(M*p)

            elif cmd == 'Q':
                np = len(args)
                for i in range(0, np, 4):
                    p0 = cp
                    p1 = Point(args[i*4], args[i*4+1])
                    p2 = Point(args[i*4+2], args[i*4+3])
                    cp = p2
                    for p in BezierQuadratic(p0, p1, p2):
                        bb.union_point(M*p)

            elif cmd == 'A':
                np = len(args)
                for i in range(0, np, 7):

                    # Start and end points
                    p0 = cp
                    p1 = Point(args[5], args[6])
                    # start and end points are equal... we ommit the arc command
                    if p0 == p1:
                        continue

                    # set the current point
                    cp = p1

                    # Radii
                    rx = abs(args[0])
                    ry = abs(args[1])
                    if rx == 0.0 or ry == 0.0:
                        # we have a line
                        bb.union_point(M*p0)
                        bb.union_point(M*p1)
                        continue

                    # Rotation angle
                    phi = math.fmod(args[2]*math.pi/180.0, twopi)
                    if phi < 0:
                        phi = phi + twopi

                    fa = args[3]
                    fs = args[4]

                    if fa != 0:
                        fa = 1

                    if fs != 0:
                        fs = 1

                    for p in EvalArc(rx, ry, phi, fa, fs, p0, p1):
                        bb.union_point(M*p)

        self.bb = bb
        return bb


class ObjectHelper(object):
    """
        Helper class that creates commonly used objects and shapes with predefined styles and
        few but often used parameters. Used to avoid more complex coding for common tasks.
    """

    def createPath(self, strokewidth=1, stroke='black', fill='none'):
        style = {'fill': fill, 'stroke-width': strokewidth, 'stroke': stroke}
        return path(style_dict=style)

    def createCircle(self, cx, cy, r, strokewidth=1, stroke='black', fill='none'):
        """Creates a circle.

        Args:
        ----
            cx: starting x-coordinate
            cy: starting y-coordinate
            r:  radius
            strokewidth: width of the pen used to draw
            stroke: color with which to draw the outer limits
            fill: color with which to fill the element (default: no filling)

        Return:
        ------
            A circle object

        """
        style_dict = {'fill': fill, 'stroke-width': strokewidth, 'stroke': stroke}
        return circle(cx, cy, r, style_dict)

    def createEllipse(self, cx, cy, rx, ry, strokewidth=1, stroke='black', fill='none'):
        """
        Creates an ellipse
        @type  cx: string or int
        @param cx:  starting x-coordinate
        @type  cy: string or int
        @param cy:  starting y-coordinate
        @type  rx: string or int
        @param rx:  radius in x direction
        @type  ry: string or int
        @param ry:  radius in y direction
        @type  strokewidth: string or int
        @param strokewidth:  width of the pen used to draw
        @type  stroke: string (either css constants like 'black' or numerical values like '#FFFFFF')
        @param stroke:  color with which to draw the outer limits
        @type  fill: string (either css constants like 'black' or numerical values like '#FFFFFF')
        @param fill:  color with which to fill the element (default: no filling)
        @return:  an ellipse object
        """
        style_dict = {'fill': fill, 'stroke-width': strokewidth, 'stroke': stroke}
        return ellipse(cx, cy, rx, ry, style_dict)

    def createRect(self, x, y, width, height, rx=None, ry=None, strokewidth=1, stroke='black', fill='none'):
        """
        Creates a Rectangle
        @type  x: string or int
        @param x:  starting x-coordinate
        @type  y: string or int
        @param y:  starting y-coordinate
        @type  width: string or int
        @param width:  width of the rectangle
        @type  height: string or int
        @param height:  height of the rectangle
        @type  rx: string or int
        @param rx:  For rounded rectangles, the x-axis radius of the ellipse used to round off the corners of the rectangle.
        @type  ry: string or int
        @param ry:  For rounded rectangles, the y-axis radius of the ellipse used to round off the corners of the rectangle.
        @type  strokewidth: string or int
        @param strokewidth:  width of the pen used to draw
        @type  stroke: string (either css constants like 'black' or numerical values like '#FFFFFF')
        @param stroke:  color with which to draw the outer limits
        @type  fill: string (either css constants like 'black' or numerical values like '#FFFFFF')
        @param fill:  color with which to fill the element (default: no filling)
        @return:  a rect object
        """
        style_dict = {'fill': fill, 'stroke-width': strokewidth, 'stroke': stroke}
        return rect(x, y, width, height, rx, ry, style_dict)

    def createPolygon(self, points, strokewidth=1, stroke='black', fill='none'):
        """
        Creates a Polygon
        @type  points: string in the form 'x1,y1 x2,y2 x3,y3'
        @param points:  all points relevant to the polygon
        @type  strokewidth: string or int
        @param strokewidth:  width of the pen used to draw
        @type  stroke: string (either css constants like 'black' or numerical values like '#FFFFFF')
        @param stroke:  color with which to draw the outer limits
        @type  fill: string (either css constants like 'black' or numerical values like '#FFFFFF')
        @param fill:  color with which to fill the element (default: no filling)
        @return:  a polygon object
        """
        style_dict = {'fill': fill, 'stroke-width': strokewidth, 'stroke': stroke}
        return polygon(points=points, style_dict=style_dict)

    def createPolyline(self, points, strokewidth=1, stroke='black'):
        """
        Creates a Polyline
        @type  points: string in the form 'x1,y1 x2,y2 x3,y3'
        @param points:  all points relevant to the polygon
        @type  strokewidth: string or int
        @param strokewidth:  width of the pen used to draw
        @type  stroke: string (either css constants like 'black' or numerical values like '#FFFFFF')
        @param stroke:  color with which to draw the outer limits
        @return:  a polyline object
        """
        style_dict = {'fill': 'none', 'stroke-width': strokewidth, 'stroke': stroke}
        return polyline(points=points, style_dict=style_dict)

    def createLine(self, x1, y1, x2, y2, strokewidth=1, stroke="black"):
        """
        Creates a line
        @type  x1: string or int
        @param x1:  starting x-coordinate
        @type  x1: string or int
        @param y1:  starting y-coordinate
        @type  y2: string or int
        @param x2:  ending x-coordinate
        @type  y2: string or int
        @param y2:  ending y-coordinate
        @type  strokewidth: string or int
        @param strokewidth:  width of the pen used to draw
        @type  stroke: string (either css constants like 'black' or numerical values like '#FFFFFF')
        @param stroke:  color with which to draw the outer limits
        @return:  a line object
        """
        style_dict = {'stroke-width': strokewidth, 'stroke': stroke}
        return line(x1, y1, x2, y2, style_dict)


class StyleHelper(object):
    """ Helper Class to create a style_dict for those not familiar with svg attribute names. #@IndentOk
    """

    def __init__(self):
        self.style_dict = {}

    def clear(self):
        self.style_dict.clear()
    # tested below

    def setFontFamily(self, fontfamily):
        '''
        @param fontfamily:
        '''
        self.style_dict["font-family"] = fontfamily

    def setFontSize(self, fontsize):
        '''
        @param fontsize:
        '''
        self.style_dict["font-size"] = fontsize

    def setFontStyle(self, fontstyle):
        """  x
        """
        self.style_dict["font-style"] = fontstyle

    def setFontWeight(self, fontweight):
        """  x
        """
        self.style_dict["font-weight"] = fontweight

    # tested
    def setFilling(self, fill):
        """  x
        """
        self.style_dict["fill"] = fill

    def setOpacity(self, opacity):
        """ x """
        self.style_dict["opacity"] = opacity

    def setFillOpacity(self, fillopacity):
        """  x
        """
        self.style_dict["fill-opacity"] = fillopacity

    def setFillRule(self, fillrule):
        """  x
        """
        self.style_dict["fill-rule"] = fillrule

    def setStrokeWidth(self, strokewidth):
        """  x
        """
        self.style_dict["stroke-width"] = strokewidth

    def setStroke(self, stroke):
        """  x
        """
        self.style_dict["stroke"] = stroke

    # untested below
    def setStrokeDashArray(self, strokedasharray):
        """  x
        """
        self.style_dict["stroke-dasharray"] = strokedasharray

    def setStrokeDashOffset(self, strokedashoffset):
        """  x
        """
        self.style_dict["stroke-dashoffset"] = strokedashoffset

    def setStrokeLineCap(self, strikelinecap):
        """  x
        """
        self.style_dict["stroke-linecap"] = strikelinecap

    def setStrokeLineJoin(self, strokelinejoin):
        """  x
        """
        self.style_dict["stroke-linejoin"] = strokelinejoin

    def setStrokeMiterLimit(self, strokemiterlimit):
        """  x
        """
        self.style_dict["stroke-miterlimit"] = strokemiterlimit

    def setStrokeOpacity(self, strokeopacity):
        """  x
        """
        self.style_dict["stroke-opacity"] = strokeopacity

    # is used to provide a potential indirect value (currentColor) for the 'fill', 'stroke', 'stop-color' properties.

    def setCurrentColor(self, color):
        """  x
        """
        self.style_dict["color"] = color

    # Gradient properties:
    def setStopColor(self, stopcolor):
        """  x
        """
        self.style_dict["stop-color"] = stopcolor

    def setStopOpacity(self, stopopacity):
        """  x
        """
        self.style_dict["stop-opacity"] = stopopacity

    # rendering properties
    def setColorRendering(self, colorrendering):
        """  x
        """
        self.style_dict["color-rendering"] = colorrendering

    def setImageRendering(self, imagerendering):
        """  x
        """
        self.style_dict["image-rendering"] = imagerendering

    def setShapeRendering(self, shaperendering):
        """  x
        """
        self.style_dict["shape-rendering"] = shaperendering

    def setTextRendering(self, textrendering):
        """  x
        """
        self.style_dict["text-rendering"] = textrendering

    def setSolidColor(self, solidcolor):
        """  x
        """
        self.style_dict["solid-color"] = solidcolor

    def setSolidOpacity(self, solidopacity):
        """  x
        """
        self.style_dict["solid-opacity"] = solidopacity

    # Viewport properties
    def setVectorEffect(self, vectoreffect):
        """  x
        """
        self.style_dict["vector-effect"] = vectoreffect

    def setViewPortFill(self, viewportfill):
        """  x
        """
        self.style_dict["viewport-fill"] = viewportfill

    def setViewPortOpacity(self, viewportfillopacity):
        """  x
        """
        self.style_dict["viewport-fill_opacity"] = viewportfillopacity

    # Text properties
    def setDisplayAlign(self, displayalign):
        """  x
        """
        self.style_dict["display-align"] = displayalign

    def setLineIncrement(self, lineincrement):
        """  x
        """
        self.style_dict["line-increment"] = lineincrement

    def setTextAnchor(self, textanchor):
        """  x
        """
        self.style_dict["text-anchor"] = textanchor

    def setTextAlignment(self, textalign):
        self.style_dict['text-align'] = textalign

    def getStyleDict(self):
        """  x
        """
        return self.style_dict


class TransformHelper(object):
    def __init__(self, transform_dict=None):
        if transform_dict:
            self.transform_dict = [t for t in transform_dict]
        else:
            self.transform_dict = []

    def setMatrix(self, a, b, c, d, e, f):
        self.transform_dict.insert(0, 'matrix(%s %s %s %s %s %s)' % (a, b, c, d, e, f))

    def copyMatrix(self, m):
        self.transform_dict.insert(0, 'matrix(%s %s %s %s %s %s)' % tuple(m))

    def setTransform(self, angle, cx, cy):
        """ Creates a matrix combining a translation and a rotation
        """
        angle *= Units.radian
        ca = math.cos(angle)
        sa = math.sin(angle)
        self.transform_dict.insert(0, 'matrix(%s %s %s %s %s %s)' % (ca, sa, -sa, ca, cx, cy))

    def setRotation(self, angle, cx=None, cy=None):
        """ Rotation of angle around point (cx, cy)
        """
        if cx is not None and cy is not None:
            self.transform_dict.insert(0, 'rotate(%s %s %s)' % (angle, cx, cy))
        else:
            self.transform_dict.insert(0, 'rotate(%s)' % (angle))

    def setTranslation(self, x, y=0):
        self.transform_dict.insert(0, 'translate(%s %s)' % (x, y))

    def Unitscaling(self, scale):
        self.transform_dict.insert(0, 'scale(%s)' % (scale))

    def setScaling(self, x=None, y=None):
        if x is None and y is not None:
            x = y
        elif x is not None and y is None:
            y = x

        self.transform_dict.insert(0, 'scale(%s %s)' % (x, y))

    def setSkewY(self, skewY):
        self.transform_dict.insert(0, 'skewY(%s)' % (skewY))

    def setSkewX(self, skewX):
        self.transform_dict.insert(0, 'skewX(%s)' % (skewX))

    def addFlipX(self):
        self.transform_dict.insert(0, 'matrix(-1,0,0, 1,0,0)')

    def addFlipY(self):
        self.transform_dict.insert(0, 'matrix(1,0,0,-1,0,0)')

    def addFlip(self):
        self.transform_dict.insert(0, 'matrix(-1,0,0,-1,0,0)')

    def getTransformDict(self):
        return self.transform_dict


def test_svg():
    """ Tests the package
    """
    O = ObjectHelper()
    T = TransformHelper()
    group = Group("the_rect")

    rw = 20
    rh = 30
    # rect = O.createRect(0, 0, rw, rh, strokewidth=2, stroke="black", fill="red")
    # group.addElement(rect)

    # line = O.createLine(0, 0, rw, rh, strokewidth=1, stroke="black")
    # group.addElement(line)

    style = {'stroke': "black", "stroke-width": 2, "fill": "none"}
    P = path()
    P.style_dict = style
    P.appendMoveToPath(100, 350, False)
    P.appendQuadraticCurveToPath(150, -300, 300, 0, False)
    group.addElement(P)
    B = group.bounding_box()
    print("BB no rotations;", B.bb, "W:", B.width(), "H:", B.height())

    T.setRotation(45)
    group.transform_dict = T.getTransformDict()

    B = group.bounding_box()
    print("BB after rotations;", B.bb, "W:", B.width(), "H:", B.height())

    doc = SVG()
    doc.addElement(group)
    doc.adjust_to_window()
    doc.saveSVG("kkdvk.svg")


if __name__ == "__main__":
    print("Testing svg.py")
    test_svg()
    print("...done")
