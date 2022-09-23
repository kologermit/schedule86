import config
import requests
import json
from datetime import datetime
def main():
	key = config.API_KEY
	url = "http://api.openweathermap.org/data/2.5/weather"
	r = requests.get(url, params={"lat": 56.875299, "lon": 53.219367, "appid": key, "units": "metric", "lang": "ru"})
	r = json.loads(r.content)
	if r["cod"] == 200:
		return {"weather": r["weather"][0]["main"], "weather_d": r["weather"][0]["description"], "temp": r["main"]["temp"], "wind_speed": r["wind"]["speed"]}
	else:
		return None

def okonchanie(temp):
	temp = abs(temp)
	if temp % 10 == 1 and temp % 100 != 11:
		return ""
	elif temp % 10 >= 2 and temp % 10 <= 4 and temp % 100 >= 12 and temp % 100 <= 14:
		return "а"
	else:
		return "ов"

def where_fizra():
	data = main()
	if data == None:
		return None
	now  = datetime.now().month
	if now >= 12 or now <= 3 and data['temp'] >= -15:
		return f"Похоже, что на улице зима. \n<b>Время кататься на лыжах или бегать вокруг школы.</b>\nЗа окном {data['temp']} градус{okonchanie(data['temp'])}"
	elif now >= 12 or now <= 3 and data['temp'] <= -15:
		return f"В такой мороз лучше не гулять.\n<b>Поэтому занятие наверное будет в зале.</b>\nЗа окном {data['temp']} градус{okonchanie(data['temp'])}"
	elif data["weather"] == "Rain":
		return f"На улице дождь.\nОднозначно не улица.\n<b>Поэтому занятие наверное будет в зале.</b>\nЗа окном {data['temp']} градус{okonchanie(data['temp'])}"
	elif data["weather"] == "Clouds":
		return f"На улице облачно.\nДумаю, что скоро может нагрянуть дождь.\n<b>Лучше провести занятие в зале.</b>\nЗа окном {data['temp']} градус{okonchanie(data['temp'])}"
	elif data["weather"].upper() in ["CLEAR", "PARTY CLOUD", "PARTY CLOUDS"]:
		return f"Небо чисто.\nПочему бы и не погулять?\n<b>Думаю, что занятие будет на улице.</b>\nЗа окном {data['temp']} градус{okonchanie(data['temp'])}"
	else:
		return f"<b>Даже не знаю, что за погода на улице, но за окном</b> {data['temp']} градус{okonchanie(data['temp'])}"
