from enum import Flag, auto
from typing import List
from dataclasses import dataclass, field
from .markets import Market



class Pricefinding_Type(Flag):
    INTERRUPTED = auto()
    CONTINUOUS = auto()


class TimeFrame_Type(Flag):
    WHOLE_DAY = auto()
    TIMEFRAME = auto()




@dataclass
class TimeFrameValidation():
    passed :bool
    def return_Validation_Result(self):
        if self.passed == False:
            return "<br> 🚨 <mark> Your Timeframe is SHORTER than your desired ON Time</mark> "
        else:
            return ""

@dataclass
class Resolution():
    name :str 
    value: float



@dataclass
class Config():
    #TODO Implement resolution 15Min, 30Min etc....
    nr_of_Hours_On :int
    pricefinding_Type :Pricefinding_Type
    market : Market 
    timeframe :List[List[int]] 
    timeframe_Type : TimeFrame_Type = field(init=False)
    week: int | None = field(init=False,default=None)
    resolution: Resolution = field(default_factory=lambda: Resolution("One_Hour", 1))
    timeFrameValidation = TimeFrameValidation(False)

    def __post_init__(self):
        def check_Period_type():
            if len(self.find_Possible_Hours())>=24:
                self.timeframe_Type = TimeFrame_Type.WHOLE_DAY
            else:
                self.timeframe_Type = TimeFrame_Type.TIMEFRAME

        def check_nr_of_Hours_not_0():
            if self.nr_of_Hours_On < 1:
                raise ValueError(f"Hey your Number of Hours On can't be zero")

        def check_TimeFrame_is_large_enogh():
            if len(self.find_Possible_Hours()) > self.nr_of_Hours_On:
                self.timeFrameValidation = TimeFrameValidation(True)
            else:
                self.timeFrameValidation = TimeFrameValidation(False)
        
        def checkLogic():
            if self.pricefinding_Type == Pricefinding_Type.CONTINUOUS:
                if len(self.timeframe) > 1:
                    raise ValueError(f"Hey your Timeframe has the Attribute of Beeing CONTINUOUS means you can't have multiple timeframes")



        def check_Overlapping_Arrays():
            possible_Hours = self.find_Possible_Hours()
            if(len(set(possible_Hours)) != len(possible_Hours)):
                raise ValueError(f"Hey your Timeframes {self.timeframe} have overlapping Hours. Reduce it to one")
            
        check_Period_type()
        check_nr_of_Hours_not_0()
        check_TimeFrame_is_large_enogh()
        checkLogic()
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
    
    def return_possible_Starting_Hours(self):
        if self.timeframe_Type == TimeFrame_Type.WHOLE_DAY:
            valid_Hours_List = self.find_Possible_Hours()

        elif self.timeframe_Type == TimeFrame_Type.TIMEFRAME:
            '''Deletes Hours that are outside the timeframe End'''
            possible_Hours = self.find_Possible_Hours()
            nr_of_Hours_On = self.nr_of_Hours_On
            
            valid_Hours_List = []
            for hour in possible_Hours:
                    if hour + nr_of_Hours_On - self.resolution.value in possible_Hours:
                            valid_Hours_List.append(hour)
            
        return valid_Hours_List


