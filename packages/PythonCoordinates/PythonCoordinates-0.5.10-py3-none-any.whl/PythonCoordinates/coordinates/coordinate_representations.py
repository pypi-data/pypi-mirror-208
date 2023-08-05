import numpy as np
from ..measurables.physical_quantities import Length, Angle, Speed
from ..measurables.Measurable import InvalidUnitOfMeasureException
from ..linear_algebra.MatrixRotations import MatrixRotations


class CartesianCoordinate:
    def __init__(self, a=None, b=None, c=None):
        """
        This builds a Cartesian coordinate in multiple ways.

        1) You may specify each of the Cartesian coordinates as lengths (i.e. a, b, and c are Length objects)
        2) You may specify a CartesianCoordinate object as a, with b and c being None objects
        3) You may specify a and b as CartesianCoordinates, and c as none - in which case this class represents the
        difference between a and b (i.e. self = a - b)
        4) You may specify a, b, and c as integer/floating point values and the system will assume that these are
        representative of meter lengths and create new objects within the class to represent the data in this manner.
        :param a: CartesianCoordinate, Length, float or int
            Corresponding to the X-direction
        :param b: CartesianCoordinate, Length, float or int
            Corresponding to the Y-direction
        :param c: Length, float, int, or None
            Corresponding to the Z-direction
        """
        if a is None and b is None and c is None:
            self._x = Length()
            self._y = Length()
            self._z = Length()
        elif isinstance(a, CartesianCoordinate) and b is None and c is None:
            self._x = a.x
            self._y = a.y
            self._z = a.z
        elif isinstance(a, CartesianCoordinate) and isinstance(b, CartesianCoordinate) and c is None:
            self._x = b.x - a.x
            self._y = b.y - a.y
            self._z = b.z - a.z
        elif isinstance(a, Length) and isinstance(b, Length) and isinstance(c, Length):
            # print('old: {}, {}, {}'.format())
            self._x = a
            self._y = b
            self._z = c
        elif (isinstance(a, float) or isinstance(a, int)) and \
                (isinstance(b, float) or isinstance(b, int)) and \
                (isinstance(c, float) or isinstance(c, int)):
            self._x = Length(a)
            self._y = Length(b)
            self._z = Length(c)
        else:
            print('parameters are invalid!')
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            raise InvalidUnitOfMeasureException

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, v):
        if isinstance(v, Length):
            self._x = v

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, v):
        if isinstance(v, Length):
            self._y = v

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, v):
        if isinstance(v, Length):
            self._z = v

    @property
    def array(self):
        return np.array([self.x.meters, self.y.meters, self.z.meters])

    @property
    def length(self):
        return Length(np.linalg.norm(np.array([self.x.meters, self.y.meters, self.z.meters])), Length.Units.Meters)

    def to_spherical(self):
        return SphericalCoordinate(self)

    def to_cylindrical(self):

        return CylindricalCoordinate(self)

    def to_body_reference(self):
        matrix = MatrixRotations.geo_to_body().dot(self.array)
        return CartesianCoordinate(Length(matrix[0]), Length(matrix[1]), Length(matrix[2]))

    def to_geo_reference(self):
        return self.to_body_reference()

    def orient_vector(self, yaw, pitch, roll):
        """
        This function will take the three angles and rotate the internal representation of the CartesianCoordinate in
        the appropriate manner using the specific rotation matrices.
        :param yaw: Angle
            the angle that we rotate about the Z-axis
        :param pitch: Angle
            the angle that we rotate about the Y-axis
        :param roll: Angle
            the angle that we rotate about the X-axis
        """
        if isinstance(yaw, Angle) and isinstance(pitch, Angle) and isinstance(roll, Angle):
            v = MatrixRotations.rz(yaw).dot(self.array)
            v = MatrixRotations.ry(pitch).dot(v)
            v = MatrixRotations.rx(roll).dot(v)

            self.x = Length(v[0])
            self.y = Length(v[1])
            self.z = Length(v[2])
        else:
            raise InvalidUnitOfMeasureException("The function expects Angle objects for arguments.")

    def to_string(self):
        return '[{}, {}, {}]'.format(self.x.meters, self.y.meters, self.z.meters)

    def __sub__(self, other):
        if isinstance(other, CartesianCoordinate):
            x = (self.x - other.x)
            y = (self.y - other.y)
            z = (self.z - other.z)
            out = CartesianCoordinate(x, y, z)
            return out
        else:
            print('no')

    def __add__(self, other):
        if isinstance(other, CartesianCoordinate):
            return CartesianCoordinate((self.x + other.x), (self.y + other.y), (self.z + other.z))

    def dot_product(self, other):
        if isinstance(other, CartesianCoordinate):
            output = np.matrix.dot(self.array, other.array)
            return output

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            x = (self.x / other)
            y = (self.y / other)
            z = (self.z / other)
            return CartesianCoordinate(x, y, z)

    def nominal_wind_speed(self, receiver_location, velocity: Speed, direction: Angle):
        """
        This function attempts to approximate the portion of the wind that is along a particular direction
        :param receiver_location: the location of the receiver
        :param velocity: the magnitude of the wind
        :param direction: the direction of the wind
        :return: the partial speed along the direction pointing from the source to the receiver
        """

        p = receiver_location - self
        u = SphericalCoordinate(r=Length(1), polar=Angle(90),
                                azimuthal=direction).to_cartesian().to_body_reference()
        norm = p.length.meters
        a = p / norm
        scale = a.dot_product(u)
        return Speed(scale * velocity.knots, Speed.Units.Knots)


class CylindricalCoordinate:
    def __init__(self, cc=None, rho=None, phi=None, height=None):
        from ..measurables.physical_quantities import Length, Angle, Speed

        if cc is None:
            if rho is not None:
                if isinstance(rho, Length):
                    self._rho = rho
            else:
                self._rho = Length()
            if phi is not None:
                if isinstance(phi, Angle):
                    self._phi = phi
            else:
                self._phi = Angle()
            if height is not None:
                if isinstance(height, Length):
                    self._height = height
            else:
                self._height = Length()
        else:
            if isinstance(cc, CartesianCoordinate):
                self._rho = Length(
                    np.sqrt(cc.x.meters * cc.x.meters +
                            cc.y.meters * cc.y.meters), Length.Units.Meters)
                self._height = cc.z
                self._phi = Angle.atan2(cc.y.meters, cc.x.meters)
            else:
                raise InvalidUnitOfMeasureException('c parameter is not of type CartesianCoordinate')

    def to_cartesian(self):
        return CartesianCoordinate(a=(self.rho * self.phi.cos()),
                                   b=(self.rho * self.phi.sin()),
                                   c=self.height)

    def to_spherical(self):
        return SphericalCoordinate(self.to_cartesian())

    @property
    def rho(self):
        return self._rho

    @property
    def height(self):
        return self._height

    @property
    def phi(self):
        return self._phi


class SphericalCoordinate:
    def __init__(self, r=None, polar=None, azimuthal=None):
        import sys

        if r is not None and polar is not None and azimuthal is not None:
            if isinstance(r, Length):
                self.r = r
            else:
                self.r = Length()
            if isinstance(azimuthal, Angle):
                self.azimuthal = azimuthal
            else:
                self.azimuthal = Angle()
            if isinstance(polar, Angle):
                self.polar = polar
            else:
                self.polar = Angle()
        elif r is not None and polar is None and azimuthal is None:
            if isinstance(r, CartesianCoordinate):
                self.r = r.length
                self.azimuthal = Angle.atan2(r.y, r.x)
                self.polar = Angle.acos(r.z / (self.r + sys.float_info.epsilon))
            elif isinstance(r, SphericalCoordinate):
                self.r = r.r
                self.polar = r.polar
                self.azimuthal = r.azimuthal
            else:
                print('c parameter is not of type CartesianCoordinate or SphericalCoordinate')
                raise InvalidUnitOfMeasureException
        else:
            self.r = Length()
            self.azimuthal = Angle()
            self.polar = Angle()

    @property
    def length(self):
        return self.r

    def to_cartesian(self):
        x = self.r * self.azimuthal.cos() * self.polar.sin()
        y = self.r * self.azimuthal.sin() * self.polar.sin()
        z = self.r * self.polar.cos()
        return CartesianCoordinate(a=x, b=y, c=z)

    def to_string(self, use_radius=False, use_azimuth=True, use_polar=True):
        radius = '{:.2f} m'.format(self.r.meters)
        az = 'AZ: {:.2f}°'.format(self.azimuthal.degrees)
        el = 'EL: {:.2f}°'.format(self.polar.degrees)
        output = ''
        if use_radius:
            output += radius
        if use_azimuth:
            output += az
        if use_polar:
            output += el
        return output

