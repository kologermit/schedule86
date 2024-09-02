import telebot, excel_reader, config, json, get_weather, os, urllib, time, sys, logging
from datetime import datetime
from telebot import types
from DB import DB
from threading import Thread
from time import sleep

logging.basicConfig(filename=config.log_filename)
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

logging.info("Start bot")

bot = telebot.TeleBot(config.TOKEN)
database = DB(config.db_filename)

if ("config") not in database.select("sqlite_master", ["name"], [["type", "=", "table"]]):
    db_init_file = open(config.db_init_filename, "r")
    for sql in db_init_file.read().split(";"):
        database.query(sql)
    db_init_file.close()

if database.select("schedule_classes") == []:
    for cl in database.select("config", ["data"], [["theme", "=", "classes"]], 1):
        logging.info(cl[0])
        data = json.loads(cl[0])
        for parallel in data:
            for symbol in data[parallel]:
                database.insert("schedule_classes", ["parallel", "symbol"], [[parallel, symbol]])

def bot_send_message(bot, user_id, message, parse_mode=None, reply_markup=None):
    params = {
    }
    if parse_mode:
        params["parse_mode"] = parse_mode
    if reply_markup:
        params["reply_markup"] = reply_markup
    try:
        bot.send_message(user_id, message, **params)
    except Exception as err:
        logging.exception(err)

bot_send_message(bot, 847721936, "Start Bot") #847721936

def json_loads(data):
    try:
        return json.loads(data)
    except:
        return None

def get_user(message):
    data = database.select('users', ['id', 'name', 'status', 'settings'], [['id', '=', message.chat.id]], 1)
    if (data):
        return {"id": data[0][0], "name": data[0][1], "status": data[0][2], "settings": json.loads(data[0][3])}
    else:
        database.insert('users', ['id', 'name', 'status', 'settings'], [[message.chat.id, message.chat.first_name, 'menu', '{\"subscribe\": [], \"commands\": []}']])
        return {"id": message.chat.id, "name": message.chat.first_name, "status": 'menu', "settings": {"subscribe": [], "commands": []}}

def log(message, user):
    # database.insert('log', ['text'], [[json.dumps({
    #     "user": user,
    #     "message": message.text,
    #     "time": str(datetime.now())
    # }, indent=2)]])
    pass
    
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

def user_update(user, status=None, settings=None):
    if status and not settings:
        database.update('users', {'status': status}, [['id', '=', user['id']]])
    elif settings and not status:
        database.update('users', {'settings': settings}, [['id', '=', user['id']]])
    else:
        database.update('users', {'status': status, 'settings': settings}, [['id', '=', user['id']]])

def markups(buttons):
    buttons.append("Меню")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b = []
    for i in buttons:
        b.append(types.KeyboardButton(i))
    markup.add(*b)
    return markup

def is_class(text, database):
    if len(text) == 2:
        if text[0].isdigit():
            if int(text[0]) >= 5:
                classes = database.select("config", "data", [["theme", "=", "classes"]])
                if not classes:
                    return None
                classes = json_loads(classes[0][0])
                if not classes or type(classes) != type({}):
                    return None
                if text[1] in classes[text[0]]:
                    return {
                        "parallel": int(text[0]),
                        "symbol": text[1]
                    }
    elif len(text) == 3:
        if text[0:2].isdigit():
            if int(text[0:2]) >= 10 and int(text[0:2]) <= 11:
                classes = database.select("config", "data", [["theme", "=", "classes"]])
                if not classes:
                    return None
                classes = json_loads(classes[0][0])
                if not classes or type(classes) != type({}):
                    return None
                if text[2] in classes[text[0:2]]:
                    return {
                        "parallel": int(text[0:2]),
                        "symbol": text[1]
                    }

def menu_markups(user):
    answer = markups(["Уроки📅", "Звонки🔔", "Каникулы🎅", "Инфоℹ", "Где ФК?⚽", "Настройки⚙️"])
    b = []
    for i in user["settings"]["commands"]:
        b.append(types.KeyboardButton(i))
    if b:
        answer.add(*b)
    return answer
    
settings_markup = markups(["Подписка на расписание📅", "Избранные команды📌", "Назад🔙"])

@bot.message_handler(commands=['start'])
def start_message(message):
    user = get_user(message)
    bot_send_message(bot, message.chat.id,"Привет! Я бот, который помогает узнать информацию, нужную для учёбы в ГЮЛ 86", reply_markup=menu_markups(user))
    log(message, user)
    user_update(user, "menu")

@bot.message_handler(commands=['restart', 'menu'])
def start_message(message):
    user = get_user(message)
    bot_send_message(bot, message.chat.id,"Перезаряжаю!!!!!!!!!!", reply_markup=menu_markups(user))
    log(message, user)
    user_update(user, "menu")

@bot.message_handler(commands=['t'])
def t(message):
    user = get_user(message)
    log(message, user)
    if user["status"] == "settings:commands:add":
        return MessageHandler.Settings.Commands.add(bot, message, user)
    elif user["status"] == "settings:commands:delete":
        return MessageHandler.Settings.Commands.delete(bot, message, user)
    message_data = [i for i in message.text.split(" ") if i]
    if len(message_data) == 1:
        bot_send_message(bot, user["id"],"Вы не написали фамилию учителя")
        return True
    data = database.select("teachers", ["schedule", "name"], [["upper(name)","RLIKE",message_data[1].upper()]])
    if not data:
        bot_send_message(bot, user["id"],"Данный учитель не найден")
        return True
    day = None
    if len(message_data) >= 3:
        day = weekday(message_data[2])
    if not day and len(message_data) >= 4:
        day = weekday(f"{message_data[2]} {message_data[3]}")
    if not day:
        day = weekday("вн")
    data, name = json_loads(data[0][0]), data[0][1]
    if not data:
        bot_send_message(bot, user["id"], "Произошла ошибка получения раписания!")
        return True
    if type(data) != type({}):
        bot_send_message(bot, user["id"], "Произошла ошибка получения раписания!")
        return True
    if data.get("standart") is None or data.get("edited") is None:
        bot_send_message(bot, user["id"], "Произошла ошибка получения раписания!")
        return True
    if type(data["standart"]) != type({}) or type(data["edited"]) != type({}):
        bot_send_message(bot, user["id"], "Произошла ошибка получения раписания!")
        return True
    if day != "ВСЯ НЕДЕЛЯ":
        answer = f"<b>Расписание {name} на {day}:\n</b>"
        for i in range(len(data['standart'][day])):
            answer += f"<b>{i + 1})</b> {data['standart'][day][i]}\n"
        if data["edited"].get(day):
            answer += "\n<b>Изменения:</b>\n"
            for i in range(len(data["edited"][day])):
                answer += f"<b>{i + 1})</b> {data['edited'][day][i]}\n"
        else:
            answer += "\n<b>Изменений нет</b>"
    else:
        answer = f"<b>Раписание {name} на всю неделю:</b>\n"
        for i in data["standart"]:
            answer += f"<b>{i.capitalize()}:</b>\n"
            for j in range(len(data["standart"][i])):
                answer += f"<b>{j + 1})</b> {data['standart'][i][j]}\n"
            answer += "\n"
        if data["edited"]:
            answer += "<b>Изменения:</b>\n"
            for i in data["edited"]:
                answer += f"<b>{i.capitalize()}:</b>\n"
                for j in range(len(data["edited"][i])):
                    answer += f"<b>{j + 1})</b> {data['edited'][i][j]}\n"
                answer += "\n"
        else:
            answer += "<b>Изменений нет</b>"
    bot_send_message(bot, user["id"], answer, parse_mode="HTML", reply_markup=menu_markups(user))
    return True

@bot.message_handler(commands=['ts'])
def ts(message):
    user = get_user(message)
    log(message, user)
    message_data = [i for i in message.text.split(" ") if i]
    if len(message_data) == 1:
        bot_send_message(bot, user["id"],"Вы не написали фамилию учителя")
        return True
    data = database.select("teachers", ["subscribe", "name"], [["name","RLIKE",message_data[1]]])
    if not data:
        bot_send_message(bot, user["id"],"Данный учитель не найден")
        return True
    data, name = json_loads(data[0][0]), data[0][1]
    if data is None:
        bot_send_message(bot, "Произошла ошибка")
        return True
    if type(data) != type([]):
        bot_send_message(bot, "Произошла ошибка")
        return True
    if user["id"] in data:
        bot_send_message(bot, user["id"], f"Вы уже подписаны на {name}")
        return True
    data.append(user["id"])
    database.update("teachers", {"subscribe": json.dumps(data, indent=2)}, [["name", "=", name]])
    bot_send_message(bot, user["id"], f"Вы успешно подписались на учителя {name}")
    return True

@bot.message_handler(commands=['tu'])
def tu(message):
    user = get_user(message)
    log(message, user)
    message_data = [i for i in message.text.split(" ") if i]
    if len(message_data) == 1:
        bot_send_message(bot, user["id"],"Вы не написали фамилию учителя")
        return True
    data = database.select("teachers", ["subscribe", "name"], [["name","RLIKE",message_data[1]]])
    if not data:
        bot_send_message(bot, user["id"],"Данный учитель не найден")
        return True
    data, name = json_loads(data[0][0]), data[0][1]
    if data is None:
        bot_send_message(bot, "Произошла ошибка")
        return True
    if type(data) != type([]):
        bot_send_message(bot, "Произошла ошибка")
        return True
    if user["id"] not in data:
        bot_send_message(bot, user["id"], f"Вы не подписаны на {name}")
        return True
    data.remove(user["id"])
    database.update("teachers", {"subscribe": json.dumps(data, indent=2)}, [["name", "=", name]])
    bot_send_message(bot, user["id"], f"Вы успешно отписались на учителя {name}")
    return True

@bot.message_handler(content_types=['document'])
def document(message):
    user = get_user(message)
    teachers = database.select("config", ["data"], [["theme","=","teachers"]])
    if not teachers:
        return False
    teachers = json_loads(teachers[0][0])
    if type(teachers) != type({}):
        return False
    teachers = [teachers[i] for i in teachers]
    if user["id"] not in teachers:
        return True
    file_name = message.document.file_name
    if not file_name.endswith(".xls"):
        bot_send_message(bot, user["id"], "Расширение файла не .xls!")
        return True
    file_name = file_name.replace(".xls", "")
    file_name_data = [i for i in file_name.split(" ") if i]
    if len(file_name_data) < 3:
        bot_send_message(bot, user["id"], "Не хватает параметров! (3)")
        return True
    day = weekday(file_name_data[0].upper())
    if day in ["ВСЯ НЕДЕЛЯ", None]:
        bot_send_message(bot, user["id"], "Неверный параметр [ДЕНЬ]!")
        return True
    edited = None
    if file_name_data[1].upper() not in ["EDITED", "STANDART", "EDIT", "ИЗМЕНЕНИЯ", "ОСНОВНОЕ", "СТАНДАРТНОЕ", "ИЗМЕНЕНИЕ"]:
        bot_send_message(bot, user["id"], "Неверный параметр [ОСНОВНОЕ/ИЗМЕНЕНИЯ]!")
        return True
    if file_name_data[1].upper() in ["EDITED", "EDIT", "ИЗМЕНЕНИЯ", "ИЗМЕНЕНИЕ"]:
        edited = True
    else:
        edited = False
    is_classes = None
    if file_name_data[2].upper() not in ["CLASS", "CLASSES", "КЛАСС", "КЛАССЫ", "TEACHERS", "TEACHER", "TEACH", "УЧИТЕЛЯ", "УЧИТЕЛЬ"]:
        bot_send_message(bot, user["id"], "Неверный параметр [КЛАССЫ/УЧИТЕЛЯ]!")
        return True
    if file_name_data[2].upper() in ["CLASS", "CLASSES", "КЛАСС", "КЛАССЫ"]:
        is_classes = True
    else:
        is_classes = False
    if not os.path.exists("Temp"):
        os.mkdir("Temp")
    if not os.path.exists(f"Temp/{user['id']}"):
        os.mkdir(f"Temp/{user['id']}")
    if not os.path.exists(f"Temp/{user['id']}/documents"):
        os.mkdir(f"Temp/{user['id']}/documents")
    try:
        file_path = bot.get_file(message.document.file_id).file_path
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{config.TOKEN}/{file_path}', f"Temp/{user['id']}/{file_path}")
        bot_send_message(bot, user["id"], "Файл успешно получен")
    except Exception as err:
        bot_send_message(bot, user["id"], f"Произошла ошибка получения файла: {err}")
        logging.exception(err)
        return True
    try:
        if is_classes:
            excel_reader.read_classes(bot, user, f"Temp/{user['id']}/{file_path}", day, edited)
        else:
            excel_reader.read_teachers(bot, user, f"Temp/{user['id']}/{file_path}", day, edited)
    except Exception as err:
        logging.exception(f"Error in excel reader: {err}")
        bot_send_message(bot, user["id"], f"Произошла ошибка во время обработки файла:\nУчителя:{not is_classes}\nИзменения:{edited}\nДень:{day}")

def next_word(line):
    line = line.strip()
    space = line.find(" ")
    enter = line.find("\n")
    if line == "":
        return ("", "")
    if space == -1 and enter == -1:
        return (line, "")
    min = 1e10
    if space != -1 and min > space:
        min = space
    if enter != -1 and min > enter:
        min = enter
    return (line[0: min], line[min + 1:])

@bot.message_handler(commands=['python_command'])
def python_command(message):
    user = get_user(message)
    log(message, user)
    if user["status"] == "settings:commands:add":
        return MessageHandler.Settings.Commands.add(bot, message, user)
    elif user["status"] == "settings:commands:delete":
        return MessageHandler.Settings.Commands.delete(bot, message, user)
    answer = next_word(message.text)
    try:
        try:
            exec(answer[1])
        except Exception as e:
            logging.exception(e)
        try:
            bot_send_message(bot, message.chat.id, e)
        except:
            pass
    except:
        try:
            bot_send_message(bot, message.chat.id, "Произошла ошибка во время выполненя кода")
        except:
            pass


class MessageHandler:
    def menu(bot, message, user):
        if "УРОКИ" in message.text:
            return MessageHandler.Schedule.to_parall(bot, message, user)

        if "ЗВОНКИ" in message.text:
            data = database.select('config', 'data', [['theme', '=', 'call_schedule']])
            if not data:
                bot_send_message(bot, user["id"], "Произошла ошибка получшения расписания звонков")
            else:
                data = json_loads(data[0][0])
                if type(data) == type(list()):
                    answer = "<b>Расписание звонков:\n</b>"
                    for i in range(len(data)):
                        answer += f"<b>{i + 1})</b> {data[i]} \n"
                    bot_send_message(bot, user["id"], answer, parse_mode="HTML")
                else:
                    bot_send_message(bot, user["id"], "Произошла ошибка получшения расписания звонков")
            return True
        if "КАНИКУЛЫ" in message.text:
            data = database.select('config', 'data', [['theme','=','holidays']])
            if not data:
                bot_send_message(bot, user["id"], "Произошла ошибка получшения расписания")
            else:
                bot_send_message(bot, user["id"], data[0][0], parse_mode="HTML")
            return True
        if "ИНФО" in message.text:
            # bot_send_message(bot, user["id"],"Данный бот создан выпускником\nМБОУ 'ГЮЛ №86' г.Ижевска\nКологерманским Фёдором (@kologermit)\nУчебный год 20/21")
            bot_send_message(bot, user["id"],"Кнопки для пользования ботом:\n1. Уроки - Узнать расписание уроков\n2. Звонки - Узнать расписание звонков\n3. Информация - Узнать подробную информацию о боте\n4. Где физ-ра? - Узнать, где будет физ-ра - на улице или в зале.\n\nКоманды:\n1. /start - Начать работу с ботом\n2. /restart - Перезапустить бота\n3. /info - Узнать подробную информацию о боте\n4. КлассБуква ДеньНедели (10а вторник) - Узнать расписание сразу на нужный класс и день (всю неделю)")
            return True
        if message.text.isdigit():
            if int(message.text) >= 5 and int(message.text) <= 11:
                classes = database.select("config", "data", [["theme", "=", "classes"]])
                if not classes:
                    bot_send_message(bot, user["id"], "Произошла ошибка!")
                    return True
                classes = json_loads(classes[0][0])
                bot_send_message(bot, user["id"], "Выберите букву:", reply_markup=markups([i for i in classes[str(int(message.text))]] + ["Назад🔙"]))
                user["settings"]["class_parallel"] = int(message.text)
                user_update(user, "schedule:symbol", json.dumps(user["settings"], indent=2))
                return True
        if len(message.text) == 2:
            if message.text[0].isdigit():
                if int(message.text[0]) >= 5: 
                    classes = database.select("config", "data", [["theme", "=", "classes"]])
                    if not classes:
                        bot_send_message(bot, user["id"], "Произошла ошибка!")
                        return True
                    classes = json_loads(classes[0][0])
                    if not classes or type(classes) != type({}):
                        bot_send_message(bot, user["id"], "Произошла ошибка!")
                        return True
                    if message.text[1] in classes[message.text[0]]:
                        user["settings"]["class_parallel"] = int(message.text[0])
                        message.text = message.text[-1]
                        return MessageHandler.Schedule.symbol(bot, message, user)
        elif len(message.text) == 3:
            if message.text[0:2].isdigit():
                if int(message.text[0:2]) >= 10 and int(message.text[0:2]) <= 11:
                    classes = database.select("config", "data", [["theme", "=", "classes"]])
                    if not classes:
                        bot_send_message(bot, user["id"], "Произошла ошибка!")
                        return True
                    classes = json_loads(classes[0][0])
                    if not classes or type(classes) != type({}):
                        bot_send_message(bot, user["id"], "Произошла ошибка!")
                        return True
                    if message.text[2] in classes[message.text[0:2]]:
                        user["settings"]["class_parallel"] = int(message.text[0:2])
                        message.text = message.text[-1]
                        return MessageHandler.Schedule.symbol(bot, message, user)

        message_data = [i for i in message.text.split(" ") if i]
        if len(message_data) == 2:
            data = is_class(message_data[0], database)
            day = weekday(message_data[1])
            if data and day:
                message.text = day
                user["settings"]["class_parallel"] = data["parallel"]
                user["settings"]["class_symbol"] = data["symbol"]
                return MessageHandler.Schedule.day(bot, message, user)

        if len(message_data) == 3:
            data = is_class(message_data[0], database)
            day = weekday(f"{message_data[1]} {message_data[2]}")
            if data and day:
                message.text = day
                user["settings"]["class_parallel"] = data["parallel"]
                user["settings"]["class_symbol"] = data["symbol"]
                return MessageHandler.Schedule.day(bot, message, user)

        if "ГДЕ ФК?" in message.text:
            bot_send_message(bot, user["id"], get_weather.where_fizra(), parse_mode="HTML")
            return True

        if "НАСТРОЙКИ" in message.text:
            return MessageHandler.Settings.to_main(bot, message, user)

    def to_menu(bot, message, user):
        bot_send_message(bot, user["id"], "Хорошего дня!", reply_markup=menu_markups(user))
        user_update(user, status="menu")
        return True

    class Schedule:
        def parallel(bot, message, user):
            if message.text.isdigit():
                if int(message.text) >= 5 and int(message.text) <= 11:
                    classes = database.select("config", "data", [["theme", "=", "classes"]])
                    if not classes:
                        bot_send_message(bot, user["id"], "Произошла ошибка!")
                        return True
                    classes = json_loads(classes[0][0])
                    bot_send_message(bot, user["id"], "Выберите букву:", reply_markup=markups([i for i in classes[str(int(message.text))]] + ["Назад🔙"]))
                    user["settings"]["class_parallel"] = int(message.text)
                    user_update(user, "schedule:symbol", json.dumps(user["settings"], indent=2))
                    return True
            elif "НАЗАД" in message.text:
                return MessageHandler.to_menu(bot, message, user)

        def to_parall(bot, message, user):
            bot_send_message(bot, user["id"], "Выберите параллель:", reply_markup=markups(["5", "6", "7", "8", "9", "10", "11", "Назад🔙"]))
            user_update(user, status="schedule:parallel")
            return True

        def symbol(bot, message, user):
            classes = database.select("config", "data", [["theme", "=", "classes"]])
            if not classes:
                bot_send_message(bot, user["id"], "Произошла ошибка!")
                return True
            classes = json_loads(classes[0][0])
            if len(message.text) == 1 and message.text in classes[str(user["settings"]["class_parallel"])]:
                bot_send_message(bot, user["id"], "Выберите день недели:", reply_markup=markups(["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Вся неделя", "Назад🔙"]))
                user["settings"]["class_symbol"] = message.text
                user_update(user, "schedule:day", json.dumps(user["settings"], indent=2))
                return True
            elif "НАЗАД" in message.text:
                return MessageHandler.Schedule.to_parall(bot, message, user)

        def day(bot, message, user):
            if weekday(message.text):
                message.text = weekday(message.text)
                data = database.select('schedule_classes', 'schedule', [['parallel','=',user['settings']['class_parallel']], ['symbol','=',user['settings']['class_symbol']]])
                if not data:
                    bot_send_message(bot, user["id"], "Произошла ошибка получшения расписания")
                else:
                    data = json_loads(data[0][0])
                    answer = ""
                    if type(data) == type(dict()):
                        if "ВСЯ НЕДЕЛЯ" not in message.text:
                            answer = f"<b>Расписание {user['settings']['class_parallel']}{user['settings']['class_symbol']} на {message.text.lower()}:\n</b>"
                            for i in range(len(data['standart'][message.text])):
                                answer += f"<b>{i + 1})</b> {data['standart'][message.text][i]}\n"
                            if data["edited"].get(message.text):
                                answer += "\n<b>Изменения:</b>\n"
                                for i in range(len(data["edited"][message.text])):
                                    answer += f"<b>{i + 1})</b> {data['edited'][message.text][i]}\n"
                            else:
                                answer += "\n<b>Изменений нет</b>"
                        else:
                            answer = f"<b>Раписание {user['settings']['class_parallel']}{user['settings']['class_symbol']} на всю неделю:</b>\n"
                            for i in data["standart"]:
                                answer += f"<b>{i.capitalize()}:</b>\n"
                                for j in range(len(data["standart"][i])):
                                    answer += f"<b>{j + 1})</b> {data['standart'][i][j]}\n"
                                answer += "\n"
                            if data["edited"]:
                                answer += "<b>Изменения:</b>\n"
                                for i in data["edited"]:
                                    answer += f"<b>{i.capitalize()}:</b>\n"
                                    for j in range(len(data["edited"][i])):
                                        answer += f"<b>{j + 2})</b> {data['edited'][i][j]}\n"
                                    answer += "\n"
                            else:
                                answer += "<b>Изменений нет</b>"
                        bot_send_message(bot, user["id"], answer, parse_mode="HTML", reply_markup=menu_markups(user))
                        user["settings"].pop("class_parallel")
                        user["settings"].pop("class_symbol")
                        user_update(user, "menu", json.dumps(user["settings"], indent=2))
                    else:
                        bot_send_message(bot, user["id"], "Произошла ошибка получшения расписания")
                return True
            elif "НАЗАД" in message.text:
                classes = database.select("config", "data", [["theme", "=", "classes"]])
                if not classes:
                    bot_send_message(bot, user["id"], "Произошла ошибка!")
                    return True
                classes = json_loads(classes[0][0])
                bot_send_message(bot, user["id"], "Выберите букву:", reply_markup=markups([i for i in classes[str(user["settings"]["class_parallel"])]] + ["Назад🔙"]))
                user_update(user, "schedule:symbol")
                return True

    class Settings:
        def to_main(bot, mesage, user):
            bot_send_message(bot, user["id"], "Какие настройки хотите поменять?", reply_markup=settings_markup)
            user_update(user, "settings")
            return True

        def main(bot, message, user):
            if "НАЗАД" in message.text:
                return MessageHandler.to_menu(bot, message, user)

            elif "ПОДПИСКА НА РАСПИСАНИЕ" in message.text:
                return MessageHandler.Settings.Subscribe.to_main(bot, message, user)

            elif "ИЗБРАННЫЕ КОМАНДЫ" in message.text:
                return MessageHandler.Settings.Commands.to_main(bot, message, user)
                

        class Subscribe:
            def to_main(bot, message, user):
                answer = ""
                if user["settings"]["subscribe"]:
                    answer += "Классы, на которые вы подписаны:\n"
                    for i in range(len(user["settings"]["subscribe"])):
                        answer += f"{i + 1}. {user['settings']['subscribe'][i]}\n"
                else:
                    answer = "Вы не подписаны на классы"
                bot_send_message(bot, user["id"], answer, reply_markup=markups(["Добавить➕", "Удалить❌", "Назад🔙"]))
                user_update(user, "settings:subscribe")
                return True

            def main(bot, message, user):
                if "НАЗАД" in message.text:
                    return MessageHandler.Settings.to_main(bot, message, user)
                
                if "ДОБАВИТЬ" in message.text:
                    if user["settings"].get("subscribe"):
                        if len(user["settings"]["subscribe"]) >= 4:
                            bot_send_message(bot, user["id"], "Больше четырёх классов добавить нельзя!")
                            return True
                    classes = database.select("config", "data", [["theme", "=", "classes"]])
                    if not classes:
                        bot_send_message(bot, user["id"], "Произошла ошибка!")
                        return True
                    classes = json_loads(classes[0][0])
                    if not classes or type(classes) != type({}):
                        bot_send_message(bot, user["id"], "Произошла ошибка!")
                        return True
                    data = []
                    for i in classes:
                        for j in classes[i]:
                            if f"{i}{j}" not in user["settings"]["subscribe"]:
                                data.append(f"{i}{j}")
                    data.append("Назад🔙")
                    bot_send_message(bot, user["id"], "На какой класс хотите подписаться", reply_markup=markups(data))
                    user_update(user, "settings:subscribe:add")
                    return True

                if "УДАЛИТЬ" in message.text:
                    if not user["settings"]["subscribe"]:
                        bot_send_message(bot, user["id"], "Вы не подписаны на классы!")
                        return True
                    bot_send_message(bot, user["id"], "От расписания какого класса хотите отписаться?", reply_markup=markups(user["settings"]["subscribe"] + ["Назад🔙"]))
                    user_update(user, "settings:subscribe:delete")
                    return True

            def add(bot, message, user):
                if "НАЗАД" in message.text:
                    return MessageHandler.Settings.to_main(bot, message, user)

                if len(message.text) == 2:
                    if message.text[0].isdigit():
                        if int(message.text[0]) >= 5: 
                            classes = database.select("config", "data", [["theme", "=", "classes"]])
                            if not classes:
                                bot_send_message(bot, user["id"], "Произошла ошибка!")
                                return True
                            classes = json_loads(classes[0][0])
                            if not classes or type(classes) != type({}):
                                bot_send_message(bot, user["id"], "Произошла ошибка!")
                                return True
                            if message.text[1] in classes[message.text[0]] and message.text not in user["settings"]["subscribe"]:
                                bot_send_message(bot, user["id"], f"Вы успешно подписались на расписание {message.text} класса", reply_markup=settings_markup)
                                user["settings"]["subscribe"].append(message.text)
                                user_update(user, "settings", json.dumps(user["settings"], indent=2))
                                schedule_class = database.select("schedule_classes", ["parallel", "symbol", "subscribe"], [["parallel", "=", int(message.text[:-1])], ["symbol", "=", message.text[-1]]])
                                if not schedule_class:
                                    return True
                                schedule_class = {
                                    "parallel": schedule_class[0][0],
                                    "symbol": schedule_class[0][1],
                                    "subscribe": json.loads(schedule_class[0][2])
                                }
                                schedule_class["subscribe"].append(user["id"])
                                database.update("schedule_classes", {"subscribe": json.dumps(schedule_class["subscribe"], indent=2)}, [["parallel", "=", schedule_class["parallel"]], ["symbol", "=", schedule_class["symbol"]]])
                                return True
                elif len(message.text) == 3:
                    if message.text[0:2].isdigit():
                        if int(message.text[0:2]) >= 10 and int(message.text[0:2]) <= 11:
                            classes = database.select("config", "data", [["theme", "=", "classes"]])
                            if not classes:
                                bot_send_message(bot, user["id"], "Произошла ошибка!")
                                return True
                            classes = json_loads(classes[0][0])
                            if not classes or type(classes) != type({}):
                                bot_send_message(bot, user["id"], "Произошла ошибка!")
                                return True
                            if message.text[2] in classes[message.text[0:2]] and message.text not in user["settings"]["subscribe"]:
                                bot_send_message(bot, user["id"], f"Вы успешно подписались на расписание {message.text} класса", reply_markup=settings_markup)
                                user["settings"]["subscribe"].append(message.text)
                                user_update(user, "settings", json.dumps(user["settings"], indent=2))
                                schedule_class = database.select("schedule_classes", ["parallel", "symbol", "subscribe"], [["parallel", "=", int(message.text[:-1])], ["symbol", "=", message.text[-1]]])
                                if not schedule_class:
                                    return True
                                schedule_class = {
                                    "parallel": schedule_class[0][0],
                                    "symbol": schedule_class[0][1],
                                    "subscribe": json.loads(schedule_class[0][2])
                                }
                                schedule_class["subscribe"].append(user["id"])
                                database.update("schedule_classes", {"subscribe": json.dumps(schedule_class["subscribe"], indent=2)}, [["parallel", "=", schedule_class["parallel"]], ["symbol", "=", schedule_class["symbol"]]])
                                return True

            def delete(bot, message, user):
                if message.text in user["settings"]["subscribe"]:
                    user["settings"]["subscribe"].remove(message.text)
                    bot_send_message(bot, user["id"], f"Вы успешно отписались от раписания {message.text} класса", reply_markup=settings_markup)
                    user_update(user, "settings", json.dumps(user["settings"], indent=2))
                    schedule_class = database.select("schedule_classes", ["parallel", "symbol", "subscribe"], [["parallel", "=", int(message.text[:-1])], ["symbol", "=", message.text[-1]]])
                    if not schedule_class:
                        return True
                    schedule_class = {
                        "parallel": schedule_class[0][0],
                        "symbol": schedule_class[0][1],
                        "subscribe": json.loads(schedule_class[0][2])
                    }
                    if user["id"] in schedule_class["subscribe"]:
                        schedule_class["subscribe"].remove(user["id"])
                        database.update("schedule_classes", {"subscribe": json.dumps(schedule_class["subscribe"], indent=2)}, [["parallel", "=", schedule_class["parallel"]], ["symbol", "=", schedule_class["symbol"]]])
                    return True
                elif "НАЗАД" in message.text:
                    return MessageHandler.Settings.to_main(bot, message, user)
        
        class Commands:
            def to_main(bot, message, user):
                answer = ""
                if user["settings"]["commands"]:
                    answer += "Ваши избранные команды:\n"
                    for i in range(len(user["settings"]["commands"])):
                        answer += f"{i + 1}. {user['settings']['commands'][i]}\n"
                else:
                    answer = "У вас нет избранных команд"
                bot_send_message(bot, user["id"], answer, reply_markup=markups(["Добавить➕", "Удалить❌", "Назад🔙"]))
                user_update(user, "settings:commands")
                return True
            def main(bot, message, user):
                if "НАЗАД" in message.text:
                    return MessageHandler.Settings.to_main(bot, message, user)
                
                if "ДОБАВИТЬ" in message.text:
                    if len(user["settings"]["commands"]) >= 10:
                        bot_send_message(bot, user["id"], "Больше десяти команд добавить нельзя!")
                        return True
                    bot_send_message(bot, user["id"], "Какую команду хотите добавить?", reply_markup=markups(["Назад🔙"]))
                    user_update(user, "settings:commands:add")
                    return True

                if "УДАЛИТЬ" in message.text:
                    if not user["settings"]["commands"]:
                        bot_send_message(bot, user["id"], "У вас нет команд для удаления")
                        return True
                    bot_send_message(bot, user["id"], "Какую команду хотите удалить?", reply_markup=markups(user["settings"]["commands"] + ["Назад🔙"]))
                    user_update(user, "settings:commands:delete")
                    return True

            def add(bot, message, user):
                if "НАЗАД" in message.text.upper():
                    return MessageHandler.Settings.Commands.to_main(bot, message, user)
                else:
                    bot_send_message(bot, user["id"], f"Команда {message.text} успешно добавлена", reply_markup=settings_markup)
                    user["settings"]["commands"].append(message.text)
                    user_update(user, "settings", json.dumps(user["settings"], indent=2))
                    return True

            def delete(bot, message, user):
                if "НАЗАД" in message.text.upper():
                    return MessageHandler.Settings.Commands.to_main(bot, message, user)
                elif message.text in user["settings"]["commands"]:
                    bot_send_message(bot, user["id"], f"Команда {message.text} успешно удалена", reply_markup=settings_markup)
                    user["settings"]["commands"].remove(message.text)
                    user_update(user, "settings", json.dumps(user["settings"], indent=2))
                    return True

def today(last_day = False):
    now = datetime.now().weekday() + 1
    if now == 7:
        now = 6
    if last_day:
        now -= 1
    if now == 0:
        now = 6
    return now

def weekday_thread():
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
            bot_send_message(bot, 847721936, f"Удаление расписания на {last_day}")
        time_last = weekday(today())
        time.sleep(2)

thread2 = Thread(target=weekday_thread)
thread2.start()

@bot.message_handler(content_types=["text"])
def handle_text(message):
    logging.info(f"{message.chat.id} {message.chat.first_name} |{message.text}|")
    message.text = message.text.strip().replace("  ", " ").replace("\t\t", "\t")
    user = get_user(message)
    if message.text.upper() == "МЕНЮ":
        user_update(user, "menu")
        bot_send_message(bot, user["id"], "Запуская меню", reply_markup=menu_markups(user))
        return
    if user["status"] not in ["settings:commands:add", "settings:commands:delete"]:
        message.text = message.text.upper()
    log(message, user)
    action = {
        "menu": MessageHandler.menu,
        "schedule:parallel": MessageHandler.Schedule.parallel,
        "schedule:symbol" : MessageHandler.Schedule.symbol,
        "schedule:day": MessageHandler.Schedule.day,
        "settings": MessageHandler.Settings.main,
        "settings:subscribe": MessageHandler.Settings.Subscribe.main,
        "settings:subscribe:add": MessageHandler.Settings.Subscribe.add,
        "settings:subscribe:delete": MessageHandler.Settings.Subscribe.delete,
        "settings:commands": MessageHandler.Settings.Commands.main,
        "settings:commands:add": MessageHandler.Settings.Commands.add,
        "settings:commands:delete": MessageHandler.Settings.Commands.delete
    }
    if action.get(user["status"]):
        try:
            if not action[user["status"]](bot, message, user):
                bot_send_message(bot, user["id"], "Не понял!")
        except Exception as err:
            logging.exception(err)
            bot_send_message(bot, user["id"], "Произошла ошибка")
    else:
        bot_send_message(bot, user["id"], f"Статус {user['status']} не найден!")
    return

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            sleep(0.3)
