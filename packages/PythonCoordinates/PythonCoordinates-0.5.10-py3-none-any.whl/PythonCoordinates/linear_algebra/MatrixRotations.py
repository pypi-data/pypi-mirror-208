import numpy
from ..measurables.Measurable import InvalidUnitOfMeasureException
from ..measurables.physical_quantities import Angle


class MatrixRotations:
    """
    A collection of functions that provide the matrices for specific canonical rotations about Cartesian coordinate
    direction vectors.
    """
    @staticmethod
    def geo_to_body():
        """
        This is the matrix that converts the coordinate system from a geographic reference to the center of mass of the
        vehicle.  This amounts to a rz(numpy.pi/2).dot(rz(numpy.pi)).
        """
        return numpy.array([[0, 1, 0],
                           [1, 0, 0],
                           [0, 0, -1]])

    @staticmethod
    def rx(x):
        """
        Canonical rotation about the Cartesian X-axis

        x : Angle
            The rotation that must be executed

        returns : double, array-like
            the 3x3 matrix that represents the rotation around the x-axis
        """
        if isinstance(x, Angle):
            return numpy.array([[1, 0, 0],
                                [0, x.cos(), x.sin()],
                                [0, -x.sin(), x.cos()]])
        else:
            raise InvalidUnitOfMeasureException

    @staticmethod
    def ry(y):
        """
        Canonical rotation about the Cartesian y-axis

        y : Angle
            The rotation that must be executed

        returns : double, array-like
            the 3x3 matrix that represents the rotation around the y-axis
        """
        if isinstance(y, Angle):
            return numpy.array([[y.cos(), 0, -y.sin()],
                                [0, 1, 0],
                                [y.sin(), 0, y.cos()]])

        else:
            raise InvalidUnitOfMeasureException

    @staticmethod
    def rz(z):
        """
        Canonical rotation about the Cartesian z-axis

        z : Angle
            The rotation that must be executed

        returns : double, array-like
            the 3x3 matrix that represents the rotation around the z-axis
        """

        if isinstance(z, Angle):
            return numpy.array([[z.cos(), z.sin(), 0],
                                [-z.sin(), z.cos(), 0],
                                [0, 0, 1]])

        else:
            raise InvalidUnitOfMeasureException
