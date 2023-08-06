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
  