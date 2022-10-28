import os
import xlrd
import json
from DB import DB
from config import mysql

def json_loads(data):
    try:
        return json.loads(data)
    except:
        return None

def is_class_name(classes, line):
    data = []
    for i in [[f"{i}{j}".upper() for j in classes[i]] for i in classes]:
        data += i
    return line.upper() in data

def read_classes(bot, user, path, day, edited):
    database = DB(mysql)
    classes = database.select("config", "data", [["theme", "=", "classes"]])
    if not classes:
        bot.send_message(user["id"], "Произошла ошибка получения классов!")
        print(classes)
        return True
    classes = json_loads(classes[0][0])
    if type(classes) != type({}):
        bot.send_message(user["id"], "Произошла ошибка декодирования классов!")
        return True
    try:
        rd = xlrd.open_workbook(path, formatting_info=True)
        sheet = rd.sheet_by_index(0)
    except:
        bot.send_message(user["id"], "Не получилось открыть файл")
        os.remove(path)
        return
    data = {}
    classes_in_excel = []
    for i in range(sheet.nrows):
        for j in range(sheet.ncols):
            key = str(sheet.cell_value(i, j))
            if is_class_name(classes, key):
                classes_in_excel.append(key)
                data[key] = []
                for i1 in range(1, 17, 2):
                    try:
                        if str(sheet.cell_value(i + i1, j)) == "":
                            data[key].append("-")
                        else:
                            data[key].append(str(sheet.cell_value(i + i1, j)))
                    except:
                        pass
                while data[key][-1] == "-":
                    data[key] = data[key][:-1]
    bot.send_message(user["id"], f"Полученные классы: {str(list(data))}")
    for i in data:
        base_data = database.select("schedule_classes", ["schedule", "subscribe"], where=[["parallel", "=", int(i[:-1])], ["symbol", "=", i[-1]]], limit=1)
        if not base_data:
            continue
        subscribe = json.loads(base_data[0][1])
        base_data = json.loads(base_data[0][0])
        base_data["edited" if edited else "standart"][day] = data[i]
        # print(int(i[:-1]))
        # print(i[-1])
        database.update("schedule_classes", {"schedule": json.dumps(base_data, indent=2)}, where=[["parallel", "=",int(i[:-1])], ["symbol", "=", i[-1]]])
        for j in subscribe:
            try:
                answer = f"<b>Изменения в {'стандартном ' if edited == False else ''}расписании для {i} класса:</b>\n"
                for k in range(len(data[i])):
                    answer += f"<b>{k + 1}.</b> {data[i][k]}\n"
                bot.send_message(j, answer, parse_mode="HTML")
            except:
                pass
    os.remove(path)
    del database
    pass

def read_teachers(bot, user, path, day, edited):
    database = DB(mysql)
    teachers = database.select("teachers", ["name", "subscribe", "schedule"])
    if not teachers:
        bot.send_message(user["id"], "Проблема получения данных учителей")
        os.remove
        return False
    try:
        rd = xlrd.open_workbook(path, formatting_info=True)
        sheet = rd.sheet_by_index(0)
    except:
        bot.send_message(user["id"], "Не получилось открыть файл")
        os.remove(path)
        return
    answer = []
    for k in teachers:
        name = k[0]
        subscribe = json.loads(k[1])
        schedule = json.loads(k[2])
        flag = False
        for i in range(sheet.nrows):
            if flag:
                break
            for j in range(sheet.ncols):
                if flag:
                    break
                try:
                    sheet.cell_value(i, j)
                except:
                    continue
                if name == sheet.cell_value(i, j):
                    answer.append(name)
                    flag = True
                    data = []
                    for k in range(1, 18, 2):
                        try:
                            data.append(sheet.cell_value(i, j + k))
                            if data[-1] == "":
                                data[-1] = "-"
                        except:
                            pass
                    count = 0
                    for p in data[::-1]:
                        if p == "-":
                            count += 1
                        else:
                            break
                    if count:
                        data = data[:-count]
                    if not data:
                        data = ["-", "-", "-", "-", "-", "-"]
                    for s in subscribe:
                        answer = f"<b>Изменения в {'стандартном ' if edited == False else ''}расписании для {name}:</b>\n"
                        for p in range(len(data)):
                            answer += f"<b>{p + 1}.</b> {data[p]}\n"
                        try:
                            bot.send_message(s, answer, parse_mode="HTML")
                        except:
                            pass
                    schedule["edited" if edited else "standart"][day] = data
                    database.update("teachers", {"schedule": json.dumps(schedule, indent=2)}, [["name", "=", name]])
    # bot.send_message(user["id"], f"Расписание: teachers\nИзменения: {edited}\nДень: {day}")
    bot.send_message(user["id"], "Всё ок")
    os.remove(path)
    del database