from dataclasses import dataclass,field


@dataclass
class Unit:
    name: str
    unit: str

class Units():
    temperature = Unit("Temperature","°C")

@dataclass
class Humidity(Unit):
    name = "Humidity"
    unit = "%"

@dataclass
class Co2(Unit):
    name = "Co2"
    unit = "ppm"

@dataclass
class Pressure(Unit):
    name = "Pressure"
    unit = "P"


@dataclass
class Volt(Unit):
    name = "Measurement"
    unit = "mV"