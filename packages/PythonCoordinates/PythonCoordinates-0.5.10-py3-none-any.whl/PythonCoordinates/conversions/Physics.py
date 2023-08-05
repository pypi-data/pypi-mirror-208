import math
from ..measurables.physical_quantities import Temperature, Humidity, Pressure, InvalidUnitOfMeasureException


class Physics:
    @staticmethod
    def rel_humidity(dew_point, ambient):

        if isinstance(dew_point, Temperature) and isinstance(ambient, Temperature):
            eambient = 6.11 * math.pow(10, 7.5 * ambient.celsius / (237.7 + ambient.celsius))
            edew_point = 6.11 * math.pow(10, 7.5 * dew_point.celsius / (237.7 + dew_point.celsius))
            return Humidity(100.0 * edew_point / eambient)
        else:
            print('dew_point and ambient parameters are not of type Temperature')

    @staticmethod
    def dew_point(humidity, ambient):
        if isinstance(humidity, Humidity) and isinstance(ambient, Temperature):
            log1 = (math.log(humidity.percentage / 100) + ((17.625 * ambient.celsius) / (243.04 + ambient.celsius)))
            den = (17.625 - math.log(humidity.percentage / 100) - ((17.625 * ambient.celsius) / (
                    243.04 + ambient.celsius)))
            dew_point_temperature_value = 243.03 * log1 / den
            return Temperature(dew_point_temperature_value, Temperature.Units.Celsius)
        else:
            if not isinstance(humidity, Humidity):
                print('humidity parameter is not of type Humidity')
            if not isinstance(ambient, Temperature):
                print('ambient paramter is not of type Temperature')

    @staticmethod
    def molar_concentration_water_vapor(pressure, humidity, temperature, s=None):
        if isinstance(pressure, Pressure) and isinstance(humidity, Humidity) and isinstance(temperature, Temperature):
            if s is None:
                return Physics.molar_concentration_water_vapor(
                    pressure, humidity, temperature, Physics.build_psat_ratio(temperature))
            else:
                if isinstance(s, float) or isinstance(s, int):
                    return (Pressure.ref_pressure() / pressure) * humidity.percentage * s
                else:
                    raise InvalidUnitOfMeasureException("s is Not of the type Temperature")
        else:
            if not isinstance(pressure, Pressure):
                InvalidUnitOfMeasureException('pressure parameter is not of type Pressure')
            if not isinstance(humidity, Humidity):
                InvalidUnitOfMeasureException('humidity parameter is not of type Humidity')
            if not isinstance(temperature, Temperature):
                InvalidUnitOfMeasureException('temperature parameter is not of type Temperature')

    @staticmethod
    def build_psat_ratio(temperature) -> float:
        if isinstance(temperature, Temperature):
            t_ratio = temperature / Temperature.temperature01k()
            return_ratio = 10.79586 * (1 - 1 / t_ratio)
            return_ratio += -5.02808 * math.log10(t_ratio)
            return_ratio += 0.000150474 * (1 - math.pow(10.0, -8.29692 * (t_ratio - 1)))
            return_ratio += -0.00042873 * (1 - math.pow(10.0, -4.76955 * (1 / t_ratio - 1)))
            return_ratio += -2.2195983
            return math.pow(10.0, return_ratio)
        else:
            raise InvalidUnitOfMeasureException('temperature parameter is not of type Temperature')

    @staticmethod
    def build_psat_ratio_old(temperature) -> float:
        if isinstance(temperature, Temperature):
            c = -6.8346 * math.pow(Temperature.temperature01k() / temperature, 1.261) + 4.6151
            return math.pow(10.0, c)
        else:
            raise InvalidUnitOfMeasureException('temperature paramter is not of type Temperature')
