from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def format_date(value, relative=True):
    if not value:
        return ""
    
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    
    prague_tz = ZoneInfo("Europe/Prague")
    local_time = value.astimezone(prague_tz)
    
    if not relative:
        return local_time.strftime('%d.%m. %H:%M')
    
    now = datetime.now(prague_tz)
    
    if local_time.date() == now.date():
        return f"Dnes {local_time.strftime('%H:%M')}"
    elif local_time.date() == (now.date() - timedelta(days=1)):
        return f"Včera {local_time.strftime('%H:%M')}"
    else:
        return local_time.strftime('%d.%m. %H:%M')