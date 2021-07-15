import telebot
import datetime


token = "1861615620:AAGQvhdnWD_o9m836l1vvBat4ohnyCHpMGM"
bot = telebot.TeleBot(token)


Actual_date = None
Actual_month = 0


def work_with_dates():
    today = datetime.date.today()
    d1 = today.strftime("%d/%m")
    global Actual_date, Actual_month
    Date = int(d1[0:2])
    Month = int(d1[-2:])
    print(Month)


Month_days = {"1": (31, "JAN"), "2": (28, "FEB"), "3": (31, "MAR"), "4": (30, "APR"), "5": (31, "MAY"), "6": (30, "JUN"),
              "7": (31, "JUL"), "8": (31, "AUG"), "9": (30, "SEP"), "10": (31, "OCT"), "11": (30, "NOV"), "12": (31, "DEC")}


work_with_dates()


SCHEDULE = {}
list_days = list()
STATE = None
DAY_IS_EXPECTED = True
MONTH_IS_EXPECTED = True
TIME_START_IS_EXPECTED = True
TIME_END_IS_EXPECTED = True
ACTIVITY_IS_EXPECTED = True

Showing_date = 0
Chosen_date = 0
Chosen_month = None
Chosen_time_start = 0
Chosen_time_end = 0
Action = None


@bot.message_handler(commands=['help'])
def help_command(message):
   keyboard = telebot.types.InlineKeyboardMarkup()
   keyboard.add(
       telebot.types.InlineKeyboardButton(
           'Message the developer', url='telegram.me/artiomtb'
       )
   )
   bot.send_message(
       message.chat.id,
       '1) To receive a list of available currencies press /exchange.\n' +
       '2) Click on the currency you are interested in.\n' +
       '3) You will receive a message containing information regarding the source and the target currencies, ' +
       'buying rates and selling rates.\n' +
       '4) Click “Update” to receive the current information regarding the request. ' +
       'The bot will also show the difference between the previous and the current exchange rates.\n' +
       '5) The bot supports inline. Type @<botusername> in any chat and the first letters of a currency.',
       reply_markup=keyboard
   )


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
def callback_worker(call):
    global STATE, Chosen_month
    if call.data == "show":
        STATE = "SHOW"
        bot.send_message(call.message.chat.id, "Choose date")
    elif call.data == "change":
        STATE = "CHANGE"
        change_schedule(call.message)
    elif call.data == "add":
        STATE = "ADD"
    elif call.data in list_days:
        Chosen_month = call.data


@bot.message_handler(content_types=['text'])
def read_message(message):
    global Chosen_date
    if STATE is "ADD":
        add_to_schedule(message)
    elif STATE is "SHOW":
        Chosen_date = str(message.text)
        show_schedule(message, Chosen_date)


def choose_month(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    global list_days
    for key in Month_days.keys():
        if int(key) >= Actual_month:
            list_month.append(Month_days[key][1])
    for month in list_month:
        telebot.types.InlineKeyboardButton(month, callback_data=month.lower()),

    bot.send_message(message.chat.id, "MONTH", reply_markup=keyboard)


def add_to_schedule(message):
    global Chosen_time_start, Chosen_time_end, DAY_IS_EXPECTED, TIME_START_IS_EXPECTED, TIME_END_IS_EXPECTED, ACTIVITY_IS_EXPECTED, Action, Chosen_date
    if MONTH_IS_EXPECTED and DATE_IS_EXPECTED and TIME_END_IS_EXPECTED and TIME_START_IS_EXPECTED and ACTIVITY_IS_EXPECTED:
        choose_month(message)

    elif DATE_IS_EXPECTED and TIME_END_IS_EXPECTED and TIME_START_IS_EXPECTED and ACTIVITY_IS_EXPECTED and not MONTH_IS_EXPECTED:
        Chosen_date = str(message.text)
        if check_date(Chosen_date):
            DATE_IS_EXPECTED = False
            bot.send_message(message.chat.id, "Choose time start")
        else:
            bot.send_message(message.chat.id, "Sorry, choose date again")
    elif TIME_START_IS_EXPECTED and not DATE_IS_EXPECTED and TIME_END_IS_EXPECTED and ACTIVITY_IS_EXPECTED:
        Chosen_time_start = str(message.text)
        if check_time_str(Chosen_time_start):
            TIME_START_IS_EXPECTED = False
            Chosen_time_start = process_time_string(Chosen_time_start)
            bot.send_message(message.chat.id, "Choose time end")
        else:
            bot.send_message(message.chat.id, "Sorry, choose time start again")
    elif TIME_END_IS_EXPECTED and not TIME_START_IS_EXPECTED and not DATE_IS_EXPECTED and ACTIVITY_IS_EXPECTED:
        Chosen_time_end = str(message.text)
        if check_time_str(Chosen_time_end):
            TIME_END_IS_EXPECTED = False
            Chosen_time_end = process_time_string(Chosen_time_end)
            bot.send_message(message.chat.id, "Write activity")
        else:
            bot.send_message(message.chat.id, "Sorry, choose time end again")
    elif ACTIVITY_IS_EXPECTED and not TIME_END_IS_EXPECTED and not TIME_START_IS_EXPECTED and not DATE_IS_EXPECTED:
        Action = message.text
        ACTIVITY_IS_EXPECTED = False
        add_activity(Chosen_date, Chosen_time_start, Chosen_time_end, Action, message)
        start_command(message)
        DATE_IS_EXPECTED = True
        TIME_END_IS_EXPECTED = True
        TIME_START_IS_EXPECTED = True
        ACTIVITY_IS_EXPECTED = True


def check_time_str(time_str):
    num_set = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ":", ";", ",", "_", "-"]
    for symbol in time_str:
        if symbol not in num_set:
            return False
    return True


def check_date(date):
    num_set = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    if len(date) > 2:
        return False
    for symbol in date:
        if symbol not in num_set:
            return False
    return True


def add_activity(date, time1, time2, action, message):
    bot.send_message(message.chat.id, "You have added a new activity to your schedule")
    time1_to_schedule = process_time_string(time1)
    time2_to_schedule = process_time_string(time2)
    if date not in SCHEDULE.keys():
        SCHEDULE[date] = {time1_to_schedule + " - " + time2_to_schedule: action}
    else:
        SCHEDULE[date][time1_to_schedule + " - " + time2_to_schedule] = action


def process_time_string(time_str):
    if len(time_str) is 2:
        return time_str + ":" + "00"
    elif len(time_str) is 3:
        return time_str[0:2] + ":" + time_str[2:] + "0"
    elif len(time_str) >= 4:
        return time_str[0:2] + ":" + time_str[-2:]


def show_schedule(message, chosen_date):
    if chosen_date in SCHEDULE.keys():
        day_activity = SCHEDULE[chosen_date]
        for key in day_activity:
            bot.send_message(message.chat.id, str(key) + ": " + str(day_activity[key] + "\n"))
    else:
        bot.send_message(message.chat.id, "There are no activities for this day yet")
    start_command(message)


def change_schedule(message):
    bot.send_message(message.chat.id, "Make some changes in schedule")


if __name__ == '__main__':
     bot.polling(none_stop=True)
