import pytz
import pandas as pd
from entsoe import EntsoePandasClient
from entsoe.mappings import Area
from datetime import datetime


from spotON_sdk import Country,Market
from entsoe.exceptions import NoMatchingDataError

'''from mySecrets import mySecrets
client = EntsoePandasClient(api_key=mySecrets.ENTSOE_KEY)'''

def get_Time_in(timezone:str):
    # set the timezone for Lisbon
    local_tz = pytz.timezone(timezone)

    # get the current date and time in Lisbon timezone
    now_local_tz = pd.Timestamp.now(tz=local_tz)

    # set the time to 0:00
    today_0am = now_local_tz.floor('D')
    return today_0am

def timezone_difference(tz1, tz2 = Area.AT.tz, date=None):
    if date is None:
        date = datetime.now()

    timezone1 = pytz.timezone(tz1)
    timezone2 = pytz.timezone(tz2)

    tz1_offset = timezone1.utcoffset(date)
    tz2_offset = timezone2.utcoffset(date)

    timedelta = tz2_offset - tz1_offset
    return pd.Timedelta(timedelta)


def getTimeStamps(country_code,tomorrow,overrideTime,query_Month):
    
    tomorrow_timestamp = tomorrow.strftime("%Y%m%d")

    timestamp_start = pd.Timestamp(tomorrow_timestamp,tz=country_code.tz)

    timestamp_end = timestamp_start + pd.Timedelta(hours=23)
    if query_Month:
        timestamp_start = timestamp_start - pd.Timedelta(days=31)
        timestamp_end = timestamp_start + pd.Timedelta(hours=23,days=31)

    CET_Difference = timezone_difference(country_code.tz) 
    timestamp_start = timestamp_start - CET_Difference

    start = pd.Timestamp(timestamp_start)
    end = pd.Timestamp(timestamp_end)

    # Override Start
    if overrideTime:
        start = pd.Timestamp(overrideTime,tz=country_code.tz)

    return start,end,CET_Difference

def query_Data(country_code,client):
    today = get_Time_in(country_code.tz)
    tomorrow = today + pd.Timedelta(days=1)
    tomorrow = today


    start,end,CET_Difference = getTimeStamps(country_code,tomorrow)
    print (f"{start=}   {end=}  {CET_Difference=}")
    series = client.query_day_ahead_prices(country_code,start=start,end=end)
    return series,CET_Difference

def create_Dataframe(s:pd.Series,country_code):
    # Convert series to dataframe
    df = s.to_frame()

    # Rename the column
    df.columns = ['value']

    # Set the index to be a DatetimeIndex
    df.index = pd.DatetimeIndex(df.index,tz=country_code.tz)
    df.index = df.index 

    return df

def query_Data(country_code,client,overrideTime :str|None = None,today_instead_of_tomorrow= False,query_Month = False):
    today = get_Time_in(country_code.tz)
    tomorrow = today + pd.Timedelta(days=1)

    if today_instead_of_tomorrow:
        tomorrow = today


    start,end,CET_Difference = getTimeStamps(country_code,tomorrow,overrideTime,query_Month)
    
    print (f"{start=}   {end=}  {CET_Difference=}")
    try:
        series = client.query_day_ahead_prices(country_code,start=start,end=end)
        return series,CET_Difference
    except NoMatchingDataError as e:
        print(f"No Values to fetch {start=}   {end=}  {CET_Difference=} \n Is it before 13:30 UTC?","NoMatchingDataError occurred:", str(e))
        


def create_Dataframe(s:pd.Series,market:Market):

    # Convert series to dataframe
    df = s.to_frame()

    # Rename the column
    df.columns = ['value']

    # Set the index to be a DatetimeIndex
    df.index = pd.DatetimeIndex(df.index,tz=market.area.tz)
    df.index = df.index 
    df["Area_Code"] = market.area_code

    return df

