from config import *
from DB import DB
import json
database = DB(mysql)
classes = database.select(table="config", columns=["data"], where=[['theme', '=', 'classes']])
if not classes:
	print("Classes not found")
	exit()
classes = json.loads(classes[0][0])
test_schedule = """{
  "standart": {
    "\u041f\u041e\u041d\u0415\u0414\u0415\u041b\u042c\u041d\u0418\u041a": [
    ],
    "\u0412\u0422\u041e\u0420\u041d\u0418\u041a": [
    ],
    "\u0421\u0420\u0415\u0414\u0410": [
    ],
    "\u0427\u0415\u0422\u0412\u0415\u0420\u0413": [
    ],
    "\u041f\u042f\u0422\u041d\u0418\u0426\u0410": [
    ],
    "\u0421\u0423\u0411\u0411\u041e\u0422\u0410": [
    ]
  },
  "edited": {}
}"""
for parallel in classes:
	for symbol in classes[parallel]:
		database.insert(table="schedule_classes", columns=["parallel", "symbol", "schedule", "subscribe"],
			values=[[parallel, symbol, test_schedule, "[]"]])