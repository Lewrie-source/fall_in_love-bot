from keyboa import *
from telebot import *
from additionally import *
from db import *
from random import *
from datetime import *
import configparser
import os

config = configparser.ConfigParser()
config.read("config.ini")

bot = telebot.TeleBot(str(config['Bot']['token']))


# region Additionally

def extract_arg(arg: string) -> string:
    return arg.split(' ')[1:]


months = {
    "1": 31,
    "2": 29,
    "3": 31,
    "4": 30,
    "5": 31,
    "6": 30,
    "7": 31,
    "8": 31,
    "9": 30,
    "10": 31,
    "11": 30,
    "12": 31
}

months_name = {
    "1": "Январь",
    "2": "Февраль",
    "3": "Март",
    "4": "Апрель",
    "5": "Май",
    "6": "Июнь",
    "7": "Июль",
    "8": "Авугст",
    "9": "Сентябрь",
    "10": "Октябрь",
    "11": "Ноябрь",
    "12": "Декабрь"
}


def relation_check(m):
    if get_record("fil_bot", "fil", "relation_date", ["id"], [m.from_user.id])[0][0] != "0":
        return True
    else:
        return False


def kbbut(name, cb_data='0'):
    return telebot.types.InlineKeyboardButton(name, callback_data=cb_data)


def create_calendar(month, year):
    max_days = months[f"{month}"]
    weekday = datetime(int(year), int(month), 1).weekday()
    btns = []
    btns.append([kbbut(f'{year}', cb_data=f'0-{month}-{year}-calendar'),
                 kbbut(f'{months_name[f"{month}"]}', cb_data=f'1-{month}-{year}-calendar')])
    btns.append([kbbut("ПН"), kbbut("ВТ"), kbbut("СР"), kbbut("ЧТ"), kbbut("ПТ"), kbbut("СБ"), kbbut("ВС")])
    days = []
    for i in range(1, max_days + weekday + 1):
        if i <= weekday:
            days.append(kbbut(" "))
        else:
            days.append(kbbut(i - weekday, f"{i - weekday}-{month}-{year}-calendardate"))
    space_ac = len(days)
    for i in range(1, 8):
        if space_ac % 7 == 0:
            break
        else:
            space_ac += 1
    for i in range(0, space_ac - len(days)):
        days.append(kbbut(" "))
    month_nametag = Keyboa(items=btns).keyboard
    month_calendar = Keyboa(items=days, items_in_row=7).keyboard
    keyboard = Keyboa.combine(keyboards=(month_nametag, month_calendar))
    return keyboard


# endregion


@bot.message_handler(commands=["start"])
def start(m):
    status = extract_arg(m.text)
    if add_record("fil_bot", "fil", ["id"], [m.from_user.id], check_existence=True):
        bot.send_message(m.from_user.id,
                         f'🎉 <b>Вы были зарегистрированы в нашем боте!</b>\nСпасибо, за то что выбрали нас\n\n'
                         f'💌 Пусть ваш партнер перейдет по этой ссылке, чтобы вы зарегистрировали отношения!\nhttps://t.me/relations_fil_bot?start={m.from_user.id}',
                         parse_mode="html")
    else:
        bot.send_message(m.from_user.id, f"💓 Вы уже зарегистрированы в нашем боте, но спасибо что вернулись!")
    if status != [] and int(get_record("fil_bot", "fil", "partner_id", ["id"], [m.from_user.id])[0][0]) == 0:
        date = datetime.now().today()
        date_str = f"{date.day}.{date.month}.{date.year}"
        bot.send_message(m.from_user.id,
                         "💝 <b>Поздравляю, вы зарегистрировали свои отношения!</b>\nЧтобы изменить дату начала отношений, используйте команду <i>/new_date</i>",
                         parse_mode="html")
        bot.send_message(status[0],
                         "💝 <b>Поздравляю, вы зарегистрировали свои отношения!</b>\nЧтобы изменить дату начала отношений, используйте команду <i>/new_date</i>",
                         parse_mode="html")
        edit_record("fil_bot", "fil", ["partner_id", "relation_date"], [status[0], date_str], "id", m.from_user.id)
        edit_record("fil_bot", "fil", ["partner_id", "relation_date"], [m.from_user.id, date_str], "id", status[0])
    else:
        bot.send_message(m.from_user.id, f"💓 Вы уже состоите в отношениях!")


@bot.message_handler(commands=["relation_info"])
def relation_info(m):
    if relation_check(m):
        dates = datetime.strptime(get_record("fil_bot", "fil", "relation_date", ["id"], [m.from_user.id])[0][0],
                                  '%d.%m.%Y')
        days = datetime.now().date() - dates.date()
        kises = get_record("fil_bot", "fil", "kisses", ["id"], [m.from_user.id])[0][0]
        hugs = get_record("fil_bot", "fil", "hugs", ["id"], [m.from_user.id])[0][0]
        bot.send_message(m.from_user.id, f"💝 <b>Информация о ваших отношениях</b>\n"
                                         f"📆 {dates.day}.{dates.month}.{dates.year}\n"
                                         f"💑 Вместе: {days.days + 1}\n"
                                         f"😘 Поцелуев: {kises}\n"
                                         f"🤗 Обнимашек: {hugs}\n", parse_mode="html")
    else:
        bot.send_message(m.from_user.id, "😥 Вы не состоите в отношениях")


@bot.message_handler(commands=["admin_panel"])
def admin_panel(m):
    if int(get_record("fil_bot", "fil", "is_admin", ["id"], [m.from_user.id])[0][0]) == 1:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(kbbut("🖼 Добавить парные аватарки", "1-adm"), kbbut("🎞 Добавить в список просмотра", "2-adm"))
        bot.send_message(m.from_user.id, "👤 <b>Админ панель</b>", parse_mode="html", reply_markup=keyboard)


@bot.message_handler(commands=["minigames"])
def minigames(m):
    if relation_check(m):
        keyboard = telebot.types.InlineKeyboardMarkup()
        btns = []
        btns.append(telebot.types.InlineKeyboardButton('🎲', callback_data='🎲-games'))
        btns.append(telebot.types.InlineKeyboardButton('🎯', callback_data='🎯-games'))
        btns.append(telebot.types.InlineKeyboardButton('🏀', callback_data='🏀-games'))
        btns.append(telebot.types.InlineKeyboardButton('⚽', callback_data='⚽-games'))
        btns.append(telebot.types.InlineKeyboardButton('🎳', callback_data='🎳-games'))
        btns.append(telebot.types.InlineKeyboardButton('🎰', callback_data='🎰-games'))
        keyboard.add(btns[0], btns[1])
        keyboard.add(btns[2], btns[3])
        keyboard.add(btns[4], btns[5])
        bot.send_message(m.from_user.id, "🎰 Список миниигр:", reply_markup=keyboard)
    else:
        bot.send_message(m.from_user.id, "😥 Вы не состоите в отношениях")


@bot.message_handler(commands=["random_m_pfps"])
def random_m_pfps(m):
    if relation_check(m):
        ran = randint(1, (len(os.listdir("matching_pfps")) / 2))
        bot.send_media_group(m.chat.id, [telebot.types.InputMediaPhoto(open(f'matching_pfps/{ran}0.jpg', 'rb')),
                                         telebot.types.InputMediaPhoto(open(f'matching_pfps/{ran}1.jpg', 'rb'))])
    else:
        bot.send_message(m.from_user.id, "😥 Вы не состоите в отношениях")


@bot.message_handler(commands=["random_to_watch"])
def random_to_watch(m):
    if relation_check(m):
        keyboard = telebot.types.InlineKeyboardMarkup()
        btns = []
        btns.append(telebot.types.InlineKeyboardButton('🎥 Фильмы', callback_data='films-wtw'))
        btns.append(telebot.types.InlineKeyboardButton('🎞 Сериалы', callback_data='serials-wtw'))
        btns.append(telebot.types.InlineKeyboardButton('🎭 Мультфильмы', callback_data='multfilm-wtw'))
        btns.append(telebot.types.InlineKeyboardButton('🎫 Мультсериалы', callback_data='multserials-wtw'))
        btns.append(telebot.types.InlineKeyboardButton('🔄 Случайно', callback_data='5-wtw'))
        keyboard.add(btns[0], btns[1])
        keyboard.add(btns[2], btns[3])
        keyboard.add(btns[4])
        bot.send_message(m.from_user.id, "💟 Выберите, какая категория вас интересует", reply_markup=keyboard)
    else:
        bot.send_message(m.from_user.id, "😥 Вы не состоите в отношениях")


@bot.callback_query_handler(func=lambda call: True)  ## callback баллов, и запись их в массив
def callbacks(call):
    if str(call.data).endswith("games"):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(f'✅ Принять', callback_data=f'{str(call.data[0])}-accept'))
        bot.send_message(call.message.chat.id, f"🎰 Вы предложили партнеру сыграть в {str(call.data)[0]}")
        bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                         f"🎰 Партнер предложил сыграть вам в {str(call.data)[0]}", reply_markup=keyboard)
    if str(call.data).endswith("accept"):
        if str(call.data)[0] == "🎲":
            you = bot.send_dice(call.message.chat.id, emoji="🎲")
            relation = bot.send_dice(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), emoji="🎲")
            if you.dice.value > relation.dice.value:
                bot.send_message(call.message.chat.id,
                                 f"🎉 Вы победили, партнеру выпало {str(call.data)[0]}{relation.dice.value}")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"😢 Вы проиграли, партнеру выпало {str(call.data)[0]}{you.dice.value}")
            elif you.dice.value < relation.dice.value:
                bot.send_message(call.message.chat.id,
                                 f"😢 Вы проиграли, партнеру выпало {str(call.data)[0]}{relation.dice.value}")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"🎉 Вы победили, партнеру выпало {str(call.data)[0]}{you.dice.value}")
            else:
                bot.send_message(call.message.chat.id,
                                 f"😶 Ничья {str(call.data)[0]}{relation.dice.value}")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"😶 Ничья {str(call.data)[0]}{you.dice.value}")
        if str(call.data)[0] == "🎯":
            you = bot.send_dice(call.message.chat.id, emoji="🎯")
            relation = bot.send_dice(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), emoji="🎯")
            if you.dice.value > relation.dice.value:
                bot.send_message(call.message.chat.id,
                                 f"🎉 Вы победили, партнер получил {str(call.data)[0]}{relation.dice.value} очков")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"😢 Вы проиграли, партнер получил {str(call.data)[0]}{you.dice.value} очков")
            elif you.dice.value < relation.dice.value:
                bot.send_message(call.message.chat.id,
                                 f"😢 Вы проиграли, партнер получил {str(call.data)[0]}{relation.dice.value} очков")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"🎉 Вы победили, партнер получил {str(call.data)[0]}{you.dice.value} очков")
            else:
                bot.send_message(call.message.chat.id,
                                 f"😶 Ничья {str(call.data)[0]}{relation.dice.value}")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"😶 Ничья {str(call.data)[0]}{you.dice.value}")
        if str(call.data)[0] == "🏀":
            you = bot.send_dice(call.message.chat.id, "🏀")
            relations = bot.send_dice(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), "🏀")
            if you.dice.value == 5 and you.dice.value != relations.dice.value and relations.dice.value == 4:
                bot.send_message(call.message.chat.id, "🎉 Поздравляем, вы победили. Вы забили 3х очковый!\n"
                                                       "💥 Ваш партнер тоже попал в кольцо")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 "😢 Вы проиграли. Вы попали в кольцо, но"
                                 " ваш партнер забил 3х очковый")
            elif you.dice.value == 4 and you.dice.value != relations.dice.value and relations.dice.value == 5:
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 "🎉 Поздравляем, вы победили. Вы забили 3х очковый!\n"
                                 "💥 Ваш партнер тоже попал в кольцо")
                bot.send_message(call.message.chat.id, "😢 Вы проиграли. Вы попали в кольцо, но"
                                                       " ваш партнер забил 3х очковый")
            elif you.dice.value > relations.dice.value:
                bot.send_message(call.message.chat.id, "🎉 Поздравляем, вы победили.\n"
                                                       "💥 Ваш партнер не попал в кольцо")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 "😢 Вы проиграли. Ваш партнер попал в кольцо")
            elif you.dice.value < relations.dice.value:
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 " 😢 Вы проиграли. Ваш партнер попал в кольцо\n"
                                 "💥 Ваш партнер не попал в кольцо")
                bot.send_message(call.message.chat.id, "🎉 Поздравляем, вы победили.\n"
                                                       "💥 Ваш партнер не попал в кольцо")
            else:
                bot.send_message(call.message.chat.id, "😶 Ничья")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), "😶 Ничья")
        if str(call.data)[0] == "⚽":
            you = bot.send_dice(call.message.chat.id, "⚽")
            relations = bot.send_dice(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), "⚽")
            if you.dice.value > relations.dice.value:
                bot.send_message(call.message.chat.id, f"🎉 По итогам игры, вы победили.\n"
                                                       f"Ваш партнер набрал ⚽ {relations.dice.value}\n"
                                                       f"Вы набрали ⚽ {you.dice.value}")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"😢 По итогам игры, вы проиграли.\n"
                                 f"Ваш партнер набрал ⚽ {you.dice.value}\n"
                                 f"Вы набрали ⚽ {relations.dice.value}")
            elif you.dice.value < relations.dice.value:
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"🎉 По итогам игры, вы победили.\n"
                                 f"Ваш партнер набрал ⚽ {you.dice.value}\n"
                                 f"Вы набрали ⚽ {relations.dice.value}")
                bot.send_message(call.message.chat.id, f"😢 По итогам игры, вы проиграли.\n"
                                                       f"Ваш партнер набрал ⚽ {relations.dice.value}\n"
                                                       f"Вы набрали ⚽ {you.dice.value}")
            else:
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), f"😶 Ничья")
                bot.send_message(call.message.chat.id, f"😶 Ничья")
        if str(call.data)[0] == "🎳":
            you = bot.send_dice(call.message.chat.id, "🎳")
            relations = bot.send_dice(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), "🎳")
            if you.dice.value > relations.dice.value:
                bot.send_message(call.message.chat.id, f"🎉 По итогам игры, вы победили.\n"
                                                       f"Ваш партнер сбил 🎳 {relations.dice.value}\n"
                                                       f"Вы сбили 🎳 {you.dice.value}")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"😢 По итогам игры, вы проиграли.\n"
                                 f"Ваш партнер сбил 🎳 {you.dice.value}\n"
                                 f"Вы сбили 🎳 {relations.dice.value}")
            elif you.dice.value < relations.dice.value:
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"🎉 По итогам игры, вы победили.\n"
                                 f"Ваш партнер сбил 🎳 {you.dice.value}\n"
                                 f"Вы сбили 🎳 {relations.dice.value}")
                bot.send_message(call.message.chat.id, f"😢 По итогам игры, вы проиграли.\n"
                                                       f"Ваш партнер сбил 🎳 {relations.dice.value}\n"
                                                       f"Вы сбили 🎳 {you.dice.value}")
            else:
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), f"😶 Ничья")
                bot.send_message(call.message.chat.id, f"😶 Ничья")
        if str(call.data)[0] == "🎰":
            you = bot.send_dice(call.message.chat.id, "🎰")
            relations = bot.send_dice(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), "🎰")
            if you.dice.value > relations.dice.value:
                bot.send_message(call.message.chat.id, f"🎉 По итогам игры, вы победили.\n"
                                                       f"Ваш партнер набрал 🎰 {relations.dice.value}\n"
                                                       f"Вы набрали 🎰 {you.dice.value}")
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"😢 По итогам игры, вы проиграли.\n"
                                 f"Ваш партнер набрал 🎰 {you.dice.value}\n"
                                 f"Вы набрали 🎰 {relations.dice.value}")
            elif you.dice.value < relations.dice.value:
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]),
                                 f"🎉 По итогам игры, вы победили.\n"
                                 f"Ваш партнер набрал 🎰 {you.dice.value}\n"
                                 f"Вы набрали 🎰 {relations.dice.value}")
                bot.send_message(call.message.chat.id, f"😢 По итогам игры, вы проиграли.\n"
                                                       f"Ваш партнер набрал 🎰 {relations.dice.value}\n"
                                                       f"Вы набрали 🎰 {you.dice.value}")
            else:
                bot.send_message(get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id]), f"😶 Ничья")
                bot.send_message(call.message.chat.id, f"😶 Ничья")
    if str(call.data).endswith("wtw"):
        if str(call.data)[0] != "5":
            category = str(call.data).split("-")[0]
            bot.send_message(call.message.chat.id,
                             choice(get_record("fil_bot", "wtw", "name", columns=["category"], values=[category]))[0])
        else:
            bot.send_message(call.message.chat.id, choice(get_record("fil_bot", "wtw", "name", columns=["category"],
                                                                     values=[
                                                                         f"{choice(['films', 'serials', 'multfilm', 'multserials'])}"]))[
                0])
    if str(call.data).endswith("calendar"):
        if str(call.data)[0] == "0":
            month_year = str(call.data).split("-")
            btns = [telebot.types.InlineKeyboardButton(f'{i}', callback_data=f'3-{month_year[1]}-{i}-calendar') for i in
                    range(2001, 2025)]
            keyboar = Keyboa(items=btns, items_in_row=4).keyboard
            bot.edit_message_text("📆 <b>Выберите год начала отношений</b>", call.from_user.id, call.message.message_id,
                                  parse_mode="html", reply_markup=keyboar)
        if str(call.data)[0] == "1":
            month_year = str(call.data).split("-")
            btns = [telebot.types.InlineKeyboardButton(f'{months_name[str(i)]}',
                                                       callback_data=f'3-{i}-{month_year[2]}-calendar') for i in
                    range(1, 13)]
            keyboar = Keyboa(items=btns, items_in_row=4).keyboard
            bot.edit_message_text("📆 <b>Выберите месяц начала отношений</b>", call.from_user.id,
                                  call.message.message_id, parse_mode="html", reply_markup=keyboar)
        if str(call.data)[0] == "3":
            month_year = str(call.data).split("-")
            print(month_year)
            bot.edit_message_text("💝 <b>Выберите дату начала отношений</b>", call.from_user.id, call.message.message_id,
                                  parse_mode="html", reply_markup=create_calendar(month_year[1], month_year[2]))
    if str(call.data).endswith("calendardate"):
        partner_id = get_record("fil_bot", "fil", "partner_id", ["id"], [call.from_user.id])[0][0]
        data = str(call.data).split("-")
        edit_record("fil_bot", "fil", ["relation_date"], [f"{data[0]}.{data[1]}.{data[2]}"], "id", call.from_user.id)
        edit_record("fil_bot", "fil", ["relation_date"], [f"{data[0]}.{data[1]}.{data[2]}"], "id", partner_id)
        bot.send_message(call.from_user.id,
                         f"💘 Выбрана новая дата начала отношений: <b>{data[0]}.{data[1]}.{data[2]}</b>",
                         parse_mode="html")
        bot.send_message(partner_id,
                         f"💘 Ваш партнер выбрал новую дату начала отношений: <b>{data[0]}.{data[1]}.{data[2]}</b>",
                         parse_mode="html")
    if str(call.data).endswith("adm"):
        if str(call.data)[0] == "1":
            msg = bot.send_message(call.from_user.id,
                                   "💌 Отправьте парные аватарки в чат, двумя сообщениями\n<i>Примечание, парные аватарки должны идти слева-направо.</i>",
                                   parse_mode="html")
            bot.register_next_step_handler(msg, pfps_add)
    if str(call.data).endswith("cancel"):
        files_id = str(call.data).split('-')[0]
        os.remove(f'matching_pfps/{files_id}0.jpg')
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, "❌ Процесс отменен")
    bot.answer_callback_query(call.id, text="")


def pfps_add(m):
    if not m.media_group_id:
        try:
            keyboard = telebot.types.InlineKeyboardMarkup()
            files_id = (len(os.listdir("matching_pfps")) // 2) + 1
            file_info = bot.get_file(m.photo[len(m.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = f'matching_pfps/{files_id}0.jpg'
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            keyboard.add(kbbut("❌ Отменить", f"{files_id}-cancel"))
            bot.send_message(m.from_user.id,
                             "📸 Парная аватарка добавлена!\nОтправьте правую парную аватарку, чтобы закончить процесс добавления. Если нажмите кнопку <i>Отменить</i>, чтобы прервать процесс",
                             parse_mode="html", reply_markup=keyboard)
            bot.register_next_step_handler(m, lambda m: pfps_add_2(m, files_id))
        except:
            pass
    else:
        pass


def pfps_add_2(m, id):
    if not m.media_group_id:
        file_info = bot.get_file(m.photo[len(m.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'matching_pfps/{id}1.jpg';
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(m.from_user.id,
                         "📸 Парная аватарка добавлена!",
                         parse_mode="html")
    else:
        pass


@bot.message_handler(commands=["delete_relation"])
def delete_relation(m):
    if relation_check(m):
        partner_id = get_record("fil_bot", "fil", "partner_id", ["id"], [m.from_user.id])[0][0]
        bot.send_message(m.from_user.id, "💔 Партнер разорвал ваши отношения")
        bot.send_message(partner_id, "💔 Партнер разорвал ваши отношения")
        edit_record("fil_bot", "fil", ["partner_id", "relation_date", "kisses", "hugs"], ["0", "0", 0, 0], "id",
                    partner_id)
        edit_record("fil_bot", "fil", ["partner_id", "relation_date", "kisses", "hugs"], ["0", "0", 0, 0], "id",
                    m.from_user.id)
    else:
        bot.send_message(m.from_user.id, "😥 Вы не состоите в отношениях")


@bot.message_handler(commands=["kiss"])
def kis(m):
    if relation_check(m):
        partner_id = get_record("fil_bot", "fil", "partner_id", ["id"], [m.from_user.id])[0][0]
        kisses = get_record("fil_bot", "fil", "kisses", ["id"], [m.from_user.id])[0][0]
        bot.send_message(m.from_user.id, "😘 Вы поцеловали своего партнера")
        bot.send_message(partner_id, "😘 Ваш партнер, вас поцеловал")
        bot.send_sticker(partner_id,
                         choice(get_record("fil_bot", "stickers", "id", columns=["category"], values=["kiss"]))[0])
        edit_record("fil_bot", "fil", ["kisses"], [kisses + 1], "id", m.from_user.id)
        edit_record("fil_bot", "fil", ["kisses"], [kisses + 1], "id", partner_id)
    else:
        bot.send_message(m.from_user.id, "😥 Вы не состоите в отношениях")


@bot.message_handler(commands=["hug"])
def hug(m):
    if relation_check(m):
        partner_id = get_record("fil_bot", "fil", "partner_id", ["id"], [m.from_user.id])[0][0]
        hugs = get_record("fil_bot", "fil", "hugs", ["id"], [m.from_user.id])[0][0]
        bot.send_message(m.from_user.id, "🤗 Вы обняли своего партнера")
        bot.send_message(partner_id, "🤗 Ваш партнер, вас обнял")
        bot.send_sticker(partner_id,
                         choice(get_record("fil_bot", "stickers", "id", columns=["category"], values=["hugs"]))[0])
        edit_record("fil_bot", "fil", ["hugs"], [hugs + 1], "id", m.from_user.id)
        edit_record("fil_bot", "fil", ["hugs"], [hugs + 1], "id", partner_id)
    else:
        bot.send_message(m.from_user.id, "😥 Вы не состоите в отношениях")


@bot.message_handler(commands=["new_date"])
def new_date(m):
    if relation_check(m):
        bot.send_message(m.from_user.id, "💝 <b>Выберите дату начала отношений</b>", parse_mode="html",
                         reply_markup=create_calendar(datetime.now().month, datetime.now().year))
    else:
        bot.send_message(m.from_user.id, "😥 Вы не состоите в отношениях")


if __name__ == '__main__':
    connect_db()
    bot.skip_pending = True
    bot.polling(none_stop=True)
