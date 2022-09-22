import xlrd
import imaplib
import email
import os
import base64, telebot, BD_query, json
from config import *
import 
import 
import time
from datetime import datetime
bot = telebot.TeleBot(TOKEN)
senders = BD_query.BD_query(BD_query.get_sql(**mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "teachers")])
print(senders)
senders = json.loads(senders[0][0])
imap = imaplib.IMAP4_SSL("imap.gmail.com")
imap.login(GM_LOGIN, GM_PASSWORD)
def erase_null(line):
	if str(type(line)) == "<class 'float'>":
		return int(line)
	return line
def get_sql():
	return BD_query.get_sql(**mysql_config)

def is_num(line):
	try:
		float(line)
		return True
	except:
		
		return False

def is_date(line):
	# dd.mm.yyyy
	# dd/mm/yyyy
	if len(line) < 8 or len(line) > 10:
		return False
	if line.count(".") != 2 and line.count("/") != 2:
		return False
	if line.count(".") == 2:
		line = line.split('.')
	else:
		line = line.split('/')
	if is_num(line[0]) == False or is_num(line[1]) == False or is_num(line[2]) == False:
		return False
	line = [int(line[0]), int(line[1]), int(line[2])]
	if line[1] < 1 or line[1] > 12 or line[2] < 2020 or line[2] > 2021:
		return False
	if line[1] in [1, 3, 5, 7, 8, 10, 12] and (line[0] < 1 or line[0] > 31):
		return False
	if line[1] in [4, 6, 9, 11] and (line[0] < 1 or line[0] > 30):
		return False
	if line[2] % 4 == 0:
		if line[2] % 400 != 0: 
			if line[1] == 2 and (line[0] < 1 or line[0] > 29):
				return False
			else:
				return line
	if line[1] == 2 and (line[0] < 1 or line[0] > 28):
		return False
	return line
def is_class_name(classes, line):
	abc = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
	line = line.strip().upper()
	size = len(line)
	if size <= 1 or size > 3:
		return False
	if size == 2 and is_num(line[0]):
		if classes.get((line[0])) != None:
			if line[1] in classes.get((line[0])):
				return True
	if size == 3 and is_num(line[0:2]) and line[2] in abc:
		if classes.get((line[0:2])) != None:
			if line[2] in classes.get((line[0:2])):
				return True
	
	return False
def is_week_day(line):
	arr = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ"]
	return line.upper() in arr
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
def week_min(line):
	if line == 'ПН':
		return "ПОНЕДЕЛЬНИК"
	if line == 'ВТ':
		return "ВТОРНИК"
	if line == 'СР':
		return "СРЕДА"
	if line == 'ЧТ':
		return "ЧЕТВЕРГ"
	if line == 'ПТ':
		return "ПЯТНИЦА"
	if line == 'СБ':
		return "СУББОТА"
	return line
def words(line):
	answer = []
	line = line.strip()
	a = next_word(line)
	while (a[0]):
		answer.append(a[0])
		a = next_word(a[1])
	return answer

admins = BD_query.BD_query(BD_query.get_sql(**mysql_config), "SELECT", "info", columns="text", where=[("theme", "=", "admins")])
if admins:
    admins = json.loads(admins[0][0])
for key in admins:
    try:
    	bot.send_message(key, f"Произошёл запуск почты")
    except:
    	pass

while True:
	flag = False
	while not flag:
		for i in senders:
			status, select_data = imap.select("inbox")
			status, search_data = imap.search(None, 'FROM', i)
			if search_data[0] != b"":
				print(i)
				flag = True
				sender = i
				sender_id = senders[i]
	log_query = {
		"sender": sender,
		"sender_id": sender_id,
		"filelist": [],
		"date": datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
	}
	print(f"Sender: {sender}")
	status, msg_data = imap.fetch("1", '(RFC822)')
	mail = email.message_from_bytes(msg_data[0][1])
	if mail.is_multipart():
		filelist = []
		for part in mail.walk():
			print(part)
			content_type = part.get_content_type()
			print(content_type)
			filename = part.get_filename()
			print(filename)
			if "UTF-8" in str(filename):
				f = filename.split("?")
				filename = ""
				for i in f:
					if not i.replace("=", "") in ["B", "UTF-8"]:
						filename += base64.b64decode(i).decode()
			print(filename)
			if filename:
				print(f"CT: {content_type}")
				print(f"filename: {filename}")
				filelist.append(filename)
				log_query["filelist"].append(filename)
				with open(filename, 'wb') as new_file:
					new_file.write(part.get_payload(decode=True))
	else:
		print(None)
	BD_query.BD_query(get_sql(), "INSERT", "log_query", data=[{"text": json.dumps(log_query, indent=2).replace('\\\\', '')}])
	imap.select("inbox", readonly = False)
	result, data = imap.search(None, "ALL")
	ids = data[0]
	id_list = ids.split()
	 
	for mail_id in id_list:
		imap.store(mail_id, '+FLAGS', '\\Deleted')
	imap.expunge()
	for filename in filelist:
		bot.send_message(sender_id, f"Файл {filename} принят на обработку")
		edited = None
		day = None
		name = words(filename.replace(".xls", ""))
		for i in range(len(name)):
			name[i] = name[i].upper()
		# print(name)
		for i in name:
			if is_week_day(i):
				day = week_min(i)
				break
		for i in name:
			if i in ["STANDART", "ОСНОВНОЕ", "ИМЕНЕНИЯ", "ИЗМЕНЕНИЕ", "EDITED"]:
				if i in ["STANDART", "ОСНОВНОЕ"]:
					edited = 'standart'
				else:
					edited = 'edited'
				break
		for i in name:
			if i in ["TEACHERS", "TEACHER", "УЧИТЕЛЬ", "УЧИТЕЛЯ"]:
				is_teachers = True
				break
			elif i in ["CLASSES", "CLASS", "КЛАССЫ", "КЛАСС"]:
				is_teachers = False
				break
			is_teachers = None
		if None in [is_teachers, day, edited]:
			bot.send_message(sender_id, f"Что-то неправильно в файле {filename}")
			continue
			result = None
		if is_teachers == False:
			classes = BD_query.BD_query(BD_query.get_sql(**mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "classes")])
			chat_id = BD_query.BD_query(BD_query.get_sql(**mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "teachers")])
			if classes != []:
				classes = classes[0][0]
			classes = json.loads(classes)
			rb = xlrd.open_workbook(filename, formatting_info=True)
			sheet = rb.sheet_by_index(0)
			chat_id = None
			data = {}
			classes_in_excel = []
			for i in range(sheet.nrows):
				for j in range(sheet.ncols):
					key = sheet.cell_value(i, j)
					if is_class_name(classes, str(key)):
						classes_in_excel.append(key)
						data[key] = []
						# try:
						for i1 in range(1, 17, 2):
							if str(sheet.cell_value(i + i1, j)) == "":
								data[key].append("-")
								continue

							lesson = f"{erase_null(sheet.cell_value(i + i1, j))} "
							data[key].append(lesson)
						# except:
						# 	pass
						while len(data[key]) and data[key][-1] == "-":
							data[key].pop()
			answer = f"День: {day}\nРасписание: {edited}\nКлассы: {classes_in_excel}"
			bot.send_message(sender_id, answer)
			users = BD_query.BD_query(get_sql(), "SELECT", "users", columns=["id", "settings"])
			for i in range(len(users)):
				temp = {
					"id": users[i][0],
					"featured_classes": json.loads(users[i][1])["featured_classes"]
				}
				users[i] = temp
			for key in users:
				for key2 in key["featured_classes"]:
					if day in ["ПЯТНИЦА", "СУББОТА", "СРЕДА"]:
						day = day[:len(day) - 1] + "У"
					if key2 in data.keys():
						if is_num(key2[0:2]):
							class_n = int(key2[0:2])
						else:
							class_n = int(key2[0])
						class_b = key2[-1]
						js = data
						if day in ["ПЯТНИЦА", "СУББОТА", "СРЕДА"]:
							day = day[:len(day) - 1] + "У"
						if edited == 'edited':
							answer = f'Изменения в расписании на {day} для {key2}:\n'
						else:
							answer = f'Изменения в основном расписании на {day} для {key2}:\n'
						if len(data[key2]) == 0:
							for l in range(6):
								data[key2].append('-')
						for i in range(len(data[key2])):
							answer += f"{i + 1}. {data[key2][i]}\n"
						try:
							try:
								bot.send_message(key["id"], answer)
							except:
								pass
						except:
							pass
					if day in ["ПЯТНИЦУ", "СУББОТУ", "СРЕДУ"]:
						day = day[:len(day) - 1] + "А"
			for key in list(data.items()):
				if len(key[0]) == 3:
					class_n = int(key[0][0:2])
					class_b = key[0][2]
				else:
					class_n = int(key[0][0])
					class_b = key[0][1]
				answer = BD_query.BD_query(get_sql(), "SELECT", "classes", columns="schedule", where=[("class_b", "=", class_b), ("class_n", "=", class_n)])
				if answer == []:
					raise Exception("BD_query: Error")
				else:
					answer = answer[0][0]
				answer = json.loads(answer)
				answer[edited][day.upper()] = key[1]
				r = BD_query.BD_query(get_sql(), "UPDATE", "classes", where=[("class_b", "=", class_b), ("class_n", "=", class_n)], data=[("schedule", json.dumps(answer, indent=2).replace('\\\\', ''))])
		else:
			teachers = BD_query.BD_query(BD_query.get_sql(**mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "teachers_table")])
			if teachers != []:
				teachers = teachers[0][0]
			teachers = json.loads(teachers.upper())
			rb = xlrd.open_workbook(filename, formatting_info=True)
			sheet = rb.sheet_by_index(0)
			data = {}
			for i in range(sheet.nrows):
				for j in range(sheet.ncols):
					if str(sheet.cell_value(i, j)).upper().replace(',', '.') in teachers:
						schedule = []
						for ii in range(1, 17, 2):
							try:
								s = f"{str(sheet.cell_value(i, j + ii))}"
								if s.strip():
									schedule.append(s)
								else:
									schedule.append("-")
							except:
								pass
						while len(schedule) and schedule[-1] == '-':
							schedule.pop(-1)
						data[sheet.cell_value(i, j)] = schedule
			answer = f"День: {day}\nРасписание: {edited}\nУчителя: {data.keys()}"
			bot.send_message(sender_id, answer)
			k = list(data.keys())
			for i in k:
				teacher = BD_query.BD_query(get_sql(), "SELECT", "teachers", columns=["name", "schedule", "subscribe"], where=[("name", "RLIKE", i)])
				if not teacher:
					continue
				teacher = list(teacher[0])
				teacher[1] = json.loads(teacher[1])
				teacher[2] = json.loads(teacher[2])
				teacher[1][edited][day] = data[i]
				BD_query.BD_query(get_sql(), "UPDATE", "teachers", where=[("name", "RLIKE", i)], data=[("schedule", json.dumps(teacher[1], indent=2).replace('\\\\', ''))])
				if edited == 'edited':
					answer = f"Изменения в расписаниии для учителя {i} на {day}:\n"
				else:
					answer = f"Изменения в основном расписаниии для учителя {i} на {day}:\n"
				if len(data[i]) == 0:
					for j in range(6):
						data[i].append(i)
				for j in range(len(data[i])):
					answer += f"{j + 1}. {data[i][j]}\n"
				for j in teacher[2]:
					try:
						try:
							bot.send_message(j, answer)
						except:
							pass
					except:
						pass
		bot.send_message(sender_id, f"Файл {filename} обработан")
		os.remove(filename)

