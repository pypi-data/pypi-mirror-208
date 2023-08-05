from .coordinate_representations import CartesianCoordinate, SphericalCoordinate
from ..measurables.physical_quantities import Length, Angle, Speed, Temperature, Pressure, Humidity
from ..measurables.Measurable import InvalidUnitOfMeasureException
import numpy as np
import math
import datetime


class Constants:
    @staticmethod
    def deg_to_rad():
        return np.pi / 180

    @staticmethod
    def rad_to_deg():
        return 180 / np.pi

    @staticmethod
    def a():
        return 6378137.0

    @staticmethod
    def f():
        return 1/298.257223563

    @staticmethod
    def b():
        return 6356752.314245

    @staticmethod
    def c():
        return 6371007.180918

    @staticmethod
    def n():
        return 0.00167922038638370

    @staticmethod
    def e2():
        return ((Constants.a()**2) - (Constants.b()**2))/(Constants.a()**2)

    @staticmethod
    def ep2():
        return ((Constants.a()**2) - (Constants.b()**2))/(Constants.b()**2)


class CoordinateConversion:
    # C++ allows passing by reference. Python does, but only for certain mutable objects such as lists.
    # As such, it's better to simply return values and use those
    @staticmethod
    def ll_to_utm_x(lat, lon, utm_northing=None, utm_easting=None, zone_number=-1):

        semimajor_a = 6378137.0
        semiminor_b = 6356752.31424
        equ_radius = 6378137.0
        ecc_squared = ((semimajor_a ** 2) - (semiminor_b ** 2)) / (semimajor_a ** 2)
        k0 = 0.9996
        long_temp = (lon + 180) - int((lon + 180) / 360) * 360 - 180
        lat_rad = lat * Constants.deg_to_rad()
        long_rad = long_temp * Constants.deg_to_rad()
        if zone_number == -1:
            zone_number = int((long_temp + 180) / 6) + 1
            if 56.0 <= lat < 64.0 and 3.0 <= long_temp < 12.0:
                zone_number = 32

            if 72.0 <= lat < 84.0:
                if 0.0 <= long_temp < 9.0:
                    zone_number = 31
                elif 9.0 <= long_temp < 21.0:
                    zone_number = 33
                elif 21.0 <= long_temp < 33.0:
                    zone_number = 35
                elif 33.0 <= long_temp < 42.0:
                    zone_number = 37
        long_origin = (zone_number - 1.0) * 6.0 - 180.0 + 3.0
        long_origin_rad = long_origin * Constants.deg_to_rad()
        ecc_prime_squared = ecc_squared / (1.0 - ecc_squared)
        n = equ_radius / math.sqrt(1.0 - ecc_squared * math.sin(lat_rad) * math.sin(lat_rad))
        t = math.tan(lat_rad) * math.tan(lat_rad)
        c = ecc_prime_squared * math.cos(lat_rad) * math.cos(lat_rad)
        a = math.cos(lat_rad) * (long_rad - long_origin_rad)

        m = equ_radius * ((1.0 - ecc_squared / 4.0 - 3.0 * ecc_squared * ecc_squared / 64.0 - 5.0 * ecc_squared *
                           ecc_squared * ecc_squared / 256.0) * lat_rad - (
                                      3.0 * ecc_squared / 8.0 + 3.0 * ecc_squared *
                                      ecc_squared / 32.0 + 45.0 * ecc_squared *
                                      ecc_squared * ecc_squared / 1024.0) *
                          math.sin(2.0 * lat_rad) + (15.0 * ecc_squared * ecc_squared / 256.0 + 45.0 * ecc_squared *
                                                     ecc_squared * ecc_squared / 1024.0) * math.sin(4.0 * lat_rad) -
                          (35.0 * ecc_squared * ecc_squared * ecc_squared / 3072.0) * math.sin(6.0 * lat_rad))
        a2 = a * a
        a4 = a2 * a2
        utm_easting = (k0 * n * (a + (1.0 - t + c) * a2 * a / 6.0 + (
                    5.0 - 18.0 * t + t * t + 72.0 * c - 58.0 * ecc_prime_squared) * a4 * a / 120.0) + 500000.0)
        utm_northing = (k0 * (m + n * math.tan(lat_rad)
                              * (a2 / 2.0 + (5.0 - t + 9.0 * c + 4.0 * c * c) * a4 / 24.0
                                 + (61.0 - 58.8 * t + t * t + 600.0 * c - 330.0 * ecc_prime_squared)
                                 * a4 * a2 / 720.0)))
        if lat < 0:
            utm_northing += 10000000.0
        return utm_easting, utm_northing, zone_number

    @staticmethod
    def get_zone_number(lat, lon):
        long_temp = (lon + 180) - int((lon + 180) / 360) * 360 - 180
        lat_rad = lat * Constants.deg_to_rad()
        long_rad = long_temp * Constants.deg_to_rad()
        zone_number = int((long_temp + 180) / 6) + 1
        if 56.0 <= lat < 64.0 and 3.0 <= long_temp < 12.0:
            zone_number = 32

        if 72.0 <= lat < 84.0:
            if 0.0 <= long_temp < 9.0:
                zone_number = 31
            elif 9.0 <= long_temp < 21.0:
                zone_number = 33
            elif 21.0 <= long_temp < 33.0:
                zone_number = 35
            elif 33.0 <= long_temp < 42.0:
                zone_number = 37
        return zone_number

    @staticmethod
    def ll_to_utm(latitude, longitude, utm_northing=None, utm_easting=None, zone_number=-1):
        e2_squared = 0.0067394967423334640
        c = 6399593.6257586740
        lat = latitude * Constants.deg_to_rad()
        lon = longitude * Constants.deg_to_rad()

        if zone_number < 0:
            zone_number = int((longitude / 6.0) + 31.0)
            if 56.0 <= latitude < 64.0 and 3.0 <= longitude < 12.0:
                zone_number = 32
            if 72.0 <= latitude < 84.0:
                if 0.0 <= longitude < 9.0:
                    zone_number = 31
                elif 9.0 <= longitude < 21.0:
                    zone_number = 33
                elif 21.0 <= longitude < 33.0:
                    zone_number = 35
                elif 33.0 <= longitude < 42.0:
                    zone_number = 37
        s = ((zone_number * 6.0) - 183.0)
        delta_s = lon - (s * Constants.deg_to_rad())
        cos_lat = math.cos(lat)
        a = cos_lat * math.sin(delta_s)  # TODO: becomes infinite at equator
        epsilon = 0.5 * math.log((1 + a) / (1.0 - a))
        nu = math.atan(math.tan(lat) / math.cos(delta_s)) - lat
        v = c / math.sqrt(1 + (e2_squared * cos_lat * cos_lat)) * 0.9996
        ta = (e2_squared / 2) * epsilon * epsilon * cos_lat * cos_lat
        a1 = math.sin(2.0 * lat)
        a2 = a1 * cos_lat * cos_lat
        j2 = lat + (a1 / 2.0)
        j4 = ((3.0 * j2) + a2) / 4.0
        j6 = (5.0 * j4 + a2 * cos_lat * cos_lat) / 3.0
        alfa = (3.0 / 4.0) * e2_squared
        beta = (5.0 / 3.0) * alfa * alfa
        gamma = (35.0 / 27.0) * alfa * alfa * alfa

        utm_easting = epsilon * v * (1.0 + (ta / 3.0)) + 500000.0
        utm_northing = nu * v * (1.0 + ta) + 0.9996 * c * (lat - alfa * j2 + beta * j4 - gamma * j6)
        if utm_northing < 0:
            utm_northing += 10000000
        return utm_easting, utm_northing, zone_number


class GeospatialCoordinate(CartesianCoordinate):
    """CLAWSCoordinate Constructor

    If using 1 variable, it must be of type CLAWSCoordinate or CartesianCoordinate.
    If using 2 variables, they must be of type CLAWSCoordinate, or latitude + longitude (IN THAT ORDER)
    If using 3 variables, they must latitude + longitude + aboveGroundLevel IN THAT ORDER"""

    def __init__(self, a=None, b=None, c=None):
        """
        This constructor forms a CartesianCoordinate through the application of the three arguments. However, the
        details of how the coordinate is formed must be addressed. Unlike the base class, this class can represent a
        geodetic (latitude/longitude) location with an associated above ground level. If the arguments create this
        type of location, then the data is converted to the geodesic (Universal Transverse Mercurator (UTM)) projection.

        There are a multitude of ways to create this location representation.
        1) a is a Geospatial coordinate, and b and c are None. This is a copy constructor that creates a new
        representation of the data in a.
        2) a is a CartesianCoordinate, and b and c are None. Like the first method, this creates a copy. However,
        the data is represented as a base CartesianCoordinate rather than a geodetic location.
        3) a and b are either a GeospatialCoordinate or a CartesianCoordinate and c is None. Like the base class,
        the result of this constructor is the difference between a and b (i.e. self = a - b)
        4) a and b are either floating point or integer values and c is None. This creates a new GeospatialCoordinate
        object with a zero above ground level, and the UTM projection is determined with a representing the latitude
        and b representing the longitude
        4) a and b are either floating point or integer values and c is a length. This creates a similar
        GeospatialCoordinate as the previous method, but this time the above ground level is set to the value of c
        :param a: GeospatialCoordinate, CartesianCoordinate, float, int
            the object to copy, the x-coordinate, or the latitude
        :param b: GeospatialCoordinate, CartesianCoordinate, float, int, None
            the object to copy, the y-coordinate, or the longitude
        :param c: Length or None
            the above ground level of the point
        """

        #   Call the base class without arguments to establish the underlying structure of the class
        super().__init__()

        #   Based on the type of data determine how to create the class.
        if isinstance(a, GeospatialCoordinate) and b is None and c is None:
            super().__init__(a)
            self.zone_letter = a.zone_letter
            self.zone_number = a.zone_number
            self.latitude = a.latitude
            self.longitude = a.longitude
        elif isinstance(a, CartesianCoordinate) and b is None and c is None:
            super().__init__(a)
        elif (isinstance(a, GeospatialCoordinate) or isinstance(a, CartesianCoordinate)) and \
                (isinstance(b, GeospatialCoordinate) or isinstance(b, CartesianCoordinate)) and c is None:
            super().__init__(a, b)
        elif (isinstance(a, float) or isinstance(a, int)) and (
                isinstance(b, float) or isinstance(b, int)) and c is None:  # this is a lat + lon
            utm_easting, utm_northing, zone_number = CoordinateConversion.ll_to_utm_x(a, b)
            easting, northing = GeospatialCoordinate.ll_to_utm(a, b)
            self.zone_letter = self.letter_from_lat(a)
            self.zone_number = zone_number
            self.latitude = a
            self.longitude = b
            self.x = Length(easting, Length.Units.Meters)
            self.y = Length(northing, Length.Units.Meters)
        elif (isinstance(a, float) or isinstance(a, int)) and \
                (isinstance(b, float) or isinstance(b, int)) and \
                isinstance(c, Length):  # lat + lon + ?
            utm_easting, utm_northing, zone_number = CoordinateConversion.ll_to_utm_x(a, b)
            easting, northing = GeospatialCoordinate.ll_to_utm(a, b)
            self.zone_letter = self.letter_from_lat(a)
            self.zone_number = zone_number
            self.latitude = a
            self.longitude = b
            self.x = Length(easting, Length.Units.Meters)
            self.y = Length(northing, Length.Units.Meters)
            self.above_ground_level = c
        elif a is None and b is None and c is None:
            self.latitude = 0.0
            self.longitude = 0.0
            utm_easting, utm_northing, zone_number = CoordinateConversion.ll_to_utm_x(0.0, 0.0)
            self.zone_number = zone_number
            self.zone_letter = self.letter_from_lat(0.0)
            self.x = Length()
            self.y = Length()
            self.z = Length()
        else:
            raise InvalidUnitOfMeasureException

    @staticmethod
    def letter_from_lat(lat: float):
        """
        Based on the latitude that is passed to the function we can determine a representation of the zone letter
        :param lat: float
            the latitude of the point that we want to examine
        :return: str
            the UTM zone letter
        """
        if lat < -80:
            return 'A'
        elif -80 <= lat < -72:
            return 'C'
        elif -72 <= lat < -64:
            return 'D'
        elif -64 <= lat < -56:
            return 'E'
        elif -56 <= lat < -48:
            return 'F'
        elif -48 <= lat < -40:
            return 'G'
        elif -40 <= lat < -32:
            return 'H'
        elif -32 <= lat < -24:
            return 'J'
        elif -24 <= lat < -16:
            return 'K'
        elif -16 <= lat < -8:
            return 'L'
        elif -8 <= lat < 0:
            return 'M'
        elif 0 <= lat < 8:
            return 'N'
        elif 8 <= lat < 16:
            return 'P'
        elif 16 <= lat < 24:
            return 'Q'
        elif 24 <= lat < 32:
            return 'R'
        elif 32 <= lat < 40:
            return 'S'
        elif 40 <= lat < 48:
            return 'T'
        elif 48 <= lat < 56:
            return 'U'
        elif 56 <= lat < 64:
            return 'V'
        elif 64 <= lat < 72:
            return 'W'
        elif 72 <= lat < 80:
            return 'X'
        elif 80 <= lat:
            return 'Z'

    @staticmethod
    def conex_location():
        return GeospatialCoordinate(33.5649870, -106.6706207, Length())

    @staticmethod
    def conex_wx():
        return GeospatialCoordinate(33.5649870, -106.6706207, Length(3.0))

    @staticmethod
    def east_tower_location():
        return GeospatialCoordinate(33.55232639, -106.6783867, Length())

    @staticmethod
    def east_tower_wx_35ft():
        return GeospatialCoordinate(33.55232639, -106.6783867, Length(10.7))

    @staticmethod
    def east_tower_wx_54ft():
        return GeospatialCoordinate(33.55232639, -106.6783867, Length(16.5))

    @staticmethod
    def east_tower_wx_137ft():
        return GeospatialCoordinate(33.55232639, -106.6783867, Length(41.8))

    @staticmethod
    def east_tower_wx_165ft():
        return GeospatialCoordinate(33.55232639, -106.6783867, Length(50.3))

    @staticmethod
    def east_tower_wx_270ft():
        return GeospatialCoordinate(33.55232639, -106.6783867, Length(82.3))

    @staticmethod
    def east_tower_wx_285ft():
        return GeospatialCoordinate(33.55232639, -106.6783867, Length(86.9))

    @staticmethod
    def west_tower_location():
        return GeospatialCoordinate(33.55231583, -106.6810122, Length())

    @staticmethod
    def west_tower_wx_35ft():
        return GeospatialCoordinate(33.55231583, -106.6810122, Length(10.7))

    @staticmethod
    def west_tower_wx_93ft():
        return GeospatialCoordinate(33.55231583, -106.6810122, Length(28.3))

    @staticmethod
    def west_tower_wx_137ft():
        return GeospatialCoordinate(33.55231583, -106.6810122, Length(41.8))

    @staticmethod
    def west_tower_wx_200ft():
        return GeospatialCoordinate(33.55231583, -106.6810122, Length(61))

    @staticmethod
    def west_tower_wx_285ft():
        return GeospatialCoordinate(33.55231583, -106.6810122, Length(86.9))

    @staticmethod
    def array_center():
        return GeospatialCoordinate(33.55232361, -106.6797006, Length(0.0))

    @staticmethod
    def harriet_location():
        return GeospatialCoordinate(33.56251596, -106.6443884, Length.average_listener_height())

    @staticmethod
    def cain_location():
        return GeospatialCoordinate(33.57582656, -106.70375776, Length.average_listener_height())

    @staticmethod
    def gap_location():
        return GeospatialCoordinate(33.530860, -106.422960, Length.average_listener_height())

    # NOTE: The C# version of the following method was missing the final entry - gap_location. Added here.
    @staticmethod
    def known_locations():
        output = [GeospatialCoordinate.conex_location(), GeospatialCoordinate.conex_wx(), GeospatialCoordinate.east_tower_location(),
                  GeospatialCoordinate.east_tower_wx_35ft(), GeospatialCoordinate.east_tower_wx_54ft(),
                  GeospatialCoordinate.east_tower_wx_137ft(), GeospatialCoordinate.east_tower_wx_165ft(),
                  GeospatialCoordinate.east_tower_wx_270ft(), GeospatialCoordinate.east_tower_wx_285ft(),
                  GeospatialCoordinate.west_tower_location(), GeospatialCoordinate.west_tower_wx_35ft(),
                  GeospatialCoordinate.west_tower_wx_93ft(), GeospatialCoordinate.west_tower_wx_137ft(),
                  GeospatialCoordinate.west_tower_wx_200ft(), GeospatialCoordinate.west_tower_wx_285ft(),
                  GeospatialCoordinate.array_center(), GeospatialCoordinate.harriet_location(), GeospatialCoordinate.cain_location(),
                  GeospatialCoordinate.gap_location()]
        return output

    @staticmethod
    def utm_to_coordinate(easting: Length, northing: Length, zone_num: int, zone_l: str):
        """
        This function is a conversion of code to convert a UTM location base to latitude/longitude pairs.
        :param easting: Length
            the distance from the easter edge of the zone
        :param northing: Length
            the distance from the southern edge of the zone
        :param zone_num: int
            the zone number of the current UTM zone
        :param zone_l: str
            the letter of the zone which determines the latitude location of the point
        Revision History
        ----------------

        20221011 - FSM - Took the meters units for the Easting/Northing coordinate to determine the location
        """

        a = 6378137.0
        b = 6356752.3142
        e2 = 0.00669438
        e4 = e2 * e2
        e6 = e2 * e4
        ep2 = -1.0
        if e2 != 1.0:
            ep2 = e2 / (1.0 - e2)
        ep4 = ep2 * ep2
        ep6 = ep4 * ep2
        ep8 = ep2 * ep6
        k01 = 0.9996
        k02 = k01 * k01
        k03 = k01 * k02
        k04 = k01 * k03
        k05 = k01 * k04
        k06 = k01 * k05
        k07 = k01 * k06
        k08 = k01 * k07
        north = GeospatialCoordinate.in_north(zone_l)
        if not north:
            northing -= 10000000.0
        k1 = northing.meters
        k2 = a * k01 * (1.0 - e2 / 4.0 - (3.0 / 64.0) * e4 - (5.0 / 256.0) * e6)
        mu = k1 / k2
        sin2mu = np.sin(2.0 * mu)
        sin4mu = np.cos(4.0 * mu)
        sin6mu = np.sin(6.0 * mu)
        sin8mu = np.cos(8.0 * mu)
        n1 = (a - b) / (a + b)
        n2 = n1 * n1
        n3 = n1 * n2
        n4 = n1 * n3
        j1 = (3.0 / 2.0) * n1 - (27.0 / 32.0) * n3
        j2 = (21.0 / 16.0) * n2 - (55.0 / 32.0) * n4
        j3 = (151.0 / 96.0) * n3
        j4 = (1097.0 / 512.0) * n4
        fplat = mu + j1 * sin2mu + j2 * sin4mu + j3 * sin6mu + j4 * sin8mu
        sin1 = np.sin(fplat)
        sin2 = sin1 * sin1
        cos1 = np.cos(fplat)
        cos2 = cos1 * cos1
        cos3 = cos1 * cos2
        cos4 = cos1 * cos3
        cos5 = cos1 * cos4
        cos6 = cos1 * cos5
        cos7 = cos1 * cos6
        cos8 = cos1 * cos7
        tan1 = sin1 / cos1
        tan2 = tan1 * tan1
        tan3 = tan1 * tan2
        tan4 = tan1 * tan3
        tan5 = tan1 * tan4
        tan6 = tan1 * tan5
        p = a * (1.0 - e2) / np.pow((1.0 - e2 * sin2), 1.5)
        q1 = p * (1.0 + ep2 * cos2)
        q2 = q1 * q1
        q3 = q1 * q2
        q4 = q1 * q3
        q5 = q1 * q4
        q6 = q1 * q5
        q7 = q1 * q6
        fe = 500000.0
        de1 = easting.meters - fe
        de2 = de1 * de1
        de3 = de1 * de2
        de4 = de1 * de3
        de5 = de1 * de4
        de6 = de1 * de5
        de7 = de1 * de6
        de8 = de1 * de7

        k1 = 2.0 * p * q1 * k02
        t10 = tan1 / k1

        k1 = 5.0 + 3.0 * tan2 + ep2 * cos2 - 4.0 * ep4 * cos4 - 9.0 * tan2 * ep2 * cos2
        k2 = 24.0 * p * q3 * k04
        t11 = tan1 * k1 / k2

        k1 = 61.0 + 90.0 * tan2 + 46.0 * ep2 * cos2 + 45.0 * tan4 - 252.0 * tan2 * ep2 * cos2
        k2 = -3.0 * ep4 * cos4 + 100.0 * ep6 * cos6 - 66.0 * tan2 * ep4 * cos4
        k3 = -90.0 * tan4 * ep2 * cos2 + 88.0 * ep8 * cos8 + 225.0 * tan4 * ep4 * cos4
        # should the following be negative?
        k4 = 84.0 * tan2 * ep6 * cos6 - 192.0 * tan2 * ep8 * cos8
        k5 = 720.0 * p * q5 * k06
        t12 = tan1 * (k1 + k2 + k3 + k4) / k5

        k1 = 1385.0 + 3633.0 * tan2 + 4095.0 * tan4 + 1575.0 * tan6
        k2 = 40320.0 * p * q7 * k08
        t13 = tan1 * k1 / k2

        k1 = q1 * cos1 * k01
        t14 = 1.0 / k1

        k1 = 1.0 + 2.0 * tan2 + ep2 * cos2
        k2 = 6.0 * q3 * cos1 * k03
        t15 = k1 / k2

        k1 = 5.0 + 6.0 * ep2 * cos2 + 28.0 * tan2 - 3.0 * ep4 * cos4 + 8.0 * tan2 * ep2 * cos2
        k2 = 24.0 * tan4 - 4.0 * ep6 * cos6 + 4.0 * tan2 * ep4 * cos4 + 24.0 * tan2 * ep6 * cos6
        k3 = 120.0 * q5 * cos1 * k05
        t16 = (k1 + k2) / k3

        k1 = 61.0 + 662.0 * tan2 + 1320.0 * tan4 + 720.0 * tan6
        k2 = 5040.0 * q7 * cos1 * k07
        t17 = k1 / k2

        lat_deg = Constants.rad_to_deg() * fplat
        lon_deg = 6.0 * (zone_num - 1.0) - 180 + 3.0
        lat = lat_deg + (Constants.rad_to_deg() * (-de2 * t10 + de4 * t11 - de6 * t12 + de8 * t13))
        lon = lon_deg + (Constants.rad_to_deg() * (de1 * t14 - de3 * t15 + de5 * t16 - de7 * t17))
        return lat, lon

    @staticmethod
    def utm_to_ll(easting, northing, lonZone, zone_l):
        A = 6378137.0
        B = 6356752.3142
        E2 = 0.00669438

        E4 = E2 * E2
        E6 = E2 * E4

        EP2 = -1.0
        if E2 != 1.0:
            EP2 = E2 / (1.0 - E2)

        EP4 = EP2 * EP2
        EP6 = EP2 * EP4
        EP8 = EP2 * EP6

        K01 = 0.9996
        K02 = K01 * K01
        K03 = K01 * K02
        K04 = K01 * K03
        K05 = K01 * K04
        K06 = K01 * K05
        K07 = K01 * K06
        K08 = K01 * K07

        north = GeospatialCoordinate.in_north(zone_l)
        k1 = northing.meters
        if not north:
            k1 -= 10000000.0

        k2 = A * K01 * (1.0 - E2 / 4.0 - (3.0 / 64.0) * E4 - (5.0 / 256.0) * E6)

        MU = k1 / k2
        SIN2MU = np.sin(2.0 * MU)
        SIN4MU = np.cos(4.0 * MU)
        SIN6MU = np.sin(6.0 * MU)
        SIN8MU = np.cos(8.0 * MU)

        N1 = (A - B) / (A + B)
        N2 = N1 * N1
        N3 = N1 * N2
        N4 = N1 * N3

        J1 = (3.0 / 2.0) * N1 - (27.0 / 32.0) * N3
        J2 = (21.0 / 16.0) * N2 - (55.0 / 32.0) * N4
        J3 = (151.0 / 96.0) * N3
        J4 = (1097.0 / 512.0) * N4

        FPLAT = MU + J1 * SIN2MU + J2 * SIN4MU + J3 * SIN6MU + J4 * SIN8MU

        SIN1 = np.sin(FPLAT)
        SIN2 = SIN1 * SIN1

        COS1 = np.cos(FPLAT)
        COS2 = COS1 * COS1
        COS3 = COS1 * COS2
        COS4 = COS1 * COS3
        COS5 = COS1 * COS4
        COS6 = COS1 * COS5
        COS7 = COS1 * COS6
        COS8 = COS1 * COS7

        TAN1 = SIN1 / COS1
        TAN2 = TAN1 * TAN1
        TAN3 = TAN1 * TAN2
        TAN4 = TAN1 * TAN3
        TAN5 = TAN1 * TAN4
        TAN6 = TAN1 * TAN5

        P = A * (1.0 - E2) / ((1.0 - E2 * SIN2)**1.5)
        Q1 = P * (1.0 + EP2 * COS2)
        Q2 = Q1 * Q1
        Q3 = Q1 * Q2
        Q4 = Q1 * Q3
        Q5 = Q1 * Q4
        Q6 = Q1 * Q5
        Q7 = Q1 * Q6

        FE = 500000.0
        DE1 = easting.meters - FE
        DE2 = DE1 * DE1
        DE3 = DE1 * DE2
        DE4 = DE1 * DE3
        DE5 = DE1 * DE4
        DE6 = DE1 * DE5
        DE7 = DE1 * DE6
        DE8 = DE1 * DE7

        k1 = 2.0 * P * Q1 * K02
        T10 = TAN1 / k1

        k1 = 5.0 + 3.0 * TAN2 + EP2 * COS2 - 4.0 * EP4 * COS4 - 9.0 * TAN2 * EP2 * COS2
        k2 = 24.0 * P * Q3 * K04
        T11 = TAN1 * k1 / k2

        k1 = 61.0 + 90.0 * TAN2 + 46.0 * EP2 * COS2 + 45.0 * TAN4 - 252.0 * TAN2 * EP2 * COS2
        k2 = -3.0 * EP4 * COS4 + 100.0 * EP6 * COS6 - 66.0 * TAN2 * EP4 * COS4
        k3 = -90.0 * TAN4 * EP2 * COS2 + 88.0 * EP8 * COS8 + 225.0 * TAN4 * EP4 * COS4
        k4 = +84.0 * TAN2 * EP6 * COS6 - 192.0 * TAN2 * EP8 * COS8
        k5 = 720.0 * P * Q5 * K06
        T12 = TAN1 * (k1 + k2 + k3 + k4) / k5

        k1 = 1385.0 + 3633.0 * TAN2 + 4095.0 * TAN4 + 1575.0 * TAN6
        k2 = 40320.0 * P * Q7 * K08
        T13 = TAN1 * k1 / k2

        k1 = Q1 * COS1 * K01
        T14 = 1.0 / k1

        k1 = 1.0 + 2.0 * TAN2 + EP2 * COS2
        k2 = 6.0 * Q3 * COS1 * K03
        T15 = k1 / k2

        k1 = 5.0 + 6.0 * EP2 * COS2 + 28.0 * TAN2 - 3.0 * EP4 * COS4 + 8.0 * TAN2 * EP2 * COS2
        k2 = 24.0 * TAN4 - 4.0 * EP6 * COS6 + 4.0 * TAN2 * EP4 * COS4 + 24.0 * TAN2 * EP6 * COS6
        k3 = 120.0 * Q5 * COS1 * K05
        T16 = (k1 + k2) / k3

        k1 = 61.0 + 662.0 * TAN2 + 1320.0 * TAN4 + 720.0 * TAN6
        k2 = 5040.0 * Q7 * COS1 * K07
        T17 = k1 / k2

        LATDEG = Constants.rad_to_deg() * FPLAT
        LONDEG = 6.0 * (lonZone - 1.0) - 180.0 + 3.0
        lat = LATDEG + (Constants.rad_to_deg() * (-DE2 * T10 + DE4 * T11 - DE6 * T12 + DE8 * T13))
        lon = LONDEG + (Constants.rad_to_deg() * (+DE1 * T14 - DE3 * T15 + DE5 * T16 - DE7 * T17))
        return lat, lon

    @staticmethod
    def ll_to_utm(lat, lon):
        A = 6378137.0
        B = 6356752.3142
        E2 = 0.00669438
        latValid = (-80.0 <= lat) and (lat <= +84.0)
        lonValid = (-180.0 <= lon) and (lon <= +180.0)
        ok = latValid and lonValid

        if ok:
            LATDEG = lat
            LATRAD = Constants.deg_to_rad() * lat
            LONDEG = lon

            SIN1 = np.sin(LATRAD)
            COS1 = np.cos(LATRAD)
            SIN2 = SIN1 * SIN1
            COS2 = COS1 * COS1
            COS3 = COS1 * COS2
            COS4 = COS1 * COS3
            COS5 = COS1 * COS4
            COS6 = COS1 * COS5
            COS7 = COS1 * COS6
            COS8 = COS1 * COS7
            TAN1 = SIN1 / COS1
            TAN2 = TAN1 * TAN1
            TAN3 = TAN1 * TAN2
            TAN4 = TAN1 * TAN3
            TAN5 = TAN1 * TAN4
            TAN6 = TAN1 * TAN5
            N1 = (A - B) / (A + B)
            N2 = N1 * N1
            N3 = N1 * N2
            N4 = N1 * N3
            N5 = N1 * N4
            Ap = A * (1.0 - N1 + (1.25) * (N2 - N3) + (81.0 / 64.0) * (N4 - N5))
            Bp = (1.5) * A * (N1 - N2 + (0.875) * (N3 - N4) + (55.0 / 64.0) * (N5))
            Cp = (0.9375) * A * (N2 - N3 + (0.75) * (N4 - N5))
            Dp = (35.0 / 48.0) * A * (N3 - N4 + (0.6875) * (N5))
            Ep = (315.0 / 512.0) * A * (N4 - N5)

            SIN2LAT = np.sin(2.0 * LATRAD)
            SIN4LAT = np.sin(4.0 * LATRAD)
            SIN6LAT = np.sin(6.0 * LATRAD)
            SIN8LAT = np.cos(6.0 * LATRAD)

            S = Ap * LATRAD - Bp * SIN2LAT + Cp * SIN4LAT - Dp * SIN6LAT + Ep * SIN8LAT

            EP2 = -1.0
            if E2 != 1.0:
                EP2 = E2 / (1.0 - E2)
            EP4 = EP2 * EP2
            EP6 = EP2 * EP4
            EP8 = EP2 * EP6

            K0 = 0.9996
            P = A * (1.0 - E2) / ((1.0 - E2 * SIN2)**1.5)
            Q = P * (1.0 + EP2 * COS2)

            T1 = S * K0

            T2 = Q * SIN1 * COS1 * K0 / 2.0

            k1 = Q * SIN1 * COS3 * K0 / 24.0
            k2 = 5.0 - TAN2 + 9.0 * EP2 * COS2 + 4.0 * EP4 * COS4
            T3 = k1 * k2

            k1 = Q * SIN1 * COS5 * K0 / 720.0
            k2 = 61.0 - 58.0 * TAN2 + TAN4 + 270.0 * EP2 * COS2 - 330.0 * TAN2 * EP2 * COS2
            k3 = 445.0 * EP4 * COS4 + 324.0 * EP6 * COS6 - 680.0 * TAN2 * EP4 * COS4
            k4 = 88.0 * EP8 * COS8 - 600.0 * TAN2 * EP6 * COS6 - 192.0 * TAN2 * EP8 * COS8
            T4 = k1 * (k2 + k3 + k4)

            k1 = Q * SIN1 * COS7 * K0 / 40320.0
            k2 = 1385.0 - 3111.0 * TAN2 + 543.0 * TAN4 - TAN6
            T5 = k1 * k2

            T6 = Q * COS1 * K0

            k1 = Q * COS3 * K0 / 6.0
            k2 = 1.0 - TAN2 + EP2 * COS2
            T7 = k1 * k2

            k1 = Q * COS5 * K0 / 120.0
            k2 = 5.0 - 18.0 * TAN2 + TAN4 + 14.0 * EP2 * COS2 - 58.0 * TAN2 * EP2 * COS2
            k3 = 13.0 * EP4 * COS4 + 4.0 * EP6 * COS6 - 64.0 * TAN2 * EP4 * COS4 - 24.0 * TAN2 * EP6 * COS6
            T8 = k1 * (k2 + k3)

            T9 = 61.0 - 479.0 * TAN2 + 179 * TAN4 - TAN6 * Q * COS7 * K0 / 5040.0

            LONZONE = 1 + int((LONDEG + 180.0) / 6.0)
            LONORIG = 6.0 * (LONZONE - 1) - 180.0 + 3.0

            dL1 = Constants.deg_to_rad() * (LONDEG - LONORIG)
            dL2 = dL1 * dL1
            dL3 = dL1 * dL2
            dL4 = dL1 * dL3
            dL5 = dL1 * dL4
            dL6 = dL1 * dL5
            dL7 = dL1 * dL6
            dL8 = dL1 * dL7

            FN = 0.0
            if LATDEG < 0.0:
                FN = 1.0e7
            FE = 500000.0
            _northing = FN + T1 + dL2 * T2 + dL4 * T3 + dL6 * T4 + dL8 * T5
            _easting = FE + dL1 * T6 + dL3 * T7 + dL5 * T8 + dL7 * T9
            return _easting, _northing
        else:
            return 0, 0

    @staticmethod
    def in_north(num):
        if num in ['M', 'L', 'K', 'J', 'H', 'G', 'F', 'E', 'D', 'C']:
            return False
        else:
            return True

    @property
    def above_ground_level(self):
        return self.z

    @above_ground_level.setter
    def above_ground_level(self, v):
        self.z = v

    @property
    def easting(self):
        return self.x

    @property
    def northing(self):
        return self.y

    @property
    def utm_zone(self):
        utm_string = '{}{}'.format(self.zone_number, self.zone_letter)
        return utm_string

    def move(self, distance, bearing):
        """
        This function will translate the ground based location of this coordinate to a new location based on the bearing
        and distance. These will both modify the geodetic (lat/lon) and geodesic(UTM/Easting/Northing) location.

        :distance: Length - the distance to move
        :bearing: Angle - The direction to move the point

        :returns: The new location

        Remarks
        20221205 - FSM - Adjusted the system to use the Length parameter rather than converting the new Easting/Northing
            to meters for the creation of the new location.
        """
        if isinstance(distance, Length) and isinstance(bearing, Angle):
            new_easting = self.easting + (distance * bearing.sin())
            new_northing = self.northing + (distance * bearing.cos())
            new_lat, new_lon = GeospatialCoordinate.utm_to_ll(easting=new_easting, northing=new_northing,
                                                              lonZone=self.zone_number, zone_l=self.zone_letter)
            c = GeospatialCoordinate()
            c.latitude = new_lat
            c.longitude = new_lon
            c.x = Length(new_easting.meters, Length.Units.Meters)
            c.y = Length(new_northing.meters, Length.Units.Meters)
            c.z = self.above_ground_level
            c.zone_letter = GeospatialCoordinate.letter_from_lat(c.latitude)
            c.zone_number = CoordinateConversion.get_zone_number(c.latitude, c.longitude)
            return c

    def range_to(self, c):
        if isinstance(c, CartesianCoordinate):
            c2 = GeospatialCoordinate(self, c)
            return Length(np.sqrt(c2.x.meters * c2.x.meters + c2.y.meters * c2.y.meters), Length.Units.Meters)

    def distance_to(self, c):
        if isinstance(c, CartesianCoordinate):
            c2 = GeospatialCoordinate(self, c)
            return Length(np.sqrt(c2.x.meters * c2.x.meters + c2.y.meters * c2.y.meters + c2.z.meters * c2.z.meters),
                          Length.Units.Meters)

    def bearing_to(self, point):
        if isinstance(point, CartesianCoordinate):
            c = CartesianCoordinate(point - self)
            s = SphericalCoordinate(c.to_body_reference())
            degrees = s.azimuthal.degrees
            while degrees < 0:
                degrees += 360
            while degrees > 360:
                degrees -= 360
            return Angle(degrees, Angle.Units.Degrees)

    def to_string(self):
        return '{} {} {}'.format(self.utm_zone, round(self.easting.meters), round(self.northing.meters))


class SourcePoint(GeospatialCoordinate):
    """
    This class extends the CLAWSCoordinate and adds the orientation to the class
    """

    def __init__(self, coordinate_or_latitude=None, longitude=None, above_ground_level=None, heading=None, pitch=None,
                 roll=None, velocity=None):
        """
        Class constructor
        """
        if coordinate_or_latitude is not None:
            if isinstance(coordinate_or_latitude, SourcePoint):
                super().__init__(coordinate_or_latitude)
                self.m_heading = coordinate_or_latitude.heading
                self.pitch = coordinate_or_latitude.pitch
                self.roll = coordinate_or_latitude.roll
                self.ground_velocity = coordinate_or_latitude.ground_velocity
            else:
                if longitude is not None and \
                        above_ground_level is not None and \
                        heading is not None and \
                        pitch is not None and \
                        roll is not None:
                    super().__init__(coordinate_or_latitude, longitude, above_ground_level)
                    self.m_heading = heading
                    self.pitch = pitch
                    self.roll = roll
                    self.ground_velocity = velocity
        else:
            super().__init__()
            self.m_heading = Angle()
            self.roll = Angle()
            self.pitch = Angle()
            self.ground_velocity = Speed()

    @property
    def heading(self):
        return self.m_heading

    @heading.setter
    def heading(self, value):
        if isinstance(value, Angle):
            self.m_heading = value
            self.m_heading.normalize()

    @property
    def heading_degrees(self):
        return self.m_heading.degrees

    @heading_degrees.setter
    def heading_degrees(self, value):
        if isinstance(value, Angle):
            self.m_heading = Angle(value, Angle.Units.Degrees)
            self.m_heading.normalize()

    @property
    def pitch_degrees(self):
        return self.pitch.degrees

    @pitch_degrees.setter
    def pitch_degrees(self, value):
        if isinstance(value, Angle):
            self.pitch = Angle(value, Angle.Units.Degrees)

    @property
    def roll_degrees(self):
        return self.roll.degrees

    @roll_degrees.setter
    def roll_degrees(self, value):
        if isinstance(value, Angle):
            self.roll = Angle(value, Angle.Units.Degrees)

    @property
    def ground_velocity_knots(self):
        return self.ground_velocity.knots

    @ground_velocity_knots.setter
    def ground_velocity_knots(self, value):
        self.ground_velocity = Speed(value, Speed.Units.Knots)

    @property
    def wsmr_arc_msl_adjustment(self):
        return Length(30.48, Length.Units.Meters)

    @property
    def gps_week_origin(self):
        return datetime.datetime(1980, 1, 6)

    @property
    def body_vector(self):
        """
        This property determines the vector in the body reference frame, then applies the various rotations from the
        vehicle's orientation.
        """

        c = self.to_body_reference()
        c.orient_vector(self.heading, self.pitch, self.roll)
        return c


class AtmosphericPoint(GeospatialCoordinate):
    """
    This class represents a measurement of the atmosphere at a specific location in space. Through the use of the
    GeospatialCoordinate class we can locate the measurement. Through the addition of the various measurable objects
    we define the Atmosphere. In addition, there is a need to add a time because there is a temporal component to the
    measurement of the atmosphere.
    """

    def __init__(self, a, b, c, t: Temperature = None, p: Pressure = None, h: Humidity = None, time = None,
                 u: Speed = None, u_dir: Angle = None, v: Speed = None):
        """
        This constructs the AtmosphericPoint object with the associated atmospheric paramnters
        :param a: GeospatialCoordinate, CartesianCoordinate, float, int
            the object to copy, the x-coordinate, or the latitude
        :param b: GeospatialCoordinate, CartesianCoordinate, float, int, None
            the object to copy, the y-coordinate, or the longitude
        :param c: Length or None
            the above ground level of the point
        :param t: Temperature
            the atmospheric temperature at this location and time
        :param p: Atmospheric pressure
            the pressure at this location and time
        :param h: Humidity
            the humidity at this location and time
        :param time: datetime or floating point
            either a representation of the date and time or a seconds past midnight floating point representation of
            when the measurement occurred.
        :param u: Speed
            the horizontal wind speed at this point
        :param u_dir: Angle
            the horizontal wind angle at this point
        :param v: Speed
            the vertical wind speed at this point
        """

        super().__init__(a, b, c)

        self._temperature = t
        self._pressure = p
        self._humidity = h
        self._time = time
        self._horizontal_wind_speed = u
        self._horizontal_wind_direction = u_dir
        self._vertical_wind_speed = v

    @property
    def temperature(self):
        return self._temperature

    @property
    def atmospheric_pressure(self):
        return self._pressure

    @property
    def relative_humidity(self):
        return self._humidity

    @property
    def time(self):
        return self._time

    @property
    def time_past_midnight(self):
        if isinstance(self.time, datetime.datetime):
            return 60 * (60 * self.time.hour + self.time.minute) + self.time.second + self.time.microsecond * 1e-6
        else:
            return self.time

    @property
    def horizontal_wind_speed(self):
        return self._horizontal_wind_speed

    @property
    def horizontal_wind_direction(self):
        return self._horizontal_wind_direction

    @property
    def vertical_wind_speed(self):
        return self._vertical_wind_speed

    @property
    def dew_point(self):
        from ..conversions.Physics import Physics
        return Physics.dew_point(self.relative_humidity, self.temperature)

