# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
"""
Python port of JS library SunCalc.
Origin: https://github.com/mourner/suncalc
"""

import math
from datetime import datetime


class SunCalc:
    """
    Based on http://aa.quae.nl/en/reken/zonpositie.html formulas.
    """

    RAD: float = math.pi / 180
    DAY_SEC: int = 60 * 60 * 24
    DAY_MS: int = 1000 * DAY_SEC
    J1970: int = 2440588
    J2000: int = 2451545

    # fmt: off
    _times: list[tuple[float, str, str]] = [
        (-0.833, 'sunrise',       'sunset'      ),
        (  -0.3, 'sunriseEnd',    'sunsetStart' ),
        (    -6, 'dawn',          'dusk'        ),
        (   -12, 'nauticalDawn',  'nauticalDusk'),
        (   -18, 'nightEnd',      'night'       ),
        (     6, 'goldenHourEnd', 'goldenHour'  ),
    ]
    """ sun times configuration (angle, morning name, evening name) """
    # fmt: on

    def get_position(self, date: datetime, lat: float, long: float) -> tuple[float, float]:
        """
        :return: (azimuth, altitude)
        """
        lw: float = self.RAD * -long
        phi: float = self.RAD * lat
        d: float = self._to_days(date)

        dec, ra = self._sun_coords(d)
        H = self._sidereal_time(d, lw) - ra
        return self._azimuth(H, phi, dec), self._altitude(H, phi, dec)

    def get_times(self, date: datetime, lat: float, long: float) -> dict[str, datetime]:
        """
        calculates sun times for a given date, latitude/longitude, and, optionally,
        the observer height (in meters) relative to the horizon
        """
        lw: float = self.RAD * -long
        phi: float = self.RAD * lat

        dh: float = self._observer_angle(0)
        d: float = self._to_days(date)
        n: int = self._julian_cycle(d, lw)
        ds: float = self._approx_transit(0, lw, n)

        M: float = self._solar_mean_anomaly(ds)
        L: float = self._ecliptic_longitude(M)
        dec: float = self._declination(L, 0)

        j_noon: float = self._solar_transit_j(ds, M, L)

        result: dict[str, datetime] = {
            'zenith': self._from_julian(j_noon),
            'nadir': self._from_julian(j_noon - 0.5),
        }
        for idx, time in enumerate(self._times):
            h0: float = (time[0] + dh) * self.RAD
            j_set: float|None = self._get_set_j(h0, lw, phi, dec, n, M, L)
            if j_set is None:  # acos at hour_angle() can fail
                continue
            j_rise: float = j_noon - (j_set - j_noon)

            result[time[1]] = self._from_julian(j_rise)
            result[time[2]] = self._from_julian(j_set)

        # not part of the original library:
        if 'sunrise' not in result.keys():
            if math.copysign(1, phi) == math.copysign(1, dec):  # polar day
                del result['nadir']
            else:  # polar night
                del result['zenith']
        # ==================================

        return result

    def add_time(self, angle: float, rise_name: str, set_name: str):
        """adds a custom time to the times config"""
        self._times.append((angle, rise_name, set_name))

    # -------------------------------------------------------------------------
    # date/time conversions:

    def _to_days(self, date: datetime) -> float:
        return self._to_julian(date) - self.J2000

    def _to_julian(self, date: datetime) -> float:
        return (date.timestamp() / self.DAY_SEC) - 0.5 + self.J1970

    def _from_julian(self, j: float) -> datetime:
        return datetime.fromtimestamp((j + 0.5 - self.J1970) * self.DAY_SEC)

    # -------------------------------------------------------------------------
    # general calculations for position:

    E: float = RAD * 23.4397
    """ obliquity of the Earth """

    def _right_ascension(self, l: float, b: float) -> float:
        return math.atan2(math.sin(l) * math.cos(self.E) - math.tan(b) * math.sin(self.E), math.cos(l))

    def _declination(self, l: float, b: float) -> float:
        return math.asin(math.sin(b) * math.cos(self.E) + math.cos(b) * math.sin(self.E) * math.sin(l))

    def _azimuth(self, H: float, phi: float, dec: float) -> float:
        return math.atan2(math.sin(H), math.cos(H) * math.sin(phi) - math.tan(dec) * math.cos(phi))

    def _altitude(self, H: float, phi: float, dec: float) -> float:
        return math.asin(math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(H))

    def _sidereal_time(self, d: float, lw: float):
        return self.RAD * (280.16 + 360.9856235 * d) - lw

    def _astro_refraction(self, h: float) -> float:
        if h < 0:  # the following formula works for positive altitudes only.
            h = 0  # if h = -0.08901179 a div/0 would occur.

        # formula 16.4 of "Astronomical Algorithms" 2nd edition by Jean Meeus (Willmann-Bell, Richmond) 1998.
        # 1.02 / tan(h + 10.26 / (h + 5.10)) h in degrees, result in arc minutes -> converted to rad:
        return 0.0002967 / math.tan(h + 0.00312536 / (h + 0.08901179))

    # -------------------------------------------------------------------------
    # general sun calculations:

    def _solar_mean_anomaly(self, d: float) -> float:
        return self.RAD * (357.5291 + 0.98560028 * d)

    def _ecliptic_longitude(self, M: float) -> float:
        # equation of center:
        C: float = self.RAD * (1.9148 * math.sin(M) + 0.02 * math.sin(2 * M) + 0.0003 * math.sin(3 * M))
        # perihelion of the Earth:
        P: float = self.RAD * 102.9372
        return M + C + P + math.pi

    def _sun_coords(self, d: float) -> tuple[float, float]:
        """
        :return: (declination, right_ascension)
        """
        M: float = self._solar_mean_anomaly(d)
        L: float = self._ecliptic_longitude(M)
        return self._declination(L, 0), self._right_ascension(L, 0)

    # -------------------------------------------------------------------------
    # calculations for sun times:

    J0: float = 0.0009

    def _julian_cycle(self, d: float, lw: float) -> int:
        return round(d - self.J0 - lw / (2 * math.pi))

    def _approx_transit(self, Ht: float, lw: float, n: float) -> float:
        return self.J0 + (Ht + lw) / (2 * math.pi) + n

    def _solar_transit_j(self, ds: float, M: float, L: float) -> float:
        return self.J2000 + ds + 0.0053 * math.sin(M) - 0.0069 * math.sin(2 * L)

    def _hour_angle(self, h: float, phi: float, d: float) -> float:
        return math.acos((math.sin(h) - math.sin(phi) * math.sin(d)) / (math.cos(phi) * math.cos(d)))

    def _observer_angle(self, height: float) -> float:
        return -2.076 * math.sqrt(height) / 60

    def _get_set_j(self, h: float, lw: float, phi: float, dec: float, n: float, M: float, L: float) -> float|None:
        """ returns set time for the given sun altitude """
        try:
            w: float = self._hour_angle(h, phi, dec)
        except ValueError:
            return None
        a: float = self._approx_transit(w, lw, n)
        return self._solar_transit_j(a, M, L)
