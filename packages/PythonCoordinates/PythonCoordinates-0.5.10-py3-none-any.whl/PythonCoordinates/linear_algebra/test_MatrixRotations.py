from PythonCoordinates.linear_algebra.MatrixRotations import MatrixRotations
from PythonCoordinates.measurables.physical_quantities import Angle
from unittest import TestCase
import numpy as np


class TestMatrixRotations(TestCase):
    def test_geo_to_body(self):

        m = MatrixRotations.geo_to_body()
        self.assertEqual(3, m.shape[0])
        self.assertEqual(3, m.shape[1])

        v = np.array([1, 2, 3])

        geo = MatrixRotations.geo_to_body().dot(v)

        self.assertAlmostEqual(2, geo[0])
        self.assertAlmostEqual(1, geo[1])
        self.assertAlmostEqual(-3, geo[2])

    def test_rx(self):
        radian_angle = Angle(0.45, Angle.Units.Radians)
        v = np.array([1, 2, 3])

        vprime = np.array([1, 0.495997602371663, 3.57127237528049])

        vcalc = MatrixRotations.rx(-radian_angle).dot(v)

        for i in range(3):
            self.assertAlmostEqual(vprime[i], vcalc[i], delta=1e-8)

    def test_ry(self):
        radian_angle = Angle(0.45, Angle.Units.Radians)
        v = np.array([1, 2, 3])

        vprime = np.array([2.20534370468637, 2, 2.26637577294680 ])

        vcalc = MatrixRotations.ry(-radian_angle).dot(v)

        for i in range(3):
            self.assertAlmostEqual(vprime[i], vcalc[i], delta=1e-8)

    def test_rz(self):
        radian_angle = Angle(0.45, Angle.Units.Radians)
        v = np.array([1, 2, 3])

        vprime = np.array([0.0305160341302164, 2.23585973881658, 3 ])

        vcalc = MatrixRotations.rz(-radian_angle).dot(v)

        for i in range(3):
            self.assertAlmostEqual(vprime[i], vcalc[i], delta=1e-8)


