from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def format_date(value, relative=True):
    if not value:
        return ""
    
    # 1. UTC fix
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    
    # 2. Převod na Prahu
    prague_tz = ZoneInfo("Europe/Prague")
    local_time = value.astimezone(prague_tz)
    
    # 3. Pokud nechceme relativní (Dnes/Včera), vrátíme rovnou formát
    if not relative:
        return local_time.strftime('%d.%m. %H:%M')
    
    # 4. Logika pro Dnes/Včera
    now = datetime.now(prague_tz)
    
    if local_time.date() == now.date():
        return f"Dnes {local_time.strftime('%H:%M')}"
    elif local_time.date() == (now.date() - timedelta(days=1)):
        return f"Včera {local_time.strftime('%H:%M')}"
    else:
        return local_time.strftime('%d.%m. %H:%M')