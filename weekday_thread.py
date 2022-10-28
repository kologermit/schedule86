from DB import DB
from datetime import datetime
import time, telebot
from config import *
bot = telebot.TeleBot(TOKEN)
database = DB(mysql)

def weekday(text):
    return ({
        "ПОНЕДЕЛЬНИК": "ПОНЕДЕЛЬНИК",
        "ВТОРНИК": "ВТОРНИК",
        "СРЕДА": "СРЕДА",
        "ЧЕТВЕРГ": "ЧЕТВЕРГ",
        "ПЯТНИЦА": "ПЯТНИЦА",
        "СУББОТА": "СУББОТА",
        "ПН": "ПОНЕДЕЛЬНИК",
        "ВТ": "ВТОРНИК",
        "СР": "СРЕДА",
        "ЧТ": "ЧЕТВЕРГ",
        "ПТ": "ПЯТНИЦА",
        "СБ": "СУББОТА",
        "ВСЯ НЕДЕЛЯ": "ВСЯ НЕДЕЛЯ",
        "ВН": "ВСЯ НЕДЕЛЯ",
        "1": "ПОНЕДЕЛЬНИК",
        "2": "ВТОРНИК",
        "3": "СРЕДА",
        "4": "ЧЕТВЕРГ",
        "5": "ПЯТНИЦА",
        "6": "СУББОТА",
    }).get(str(text).upper())

def today(last_day = False):
    now = datetime.now().weekday() + 1
    if now == 7:
        now = 6
    if last_day:
        now -= 1
    if now == 0:
        now = 6
    return now

time_last = weekday(today())
while True:
    if time_last == weekday(today(last_day=True)):
        last_day = weekday(today(last_day=True))
        schedule_classes = [{"parallel": i[0], "symbol": i[1], "schedule": json_loads(i[2])} for i in database.select("schedule_classes", ["parallel", "symbol", "schedule"])]
        schedule_teachers = [{"name": i[0], "schedule": json_loads(i[1])} for i in database.select("teachers", ["name", "schedule"])]
        for i in schedule_classes:
            parallel = i["parallel"]
            symbol = i["symbol"]
            schedule = i["schedule"]
            if schedule["edited"].get(last_day):
                schedule["edited"].pop(last_day)
                database.update("schedule_classes", {"schedule": json.dumps(schedule, indent=2)}, [["parallel", "=", parallel], ["symbol", "=", symbol]])
        for i in schedule_teachers:
            name = i["name"]
            if schedule["edited"].get(last_day):
                schedule["edited"].pop(last_day)
                database.update("teachers", {"schedule": json.dumps(schedule, indent=2)}, [["name", "=", name]])
        bot.send_message(847721936, f"Удаление расписания на {last_day}")
    time_last = weekday(today())
    time.sleep(30)