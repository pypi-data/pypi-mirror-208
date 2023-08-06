from matrix import Point, Line


class Path(object):
    """ This class defines a collection of subpaths that define a path.
        Each subpath is a collection of points. Subpaths are started by the
        move_to method.

        TODO: impplement curved components o a path
    """

    def __init__(self):
        self.points = []
        self.current_point = Point(0, 0)

    def add_point(self, P, relative=False):
        """ Adds a point to the current subpath
        """
        subpath = self.points[-1]
        if relative:
            P = P + self.current_point

        subpath.append(P)
        self.current_point = P

    def line_to(self, x, y, relative=False):
        """ Adds a line from current point to (x,y)
            If this is the first point given, we assume current
            is (0,0)
        """
        if len(self.points) == 0:
            self.points.append([self.current_point])

        self.add_point(Point(x, y), relative)

    def horizontal_line_to(self, x, relative=False):
        """ Horizontal line
        """
        self.line_to(x, 0, relative)

    def vertical_line_to(self, y, relative=False):
        """ vertical line
        """
        self.line_to(0, y, relative)

    def move_to(self, x, y, relative=False):
        """ Starts a new subpath
        """
        P = Point(x, y)
        self.points.append([])
        self.add_point(P, relative)

    def offset(self, value):
        """ value is positive when moving away from CoG and negative otherwise
        """
        path_list = []
        for path in self.points:
            if len(path) == 2:
                L = Line(path[0], path[1])
                V = Point(L.V.y, -L.V.x)
                path_list.append([path[0]+value*V, path[1]+value*V])
            elif len(path) > 2:
                # We assume here that the points are no aligned...
                # TODO: check the above
                #
                # Compute center of gravity
                CoG = path[0]
                for P in path[1:]:
                    CoG += P

                CoG *= 1.0/float(len(path))

                def find_direction(P1, P2, fact):
                    """ Find the direction pointing away from the CoG,
                        perpendicular to the line formed by P1 and P2
                        Returns the direction and the line parallel
                    """
                    L = Line(P1, P2)
                    # Pm points outwards away from CoG
                    M = 0.5*(P1+P2)
                    Pm = M - CoG

                    V = L.V.cw()
                    D = V.dot(Pm)
                    if D < 0:
                        V = -V

                    A = M + fact*V
                    B = A + L.V
                    L0 = Line(A, B)
                    return L0, V

                # First point is just the point displlaced, the rest
                # are obtained from the intersection of the lines
                lst = []
                lines = []
                L0, V = find_direction(path[0], path[1], value)
                lst.append(path[0]+value*V)
                lines.append(L0)
                P0 = path[1]
                for P in path[2:]:
                    L, V = find_direction(P0, P, value)
                    lst.append(L0.cross_point(L))
                    lines.append(L)
                    P0 = P
                    L0 = L

                # We need to handle here the last segment
                if path[0] == path[-1]:
                    L, V = find_direction(path[-2], path[0], value)
                    P = L.cross_point(lines[0])
                    lst.append(P)
                    lst[0] = P
                    lines.append(L)

                    new_list = [P]
                    for Q in lst[1:]:
                        new_list.append(Q)

                    # lst = new_list

                path_list.append(lst)

        path = Path()
        path.points = path_list
        path.current_point = path_list[-1][-1]
        return path


if __name__ == "__main__":
    p = Path()
    p.move_to(1, 1)
    p.line_to(1, 1, True)
    p.line_to(0, 1, True)
    p.line_to(-1, 0, True)

    p.move_to(5, 5)
    p.line_to(1, 1, True)
    p.line_to(0, 1, True)
    p.line_to(-1, 0, True)

    for sp in p.points:
        print(sp)

    D = 25
    rect = Path()
    rect.move_to(-D/2, D/2)
    rect.horizontal_line_to(D, True)
    rect.vertical_line_to(D, True)
    rect.horizontal_line_to(-D, True)
    rect.vertical_line_to(-D, True)

    for sp in rect.points:
        print(sp)
