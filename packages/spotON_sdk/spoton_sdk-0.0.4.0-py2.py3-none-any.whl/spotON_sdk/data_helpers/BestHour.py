from dataclasses import dataclass

@dataclass
class BestHour_index():
    Area_Code: str
    week:int
    Cycle_ON_Lenght:int
    TimeFrame_Start:int
    TimeFrame_End:int
    #Best_Start_Hour:int

    def return_indexString(self):
        index_String = f"{self.Area_Code}_{self.week}_{self.Cycle_ON_Lenght}_{self.TimeFrame_Start}_{self.TimeFrame_End}"
        return str(index_String)
    
def generate_index_string(row):
    index_instance = BestHour_index(
        Area_Code=row['Area_Code'],
        week=row['Week'],
        Cycle_ON_Lenght=row['Cycle_ON_Lenght'],
        TimeFrame_Start=row['TimeFrame_Start'],
        TimeFrame_End=row['TimeFrame_End']
    )
    return index_instance.return_indexString()