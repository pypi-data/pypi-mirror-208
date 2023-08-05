import datetime


class GPSTime:
    @staticmethod
    def standard_utc(gps_time):
        if isinstance(gps_time, datetime.datetime) or isinstance(gps_time, datetime.date):
            return gps_time + datetime.timedelta(seconds=GPSTime.standard_gps_correction(gps_time))
        else:
            print('gps_time parameter is not of type datetime or date')

    @staticmethod
    def standard_gps_correction(gps_time):
        if isinstance(gps_time, datetime.datetime) or isinstance(gps_time, datetime.date):
            if gps_time < datetime.datetime(1999, 1, 1, 0, 0, 13):
                return -12
            if gps_time < datetime.datetime(2006, 1, 1, 0, 0, 14):
                return -13
            if gps_time < datetime.datetime(2009, 1, 1):
                return -14
            if gps_time < datetime.datetime(2012, 7, 1):
                return -15
            if gps_time < datetime.datetime(2015, 7, 1):
                return -16
            if gps_time < datetime.datetime(2017, 1, 1):
                return -17
            return -18
        else:
            raise ValueError('gps_time parameter is not of type datetime or date')
