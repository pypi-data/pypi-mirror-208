from dataclasses import dataclass,field
from typing import List

from .markets import Market


class PeriodTypes():
    wholeDay :str = "24h Hour Period"
    timeFrame :str = "Timeframe"

@dataclass
class TimeFrameValidation():
    passed :bool
    def return_Validation_Result(self):
        if self.passed == False:
            return "<br> 🚨 <mark> Your Timeframe is SHORTER than your desired ON Time</mark> "
        else:
            return ""


@dataclass
class Config():
    nr_of_Hours_On :int
    uninterrupted :bool
    market : Market 
    timeframe :List[List[int]] 
    periodType : PeriodTypes| str = field(default="")
    dayframe: List[int] | None = field(default=None,init=False) 
    bestHour :str = ""
    week: int = 100
    timeFrameValidation = TimeFrameValidation(False)

    def __post_init__(self):
        def check_nr_of_Hours_not_0():
            if self.nr_of_Hours_On < 1:
                raise ValueError(f"Hey your Number of Hours On can't be zero")

        def check_TimeFrame_is_large_enogh():
            if len(self.find_Possible_Hours()) > self.nr_of_Hours_On:
                self.timeFrameValidation = TimeFrameValidation(True)
            else:
                self.timeFrameValidation = TimeFrameValidation(False)
        
        def checkConfig():
            if self.uninterrupted:
                if len(self.timeframe) > 1:
                    raise ValueError(f"Hey your Timeframe has the Attribute of Beeing uninterruped means you can't have multiple timeframes")



        def check_Overlapping_Arrays():
            possible_Hours = self.find_Possible_Hours()
            if(len(set(possible_Hours)) != len(possible_Hours)):
                raise ValueError(f"Hey your Timeframes {self.timeframe} have overlapping Hours. Reduce it to one")
            
        
        check_nr_of_Hours_not_0()
        check_TimeFrame_is_large_enogh()
        checkConfig()
        #check_Overlapping_Arrays()
        
    def find_Possible_Hours(self):
        possible_Hours = []
        for timeframe in self.timeframe:
            start,end = timeframe[0],timeframe[1]
            def loop_Hours(_start,_end):
                for hour in range (_start,_end):
                    possible_Hours.append(hour)
                
            if start < end:
                loop_Hours(start,end)
            elif start > end :  # timeframe goes over Midnight
                loop_Hours(start,25)
                loop_Hours(0,end)

        if possible_Hours == []:    # If its the same start and end consider the whole day is OK
            possible_Hours = [*range(0,24)]


        return possible_Hours

