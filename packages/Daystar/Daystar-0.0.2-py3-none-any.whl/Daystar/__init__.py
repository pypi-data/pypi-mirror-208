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
    return declination(date), right_ascension(date)
