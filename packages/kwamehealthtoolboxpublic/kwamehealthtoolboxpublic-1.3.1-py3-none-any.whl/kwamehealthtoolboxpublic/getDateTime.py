from datetime import datetime, timedelta
import pytz

def timeData(timezone):
    currentTimezone = pytz.timezone(timezone)
    currentDateTime = datetime.now(currentTimezone)
    currentDateTimePlus1Hr = currentDateTime + timedelta(hours=1)
    currentDateTimePlus12Hrs = currentDateTime + timedelta(hours=12)
    currentDateTimePlus24Hrs = currentDateTime + timedelta(hours=24)
    currentDateTimePlus1Month = currentDateTime + timedelta(hours=720)
    currentDateTimePlus1Year = currentDateTime + timedelta(hours=8640)
    
    return currentDateTime.strftime("%Y-%m-%d %H:%M:%S"), currentDateTimePlus1Hr.strftime("%Y-%m-%d %H:%M:%S"), currentDateTimePlus12Hrs.strftime("%Y-%m-%d %H:%M:%S"), currentDateTimePlus24Hrs.strftime("%Y-%m-%d %H:%M:%S"), currentDateTimePlus1Month.strftime("%Y-%m-%d %H:%M:%S"), currentDateTimePlus1Year.strftime("%Y-%m-%d %H:%M:%S")
