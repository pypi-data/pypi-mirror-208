"""Defines the interface of a painter."""

from pysvg_cl3.Path import Path

default_unit_scale = 1000.0


def transform_units(P, scale=default_unit_scale):
    """Closure for transform and unit conversion."""
    return P.x*scale, P.y*scale


class Layout(object):
    """Objedt that handles and manages graphic objects."""

    def __init__(self, priv, parent=None):
        """Initialize de layout.

        Args:
        ----
            priv: the 'actual object'
            painter: the painter
            parent: the upper object in the hierarchy. If given, this layout
                    is added to the parent object

        """
        self.priv = priv
        self.parent = parent
        self.painter = None

    def add(self, obj):
        """Adds an object in the the graphics layout.

        Args:
        ----
            obj: the object

        """
        self.priv.add(obj)

    def add_line(self, P1, P2, attributes={}):
        """Draw a line from P1 to P2 with the given attribute.

        Args:
        ----
            P1: starting point
            P2: ending point
            attributes: the attributes of the graphic object

        """
        return None

    def add_polyline(self, points, closed=False, attributes={}):
        """Draw a polyline form the list of points.

        Args:
        ----
            points: the list of points
            closed: if True the polyline will be closed
            attributes: the attributes of the graphic object

        """
        return None

    def add_circle(self, center, radius, attributes={}):
        """Draw a circle.

        Args:
        ----
            center: the center of the circle
            radius: the radius of the circle
            attributes: the attributes of the graphic object

        """
        return None

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
        return None

    def add_path(self, path, attributes={}):
        """Add the given path.

        Args:
        ----
            path: The path to be added
            attributes: optional attributes for the path

        """
        return None

    def add_group_ref(self, name=None, point=None, attributes={}):
        """Add a group reference or link.

        Args:
        ----
            name: the name of the block
            point: position
            attributes: Possible attributes are 'xscale', 'yscale', 'rotation'...

        """
        return None

    def get_units(self):
        """Return the units used by the painter."""
        return None

    def create_layout(self, L, parent=None):
        """Create new layout.

        Child classes should implement this to provide their particular layout.

        Args:
        ----
            L (Layout): ??
            parent (Layout, optional): The parent layout. Defaults to None.

        Returns
        -------
            Layout: The layout just created.

        """
        ret = None

        if self.painter:
            ret = self.painter.create_layout(L, parent)

        return ret

    def new_group(self, name=None):
        """Create a new group.

        Args:
        ----
            name: the name of the group.

        """
        ret = None
        if self.painter:
            ret = self.painter.new_group(name)

        return ret


class Painter(object):
    """The basic interface definition."""

    def __init__(self, out_file=None, rotation=0):
        """Initializes the instance of the class.

        Args:
        ----
            out_file: the name of the output file
            rotation: A given rotation.

        """
        self.out_file = out_file

        # this is the current group (SVG) or cell (GDS)
        self.root = None
        self.current_cell = None

        # Layout
        self.layout = Layout(None)

        # We assume that we can give named layers. Since GDSII only accepts integers,
        # we provide a dictionary to map names to integers
        self.layer_names = {}
        self.last_layer = 1

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
        pass

    # TODO: make a static generator
    def write(self, precision=1.0e-9):
        """Writes the file."""
        pass

    def set_current_cell(self, cell):
        """Set the current cell to the input."""
        self.current_cell = cell

    def new_layer(self, name=None):
        """Creates a new cell.

        TODO: Not clear what this is for. It is used by the DXF painter
              This layers are similar to the GDS layers. See how to
              make them converge

        Args:
        ----
            name: the name of the cell or layer.

        """
        self.last_layer += 1
        self.layer_names[name] = self.last_layer
        return None

    def new_group(self, name=None):
        """Create a new group.

        Args:
        ----
            name: the name of the group

        """
        return None

    def create_layout(self, L, parent=None):
        """Creates a new layout.

        Child classes shoudl implement this to provide their particular layout.

        Args:
        ----
            L: A group
            parent: The parent layout. Defaults to None.

        """
        return None

    def add_group_ref(self, name=None, point=None, attributes={}):
        """Adds a group reference or link.

        Args:
        ----
            name: the name of the block
            point: position
            attributes: Possible attributes are 'xscale', 'yscale', 'rotation'...

        """
        return self.layout.add_group_ref(name, point, attributes)

    def add_line(self, P1, P2, attributes={}):
        """Draw a line from P1 to P2 with the given attributes.

        Args:
        ----
            P1 (Point): starting point
            P2 (Point): ending point
            attributes: the attributes of the graphic object.

        """
        return self.layout.add_line(P1, P2, attributes)

    def add_polyline(self, points, closed=False, attributes={}):
        """Draw a polyline form the list of points.

        Args:
        ----
            points: the list of points
            closed: if True the polyline will be closed
            attributes: the attributes of the graphic object

        """
        return self.layout.add_polyline(points, closed, attributes)

    def add_circle(self, center, radius, attributes={}):
        """Draw a circle.

        Args:
        ----
            center: the center of the circle
            radius: the radius of the circle
            attributes: the attributes of the graphic object

        """
        return self.layout.add_circle(center, radius, attributes)

    def add_arc(self, center, radius, start_angle, end_angle, attributes={}):
        """Draws an arc.

        Args:
        ----
            center: the center of the arc
            radius: the radius of the arc
            start_angle: the starting angle
            end_angle: the end angle
            attributes: the attributes of the graphic object

        """
        return self.layout.add_arc(center, radius, start_angle, end_angle, attributes)

    def add_path(self, path, attributes={}):
        """Add the given path.

        Args:
        ----
            path (Path): The path to be added
            attributes (dict, optional): Attributes for the path. Defaults to {}.

        Returns
        -------
            [type]: [description]

        """
        return self.layout.add_path(path, attributes)

    def get_units(self):
        """Return the units used by the painter."""
        return self.layout.get_units()

    def clear(self):
        """Clears Painter memory and start from scratch."""
        return None
