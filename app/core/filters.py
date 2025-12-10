from datetime import datetime, timedelta

def format_date(value):
    if not value:
        return ""
    
    # Získáme aktuální čas. Abychom se vyhnuli chybám s časovými zónami,
    # použijeme stejnou timezonu, jakou má předaný datum (pokud ji má),
    # nebo prostě porovnáme jen dny.
    
    # Pokud je value 'naive' (bez info o zone), použijeme now() taky naive.
    if value.tzinfo is None:
        now = datetime.now()
    else:
        # Pokud má value timezone (což tvoje appka má - UTC), použijeme now(tz)
        now = datetime.now(value.tzinfo)

    today = now.date()
    article_date = value.date()

    # Logika pro Dnes / Včera / Datum
    if article_date == today:
        return f"Dnes {value.strftime('%H:%M')}"
    elif article_date == (today - timedelta(days=1)):
        return f"Včera {value.strftime('%H:%M')}"
    else:
        # Pro starší články: např. 04.12. 15:30
        return value.strftime('%d.%m. %H:%M')