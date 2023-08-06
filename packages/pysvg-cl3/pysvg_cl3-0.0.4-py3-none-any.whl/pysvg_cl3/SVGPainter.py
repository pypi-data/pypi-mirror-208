#!/usr/bin/env python
""" Draws in a SVG file
"""
import svg
from pysvg_cl3.Painter import Painter, Layout
from pysvg_cl3.matrix import Point


class GDSLayout(Layout):
    def __init__(self, priv, parent=None):
        super(GDSLayout, self).__init__(priv, parent)

        self.painter = None

        if parent is not None:
            if isinstance(parent, Layout):
                parent.priv.add(gdspy.CellReference(self.priv))

            elif isinstance(parent, Painter):
                parent.layout.priv.add(gdspy.CellReference(self.priv))

            elif isinstance(parent, gdspy.Cell):
                parent.add(gdspy.CellReference(self.priv))

    def get_layer(self, layer):
        try:
            layer = int(layer)

        except ValueError:
            if isinstance(layer, str):
                layer = self.painter.layer_names.get(layer, 0)

        return layer

    def add_group_ref(self, name=None, point=None, attributes={}):
        rotation = attributes.get('rotation', None)
        mag = attributes.get('magnification', None)
        ref = gdspy.CellReference(name, point, rotation=rotation, magnification=mag)
        self.add(ref)

    def draw_polygon(self, points, attributes={}):
        layer = self.get_layer(attributes.get('layer', 0))
        poly = gdspy.Polygon(points, layer=layer)
        self.add(poly)
        return poly

    def add_polyline(self, points, closed=False, attributes={}):
        layer = self.get_layer(attributes.get('layer', 0))
        width = attributes.get('width', 1)
        fillet = attributes.get('fillet', None)
        if closed:
            return self.draw_polygon(points, attributes)

        path = gdspy.PolyPath(points, width, 1, layer=layer)

#         path = gdspy.Path(width, points[0])
#         for i, V in enumerate(points[1:]):
#             P = Point(points[i+1]) - Point(points[i])
#             length = P.mag()
#             direction = Point(1.0, 0.0).angle(P)
#             path.segment(length, direction, layer=layer)

        if fillet is not None:
            path.fillet(width)

        self.add(path)
        return path

    def add_line(self, P1, P2, attributes={}):
        self.add_polyline((P1, P2), closed=False, attributes=attributes)

    def add_circle(self, center, radius, attributes={}):
        fill = attributes.get('fill', 'none')
        layer = self.get_layer(attributes.get('layer', 0))
        width = attributes.get('width', 1)

        if fill != "none":
            circle = gdspy.Round(center, radius, layer=layer)
            self.add(circle)

        else:
            p0 = center + Point(radius, 0.0)

            def fcircle(t):
                """ function for the parametric shape """
                a = t*twopi
                p = center + radius*Point(math.cos(a), math.sin(a))
                out = p - p0
                return (out.x, out.y)

            gpath = gdspy.Path(width, p0)
            gpath.parametric(fcircle, layer=[layer])
            self.add(gpath)

        return None

    def add_arc(self, center, radius, start_angle, end_angle, attributes={}):
        fill = attributes.get('fill', 'none')
        layer = self.get_layer(attributes.get('layer', 0))
        width = attributes.get('width', 1)
        number_of_points = attributes.get("number_of_points", None)
        if number_of_points is None:
            number_of_points = 0.01

        units = GDSUnits()

        arc = gdspy.Round(center, radius+width/2.0,
                          inner_radius=radius-width/2.0,
                          initial_angle=start_angle*units.radian,
                          final_angle=end_angle*units.radian,
                          layer=layer,
                          number_of_points=number_of_points)

        self.add(arc)

    def get_units(self):
        return GDSUnits()

    def create_layout(self, L, parent=None):
        return self.painter.create_layout(L, parent)



class SVGPainter(Painter):
    def __init__(self, name, out_file, rotation=0):
        super(SVGPainter, self).__init__(out_file, rotation=0)
        self.name = str(name)
        self.root = svg.Group("MAIN")

        self.layout = SVGLayout()
        self.layout.painter = self

    def write(self, precision=1.0e-10):
        out = open(self.out_file, "wb")
        gdspy.write_gds(out,
                        unit=1.0e-6,
                        precision=precision)
        out.close()

    def new_group(self, name):
        return gdspy.Cell(name)

    def create_layout(self, L, parent=None):
        layout = GDSLayout(L, parent)
        layout.painter = self
        return layout