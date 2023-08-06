"""Draws in a DXF file."""
import math

import ezdxf

from pysvg_cl3.matrix import Point
from pysvg_cl3.Painter import Layout
from pysvg_cl3.Painter import Painter


class DXFUnits(object):
    """Stores conversions among units.

    Base Unit is mm=1, however, to avoid rounding errors we use um=1 and scale
    at the very end.
    """

    um = 1
    mm = 1000.0*um
    cm = 10*mm
    m = 100*cm
    inch = 2.54*cm
    degree = 57.295779513082323
    radian = 0.017453292519943295

    @staticmethod
    def scale_values(P):
        """Sacale vectors."""
        try:
            return [(v[0]/1000.0, v[1]/1000.0) for v in P]
        except TypeError:
            return (P[0]/1000.0, P[1]/1000.0)

    @staticmethod
    def scale_value(P):
        """Scale scalars."""
        return P/1000.0


class DXFObject(object):
    """An object to retain."""

    def __init__(self, *args, **kargs):
        """Initialization."""
        self.args = args
        self.kargs = kargs


class DXFLayout(Layout):
    """Represents a DXF layout."""

    def __init__(self, priv, parent=None):
        """Initialization of the object."""
        super(DXFLayout, self).__init__(priv)
        if parent is not None:
            if isinstance(parent, Layout):
                parent.priv.add_blockref(self.priv.name, Point(0, 0))
            elif isinstance(parent, Painter):
                parent.layout.priv.add_blockref(self.priv.name, Point(0, 0))

    def add_group_ref(self, name=None, point=None, attributes={}):
        """Add a group reference or link.

        Args:
        ----
            name: the name of the block
            point: position
            attributes: Possible attributes are 'xscale', 'yscale', 'rotation'...

        """
        if point is None:
            point = Point(0, 0)

        point = DXFUnits.scale_values(point)
        transform = None
        if "flipX" in attributes:
            transform = ezdxf.math.UCS(ux=(1, 0, 0), uy=(0, -1, 0))
            del attributes["flipX"]

        if "flipY" in attributes:
            transform = ezdxf.math.UCS(ux=(-1, 0, 0), uy=(0, 1, 0))
            del attributes["flipY"]

        rc = self.priv.add_blockref(name, point, dxfattribs=attributes)
        if transform:
            rc.transform(transform.matrix)

    def add_polyline(self, points, closed=False, attributes={}):
        """Draw a polyline form the list of points.

        Args:
        ----
            points: the list of points
            closed: if True the polyline will be closed
            attributes: the attributes of the graphic object

        """
        layer = attributes.get('layer', None)
        width = attributes.get('width', None)
        fill = attributes.get('fill', None)
        color = attributes.get('color', None)

        # scale
        points = DXFUnits.scale_values(points)

        dxf_attr = {}
        if layer is not None:
            dxf_attr['layer'] = str(layer)

        if color is not None:
            dxf_attr['color'] = color

        given_points = points
        if width is not None:
            newP = []
            width = DXFUnits.scale_value(width)
            for P in points:
                newP.append((P[0], P[1], width, width))

            points = newP

        if fill is not None:
            hatch = self.priv.add_hatch()

            hatch.paths.add_polyline_path(given_points, is_closed=True)
#            with hatch.edit_boundary() as boundary:
#                boundary.add_polyline_path(given_points, is_closed=1)

        else:
            poly = self.priv.add_lwpolyline(points, dxfattribs=dxf_attr)
            poly.closed = closed

    def add_line(self, P1, P2, attributes={}):
        """Draw a line from P1 to P2 with the given attribute.

        Args:
        ----
            P1: starting point
            P2: ending point
            attributes: the attributes of the graphic object

        """
        layer = attributes.get('layer', None)
        width = attributes.get('width', None)

        P1 = DXFUnits.scale_values(P1)
        P2 = DXFUnits.scale_values(P2)

        dxf_attr = {}
        if layer is not None:
            dxf_attr['layer'] = str(layer)

        if width is not None:
            width = DXFUnits.scale_value(width)
            points = ((P1[0], P1[1], width, width),
                      (P2[0], P2[1], width, width))
            self.priv.add_lwpolyline(points, dxfattribs=dxf_attr)

        else:
            self.priv.add_line(P1, P2, dxfattribs=dxf_attr)

    def add_circle(self, center, radius, attributes={}):
        """Draw a circle.

        Args:
        ----
            center: the center of the circle
            radius: the radius of the circle
            attributes: the attributes of the graphic object

        """
        fill = attributes.get('fill', None)
        if fill is not None:
            del attributes['fill']

        center = DXFUnits.scale_values(center)
        radius = DXFUnits.scale_value(radius)

        dxf_attr = {}
        layer = attributes.get('layer', 0)
        if layer is not None:
            dxf_attr['layer'] = str(layer)

        width = attributes.get('width', None)
        if width is not None:
            DXFUnits.scale_values(width)
        else:
            width = 1

        # dxf_attr['width'] = width
        if 'color' in attributes:
            dxf_attr['color'] = attributes['color']

        circle = self.priv.add_circle(center, radius, dxf_attr)
        return circle

    def add_arc(self, center, radius, start_angle, end_angle, attributes={}):
        """Draw an arc.

        Args:
        ----
            center: the center of the arc
            radius: the radius of the arc
            start_angle: the starting angle in degrees
            end_angle: the end angle in degrees
            attributes: the attributes of the graphic object

        """
        if 'number_of_points' in attributes:
            del attributes['number_of_points']

        center = DXFUnits.scale_values(center)
        radius = DXFUnits.scale_value(radius)
        self.priv.add_arc(center, radius, start_angle, end_angle, attributes)

    def get_units(self):
        """Return the units used."""
        return DXFUnits()


class DXFPainter(Painter):
    """DXF Painter."""

    def __init__(self, name, out_file, rotation=0):
        """Initialize.

        Args:
        ----
            name (str): The name
            out_file (path): The output file name.

        """
        super(DXFPainter, self).__init__(out_file, rotation)
        self.name = name

        # The dxf document
        self.dwg = ezdxf.new("AC1027")
        self.dwg.header['$MEASUREMENT'] = 1  # Metric Units
        self.dwg.header['$INSUNITS'] = 13    # microns
        self.msp = self.dwg.modelspace()

        # if rotation:
        #     angle = rotation*math.pi/180.0
        #     group = self.create_layout(self.new_group("CSYS"))
        #     self.add_group_ref("CSYS", (0,0,0), attributes={"rotation": angle})

        self.layout = DXFLayout(self.msp)

    def setup_viewport(self, lower_left, upper_right, center_point=None, width=None, height=None):
        """Sets the viewport.

        Args:
        ----
            lower_left (int): The lower left coordinate
            upper_right (int): The upper right coordinate
            center_point (Point, optional): The center point. Defaults to None.
            width (int, optional): The width. Defaults to None.
            height (int, optional): The height. Defaults to None.

        """
        viewport = self.dwg.viewports.new('*ACTIVE')
        viewport.dxf.lower_left = DXFUnits.scale_values(lower_left)
        viewport.dxf.upper_right = DXFUnits.scale_values(upper_right)
        # viewport.dxf.target_point = (0, 0, 0)  # target point defines the origin of the DCS, this is the default value
        if center_point is not None:
            # move this location (in DCS) to the center of the viewport
            viewport.dxf.center_point = DXFUnits.scale_values(center_point)

        if height is not None:
            # height of viewport in drawing units, this parameter works
            viewport.dxf.height = DXFUnits.scale_value(height)

        if width is not None:
            viewport.dxf.width = DXFUnits.scale_value(width)

        # viewport.dxf.aspect_ratio = 1.0  # aspect ratio of viewport (x/y)

    def write(self, precision=1.0e-9):
        """Wrtie the file."""
        self.dwg.saveas(self.out_file)

    def new_layer(self, name):
        """Add a new layer.

        Args:
        ----
            name (str): The name of the layer.

        """
        self.dwg.layers.new(name=name)

    def new_group(self, name):
        """We implement the groups in DXF as blocks."""
        return self.dwg.blocks.new(name=name)

    def create_layout(self, L, parent=None):
        """Create a new layout."""
        layout = DXFLayout(L, parent)
        layout.painter = self
        return layout

    def get_units(self):
        """Return the units used."""
        return DXFUnits()
