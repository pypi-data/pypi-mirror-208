from dataclasses import dataclass
from entsoe import Area

import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, Dict,Any

from typing import List
from .countries import *
from .bidding_zones import bidding_zones

@dataclass
class Market():
    area:Area
    country :Country
    alias : List[str] | None = None
    area_code :str = field(init=False)
    country_code : str = field(init=False)
    region_code : str | None = field(init=False,default=None)
    cities : str = field(init=False)

    def __post_init__(self):
        self.area_code = self.area.name
        country_region = self.area_code.split("_")
        self.country_code = country_region[0]
        if len(country_region) >=2:
            self.region_code = country_region[1]

        try:
            city_List = bidding_zones[self.area_code]["cities"]
            my_string = ', '.join(city_List)
            self.cities = my_string
        except:
            self.cities = ""


        self.name = f"{self.country.emoji} {self.country.country_name} {self.area_code} {self.cities}"
        self.name = f"{self.country.emoji} {self.country.country_name}"

        #self.get_Market_by_area_code(self.area.name)

dataclass
class Markets():
    austria = Market(Area.AT,all_Countries.Austria)
    germany = Market(Area.DE_LU,all_Countries.Germany,alias="DE_LU")
    #luxembourg = Market(Area.DE_LU,Luxembourg)
    sweden1 = Market(Area.SE_1,all_Countries.Sweden)
    #sweden2 = Market(Area.SE_2,Sweden)
    #sweden3 = Market(Area.SE_3,Sweden)
    #sweden4 = Market(Area.SE_4,Sweden)
    markets_List = [value for key, value in vars().items() if isinstance(value, Market)]
    merged_Markets = []

    @staticmethod
    def get_Market_by_area_code(area_code: str) -> Optional[Market]:
        for country in Markets.markets_List:
            #print (f"Try to find {area_code =} in {country}")
            if country.country_code == area_code or country.alias == area_code:
                return country

        return None


def return_All_Areas(filterstring:str ="MBA"):
        
    result = []
    for area in Area:
        #print (area.name, area.meaning)
        if filterstring in area.meaning:
            result.append(area)
            print (area.name)

    return result


