#!/usr/bin/env python
"""Define Matrix and Point."""
import math
import re
from inspect import isfunction

rad = math.pi / 180.0
deg = 1.0 / rad

min_dist = 1.0
while True:
    val = min_dist / 2.0
    if val > 0.:
        min_dist = val
    else:
        break

min_dist = 1.e-10


def is_sequence(arg):
    """Tells if the input is a sequence."""
    return (not hasattr(arg, "strip")
            and (hasattr(arg, "__getitem__")
            or hasattr(arg, "__iter__")))


class ParabolaException(Exception):
    """A Parabola exception."""

    def __init__(self, *args):
        """Calls Exception  initialization with given arguments."""
        Exception.__init__(self, *args)


class LineException(Exception):
    """Exception for Line objects."""

    def __init__(self, *args):
        """Calls Exception  initialization with given arguments."""
        Exception.__init__(self, *args)


class MatrixException(Exception):
    """Exception for Matrix objects."""

    def __init__(self, *args):
        """Calls Exception  initialization with given arguments."""
        Exception.__init__(self, *args)


class Point(object):
    """Represents a point in a 2D space."""

    def __init__(self, x=None, y=None, name=None):
        """Initialization of a Point object.

        Arguments are coordinates and optionally a name.
        It can be initialized with individual values of
        X and Y, with tuplles or arrays or with Point objects.

        """
        self.x = None
        self.y = None

        if name:
            self.name = name
        else:
            self.name = "Point"

        if x is not None:
            if isinstance(x, Point):
                self.x = x.x
                self.y = x.y
            else:
                try:
                    self.x = float(x[0])
                    self.y = float(x[1])
                except (TypeError, IndexError):
                    try:
                        self.x = float(x)
                    except ValueError:
                        self.x = None

                    try:
                        self.y = float(y)
                    except ValueError:
                        self.y = None

    def __sub__(self, other):
        """Defference between 2 Point objects."""
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        else:
            return NotImplemented

    def __add__(self, other):
        """Addtion of 2 Point objects."""
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            return NotImplemented

    def __mul__(self, other):
        """Scalar product of 2 Point objects."""
        if isinstance(other, Point):
            return self.x * other.x + self.y * other.y
        elif isinstance(other, float) or isinstance(other, int):
            return Point(self.x * other, self.y * other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        """Multiplication by float or int."""
        if isinstance(other, float) or isinstance(other, int):
            return Point(self.x * other, self.y * other)
        else:
            return NotImplemented

    def __eq__(self, other):
        """Checks for equality."""
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        else:
            return NotImplemented

    def __ne__(self, other):
        """Checks for non equality."""
        if isinstance(other, Point):
            return self.x != other.x or self.y != other.y
        else:
            return NotImplemented

    def __lt__(self, other):
        """Lees than operator.

        A point is smaller than other if its magnitude is smaller.
        """
        if isinstance(other, Point):
            return self.mag() < other.mag()
        else:
            return NotImplemented

    def __gt__(self, other):
        """Greater than operator.

        A point is greater than other if its magnitude is greater.
        """
        if isinstance(other, Point):
            return self.mag() > other.mag()
        else:
            return NotImplemented

    def __le__(self, other):
        """Lees or equal.

        Here equality refers to magnitude.
        """
        if isinstance(other, Point):
            return self.mag() <= other.mag()
        else:
            return NotImplemented

    def __ge__(self, other):
        """Greater or equal.

        Here eauqlity refers to magnitude.
        """
        if isinstance(other, Point):
            return self.mag() >= other.mag()
        else:
            return NotImplemented

    def __neg__(self):
        """Multiply by -1."""
        return Point(-1*self.x, -1*self.y)

    def round(self):
        """Return a point with elements rounded."""
        return Point(round(self.x), round(self.y))

    def as_int(self):
        """Return a tuple with ints."""
        return (int(round(self.x)), int(round(self.y)))

    def mag(self):
        """Return the magnitude."""
        return math.sqrt(self.x*self.x + self.y*self.y)

    def mag2(self):
        """Return magnitude squared."""
        return self.x*self.x + self.y*self.y

    def norm(self):
        """Return a unit vector (magnitude is 1)."""
        v = self.mag()
        return Point(self.x/v, self.y/v)

    def unit(self):
        """Returns a unit vector from this one."""
        return (1.0/self.mag())*self

    def angle(self, P):
        """Return angle w.r.t. given poiint (angle)."""
        return math.atan2(P.cross(self), P.dot(self))

    def cw(self):
        """Return a point like this rotated +90 degrees."""
        return Point(-1*self.y, self.x)

    def ccw(self):
        """Return a point like this rotated -90 degress."""
        return Point(self.y, -1*self.x)

    def dot(self, a):
        """Dot product with given point (vector)."""
        return self.x * a.x + self.y * a.y

    def cross(self, b):
        """Cross product with given point (vector)."""
        return self.dot(b.cw())

    def phi(self):
        """Return angle w.r.t. X axis."""
        return math.atan2(self.y, self.x)

    def valid(self):
        """Tells if the point has valid values."""
        if self.x is None or self.y is None:
            return False
        else:
            return True

    def distance(self, other):
        """Distance to a Point or Line."""
        if isinstance(other, Point):
            dd = (self-other).mag()
            return dd
        elif isinstance(other, Line):
            ff = math.sqrt(other.A()**2 + other.B()**2)
            dd = other.A()*self[0] + other.B()*self[1] + other.C()
            return dd/ff
        else:
            raise ValueError

    def __getitem__(self, key):
        """Implement the getitem interface."""
        if key < 0 or key > 1:
            raise IndexError
        elif key == 0:
            return self.x
        else:
            return self.y

    def __setitem__(self, key, val):
        """Implement the setitem interface."""
        if key < 0 or key > 2:
            raise IndexError
        elif key == 0:
            self.x = val
        else:
            self.y = val

    def __len__(self):
        """Return length."""
        return 2

    def __str__(self):
        """String representation."""
        return "%f,%f" % (self.x, self.y)

    def __repr__(self):
        """String representation."""
        return "Point(%f, %f)" % (self.x, self.y)


def dot(a, b):
    """Dot product."""
    return a.x*b.x + a.y*b.y


def cross(a, b):
    """Cross product."""
    return dot(a, b.cw())


class Parabola(list):
    """Class representing a parabola."""

    def __init__(self, A=None):
        """Initialization.

        Initialized with a list (a, b, c) so that the parabola is: a*x^2+b*x+c

        """
        if A is None:
            A = (1.0, 0.0, 0.0)

        super(Parabola, self).__init__(A)
        if self[0] == 0:
            raise ParabolaException("This is a line....")

    def vertex(self):
        """Return. the minimum of the parabola."""
        xmin = -self[1]/(2.0*self[0])
        return Point(xmin, self.eval(xmin))

    def eval(self, x):
        """Evaluates at X."""
        return x*(self[0]*x + self[1]) + self[2]

    def cros_line(self, L):
        """Find the crossing points with a line.

        They are ordered w.r.t distance to vertex, closest first.
        """
        a = self[0]
        b = self[1] - L.m
        c = self[2] - L.b

        det = b*b - 4*a*c
        if det < 0.0:
            return ()

        det = math.sqrt(det)
        ff = 1.0/(2.0*a)
        x1 = (-b + det)*ff
        x2 = (-b - det)*ff
        P1 = Point(x1, L.eval(x1))
        P2 = Point(x2, L.eval(x2))
        V = self.vertex()
        if abs(P1.x - V.x) < abs(P2.x - V.x):
            return (P1, P2)
        else:
            return (P2, P1)


class Line(object):
    """Represents a line.

    We store the slope (m) and  the intercept (b).

    """

    def __init__(self, m=None, n=None):
        """Initialization.

        We create the line in various forms:
            1) m and n are floats: the slope intercept form
            2) m is a float and n is a Point: line with that slope passing
               through the given point
            3) m and n are points: line passing through 2 points
               V = n - m
               O = m
        """
        self.P1 = None
        self.P2 = None
        if isinstance(m, Point):
            self.P1 = m
            if isinstance(n, Point):
                self.P2 = n
                delta_x = (n.x - m.x)
                delta_y = (n.y - m.y)
                if delta_x == 0.0:  # vertical line
                    self.O = Point(n.x, n.y)
                    self.V = Point(0.0, 1.0)
                    self.m = None
                    self.b = None
                    return

                self.m = delta_y/delta_x
                self.b = - self.m * n.x + n.y
                self.O = Point(m.x, m.y)
                self.delta = Point(delta_x, delta_y)
                self.V = self.delta.norm()

            else:  # n has to be a number
                self.m = n
                self.b = - self.m * m.x + m.y
                alpha = math.atan(n)
                self.O = m
                self.V = Point(math.cos(alpha), math.sin(alpha))
                self.delta = self.V

        else:  # m has to be a number
            if isinstance(n, Point):
                self.m = m
                self.b = - self.m * n.x + n.y
                alpha = math.atan(m)
                self.O = n
                self.V = Point(math.cos(alpha), math.sin(alpha))
                self.delta = self.V
            else:
                self.m = m
                self.b = n
                alpha = math.atan(m)
                self.O = Point(0., n)
                self.V = Point(math.cos(alpha), math.sin(alpha))
                self.delta = self.V

    def __str__(self):
        """String representation."""
        return "Line(%f, %f)" % (self.m, self.b)

    def A(self):
        """Return A from Ax + By +C =0."""
        return self.m

    def B(self):
        """Return B from Ax + By +C =0."""
        return -1

    def C(self):
        """Return C from Ax + By +C =0."""
        return self.b

    def eval(self, x):
        """Evaluates the line at X."""
        if self.m:
            return self.m * x + self.b

        else:
            return self.b

    def __call__(self, x):
        """Evaluates the line in parametric form.

        x=0 gives P0, and x=1 gives P1
        """
        out = self.O + x*self.delta
        return out

    def line_perpendicular_at_point(self, P):
        """Return the line perpendicular passing by point."""
        L = Line(-1.0/self.m, P)
        return L

    def line_parallel_at_distance(self, d):
        """Return the line parallel to this one which is at a distance d."""
        if not self.m:
            P = Point(self.O.x + d, 0)
            V = Point(self.O.x + d, 1)
            return Line(P, V)

        else:
            new_m = self.m
            new_b = self.b + d * math.sqrt(1 + self.m*self.m)
            return Line(new_m, new_b)

    def line_at_angle(self, angle, center=None):
        """Return a line which forms an angle w.r.t center.

        If center is not givem the line origin will be used.
        """
        if not center:
            center = self.O
        else:
            res = center.y - (self.m * center.x + self.b)
            if abs(res) > min_dist:
                raise LineException("Line.line_at_angle: center does not belong to line")

        ca = math.cos(angle)
        sa = math.sin(angle)
        bx = self.V.x * ca - self.V.y * sa
        by2 = 1.0-bx*bx
        if by2 < 0:
            bx = self.V.x * ca + self.V.y * sa
            by2 = 1.0 - bx*bx

        by = math.sqrt(by2)
        b = Point(bx, by)
        b1 = center + b
        return Line(center, b1)

    def line_angle(self, P=None):
        """Return the angle with a given direction."""
        if not P:
            P = Point(1.0, 0.0)

        return P.angle(self.V)

    def angle(self, other):
        """Angle between 2 lines."""
        angle = math.atan((other.m-self.m)/(1+self.m*other.m))
        return angle

    def cross_point(self, other):
        """Intersection point with other Line."""
        if self.m is None:
            # vertical line
            if other.m is None:
                raise LineException("Parallel Lines")
            else:
                x = self.O.x
                y = other.m*x + other.b
                return Point(x, y)

        if other.m is None:
            return other.cross_point(self)

        D = other.m - self.m
        if D == 0.:
            raise LineException("Parallel Lines")

        x = (self.b - other.b)/D
        y = (-self.m*other.b + other.m*self.b)/D

        return Point(x, y)

    def is_parallel(self, other):
        """Check if this line is parallel to other."""
        return self.m == other.m

    def is_perpendicular(self, other):
        """Check if this line is perperdicular to other."""
        return self.m*other.m == -1.0

    def cross_circle(self, C, R, tmin, tmax):
        """Computes the crossing point with a circle.

        C is the center of the circle
        R is the radius
        tmin, tmax : angles limiting the crossing point or
                        tmin = function to accept a point
                        tmax ignored
        """
        a = self.m
        b = self.b
        c = C.x
        d = C.y
        func = None

        if isfunction(tmin):
            func = tmin

        else:
            if tmin < 0:
                tmin += 2*math.pi

            if tmax < 0:
                tmax += 2*math.pi

            if tmin > tmax:
                tmp = tmax
                tmax = tmin
                tmin = tmp

        xx = a*a+1.0
        det = xx*R*R - d*d + 2.0*d*(a*c+b) - a*a*c*c - 2.0*a*b*c-b*b
        if det < 0:
            return None

        det = math.sqrt(det)
        yy = a*(d-b)+c
        x1 = (det-yy)/xx
        x2 = (det+yy)/xx

        p1 = Point(x1, a*x1+b)
        p2 = Point(x2, a*x2+b)

        if func:
            if func(p1, R, C):
                return p1
            elif func(p2, R, C):
                return p2
            else:
                return None

        else:
            V = (p1-C)
            dd = V.phi()
            if dd < 0.0:
                dd += 2*math.pi

            if tmin < dd and dd < tmax:
                return p1

            V = (p2-C)
            dd = V.phi()
            if dd < 0.0:
                dd += 2*math.pi

            if tmin < dd and dd < tmax:
                return p2

            return None


def matrix_multiply(a, b):
    """Multiply 2 transformation matrices: a*b."""
    return [a[0]*b[0]+a[2]*b[1], a[1]*b[0]+a[3]*b[1],
            a[0]*b[2]+a[2]*b[3], a[1]*b[2]+a[3]*b[3],
            a[0]*b[4]+a[2]*b[5]+a[4], a[1]*b[4]+a[3]*b[5]+a[5]
            ]


class Matrix(list):
    """A matrix to perform 2D transformations.

    All transformations can be represented as 3x3 transformation
    matrices of the following form:
        | a c e |
        | b d f |
        | 0 0 1 |

    Since only six values are used in the above 3x3 matrix,
    a transformation matrix is also expressed as a vector:

    [a b c d e f].

    Transformations map coordinates and lengths from a new coordinate system
    into a previous coordinate system:

      | x_prev |    | a c e | | x_new |
      | y_prev | =  | b d f | | y_new |
      | 1      |    | 0 0 1 | | 1     |


    3-by-3 transformation matrix.

    After n operations (tranlation, rotation, etc.) on the matrix:
        m.oper_1()
        m.oper_2()
        .
        .
        m.oper_n()

    The equivalent matrix is:
        M = oper_n x .... x oper_1

    Note that the following expresions are aquivalent:

        M.oper_1()
        M.oper_2()  <=>  M.oper_1().oper_2().oper_3()
        M.oper_3()

    """

    R = re.compile(r"""(?P<T>\s*              # the transform construct
                          (?P<O>[a-zA-Z]+)\s* # the operation
                          \(                  # open par
                          \s*(?P<A>[^)]*)\s*  # arguments
                          \)                  # closing par
                          \s*){1}""", re.VERBOSE)
    A = re.compile(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')

    def __init__(self, A=None):
        """Initialization.

        Can be through an array or a string that will be parsed.
        The string follows SVG rules.
        """
        to_parse = None
        if A is None:
            A = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

        self.oper = []
        if isinstance(A, str):
            to_parse = A

        else:
            if not is_sequence(A):
                raise MatrixException("Invalid initializer: %s" % A)

            if len(A) < 6:
                # It can still be a valid one
                is_bad = True
                if len(A) == 2:
                    if len(A[0]) == 3 and len(A[1]) == 3:
                        _A = [A[0][0], A[1][0], A[0][1], A[1][1], A[0][2], A[1][2]]
                        A = _A
                        is_bad = False

                if is_bad:
                    raise MatrixException("Matrix: Too short a sequence for initialization")

            super(Matrix, self).__init__(A)

        if to_parse:
            super(Matrix, self).__init__([1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
            self.parse(A)

        else:
            if hasattr(A, "oper"):
                self.oper = [x for x in A.oper]

        self.name = "matrix"

    def from_array(self, M):
        """Copy the values of an array."""
        for i in range(0, 6):
            self[i] = M[i]

    def __str__(self):
        """String representation."""
        ss = [s+' ' for s in self.oper]
        if len(ss) > 0:
            ss.append(' = ')

        ss.append("Matrix(%.8f, %.8f, %.8f, %.8f, %.8f, %.8f)" % tuple(self))
        return ''.join(ss)

    def get_transform(self):
        """Returns the transform to be passed to SVG."""
        str = "matrix(%f %f %f %f %f %f)" % tuple(self)
        return str

    def multiply(self, other):
        """Implements some kind of unary multiplycation."""
        rc = matrix_multiply(self, other)
        self.from_array(rc)

    def __mul__(self, other):
        """Matrix multiplications."""
        if isinstance(other, Matrix):
            rc = Matrix(matrix_multiply(self, other))
            for t in self.oper:
                rc.oper.append(t)
            for t in other.oper:
                rc.oper.append(t)

            return rc

        elif isinstance(other, list) or isinstance(other, tuple):
            rc = Matrix(matrix_multiply(self, other))
            return rc

        elif isinstance(other, float) or isinstance(other, int):
            rc = [x*other for x in self]
            m = Matrix(rc)
            for t in self.oper:
                m.oper.append(t)
            m.oper.append('factor(%f)' % other)
            return m

        elif isinstance(other, Point):
            rc = self.transform(other)
            return rc

        else:
            return NotImplemented

    def __parse_matrix(self, args):
        """Parse the matrix transform."""
        if len(args) != 6:
            print("Invalid matrix:", args)
        else:
            self.multiply(args)

    def __parse_trans(self, args):
        """Parse the translate transform."""
        if len(args) > 1:
            b = [1., 0., 0., 1., args[0], args[1]]
        else:
            b = [1., 0., 0., 1., args[0], 0.0]

        self.multiply(b)

    def __parse_scale(self, args):
        """Parse the scale transform."""
        if len(args) > 0:
            fx = args[0]
            try:
                fy = args[1]
            except IndexError:
                fy = fx

            self.multiply([fx, 0.0, 0.0, fy, 0.0, 0.0])

    def __parse_rotate(self, args):
        """Parse the rotate transform."""
        a = args[0]*math.pi/180.0
        ca = math.cos(a)
        sa = math.sin(a)
        if len(args) == 1:
            self.multiply([ca, sa, -sa, ca, 0.0, 0.0])

        else:
            if len(args) < 3:
                args.append(0.)

            m1 = [1.0, 0.0, 0.0, 1.0, args[1], args[2]]
            m2 = [ca, sa, -sa, ca, 0.0, 0.0]
            m3 = [1.0, 0.0, 0.0, 1.0, -args[1], -args[2]]
            tr = matrix_multiply(m1, m2)
            tr = matrix_multiply(tr, m3)
            self.multiply(tr)

    def __parse_skewx(self, args):
        """Parse the skewx transform."""
        a = args[0]*math.pi/180.0
        b = [1.0, 0.0, math.tan(a), 1.0, 0.0, 0.0]
        self.multiply(b)

    def __parse_skewy(self, args):
        """Parse the skewy transform."""
        a = args[0]*math.pi/180.0
        b = [1.0, math.tan(a), 0.0, 1.0, 0.0, 0.0]
        self.multiply(b)

    def parse(self, transform):
        """Parses transform.

        The syntax of the transform is that of SVG.
        """
        if not transform or len(transform) == 0:
            return

        TS = {"matrix": self.__parse_matrix,
              "translate": self.__parse_trans,
              "scale": self.__parse_scale,
              "rotate": self.__parse_rotate,
              "skewX": self.__parse_skewx,
              "skewY": self.__parse_skewy}

        for m in Matrix.R.finditer(transform):
            oper = m.group('O')
            if oper in TS:
                args = [float(v.group(0))
                        for v in self.A.finditer(m.group('A'))]
                TS[oper](args)

    def identity(self):
        """Resets the matrix to identity."""
        self.from_array([1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
        self.oper = []

    def rotation(self):
        """Return the rotation part of the transform."""
        A = [self[i] for i in range(0, 4)]
        A.append(0.0)
        A.append(0.0)
        return Matrix(A)

    def transform(self, point):
        """Transforms one point.

        The point is given as a sequence of 2 coordinates [x, y]
        """
        if not is_sequence(point):
            raise ValueError

        result = [self[0]*point[0] + self[2]*point[1] + self[4],
                  self[1]*point[0] + self[3]*point[1] + self[5]
                  ]
        if isinstance(point, Point):
            return Point(result[0], result[1])
        else:
            return result

    def translate(self, tx, ty=None):
        """Make a translation.

        A translation is equivalent to
            | 1 0 tx |
            | 0 1 ty | or [ 1 0 0 1 tx ty ]
            | 0 0 1  |
        """
        if isinstance(tx, Point):
            P = tx
            tx = P.x
            ty = P.y
        else:
            try:
                P = tx
                tx = P[0]
                ty = P[1]
            except (TypeError, IndexError):
                pass

        self.oper.insert(0, "T(%f, %f)" % (tx, ty))
        m = matrix_multiply(self, [1.0, 0.0, 0.0, 1.0, tx, ty])
        self.from_array(m)
        return self

    def scale(self, sx, sy=None):
        """Scaling.

        It is eqivalent to
            | sx  0  0 |
            | 0   sy 0 | or [ sx 0 0 sy 0 0 ]
            | 0   0  1 |
        """
        if not sy:
            sy = sx

        self.oper.insert(0, "Scale(%f, %f)" % (sx, sy))
        m = matrix_multiply([sx, 0.0, 0.0, sy, 0.0, 0.0], self)
        self.from_array(m)
        return self

    def skew_x(self, angle):
        """A skew transformation around the X axis.

        Equivalent to
            | 1  tan(angle)  0 |
            | 0  1           0 |
            | 0  0           1 |
        """
        self.oper.insert(0, "SkX(%f)" % angle)
        m = matrix_multiply([1.0, 0.0, math.tan(angle), 1.0, 0.0, 0.0], self)
        self.from_array(m)
        return self

    def skew_y(self, angle):
        """A skew transformation around the Y axis.

        Equivalent to
            | 1           0  0 |
            | tan(angle)  1  0 |
            | 0           0  1 |
        """
        self.oper.insert(0, "SkY(%f)" % angle)
        m = matrix_multiply([1.0, math.tan(angle), 0.0, 1.0, 0.0, 0.0], self)
        self.from_array(m)
        return self

    def rotate(self, angle):
        """A rotation around the origin.

        It is equivalent to
            | cos(a) -sin(a) 0 |
            | sin(a)  cos(a) 0 |
            | 0       0      1 |
        """
        self.oper.insert(0, "R(%f)" % angle)
        ca = math.cos(angle)
        sa = math.sin(angle)
        self.multiply([ca, sa, -sa, ca, 0.0, 0.0])
        return self

    def rotate_around_point(self, angle, cx, cy=None):
        """A rotation around a point.

        It is equivalent to:
            translate(cx, cy) rotate(angle) translate(-cx, -cy)
        """
        if isinstance(cx, Point):
            P = cx
            cx = P.x
            cy = P.y

        self.translate(-cx, -cy).rotate(angle).translate(cx, cy)
        return self

    def flipX(self):
        """Flips X coordinate."""
        self.multiply([-1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
        return self

    def flipY(self):
        """Flips X coordinate."""
        self.multiply([1.0, 0.0, 0.0, -1.0, 0.0, 0.0])
        return self

    def inverse(self):
        """Return the inverse of the tranwformation."""
        det = self[0]*self[3]-self[1]*self[2]
        A = [x/det for x in (self[3], -self[1], -self[2], self[0])]
        A.append(-A[0]*self[4]-A[2]*self[5])
        A.append(-A[1]*self[4]-A[3]*self[5])
        return Matrix(A)


def test():
    """Make a few tests."""
    #
    # Testing points and their operations
    #
    p = Point(1.0, 2.0)
    q = Point(-1.0, 2.0)
    r = (p*q)*p + 5*q
    print(r.norm())

    #
    # Testing lines
    #
    l = Line(Point(1.0, 1.0), Point(2.0, 3.0))
    print("Creating line at 30 deg. w.r.t.", l)
    la = l.line_at_angle(30.0*rad)
    print("...new line:", la)
    print("...crossing point:", l.cross_point(la), "/ should be", l.O)
    print("...angle:", l.angle(la)*deg, " deg")

    print("Creating line at -30 deg. w.r.t.", l)
    la = l.line_at_angle(-30.0*rad)
    print("...new line:", la)
    print("...crossing point:", l.cross_point(la), "/ should be", l.O)
    print("...angle:", l.angle(la)*deg, " deg")

    print("\nTesting Matrix")
    m = Matrix()
    print(m)

    print("Translate")
    m.translate(2.0, 1.0)
    print(m)

    print("rotate 30 around (2,2)")
    m = Matrix()
    print(m)
    m.rotate_around_point(30.0*rad, 2.0, 2.0)
    print(m)
    print("(0,2) -> ", m.transform(Point(0.0, 2.0)))
    print("(0,0) -> ", m.transform(Point(0.0, 0.0)))
    print("(2,2) -> ", m.transform(Point(2.0, 2.0)))

    print("matrix inversion.")
    mi = m.inverse()
    idm = m*mi
    print("...inverse", mi)
    print("...M * M^-1 =", idm)


if __name__ == "__main__":
    test()
