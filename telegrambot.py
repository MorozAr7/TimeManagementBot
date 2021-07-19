import telebot
import datetime
from flask import Flask, request
import os


bot = telebot.TeleBot(token)
server = Flask(__name__)

Actual_date = 0
Actual_month = 0
DAYS_AMOUNT = 15


def work_with_dates():
    today = datetime.date.today()
    d1 = today.strftime("%d/%m")
    global Actual_date, Actual_month
    Actual_date = int(d1[0:2])
    Actual_month = int(d1[-2:])


work_with_dates()
list_days = list()


Month_days = {"1": (31, "JAN"), "2": (28, "FEB"), "3": (31, "MAR"), "4": (30, "APR"), "5": (31, "MAY"), "6": (30, "JUN"),
              "7": (31, "JUL"), "8": (31, "AUG"), "9": (30, "SEP"), "10": (31, "OCT"), "11": (30, "NOV"), "12": (31, "DEC")}


callback_change_dict = dict()
day_callback_and_activity_callback = dict()

SCHEDULE = dict()

Chosen_day = None
Chosen_date = None
Chosen_end_time = None
Chosen_start_time = None
Activity = None
DAY_IS_EXPECTED = True
TIME_START_IS_EXPECTED = True
TIME_END_IS_EXPECTED = True
ACTIVITY_IS_EXPECTED = True
MAIN_IS_EXPECTED = True
STATE = None
CALLBACK_ACTIVITY_TO_CHANGE = None
CHANGE_STATUS = None


@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("SHOW", callback_data='show'),
        telebot.types.InlineKeyboardButton("ADD", callback_data='add'),
        telebot.types.InlineKeyboardButton("CHANGE", callback_data='change'),
    )
    bot.send_message(message.chat.id, "MAIN MENU", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def process_calls(call):
    print(call.data)
    global STATE, Chosen_day, DAY_IS_EXPECTED, CALLBACK_ACTIVITY_TO_CHANGE, CHANGE_STATUS, DAY_IS_EXPECTED, TIME_START_IS_EXPECTED, TIME_END_IS_EXPECTED, ACTIVITY_IS_EXPECTED, MAIN_IS_EXPECTED
    days_callback = [str(i) for i in range(DAYS_AMOUNT)]
    if call.data == "show":
        STATE = "SHOW"
        choose_day(call.message)
    elif call.data == "add":
        STATE = "ADD"
        print(DAY_IS_EXPECTED, TIME_START_IS_EXPECTED, TIME_END_IS_EXPECTED, ACTIVITY_IS_EXPECTED, MAIN_IS_EXPECTED)
        choose_day(call.message)
    elif call.data == "change":
        STATE = "CHANGE"
        choose_day(call.message)
    elif call.data == "CANCEL":
        DAY_IS_EXPECTED = True
        TIME_START_IS_EXPECTED = True
        TIME_END_IS_EXPECTED = True
        ACTIVITY_IS_EXPECTED = True
        start_command(call.message)
        Chosen_day = None
        STATE = None
    elif call.data in days_callback:
        Chosen_day = list_days[int(call.data)]
        if STATE is "ADD":
            DAY_IS_EXPECTED = False
            bot.send_message(call.message.chat.id, str(Chosen_day[0]) + " " + Chosen_day[1] + "\n" + "Write the start time: ")
        elif STATE is "SHOW":
            find_in_schedule(call.message)
        elif STATE is "CHANGE":
            change_keyboard(int(call.data), call.message)
    elif call.data in day_callback_and_activity_callback:
        change_functions_keyboard(call.message, call.data)
        print(call.data, "CALL DATA")
        CALLBACK_ACTIVITY_TO_CHANGE = call.data
    elif call.data is "R":
        CHANGE_STATUS = "RENAME"
        bot.send_message(call.message.chat.id, "<b><i>Write new activity: </i></b>", parse_mode='HTML')
    elif call.data is "D":
        CHANGE_STATUS = "DELETE"
        delete_activity(call.message)
        bot.send_message(call.message.chat.id, "<b><i>Activity was successfully deleted</i></b>", parse_mode='HTML')
        print(SCHEDULE, "SCHEDULE after delete")
        start_command(call.message)
    elif call.data is "S":
        CHANGE_STATUS = "START"
    elif call.data is "E":
        CHANGE_STATUS = "END"
    elif call.data is "M":
        CHANGE_STATUS = "MAIN"
    elif call.data is "N":
        CHANGE_STATUS = "NOTMAIN"
    elif call.data == "MAIN":
        print("SOSAT")
        MAIN = True
        MAIN_IS_EXPECTED = True
        main_or_not_main(call.message, MAIN)
    elif call.data == "NOTMAIN":
        MAIN = False
        MAIN_IS_EXPECTED = True
        main_or_not_main(call.message, MAIN)
    return None


def main_or_not_main(message, MAIN):
    global TIME_START_IS_EXPECTED, TIME_END_IS_EXPECTED, ACTIVITY_IS_EXPECTED, DAY_IS_EXPECTED, STATE
    add_to_schedule(MAIN)
    add_to_callback_dict(list_days.index(Chosen_day), Chosen_end_time, Chosen_start_time)
    bot.send_message(message.chat.id, text="<b><i>Activity was added to schedule!</i></b>", parse_mode='HTML')
    start_command(message)
    TIME_END_IS_EXPECTED = True
    TIME_START_IS_EXPECTED = True
    ACTIVITY_IS_EXPECTED = True
    DAY_IS_EXPECTED = True
    STATE = None


@bot.message_handler(content_types=['text'])
def read_message(message):
    if STATE is "SHOW":
        pass
    elif STATE is "ADD":
        if Chosen_day is not None:
            add_new_activity(message)
        else:
            bot.send_message(message.chat.id, "You must choose the day!")
            choose_day(message)
    elif STATE is None:
        bot.send_message(message.chat.id, "Use the main menu!")
        start_command(message)
    elif STATE is "CHANGE":
        if CHANGE_STATUS is "RENAME":
            rename_activity(message.text)
            bot.send_message(message.chat.id, "<b><i>Activity was successfully renamed</i></b>", parse_mode='HTML')
            start_command(message)


def add_new_activity(message):
    global DAY_IS_EXPECTED, TIME_START_IS_EXPECTED, TIME_END_IS_EXPECTED, ACTIVITY_IS_EXPECTED, \
        Chosen_end_time, Chosen_date, Chosen_start_time, Activity, Chosen_day, STATE, callback_change_dict, MAIN_IS_EXPECTED
    if TIME_START_IS_EXPECTED and TIME_END_IS_EXPECTED and ACTIVITY_IS_EXPECTED and MAIN_IS_EXPECTED:
        Chosen_start_time = message.text
        Chosen_start_time = check_time_string(Chosen_start_time)
        if Chosen_start_time is False:
            bot.send_message(message.chat.id,
                             str(Chosen_day[0]) + " " + Chosen_day[1] + "\n" + "You wrote incorrect. Write the start time again: ")
        else:
            TIME_START_IS_EXPECTED = False
            bot.send_message(message.chat.id, str(Chosen_day[0]) + " " + Chosen_day[1] + "\n" + "Write the end time: ")
    elif not TIME_START_IS_EXPECTED and TIME_END_IS_EXPECTED and ACTIVITY_IS_EXPECTED and MAIN_IS_EXPECTED:
        Chosen_end_time = message.text
        Chosen_end_time = check_time_string(Chosen_end_time)
        if Chosen_end_time is False or not is_less_time(Chosen_start_time, Chosen_end_time):
            bot.send_message(message.chat.id,
                             str(Chosen_day[0]) + " " + Chosen_day[
                                 1] + "\n" + "You wrote incorrect. Write the end time again: ")
        else:
            TIME_END_IS_EXPECTED = False
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton("CANCEL AND BACK TO THE MAIN MENU", callback_data="CANCEL"))
            bot.send_message(message.chat.id, "<b><i>Write activity</i></b>", reply_markup=keyboard, parse_mode='HTML')
    elif not TIME_START_IS_EXPECTED and not TIME_END_IS_EXPECTED and ACTIVITY_IS_EXPECTED and MAIN_IS_EXPECTED:
        Activity = message.text
        ACTIVITY_IS_EXPECTED = False
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton("YES", callback_data="MAIN"),
                     telebot.types.InlineKeyboardButton("NO", callback_data="NOTMAIN")
                     )
        bot.send_message(message.chat.id, "Do you want to mark this activity like MAIN?",
                         reply_markup=keyboard)


def add_to_callback_dict(callback_chosen_day, end_time, start_time):
    if callback_chosen_day not in callback_change_dict.keys():
        callback_change_dict[callback_chosen_day] = {str(start_time) + " - " + str(end_time): ("del", "main", "rename", "chng end", "chng srt")}
        day_callback_and_activity_callback[str(callback_chosen_day) + " " + str(start_time) + " - " + str(end_time)] = ("del", "main", "rename", "chng end", "chng srt")
        print(str(callback_chosen_day) + " " + str(start_time) + " - " + str(end_time))
    else:
        callback_change_dict[callback_chosen_day][str(start_time) + " - " + str(end_time)]= ("del", "main", "rename", "chng end", "chng srt")
        day_callback_and_activity_callback[str(callback_chosen_day)+ " " + str(start_time) + " - " + str(end_time)] = ("del", "main", "rename", "chng end", "chng srt")


def change_keyboard(callback, message):
    key = list_days[callback]
    keyboard = telebot.types.InlineKeyboardMarkup()
    if key in SCHEDULE.keys():
        day_activities = SCHEDULE[list_days[callback]]
        for time in day_activities.keys():
            keyboard.add(telebot.types.InlineKeyboardButton(str(time) + " | " + str(day_activities[time][0]), callback_data = str(callback) + " " + time))
        keyboard.add(telebot.types.InlineKeyboardButton("BACK TO THE MAIN MENU", callback_data="CANCEL"))
        bot.send_message(message.chat.id, "CHOOSE WHICH ACTIVITY YOU WANT TO CHANGE", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, text="<i><b>There are no activities for this day yet!</b></i>", parse_mode='HTML')
        start_command(message)


def change_functions_keyboard(message, data):
    keyboard = telebot.types.InlineKeyboardMarkup()
    argument, counter = process_callback_activity()
    MAIN = SCHEDULE[list_days[int(argument)]][CALLBACK_ACTIVITY_TO_CHANGE[counter + 1:]][1]
    if not MAIN:
        keyboard.add(telebot.types.InlineKeyboardButton("RENAME",
                                                        callback_data="R"),
                     telebot.types.InlineKeyboardButton("CHANGE START TIME",
                                                        callback_data="S"),
                     telebot.types.InlineKeyboardButton("CHANGE END TIME",
                                                        callback_data="E"),
                     telebot.types.InlineKeyboardButton("MAKE MAIN",
                                                        callback_data="M"),
                     telebot.types.InlineKeyboardButton("DELETE",
                                                        callback_data="D"),
                     )
    else:
        keyboard.add(telebot.types.InlineKeyboardButton("RENAME",
                                                        callback_data="R"),
                     telebot.types.InlineKeyboardButton("CHANGE START TIME",
                                                        callback_data="S"),
                     telebot.types.InlineKeyboardButton("CHANGE END TIME",
                                                        callback_data="E"),
                     telebot.types.InlineKeyboardButton("REMOVE FROM MAIN",
                                                        callback_data="N"),
                     telebot.types.InlineKeyboardButton("DELETE",
                                                        callback_data="D"),
                     )
    bot.send_message(message.chat.id, "FUNC", reply_markup=keyboard)


def process_callback_activity():
    argument = ""
    counter = 0
    if CALLBACK_ACTIVITY_TO_CHANGE is not None:
        for symbol in CALLBACK_ACTIVITY_TO_CHANGE:
            if symbol is " ":
                break
            argument += symbol
            counter += 1

    return argument, counter


def rename_activity(activity_name):
    argument, counter = process_callback_activity()

    SCHEDULE[list_days[int(argument)]][CALLBACK_ACTIVITY_TO_CHANGE[counter + 1:]][0] = activity_name


def delete_activity(message):
    argument, counter = process_callback_activity()

    SCHEDULE[list_days[int(argument)]].pop(CALLBACK_ACTIVITY_TO_CHANGE[counter + 1:], 0)
    if len(SCHEDULE[list_days[int(argument)]]) is 0:
        SCHEDULE.pop(list_days[int(argument)], 0)
        bot.send_message(message.chat.id, text="<b><i>There are no activities for this day yet!</i></b>", parse_mode='HTML')


def is_less_time(timestr1, timestr2):
    time1int = int(timestr1[:2]) * 60 + int(timestr1[-2:])
    time2int = int(timestr2[:2]) * 60 + int(timestr2[-2:])
    print(time1int, time2int)
    if time1int >= time2int:
        return False
    return True


def check_time_string(time_str):
    required_syms = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ":", ";", ",", "_", "-", "/"]
    nums = required_syms[:10]
    syms = required_syms[10:]
    is_delimiter = False
    for symbol in time_str:
        if symbol not in required_syms:
            return False
        if symbol in syms:
            is_delimiter = True

    if not is_delimiter and (len(time_str) > 4 or len(time_str) < 3):
        print("ABORT")
        return False

    new_hours_str = ""
    new_mins_str = ""

    hours = True
    for symbol in time_str:
        if symbol in nums and hours:
            new_hours_str += symbol
        elif symbol in syms:
            hours = False
        elif symbol in nums and not hours:
            new_mins_str += symbol

    new_time_str = ""

    if not is_delimiter and len(time_str) is 4:
        new_time_str = time_str[:2] + ":" + time_str[-2:]
    else:
        if len(new_hours_str) < 2:
            new_time_str = "0" + new_hours_str + ":"
        else:
            new_time_str = new_hours_str + ":"

        if len(new_mins_str) < 2:
            new_time_str += (new_mins_str + "0")
        else:
            new_time_str += new_mins_str

    if int(new_time_str[0:2]) >= 24:
        return False
    elif int(new_time_str[-2:]) >= 59:
        return False

    return new_time_str


def add_to_schedule(MAIN):
    global Chosen_end_time, Chosen_date, Chosen_start_time, Activity, Chosen_day, SCHEDULE
    if MAIN is True:
        if Chosen_day not in SCHEDULE.keys():
            SCHEDULE[Chosen_day] = {str(Chosen_start_time) + " - " + str(Chosen_end_time): [Activity, True]}
        else:
            SCHEDULE[Chosen_day][str(Chosen_start_time) + " - " + str(Chosen_end_time)] = [Activity, True]
    else:
        if Chosen_day not in SCHEDULE.keys():
            SCHEDULE[Chosen_day] = {str(Chosen_start_time) + " - " + str(Chosen_end_time): [Activity, False]}
        else:
            SCHEDULE[Chosen_day][str(Chosen_start_time) + " - " + str(Chosen_end_time)] = [Activity, False]


def find_in_schedule(message):
    global STATE
    if Chosen_day in SCHEDULE.keys():
        day_activity = SCHEDULE[Chosen_day]
        for key in day_activity:
            if day_activity[key][1] is True:
                bot.send_message(message.chat.id, "<b><i>" + str(key) + " | " + str(day_activity[key][0] +"</i></b>"+ "\n"), parse_mode = "HTML")
            else:
                bot.send_message(message.chat.id, str(key) + " | " + str(day_activity[key][0] + "\n"))
    else:
        bot.send_message(message.chat.id, text="<b><i>There are no activities for this day yet!</i></b>", parse_mode='HTML')
    STATE = None
    start_command(message)


def choose_day(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    global list_days, Actual_date, Actual_month
    for day in range(Actual_date, Actual_date + DAYS_AMOUNT):
        if day > Month_days[str(Actual_month)][0]:
            DAY = day - Month_days[str(Actual_month)][0]
            MONTH = Month_days[str(Actual_month + 1)][1]
        else:
            DAY = day
            MONTH = Month_days[str(Actual_month)][1]
        list_days.append((DAY, MONTH))
    for index in range(0, 13, 3):
        keyboard.add(telebot.types.InlineKeyboardButton(str(list_days[index][0]) + " " + list_days[index][1], callback_data = str(index)),
                     telebot.types.InlineKeyboardButton(str(list_days[index + 1][0]) + " " + list_days[index + 1][1], callback_data = str(index + 1)),
                     telebot.types.InlineKeyboardButton(str(list_days[index + 2][0]) + " " + list_days[index + 2][1], callback_data = str(index + 2)),
                     )
    keyboard.add(telebot.types.InlineKeyboardButton("BACK TO THE MAIN MENU", callback_data="CANCEL"))
    bot.send_message(message.chat.id, "CHOOSE THE DAY", reply_markup=keyboard)


@server.route('/' + token, methods = ['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("url-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://mysterious-cliffs-42856.herokuapp.com/ ' + token)
    return "!", 200


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

#https://mysterious-cliffs-42856.herokuapp.com/