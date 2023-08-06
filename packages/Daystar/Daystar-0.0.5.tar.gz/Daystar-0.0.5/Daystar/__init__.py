from Solarflare.solarflare import *
import datetime


class Daystar:

  def __init__(self, lat, long):
    self.lat = lat
    self.long = long

  def risetime(self, date=datetime.datetime.now()):
    return sunrise(self.lat, self.long, date)

  def settime(self, date=datetime.datetime.now()):
    return sunset(self.lat, self.long, date)

  def solarnoon(self, date=datetime.datetime.now()):
    return fromJulian(solar_transit(self.long, date))

  def hrangle(self, date=datetime.datetime.now()):
    return hour_angle(self.long, date)

  def coordinates(self, date=datetime.datetime.now()):
    return {"dec": declination(date), "ra": right_ascension(date)}

  def mean(self, date=datetime.datetime.now()):
    return mean_anomaly(date)

  def true(self, date=datetime.datetime.now()):
    return true_anomaly(date)

  def ceq(self, date=datetime.datetime.now()):
    return equation(date)

  def solar_julian(self, date=datetime.datetime.now()):
    return {
      "rise": julian_date(sunrise(self.lat, self.long, date)),
      "set": julian_date(sunset(self.lat, self.long, date))
    }

  def alt(self, date=datetime.datetime.now()):
    return altitude(self.lat, self.long, date)

  def azi(self, date=datetime.datetime.now()):
    return azimuth(self.lat, self.long, date)

  def nadir(self, date=datetime.datetime.now()):
    return fromJulian(solar_transit(self.long, date) - 0.5)
