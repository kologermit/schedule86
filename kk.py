file = open("gmail.py", "r", encoding="utf-8")
l = file.read().split("kk1")
r = ''
last_kk = "kk0"
for i in range(len(l)):
	r += f"{l[i]}kk{i + 1}"
	last_kk = f"kk{i + 1}"
r = r.replace(last_kk, "")
file.close()
file = open("gmail.py", "w", encoding="utf-8")
file.write(r)
file.close()