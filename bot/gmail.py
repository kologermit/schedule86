import imaplib, email, os, base64, telebot, json, time, excel_reader, logging
from DB import DB
from datetime import datetime
from config import *

bot = telebot.TeleBot(TOKEN)
database = DB(mysql)
senders = None
while senders is None:
	senders = database.select("config", "data", [["theme", "=", "teachers"]])
senders = json.loads(senders[0][0])
imap = imaplib.IMAP4_SSL(GM_HOST)
imap.login(GM_LOGIN, GM_PASSWORD)
admins = database.select("config", "data", [("theme", "=", "admins")])

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
        logging.info(err)

if admins:
	admins = json.loads(admins[0][0])
for key in admins:
	try:
		bot_send_message(bot, key, f"Произошёл запуск почты")
	except:
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
		"ВН": "ВСЯ НЕДЕЛЯ"
	}).get(text.upper())

def main():
	flag = False
	while not flag:
		for i in senders:
			status, select_data = imap.select("inbox")
			status, search_data = imap.search(None, 'FROM', i)
			if search_data[0] != b"":
				logging.info(i)
				flag = True
				sender = {"email": i, "id": senders[i]}
	flag = False
	log_query = {
		"sender": sender,
		"filelist": [],
		"date": datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
	}
	logging.info(f"Sender: {sender}")
	status, msg_data = imap.fetch("1", '(RFC822)')
	mail = email.message_from_bytes(msg_data[0][1])
	if mail.is_multipart():
		filelist = []
		for part in mail.walk():
			content_type = part.get_content_type()
			filename = part.get_filename()
			if "UTF-8" in str(filename).upper():
				f = filename.split("?")
				filename = ""
				for i in f:
					if not i.replace("=", "").upper() in ["B", "UTF-8"]:
						filename += base64.b64decode(i).decode()
			if filename:
				filelist.append(filename)
				log_query["filelist"].append(filename)
				with open(filename, 'wb') as new_file:
					new_file.write(part.get_payload(decode=True))
	logging.info(filelist)
	database.insert("log", ["text"], [[json.dumps(log_query, indent=2)]])
	imap.select("inbox", readonly = False)
	result, data = imap.search(None, "ALL")
	ids = data[0]
	id_list = ids.split()
	for mail_id in id_list:
		imap.store(mail_id, '+FLAGS', '\\Deleted')
	imap.expunge()
	for filename in filelist:
		bot_send_message(bot, sender["id"], f"Файл {filename} принят на обработку")
		if not filename.endswith(".xls"):
			bot_send_message(bot, sender["id"], "Расширение файла не .xls!")
			break
		filename = filename.replace(".xls", "")
		filename_data = [i for i in filename.split(" ") if i]
		if len(filename_data) < 3:
			bot_send_message(bot, sender["id"], "Не хватает параметров! (3)")
			return True
		day = weekday(filename_data[0].upper())
		if day in ["ВСЯ НЕДЕЛЯ", None]:
			bot.send_messge(sender["id"], "Неверный параметр [ДЕНЬ]!")
			return True
		edited = None
		if filename_data[1].upper() not in ["EDITED", "STANDART", "EDIT", "ИЗМЕНЕНИЯ", "ОСНОВНОЕ", "СТАНДАРТНОЕ", "ИЗМЕНЕНИЕ"]:
			bot_send_message(bot, sender["id"], "Неверный параметр [ОСНОВНОЕ/ИЗМЕНЕНИЯ]!")
			return True
		if filename_data[1].upper() in ["EDITED", "EDIT", "ИЗМЕНЕНИЯ", "ИЗМЕНЕНИЕ"]:
			edited = True
		else:
			edited = False
		is_classes = None
		if filename_data[2].upper() not in ["CLASS", "CLASSES", "КЛАСС", "КЛАССЫ", "TEACHERS", "TEACHER", "TEACH", "УЧИТЕЛЯ", "УЧИТЕЛЬ"]:
			bot_send_message(bot, sender["id"], "Неверный параметр [КЛАССЫ/УЧИТЕЛЯ]!")
			return True
		if filename_data[2].upper() in ["CLASS", "CLASSES", "КЛАСС", "КЛАССЫ"]:
			is_classes = True
		else:
			is_classes = False
		if is_classes:
			excel_reader.read_classes(bot, sender, filename + ".xls", day, edited)
		else:
			excel_reader.read_teachers(bot, sender, filename + ".xls", day, edited)
	flag = False