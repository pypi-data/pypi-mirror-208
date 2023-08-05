from .Measurable import Measurable, InvalidUnitOfMeasureException
from enum import Enum
import numpy as np
from datetime import datetime
from typing import Union


class Angle(Measurable):
    class Units(Enum):
        Degrees = 0
        Radians = 1
        Milliradians = 2

        def __str__(self):
            if self.value == 0:
                return 'deg'
            elif self.value == 1:
                return 'rad'
            elif self.value == 2:
                return 'mrad'

    def __init__(self, angle=0.0, unit=Units.Degrees):
        super().__init__()
        factor = 1
        if isinstance(unit, str):
            if unit == str(self.Units.Degrees):
                unit = self.Units.Degrees
            elif unit == str(self.Units.Radians):
                unit = self.Units.Radians
            elif unit == str(self.Units.Milliradians):
                unit = self.Units.Milliradians
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')

        if isinstance(unit, Enum):
            if unit == self.Units.Degrees:
                factor = 1
            elif unit == self.Units.Radians:
                factor = self.deg_per_rad()
            elif unit == self.Units.Milliradians:
                factor = self.deg_per_rad() / 1000
        else:
            print('unit variable is not an enum or string!')

        if isinstance(angle, str):
            try:
                angle = float(angle)
            except ValueError:
                if angle in self.direction():
                    angle = self.wind_angle()[self.direction().index(angle)]
                elif angle == 'CALM':
                    angle = 0
                else:
                    print('angle variable cannot be parsed!')
                    angle = 0.0
        self.value = float(angle * factor)
        self.units = self.Units.Degrees
        # self.unit_symbols = [str(unit) for unit in self.Units]

    @staticmethod
    def deg_per_km():
        return ((1 / 111.694) + (1 / 110.574)) / 2

    @staticmethod
    def human_eye_angular_resolution():
        return Angle(25, Angle.Units.Milliradians)

    @staticmethod
    def deg_per_rad():
        return 180 / np.pi

    @staticmethod
    def rad_per_deg():
        return np.pi / 180

    @staticmethod
    def direction():
        return ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

    @staticmethod
    def wind_angle():
        return [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]

    @staticmethod
    def symbol_to_enum(string):
        if isinstance(string, str):
            if string == str(Angle.Units.Radians):
                return Angle.Units.Radians
            elif string == str(Angle.Units.Milliradians):
                return Angle.Units.Milliradians
            elif string == str(Angle.Units.Degrees):
                return Angle.Units.Degrees
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')
        else:
            print('string variable is not of type string')

    @staticmethod
    def asin(x):
        if isinstance(x, int) or isinstance(x, float):
            return Angle(np.arcsin(x), Angle.Units.Radians)
        else:
            print('x variable is not a number')
            raise InvalidUnitOfMeasureException

    @staticmethod
    def unit_symbols():
        return [str(unit) for unit in Angle.Units]

    @staticmethod
    def acos(x):
        if isinstance(x, int) or isinstance(x, float):
            return Angle(np.arccos(x), Angle.Units.Radians)
        elif isinstance(x, Length):
            return Angle(np.arccos(x.meters), Angle.Units.Radians)
        else:
            print('x variable is not a number')
            raise InvalidUnitOfMeasureException

    @staticmethod
    def atan(x):
        if isinstance(x, int) or isinstance(x, float):
            return Angle(np.arctan(x), Angle.Units.Radians)
        else:
            print('x variable is not a number')
            raise InvalidUnitOfMeasureException

    @staticmethod
    def atan2(x, y):
        if isinstance(x, Length) and isinstance(y, Length):
            return Angle(np.arctan2(x.meters, y.meters), Angle.Units.Radians)
        elif (isinstance(x, int) or isinstance(x, float)) and (isinstance(y, int) or isinstance(y, float)):
            return Angle(np.arctan2(x, y), Angle.Units.Radians)
        else:
            print('x and y are not valid types')

    @staticmethod
    def compass_point_to_degrees(string):
        if isinstance(string, str):
            if string in Angle.direction():
                angle = Angle.wind_angle()[Angle.direction().index(string)]
                return Angle(angle)
            else:
                print('string not valid')
        else:
            print('string variable is not a string')

    @staticmethod
    def min(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Angle) and isinstance(b, Angle):
                return Angle(min(a.value, b.value))
            else:
                print('a and b variables are not of type Angle')
        else:
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Angle):
                    print('{0} in array is not of type Angle'.format(index_val))
                    return
            return Angle(min([x.value for x in array]))

    @staticmethod
    def max(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Angle) and isinstance(b, Angle):
                return Angle(max(a.value, b.value))
            else:
                print('a and b variables are not of type Angle')
        else:
            if isinstance(array, list):
                for index_val in range(len(array)):
                    if not isinstance(array[index_val], Angle):
                        print('{0} in array is not of type Angle'.format(index_val))
                        return
                return Angle(max([x.value for x in array]))
            else:
                print('array variable is not a list')
                return

    @staticmethod
    def mean(array):
        if isinstance(array, list):
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Angle):
                    print('{0} in array is not of type Angle'.format(index_val))
                    return
            sin_sum = sum([x.sin() for x in array])
            cos_sum = sum([x.cos() for x in array])
            return Angle.atan2((sin_sum / len(array)), (cos_sum / len(array))).normalized
        else:
            print('array variable is not a list')
            return

    @property
    def radians(self):
        return self.value / self.deg_per_rad()

    @property
    def degrees(self):
        return self.value

    @property
    def milliradians(self):
        return self.radians * 1000

    @property
    def normalized(self):
        a = Angle(self.value)
        a.normalize()
        return a

    def normalize(self):
        while self.value >= 360:
            self.value -= 360
        while self.value < 0:
            self.value += 360

    def copy(self):
        return Angle(self.value)

    def in_units(self, unit):
        if isinstance(unit, Enum):
            if unit == self.Units.Degrees:
                return self.degrees
            elif unit == self.Units.Radians:
                return self.radians
            elif unit == self.Units.Milliradians:
                return self.milliradians
        else:
            print('unit variable is not of type Enum')

    def to_string(self, unit=Units.Degrees, formatting=''):
        if unit == self.Units.Degrees:
            return ('{' + formatting + '} {}').format(self.degrees, str(unit))
        elif unit == self.Units.Radians:
            return ('{' + formatting + '} {}').format(self.radians, str(unit))
        elif unit == self.Units.Milliradians:
            return ('{' + formatting + '} {}').format(self.milliradians, str(unit))
        else:
            print('unit variable not recognized as enum')

    def abs(self):
        return Angle(abs(self.value))

    def sin(self):
        return np.sin(self.radians)

    def cos(self):
        return np.cos(self.radians)

    def tan(self):
        return np.tan(self.radians)

    def to_compass_point(self):
        val = int(round(self.normalized.degrees / 22.5))
        while val > (len(self.direction()) - 1):
            val -= len(self.direction())
        return self.direction()[val]

    def to_compass(self):
        return (Angle(90) - self.normalized).normalized

    def min_normalized_difference(self, a):
        if isinstance(a, Angle):
            t = (self.normalized - a.normalized).normalized
            if t.value > 180:
                t.value = 360 - t.value
            return t

    def __add__(self, other):
        if isinstance(other, Angle):
            return Angle(angle=(self.value + other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Angle(angle=(self.value + other))
        else:
            print('other is not a number or of type Angle!')

    def __sub__(self, other):
        if isinstance(other, Angle):
            return Angle(angle=(self.value - other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Angle(angle=(self.value - other))
        else:
            print('other is not a number or of type Angle!')

    def __neg__(self):
        return Angle(self.value * -1.0)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        else:
            return False

    def __hash__(self):
        return hash(self.value)

    def __rmul__(self, other):
        return self * other

    def __mul__(self, other):
        if isinstance(other, Angle):
            return Angle(angle=(self.value * other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Angle(angle=(self.value * other))
        else:
            print('other is not a number or of type Angle!')

    def __truediv__(self, other):
        output = super().__truediv__(other)
        if output is None:
            if isinstance(other, Angle):
                return Angle(angle=(self.value / other.value))
            elif isinstance(other, float) or isinstance(other, int):
                return Angle(angle=(self.value / other))
            else:
                print('other is not a valid type!')
        else:
            return output

    def __mod__(self, other):
        if isinstance(other, Angle):
            return Angle(angle=(self.value % other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Angle(angle=(self.value % other))
        else:
            print('other is not a valid type!')

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):
        return not (self.__eq__(other))


class Humidity(Measurable):
    class Units(Enum):
        Percentage = 0

        def __str__(self):
            if self.value == 0:
                return '%'

    def __init__(self, humidity=0.0, unit=Units.Percentage):
        super().__init__()
        factor = 1
        if isinstance(unit, str):
            if unit == str(self.Units.Percentage):
                unit = self.Units.Percentage
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')

        if isinstance(humidity, str):
            try:
                humidity = float(humidity)
            except ValueError:
                print('angle variable cannot be parsed!')

        if isinstance(unit, Enum):
            if unit == self.Units.Percentage:
                factor = 1
        else:
            print('unit variable is not an enum or string!')
        self.check(humidity)
        self.value = float(humidity)
        self.units = self.Units.Percentage
        # self.unit_symbols = [str(unit) for unit in self.Units]

    @staticmethod
    def std_humidity():
        return Humidity(humidity=70, unit=Humidity.Units.Percentage)

    @staticmethod
    def symbol_to_enum(string):
        if isinstance(string, str):
            if string == str(Humidity.Units.Percentage):
                return Humidity.Units.Percentage
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')
        else:
            print('string variable is not of type string')

    @staticmethod
    def unit_symbols():
        return [str(unit) for unit in Humidity.Units]

    @staticmethod
    def min(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Humidity) and isinstance(b, Humidity):
                return Humidity(min(a.value, b.value))
            else:
                print('a and b variables are not of type Humidity')
        else:
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Humidity):
                    print('{0} in array is not of type Humidity'.format(index_val))
                    return
            return Humidity(min([x.value for x in array]))

    @staticmethod
    def max(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Humidity) and isinstance(b, Humidity):
                return Humidity(max(a.value, b.value))
            else:
                print('a and b variables are not of type Humidity')
        else:
            if isinstance(array, list):
                for index_val in range(len(array)):
                    if not isinstance(array[index_val], Humidity):
                        print('{0} in array is not of type Angle'.format(index_val))
                        return
                return Humidity(max([x.value for x in array]))
            else:
                print('array variable is not a list')
                return

    @staticmethod
    def mean(array):
        if isinstance(array, list):
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Humidity):
                    print('{0} in array is not of type Humidity'.format(index_val))
                    return
            return Humidity(sum([x.value for x in array]) / len(array))
        else:
            print('array variable is not a list')
            return

    @staticmethod
    def check(humidity):
        if (humidity > 100) or (humidity < 0):
            if humidity > 100:
                humidity = 100
            elif humidity < 0:
                humidity = 0
            # print('Relative humidity ({}) must be between 0-100'.format(humidity))

    @property
    def percentage(self):
        return self.value

    def copy(self):
        return Humidity(self.value)

    def in_units(self, unit):
        if isinstance(unit, Enum):
            if unit == self.Units.Percentage:
                return self.percentage
        else:
            print('unit variable is not of type Enum')

    def to_string(self, unit=Units.Percentage, formatting=''):
        if unit == self.Units.Percentage:
            return ('{' + formatting + '} {}').format(self.percentage, str(unit))
        else:
            print('unit variable not recognized as enum')

    def dew_point(self, temp):
        from ..conversions.Physics import Physics
        if isinstance(temp, Temperature):
            return Physics.dew_point(self, temp)
        else:
            print('temp variable is not of type Temperature')

    def abs(self):
        return Humidity(abs(self.value))

    def __add__(self, other):
        if isinstance(other, Humidity):
            return Humidity(humidity=(self.value + other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Humidity(humidity=(self.value + other))
        else:
            print('other is not a valid type!')

    def __sub__(self, other):
        if isinstance(other, Humidity):
            return Humidity(humidity=(self.value - other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Humidity(humidity=(self.value - other))
        else:
            print('other is not a valid type!')

    def __mul__(self, other):
        if isinstance(other, Humidity):
            return Humidity(humidity=(self.value * other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Humidity(humidity=(self.value * other))
        else:
            print('other is not a valid type!')

    def __neg__(self):
        return Humidity(self.value * -1.0)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        else:
            return False

    def __hash__(self):
        return hash(self.value)

    def __rmul__(self, other):
        return self * other

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):
        return not (self.__eq__(other))

    def __truediv__(self, other):
        output = super().__truediv__(other)
        if output is None:
            if isinstance(other, Humidity):
                return Humidity(humidity=(self.value / other.value))
            elif isinstance(other, float) or isinstance(other, int):
                return Humidity(humidity=(self.value / other))
            else:
                print('other is not a valid type!')
        else:
            return output

    def __mod__(self, other):
        if isinstance(other, Humidity):
            return Humidity(humidity=(self.value % other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Humidity(humidity=(self.value % other))
        else:
            print('other is not a valid type!')


class Length(Measurable):
    class Units(Enum):
        Meters = 0
        Kilometers = 1
        NauticalMiles = 2
        StatuteMiles = 3
        Feet = 4

        def __str__(self):
            if self.value == 0:
                return 'm'
            elif self.value == 1:
                return 'km'
            elif self.value == 2:
                return 'nm'
            elif self.value == 3:
                return 'mi'
            elif self.value == 4:
                return 'ft'

    def __init__(self, length=0.0, unit=Units.Meters):
        super().__init__()
        factor = 1
        if isinstance(unit, str):
            if unit == str(self.Units.Meters):
                unit = self.Units.Meters
            elif unit == str(self.Units.Kilometers):
                unit = self.Units.Kilometers
            elif unit == str(self.Units.NauticalMiles):
                unit = self.Units.NauticalMiles
            elif unit == str(self.Units.StatuteMiles):
                unit = self.Units.StatuteMiles
            elif unit == str(self.Units.Feet):
                unit = self.Units.Feet
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')

        if isinstance(unit, Enum):
            if unit == self.Units.Meters:
                factor = 1
            elif unit == self.Units.Kilometers:
                factor = 1000.0
            elif unit == self.Units.NauticalMiles:
                factor = self.meters_per_nm()
            elif unit == self.Units.StatuteMiles:
                factor = self.feet_per_mile() * self.meters_per_foot()
            elif unit == self.Units.Feet:
                factor = self.meters_per_foot()
        else:
            print('unit variable is not an enum or string!')

        if isinstance(length, str):
            try:
                length = float(length)
            except ValueError:
                print('length variable cannot be parsed!')
                length = 0.0
        self.value = float(length * factor)
        self.units = self.Units.Meters
        # self.unit_symbols = [str(unit) for unit in self.Units]

    @staticmethod
    def average_listener_height():
        return Length(length=1.2, unit=Length.Units.Meters)

    @staticmethod
    def reference_source_radius():
        return Length(length=100, unit=Length.Units.Feet)

    @staticmethod
    def meters_per_nm():
        return 1852

    @staticmethod
    def unit_symbols():
        return [str(unit) for unit in Length.Units]

    @staticmethod
    def meters_per_foot():
        return 0.3048

    @staticmethod
    def feet_per_mile():
        return 5280

    @staticmethod
    def human_height():
        return Length(length=1.2, unit=Length.Units.Meters)

    @staticmethod
    def maximum_propagation_distance_in_pointcloud():
        return Length(length=1200, unit=Length.Units.Meters)

    @staticmethod
    def reference_sphere_radius():
        return Length(length=100, unit=Length.Units.Feet)

    @staticmethod
    def to_array_of_meters(array) -> list:
        if isinstance(array, list):
            output = []
            for index_val in range(len(array)):
                if isinstance(array[index_val], Length):
                    val = array[index_val].meters
                    output.append(val)
                else:
                    print('index {0} in array is not of type Length'.format(index_val))
            return output
        else:
            print('array variable is not a list')
            return []

    @staticmethod
    def min(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Length) and isinstance(b, Length):
                return Length(min(a.value, b.value))
            else:
                print('a and b variables are not of type Length')
        else:
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Length):
                    print('{0} in array is not of type Length'.format(index_val))
                    return
            return Length(min([x.value for x in array]))

    @staticmethod
    def max(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Length) and isinstance(b, Length):
                return Length(max(a.value, b.value))
            else:
                print('a and b variables are not of type Length')
        else:
            if isinstance(array, list):
                for index_val in range(len(array)):
                    if not isinstance(array[index_val], Length):
                        print('{0} in array is not of type Length'.format(index_val))
                        return
                return Length(max([x.value for x in array]))
            else:
                print('array variable is not a list')
                return

    @staticmethod
    def mean(array):
        if isinstance(array, list):
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Length):
                    print('{0} in array is not of type Length'.format(index_val))
                    return
            output = [x.value for x in array]
            return Length(sum(output) / len(output))
        else:
            print('array variable is not a list')
            return

    @staticmethod
    def symbol_to_enum(string):
        if isinstance(string, str):
            if string == str(Length.Units.Meters):
                return Length.Units.Meters
            elif string == str(Length.Units.Kilometers):
                return Length.Units.Kilometers
            elif string == str(Length.Units.NauticalMiles):
                return Length.Units.NauticalMiles
            elif string == str(Length.Units.StatuteMiles):
                return Length.Units.StatuteMiles
            elif string == str(Length.Units.Feet):
                return Length.Units.Feet
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')
        else:
            print('string variable is not of type string')

    @property
    def feet(self):
        return self.value / Length.meters_per_foot()

    @property
    def meters(self):
        # print('value: {}'.format(self.value))
        return self.value

    @property
    def kilometers(self):
        return self.value / 1000.0

    @property
    def nautical_miles(self):
        return self.value / Length.meters_per_nm()

    @property
    def statute_miles(self):
        return self.value / (Length.feet_per_mile() * Length.meters_per_foot())

    def add(self, addition, unit=Units.Meters):
        if isinstance(addition, int) or isinstance(addition, float):
            if isinstance(unit, Enum):
                l = Length(addition, unit)
                self.value += l.value
            else:
                print('unit variable is not an enum!')
        else:
            print('addition variable is not a number!')

    def to_string(self, unit=Units.Meters, formatting=''):
        if unit == self.Units.Meters:
            return ('{' + formatting + '} {}').format(self.meters, str(unit))
        elif unit == self.Units.Kilometers:
            return ('{' + formatting + '} {}').format(self.kilometers, str(unit))
        elif unit == self.Units.NauticalMiles:
            return ('{' + formatting + '} {}').format(self.nautical_miles, str(unit))
        elif unit == self.Units.StatuteMiles:
            return ('{' + formatting + '} {}').format(self.statute_miles, str(unit))
        elif unit == self.Units.Feet:
            return ('{' + formatting + '} {}').format(self.feet, str(unit))
        else:
            print('unit variable not recognized as enum')

    def abs(self):
        return Length(abs(self.value))

    def copy(self):
        return Length(length=self.value)

    def in_units(self, unit):
        if isinstance(unit, Enum):
            if unit == self.Units.Feet:
                return self.feet
            elif unit == self.Units.Meters:
                return self.meters
            elif unit == self.Units.Kilometers:
                return self.kilometers
            elif unit == self.Units.NauticalMiles:
                return self.nautical_miles
            elif unit == self.Units.StatuteMiles:
                return self.statute_miles
        else:
            print('unit variable is not of type Enum')

    def __add__(self, other):
        if isinstance(other, Length):
            return Length(length=(self.value + other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Length(length=(self.value + other))
        else:
            print('other is not a number or of type Length!')

    def __neg__(self):
        return Length(self.value * -1.0)

    def __sub__(self, other):
        if isinstance(other, Length):
            return Length(length=(self.value - other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Length(length=(self.value - other))
        else:
            print('other is not a number or of type Length!')

    def __mul__(self, other):
        if isinstance(other, Length):
            return Length(length=(self.value * other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Length(length=(self.value * other))
        else:
            print('other is not a number or of type Length!')

    def __rmul__(self, other):
        return self * other

    def __mod__(self, other):
        if isinstance(other, Length):
            return Length(length=(self.value % other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Length(length=(self.value % other))
        else:
            print('other is not a valid type!')

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):
        return not (self.__eq__(other))

    def __truediv__(self, other):
        import datetime

        output = super().__truediv__(other)
        if output is None:
            if isinstance(other, Length):
                return self.value / other.value
            elif isinstance(other, float) or isinstance(other, int):
                return Length(length=(self.value / other))
            elif isinstance(other, Speed):
                seconds_val = self.meters / other.meters_per_second
                return datetime.timedelta(seconds=seconds_val)
            elif isinstance(other, datetime.timedelta):
                return Speed(self.meters / other.total_seconds())
            else:
                print('other is not a valid type!')
        else:
            return output

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        else:
            return False

    def __hash__(self):
        return hash(self.value)


class Pressure(Measurable):
    class Units(Enum):
        Pascal = 0
        Kilopascals = 1
        InchesMercury = 2
        Millibar = 3
        Bar = 4
        MillimeterMercury = 5

        def __str__(self):
            if self.value == 0:
                return 'Pa'
            elif self.value == 1:
                return 'kPa'
            elif self.value == 2:
                return 'inHg'
            elif self.value == 3:
                return 'mbar'
            elif self.value == 4:
                return 'bar'
            elif self.value == 5:
                return 'mmHg'

    def __init__(self, pressure=0.0, unit=Units.Kilopascals):
        super().__init__()
        factor = 1
        if isinstance(unit, str):
            if unit == str(self.Units.InchesMercury):
                unit = self.Units.InchesMercury
            elif unit == str(self.Units.Kilopascals):
                unit = self.Units.Kilopascals
            elif unit == str(self.Units.Millibar):
                unit = self.Units.Millibar
            elif unit == str(self.Units.Pascal):
                unit = self.Units.Pascal
            elif unit == str(self.Units.Bar):
                unit = self.Units.Bar
            elif unit == str(self.Units.MillimeterMercury):
                unit = self.Units.MillimeterMercury
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')

        if isinstance(unit, Enum):
            if unit == self.Units.InchesMercury:
                factor = 1 / self.inhg_per_kpa()
            elif unit == self.Units.Kilopascals:
                factor = 1
            elif unit == self.Units.Millibar:
                factor = 1 / self.millibar_per_kpa()
            elif unit == self.Units.Pascal:
                factor = 1 / self.pa_per_kpa()
            elif unit == self.Units.Bar:
                factor = 1 / self.bar_per_kpa()
            elif unit == self.Units.MillimeterMercury:
                factor = 1 / self.mmhg_per_kpa()
        else:
            print('unit variable is not an enum or string!')

        if isinstance(pressure, str):
            try:
                pressure = float(pressure)
            except ValueError:
                print('pressure variable cannot be parsed!')
                pressure = 0.0
        self.value = float(pressure * factor)
        self.units = self.Units.Kilopascals
        # self.unit_symbols = [str(unit) for unit in self.Units]

    @staticmethod
    def mmhg_per_kpa():
        return 7.500615613

    @staticmethod
    def inhg_per_kpa():
        return 760 / (101.325 * 25.4)

    @staticmethod
    def pa_per_kpa():
        return 1000.0

    @staticmethod
    def bar_per_kpa():
        return 0.01

    @staticmethod
    def millibar_per_kpa():
        return 10

    @staticmethod
    def unit_symbols():
        return [str(unit) for unit in Pressure.Units]

    @staticmethod
    def ref_pressure():
        return Pressure(101.325, Pressure.Units.Kilopascals)

    @staticmethod
    def std_pressure():
        return Pressure(29.92, Pressure.Units.InchesMercury)

    @staticmethod
    def symbol_to_enum(string):
        if isinstance(string, str):
            if string == str(Pressure.Units.Kilopascals):
                return Pressure.Units.Kilopascals
            elif string == str(Pressure.Units.MillimeterMercury):
                return Pressure.Units.MillimeterMercury
            elif string == str(Pressure.Units.Bar):
                return Pressure.Units.Bar
            elif string == str(Pressure.Units.Pascal):
                return Pressure.Units.Pascal
            elif string == str(Pressure.Units.Millibar):
                return Pressure.Units.Millibar
            elif string == str(Pressure.Units.InchesMercury):
                return Pressure.Units.InchesMercury
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')
        else:
            print('string variable is not of type string')

    @staticmethod
    def min(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Pressure) and isinstance(b, Pressure):
                return Pressure(min(a.value, b.value))
            else:
                print('a and b variables are not of type Pressure')
        else:
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Pressure):
                    print('{0} in array is not of type Pressure'.format(index_val))
                    return
            return Pressure(min([x.value for x in array]))

    @staticmethod
    def max(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Pressure) and isinstance(b, Pressure):
                return Pressure(max(a.value, b.value))
            else:
                print('a and b variables are not of type Pressure')
        else:
            if isinstance(array, list):
                for index_val in range(len(array)):
                    if not isinstance(array[index_val], Pressure):
                        print('{0} in array is not of type Pressure'.format(index_val))
                        return
                return Pressure(max([x.value for x in array]))
            else:
                print('array variable is not a list')
                return

    @staticmethod
    def mean(array):
        if isinstance(array, list):
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Pressure):
                    print('{0} in array is not of type Pressure'.format(index_val))
                    return
            return Pressure(sum([x.value for x in array]) / len(array))
        else:
            print('array variable is not a list')
            return

    @property
    def millibar(self):
        return self.value * self.millibar_per_kpa()

    @property
    def pascal(self):
        return self.value * self.pa_per_kpa()

    @property
    def kilopascal(self):
        return self.value

    @property
    def inches_mercury(self):
        return self.value * self.inhg_per_kpa()

    @property
    def millimeter_mercury(self):
        return self.value * self.mmhg_per_kpa()

    @property
    def bar(self):
        return self.value * self.bar_per_kpa()

    def copy(self):
        return Pressure(self.value)

    def in_units(self, unit):
        if isinstance(unit, Enum):
            if unit == self.Units.InchesMercury:
                return self.inches_mercury
            elif unit == self.Units.Millibar:
                return self.millibar
            elif unit == self.Units.Pascal:
                return self.pascal
            elif unit == self.Units.Bar:
                return self.bar
            elif unit == self.Units.MillimeterMercury:
                return self.millimeter_mercury
            elif unit == self.Units.Kilopascals:
                return self.kilopascal
        else:
            print('unit variable is not of type Enum')

    def to_string(self, unit=Units.Kilopascals, formatting=''):
        print(self.value)
        if unit == self.Units.Kilopascals:
            return ('{' + formatting + '} {}').format(self.kilopascal, str(unit))
        elif unit == self.Units.MillimeterMercury:
            return ('{' + formatting + '} {}').format(self.millimeter_mercury, str(unit))
        elif unit == self.Units.Bar:
            return ('{' + formatting + '} {}').format(self.bar, str(unit))
        elif unit == self.Units.Pascal:
            return ('{' + formatting + '} {}').format(self.pascal, str(unit))
        elif unit == self.Units.Millibar:
            return ('{' + formatting + '} {}').format(self.millibar, str(unit))
        elif unit == self.Units.InchesMercury:
            return ('{' + formatting + '} {}').format(self.inches_mercury, str(unit))
        else:
            print('unit variable not recognized as enum')

    def abs(self):
        return Pressure(abs(self.value))

    def __add__(self, other):
        if isinstance(other, Pressure):
            return Pressure(pressure=(self.value + other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Pressure(pressure=(self.value + other))
        else:
            print('other is not a valid type!')

    def __neg__(self):
        return Pressure(self.value * -1.0)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        else:
            return False

    def __hash__(self):
        return hash(self.value)

    def __rmul__(self, other):
        return self * other

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):
        return not (self.__eq__(other))

    def __sub__(self, other):
        if isinstance(other, Pressure):
            return Pressure(pressure=(self.value - other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Pressure(pressure=(self.value - other))
        else:
            print('other is not a valid type!')

    def __mul__(self, other):
        if isinstance(other, Pressure):
            return Pressure(pressure=(self.value * other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Pressure(pressure=(self.value * other))
        else:
            print('other is not a valid type!')

    def __truediv__(self, other):
        output = super().__truediv__(other)
        if output is None:
            if isinstance(other, Pressure):
                return Pressure(pressure=(self.value / other.value))
            elif isinstance(other, float) or isinstance(other, int):
                return Pressure(pressure=(self.value / other))
            else:
                print('other is not a valid type!')
        else:
            return output

    def __mod__(self, other):
        if isinstance(other, Pressure):
            return Pressure(pressure=(self.value % other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Pressure(pressure=(self.value % other))
        else:
            print('other is not a valid type!')


class Speed(Measurable):
    class Units(Enum):
        Knots = 0
        KilometersPerHour = 1
        MetersPerHour = 2
        MetersPerSecond = 3
        MilesPerHour = 4
        KilometersPerSecond = 5

        def __str__(self):
            if self.value == 0:
                return 'kts'
            elif self.value == 1:
                return 'kph'
            elif self.value == 2:
                return 'm/h'
            elif self.value == 3:
                return 'm/s'
            elif self.value == 4:
                return 'mi/h'
            elif self.value == 5:
                return 'kps'

    def __init__(self, speed=0.0, unit=Units.MetersPerSecond):
        super().__init__()
        factor = 1
        if isinstance(unit, str):
            if unit == str(self.Units.Knots):
                unit = self.Units.Knots
            elif unit == str(self.Units.KilometersPerHour):
                unit = self.Units.KilometersPerHour
            elif unit == str(self.Units.MetersPerHour):
                unit = self.Units.MetersPerHour
            elif unit == str(self.Units.MetersPerSecond):
                unit = self.Units.MetersPerSecond
            elif unit == str(self.Units.MilesPerHour):
                unit = self.Units.MilesPerHour
            elif unit == str(self.Units.KilometersPerSecond):
                unit = self.Units.KilometersPerSecond
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')

        if isinstance(speed, str):
            try:
                speed = float(speed)
            except ValueError:
                print('speed variable cannot be parsed!')
                speed = 0.0

        if isinstance(unit, Enum):
            if unit == self.Units.KilometersPerHour:
                factor = self.mps_per_kmph()
            elif unit == self.Units.Knots:
                factor = self.mps_per_knot()
            elif unit == self.Units.MetersPerHour:
                factor = self.mps_per_meph()
            elif unit == self.Units.MetersPerSecond:
                factor = 1
            elif unit == self.Units.MilesPerHour:
                factor = self.mps_per_miph()
            elif unit == self.Units.KilometersPerSecond:
                factor = 1000
        else:
            print('unit variable is not an enum or string!')

        self.value = float(speed * factor)
        self.units = self.Units.MetersPerSecond
        # self.unit_symbols = [str(unit) for unit in self.Units]

    @staticmethod
    def ref_speed_of_sound():
        return Speed(343.199, Speed.Units.MetersPerSecond)

    @staticmethod
    def mps_per_kmph():
        return 1.0 / 3.6

    @staticmethod
    def mps_per_knot():
        return 1.0 / 1.9438445

    @staticmethod
    def mps_per_miph():
        return 1.0 / 2.2369362921

    @staticmethod
    def mps_per_meph():
        return 1.0 / 3600.0

    @staticmethod
    def unit_symbols():
        return [str(unit) for unit in Speed.Units]

    @staticmethod
    def symbol_to_enum(string):
        if isinstance(string, str):
            if string == str(Speed.Units.Knots):
                return Speed.Units.Knots
            elif string == str(Speed.Units.KilometersPerHour):
                return Speed.Units.KilometersPerHour
            elif string == str(Speed.Units.MetersPerHour):
                return Speed.Units.MetersPerHour
            elif string == str(Speed.Units.MilesPerHour):
                return Speed.Units.MilesPerHour
            elif string == str(Speed.Units.KilometersPerSecond):
                return Speed.Units.KilometersPerSecond
            elif string == str(Speed.Units.MetersPerSecond):
                return Speed.Units.MetersPerSecond
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')
        else:
            print('string variable is not of type string')

    @staticmethod
    def adiabatic_speed_of_sound(temp):
        if isinstance(temp, Temperature):
            return Speed(Speed.ref_speed_of_sound().meters_per_second * np.sqrt(
                temp.kelvin / Temperature.ref_temperature().kelvin), Speed.Units.MetersPerSecond)
        else:
            print('temperature variable is not of type Temperature')

    @staticmethod
    def turbulence_structure_factor(temp, wind_speed):
        if isinstance(temp, Temperature) and isinstance(wind_speed, Speed):
            top = 4.0 * (
                        np.pow(np.fabs(wind_speed.meters_per_second) * 0.514, 4.0 / 3.0) / np.pow(0.1, 2.0 / 3.0))
            temp_frac = temp.value / Temperature.ref_temperature().value
            bot = np.pow((Speed.ref_speed_of_sound() / np.sqrt(temp_frac)).meters_per_second, 2.0)
            return top / bot
        else:
            if not isinstance(temp, Temperature):
                print('temp is not of type Temperature')
            if not isinstance(wind_speed, Speed):
                print('temp is not of type Speed')

    @staticmethod
    def min(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Speed) and isinstance(b, Speed):
                return Speed(min(a.value, b.value))
            else:
                print('a and b variables are not of type Speed')
        else:
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Speed):
                    print('{0} in array is not of type Speed'.format(index_val))
                    return
            return Speed(min([x.value for x in array]))

    @staticmethod
    def max(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Speed) and isinstance(b, Speed):
                return Speed(max(a.value, b.value))
            else:
                print('a and b variables are not of type Speed')
        else:
            if isinstance(array, list):
                for index_val in range(len(array)):
                    if not isinstance(array[index_val], Speed):
                        print('{0} in array is not of type Speed'.format(index_val))
                        return
                return Speed(max([x.value for x in array]))
            else:
                print('array variable is not a list')
                return

    @staticmethod
    def mean(array):
        if isinstance(array, list):
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Speed):
                    print('{0} in array is not of type Speed'.format(index_val))
                    return
            return Speed(sum([x.value for x in array]) / len(array))
        else:
            print('array variable is not a list')
            return

    @property
    def kilometers_per_hour(self):
        return self.value / self.mps_per_kmph()

    @property
    def knots(self):
        return self.value / self.mps_per_knot()

    @property
    def meters_per_hour(self):
        return self.value / self.mps_per_meph()

    @property
    def meters_per_second(self):
        return self.value

    @property
    def miles_per_hour(self):
        return self.value / self.mps_per_miph()

    @property
    def kilometers_per_second(self):
        return self.value / 1000.0

    def abs(self):
        return Speed(abs(self.value))

    def copy(self):
        return Speed(self.value)

    def in_units(self, unit):
        if isinstance(unit, Enum):
            if unit == self.Units.Knots:
                return self.knots
            elif unit == self.Units.KilometersPerHour:
                return self.kilometers_per_hour
            elif unit == self.Units.MetersPerHour:
                return self.meters_per_hour
            elif unit == self.Units.MilesPerHour:
                return self.miles_per_hour
            elif unit == self.Units.KilometersPerSecond:
                return self.kilometers_per_second
            elif unit == self.Units.MetersPerSecond:
                return self.meters_per_second
        else:
            print('unit variable is not of type Enum')

    def to_string(self, unit=Units.MetersPerSecond, formatting=''):
        if unit == self.Units.MetersPerSecond:
            return ('{' + formatting + '} {}').format(self.meters_per_second, str(unit))
        elif unit == self.Units.Knots:
            return ('{' + formatting + '} {}').format(self.knots, str(unit))
        elif unit == self.Units.KilometersPerHour:
            return ('{' + formatting + '} {}').format(self.kilometers_per_hour, str(unit))
        elif unit == self.Units.MetersPerHour:
            return ('{' + formatting + '} {}').format(self.meters_per_hour, str(unit))
        elif unit == self.Units.MilesPerHour:
            return ('{' + formatting + '} {}').format(self.miles_per_hour, str(unit))
        elif unit == self.Units.KilometersPerSecond:
            return ('{' + formatting + '} {}').format(self.kilometers_per_second, str(unit))
        else:
            print('unit variable not recognized as enum')

    def add(self, x, unit):
        factor = 1
        if isinstance(unit, Enum):
            if unit == self.Units.KilometersPerHour:
                factor = self.mps_per_kmph()
            elif unit == self.Units.Knots:
                factor = self.mps_per_knot()
            elif unit == self.Units.MetersPerHour:
                factor = self.mps_per_meph()
            elif unit == self.Units.MetersPerSecond:
                factor = 1
            elif unit == self.Units.MilesPerHour:
                factor = self.mps_per_miph()
            elif unit == self.Units.KilometersPerSecond:
                factor = 1000
        else:
            print('unit variable is not an enum!')
        self.value += (x * factor)

    def __add__(self, other):
        if isinstance(other, Speed):
            return Speed(speed=(self.value + other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Speed(speed=(self.value + other))
        else:
            print('other is not a valid type!')

    def __sub__(self, other):
        if isinstance(other, Speed):
            return Speed(speed=(self.value - other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Speed(speed=(self.value - other))
        else:
            print('other is not a valid type!')

    def __mul__(self, other):
        if isinstance(other, Speed):
            return Speed(speed=(self.value * other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Speed(speed=(self.value * other))
        else:
            print('other is not a valid type!')

    def __truediv__(self, other):
        output = super().__truediv__(other)
        if output is None:
            if isinstance(other, float) or isinstance(other, int):
                return Speed(speed=(self.value / other))
            else:
                print('other is not a valid type!')
                raise Exception
        else:
            return output

    def __neg__(self):
        return Speed(self.value * -1.0)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        else:
            return False

    def __hash__(self):
        return hash(self.value)

    def __rmul__(self, other):
        return self * other

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):
        return not (self.__eq__(other))

    def __mod__(self, other):
        if isinstance(other, Speed):
            return Speed(speed=(self.value % other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Speed(speed=(self.value % other))
        else:
            print('other is not a valid type!')


class Temperature(Measurable):
    class Units(Enum):
        Rankine = 0
        Kelvin = 1
        Fahrenheit = 2
        Celsius = 3

        def __str__(self):
            if self.value == 0:
                return 'R'
            elif self.value == 1:
                return 'K'
            elif self.value == 2:
                return 'F'
            elif self.value == 3:
                return 'C'

    def __init__(self, temp=0.0, unit=Units.Kelvin):
        super().__init__()
        if isinstance(unit, str):
            if unit == str(self.Units.Kelvin):
                unit = self.Units.Kelvin
            elif unit == str(self.Units.Celsius):
                unit = self.Units.Celsius
            elif unit == str(self.Units.Fahrenheit):
                unit = self.Units.Fahrenheit
            elif unit == str(self.Units.Rankine):
                unit = self.Units.Rankine
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except ValueError:
                print('temperature variable cannot be parsed!')
                temp = 0.0
        if isinstance(unit, Enum):
            if unit == self.Units.Rankine:
                temp = self.r_to_k(temp)
            elif unit == self.Units.Fahrenheit:
                temp = self.f_to_k(temp)
            elif unit == self.Units.Celsius:
                temp = self.c_to_k(temp)
            elif unit == self.Units.Kelvin:
                temp = temp
        else:
            print('unit variable is not an enum or string!')

        self.value = float(temp)
        self.units = self.Units.Kelvin
        # self.unit_symbols = [str(unit) for unit in self.Units]

    @staticmethod
    def ref_temperature():
        return Temperature(293.15, Temperature.Units.Kelvin)

    @staticmethod
    def std_temperature():
        return Temperature(288.15, Temperature.Units.Kelvin)

    @staticmethod
    def unit_symbols():
        return [str(unit) for unit in Temperature.Units]

    @staticmethod
    def tempature0c():
        return Temperature(273.15, Temperature.Units.Kelvin)

    @staticmethod
    def temperature01k():
        return Temperature(273.16, Temperature.Units.Kelvin)

    @staticmethod
    def k_to_r(x):
        return x * (9.0 / 5.0)

    @staticmethod
    def r_to_k(x):
        return x * (5.0 / 9.0)

    @staticmethod
    def k_to_c(x):
        return x - Temperature.tempature0c().kelvin

    @staticmethod
    def c_to_f(x):
        return ((9.0 / 5.0) * x) + 32

    @staticmethod
    def c_to_k(x):
        return x + Temperature.tempature0c().kelvin

    @staticmethod
    def f_to_c(x):
        return (x - 32) * (5.0 / 9.0)

    @staticmethod
    def k_to_f(x):
        return Temperature.c_to_f(x - Temperature.tempature0c().kelvin)

    @staticmethod
    def f_to_k(x):
        return Temperature.f_to_c(x) + Temperature.tempature0c().kelvin

    @staticmethod
    def symbol_to_enum(string):
        if isinstance(string, str):
            if string == str(Temperature.Units.Kelvin):
                return Temperature.Units.Kelvin
            elif string == str(Temperature.Units.Rankine):
                return Temperature.Units.Rankine
            elif string == str(Temperature.Units.Celsius):
                return Temperature.Units.Celsius
            elif string == str(Temperature.Units.Fahrenheit):
                return Temperature.Units.Fahrenheit
            else:
                raise InvalidUnitOfMeasureException('Invalid unit of measure')
        else:
            print('string variable is not of type string')

    @staticmethod
    def min(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Temperature) and isinstance(b, Temperature):
                return Temperature(min(a.value, b.value))
            else:
                print('a and b variables are not of type Temperature')
        else:
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Temperature):
                    print('{0} in array is not of type Temperature'.format(index_val))
                    return
            return Temperature(min([x.value for x in array]))

    @staticmethod
    def max(a=None, b=None, array=None):
        if array is None:
            if isinstance(a, Temperature) and isinstance(b, Temperature):
                return Temperature(max(a.value, b.value))
            else:
                print('a and b variables are not of type Temperature')
        else:
            if isinstance(array, list):
                for index_val in range(len(array)):
                    if not isinstance(array[index_val], Temperature):
                        print('{0} in array is not of type Temperature'.format(index_val))
                        return
                return Temperature(max([x.value for x in array]))
            else:
                print('array variable is not a list')
                return

    @staticmethod
    def mean(array):
        if isinstance(array, list):
            for index_val in range(len(array)):
                if not isinstance(array[index_val], Temperature):
                    print('{0} in array is not of type Temperature'.format(index_val))
                    return
            return Temperature(sum([x.value for x in array]) / len(array))
        else:
            print('array variable is not a list')
            return

    @property
    def rankine(self):
        return self.k_to_r(self.value)

    @property
    def kelvin(self):
        return self.value

    @property
    def fahrenheit(self):
        return self.k_to_f(self.value)

    @property
    def celsius(self):
        return self.k_to_c(self.value)

    def copy(self):
        return Temperature(temp=self.value)

    def in_units(self, unit):
        if isinstance(unit, Enum):
            if unit == self.Units.Kelvin:
                return self.kelvin
            elif unit == self.Units.Rankine:
                return self.rankine
            elif unit == self.Units.Fahrenheit:
                return self.fahrenheit
            elif unit == self.Units.Celsius:
                return self.celsius
        else:
            print('unit variable is not of type Enum')

    def to_string(self, unit=Units.Kelvin, formatting=''):
        if unit == self.Units.Kelvin:
            return ('{' + formatting + '}°{}').format(self.kelvin, str(unit))
        elif unit == self.Units.Fahrenheit:
            return ('{' + formatting + '}°{}').format(self.fahrenheit, str(unit))
        elif unit == self.Units.Celsius:
            return ('{' + formatting + '}°{}').format(self.celsius, str(unit))
        elif unit == self.Units.Rankine:
            return ('{' + formatting + '}°{}').format(self.rankine, str(unit))
        else:
            print('unit variable not recognized as enum')

    def abs(self):
        return Temperature(abs(self.value))

    def __neg__(self):
        return Temperature(self.value * -1.0)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        else:
            return False

    def __hash__(self):
        return hash(self.value)

    def __rmul__(self, other) :
        return self * other

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):
        return not (self.__eq__(other))

    def __add__(self, other):
        if isinstance(other, Temperature):
            return Temperature(temp=(self.value + other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Temperature(temp=(self.value + other))
        else:
            print('other is not a valid type!')
            raise Exception

    def __sub__(self, other):
        if isinstance(other, Temperature):
            return Temperature(temp=(self.value - other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Temperature(temp=(self.value - other))
        else:
            print('other is not a valid type!')
            raise Exception

    def __mul__(self, other):
        if isinstance(other, Temperature):
            return Temperature(temp=(self.value * other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Temperature(temp=(self.value * other))
        else:
            print('other is not a valid type!')
            raise Exception

    def __truediv__(self, other):
        output = super().__truediv__(other)
        if output is None:
            if isinstance(other, Temperature):
                return Temperature(temp=(self.value / other.value))
            elif isinstance(other, float) or isinstance(other, int):
                return Temperature(temp=(self.value / other))
            else:
                print('other is not a valid type!')
                raise Exception
        else:
            return output

    def __mod__(self, other):
        if isinstance(other, Temperature):
            return Temperature(temp=(self.value % other.value))
        elif isinstance(other, float) or isinstance(other, int):
            return Temperature(temp=(self.value % other))
        else:
            print('other is not a valid type!')


