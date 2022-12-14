from lib2to3.pytree import convert
from imessage_reader import fetch_data
import time
import sqlite3
import subprocess
from icalendar import Calendar, Event
import requests
from soccer_data_api import SoccerDataAPI
from datetime import datetime


print("STARTED")

con = sqlite3.connect("/Users/dariushaligholizadeh/Library/Messages/chat.db")
cur = con.cursor()

def results():
    return cur.execute("""
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
    JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
    JOIN message ON chat_message_join.message_id = message. "ROWID"
ORDER BY
    message_date ASC;
""")



# chat406398880183464830 = storytime

# guid = imessage.send("chat406398880183464830", "test")

def onCall(chat, message):
    
    applescript = (
    """
tell application "Messages"
	set targetBuddy to "{}"
	set targetService to id of 1st account whose service type = iMessage
	set textMessage to "{}"
	set theBuddy to participant targetBuddy of account id targetService
	send textMessage to theBuddy
end tell
""".format(chat, message)
    )
    
    args = [
        item
        for x in [("-e", l.strip()) for l in applescript.split("\n") if l.strip() != ""]
        for item in x
    ]
    proc = subprocess.Popen(["osascript"] + args, stdout=subprocess.PIPE)
    progname = proc.stdout.read().strip()

fd = fetch_data.FetchData()

my_data = fd.get_messages()

# for x in my_data:
#     # user id, message, date, service, account, is_from_me
#     user, msg, date, service, account, is_me = x;
#     if "2022-09-05" in date:
#         print(x);

def greater(first_time, second_time):
    #checking if second is greater than first

    x = [int(i) for i in first_time.split(":")]
    y = [int(i) for i in second_time.split(":")]

    if y[0] > x[0]:
        return True
    elif y[1] > x[1] and y[0] == x[0]:
        return True
    elif y[2] >= x[2] and y[1] == x[1] and y[0] == x[0]:
        return True
    else:
        return False

def greater_days(first_time, second_time):
    #checking if second is greater than first

    x = [int(i) for i in first_time.split("-")]
    y = [int(i) for i in second_time.split("-")]

    if y[0] > x[0]:
        return True
    elif y[1] > x[1] and y[0] == x[0]:
        return True
    elif y[2] >= x[2] and y[1] == x[1] and y[0] == x[0]:
        return True
    else:
        return False


def days(d):
    code_to_day = {
        "MO": "Monday",
        "TU": "Tuesday",
        "WE": "Wednesday",
        "TH": "Thursday",
        "FR": "Friday",
        "SA": "Saturday",
        "SU": "Sunday"
    }

    output = ""

    if len(d) > 1:
        if len(d) > 2:
            for day in range(len(d) - 1):
                output += "{}, ".format(code_to_day[day])
            output += "and {}".format(code_to_day[d[len(d)-1]])
        else:
            output += "{} and {}".format(code_to_day[d[0]], code_to_day[d[1]])
    else:
        output = "{}".format(code_to_day[d[0]])

    return output
    

now = datetime.now()

def convert_to_time(t):
    # print(t)
    if len(t.split(":")) > 2:
        return "{}:{} {}".format(str(int(t.split(":")[0]) - 12 if int(t.split(":")[0])>12 else int(t.split(":")[0])), 
        str(t.split(":")[1]),
        "PM" if int(t.split(":")[0])>12 else "AM")
    else:
        return "{}:{} {}".format(
            str(int(t.split(":")[0]) - 12 if int(t.split(":")[0])>12 else int(t.split(":")[0])),
            t.split(":")[1],
            "PM" if int(t.split(":")[0])>12 else "AM"
        )

while True:
    fd = fetch_data.FetchData()
    my_data = results().fetchall()

    soccer_data = SoccerDataAPI()

    now_days = now.strftime("%Y-%m-%d")
    now_hrs = now.strftime("%H:%M:%S")
    print('\n\nrunning @ ' + str(now))
    for x in my_data:
        # user id, message, date, service, account, is_from_me
        date, msg, is_me, chat = x;
        if now_days == date.split(" ")[0] and greater(now_hrs, date.split(" ")[1]): #and "!" == msg[0]:
            if msg == "!question":
                print('questioned')
                print(date)
                z = requests.get('https://facts-service.mmsport.voltaxservices.io/widget/properties/mentalfloss/random-facts?limit=20&exclude=')
                zz = z.json()['data'][0]['body']
                onCall(chat, zz)
                print(now)
                print(greater(now_hrs, date.split(" ")[1]))
            elif msg == "!youssef":
                for i in range(0,5):
                    onCall(chat, "duck youssef")
            elif msg == "!test":
                for i in range(0, 5):
                    onCall(chat, "test")
            elif msg == "!english premier" or msg == "!premierleague":
                # print(soccer_data.english_premier())
                text = ""
                teams = {}
                for x in soccer_data.english_premier():
                    teams[int(x["pos"])] = "{} is in pos {} with {} points and {}/{}/{} record.\n\n".format(x["team"], x["pos"], x["points"], x["wins"], x["losses"], x["draws"])
                
                for i in range(len(soccer_data.english_premier())):
                    text += teams[i+1]
                onCall(chat, text[:-2])
            elif msg == "!calendar" or msg == "!schedule":
                with open('my_classes.ics', 'r') as file:
                    gcal = Calendar.from_ical(file.read())

                    zz = ""
                    
                    for component in gcal.walk():
                        try:
                            # print(now_days, str(component["RRULE"]["UNTIL"][0]).split(" ")[0])
                            # print(greater_days(now_days, str(component["RRULE"]["UNTIL"][0]).split(" ")[0]))
                            if greater_days(now_days, str(component["RRULE"]["UNTIL"][0]).split(" ")[0]) == True:
                                keys = component.keys()
                                print(keys)
                                # print(convert_to_time(str(component.decoded("dtend")).split(" ")[1]))
                                print("{} class is {} in {} from {} to {}".format(
                                    component["DESCRIPTION"],
                                    days(component["RRULE"]["BYDAY"]),
                                    component["LOCATION"],
                                    convert_to_time(str(component.decoded('dtstart')).split(" ")[1]),
                                    convert_to_time(str(component.decoded("dtend")).split(" ")[1])
                                ))

                                zz = "{} class is {} in {} from {} to {}".format(
                                    component["DESCRIPTION"],
                                    days(component["RRULE"]["BYDAY"]),
                                    component["LOCATION"],
                                    convert_to_time(str(component.decoded('dtstart')).split(" ")[1]),
                                    convert_to_time(str(component.decoded("dtend")).split(" ")[1])
                                )

                                onCall(chat, zz)

                                # print(component.decoded('dtstart'), component.decoded('dtend'))
                        except:
                            ""
        # elif now_days == date.split(" ")[0] and greater(now_hrs, date.split(" ")[1]) and msg == "-":
        #     for i in range(0, 100):
        #         onCall(chat, "test!")
        #         print('test')
        # if msg == "!question":
        #     print(msg, chat, date)

    now = datetime.now()
    time.sleep(2)

# print(my_data)
