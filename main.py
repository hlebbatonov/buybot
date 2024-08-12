import telebot
from telebot import types
import csv
import os.path
import os
import datetime
from requests.exceptions import ConnectionError
from zipfile import ZipFile


bot = telebot.TeleBot('')
admins = ['Hleb_Batonov', '@kibitkas']

num_order = False
qr_code = False
description = False
flag_new_dialog = True
flag_admin = False
flag_change_num = False
flag_change_qrcode = False

change_num = '-1'
nick = ''
number_of_order = ''
description_of_order = ''
qr_code_path = ''
#start
if not os.path.exists('orders.csv'):
    with open('orders.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Ник тг', 'Номер заказа', 'Информация о заказе', 'QR-код', 'Время обновления QR-кода'])


def current_time_formatted():
    curr_time = datetime.datetime.now()
    return f"{curr_time.day}.{curr_time.month}.{curr_time.year} {curr_time.hour}:{curr_time.minute}:{curr_time.second}"


@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    global nick, number_of_order, description_of_order, qr_code_path, num_order, qr_code, description, flag_new_dialog, flag_admin, flag_change_qrcode, flag_change_num, change_num
    if message.from_user.username in admins:
        if message.text == '/admin':
            bot.send_message(message.from_user.id,
                             'Добро пожаловать в учетную запись администратора!\n"/table" - получить таблицу\n"/get {номер заказа}" - получить информацию о заказе по номеру (включая QR-код). Пример - "/get 921939"\n"/allfiles"-получить все QR-коды и таблицу')
        if message.text == '/table':
            bot.send_document(message.chat.id, open("orders.csv", 'rb'))
        if '/get' in message.text:
            number_of_order_search = message.text.replace('/get ', '')
            with open('orders.csv', encoding='utf-8') as f:
                reader = csv.reader(f)
                found = False
                for i in reader:
                    if i[1] == number_of_order_search:
                        info = i
                        found = True
                        break
                if not found:
                    bot.send_message(message.chat.id,
                                     'Заказа с таким номером в таблице нет, или он введен некорректно :(\nПопробуйте еще раз, введя "/get {номер заказа}"')
                else:
                    with open(i[3], 'rb') as photo:
                        bot.send_photo(message.chat.id, photo,
                                       caption=f'Ник тг: @{info[0]}\nНомер заказа: {info[1]} \nОписание: {info[2]}\nВремя обновления: {info[4]} MSK (UTC+3  )')
        if message.text == '/allfiles':
            list_of_files = list(filter(lambda x: '.jpg' in x, os.listdir()))
            with ZipFile('allfiles.zip', 'w') as allfiles:
                for i in list_of_files:
                    allfiles.write(i)
                allfiles.write('orders.csv')
            with open('allfiles.zip', 'rb') as send_zip:
                bot.send_document(message.chat.id, send_zip)
        if '/delete' in message.text:
            list_of_files_to_delete = message.text.replace('/delete ', '').replace(',', '').replace('  ', ' ').split(
                ' ')
            with open('orders.csv', encoding='utf-8') as f:
                reader = csv.reader(f)
                a = []
                b = []
                for i in reader:
                    if i[1] not in list_of_files_to_delete:
                        a.append(i)
                        os.remove(i[3])
                    else:
                        b.append(i[1])
                with open('orders.csv', 'w', encoding='utf-8') as ff:
                    writer = csv.writer(ff)
                    writer.writerows(a)
            bot.send_message(message.from_user.id, 'Удалены заказы с номерами:'+'\n'.join(b))
    else:
        if message.text == '/start':
            num_order = False
            qr_code = False
            description = False
            flag_change_num = False
            flag_change_qrcode = False
            change_num = '-1'
            nick = ''
            number_of_order = ''
            description_of_order = ''
            qr_code_path = ''
            bot.send_message(message.from_user.id, 'Вас приветствует бот!')
            keyboard = types.InlineKeyboardMarkup();
            key_new = types.InlineKeyboardButton(text='Да, я хочу сделать заказ', callback_data='yes');
            # keyboard.add(key_new);
            key_already = types.InlineKeyboardButton(text='Нет, я уже сделал заказ', callback_data='no');
            # keyboard.add(key_already);
            keyboard.row(key_new, key_already)
            question = 'Вы хотите сделать заказ?';
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
        if num_order and not qr_code and not description and not flag_change_num and not flag_change_qrcode:
            number_of_order = message.text
            print(number_of_order)
            description = True
            bot.send_message(message.from_user.id,
                             'Спасибо! Пришлите описание (список товаров, количество, другая информация) заказа')
        elif not qr_code and description and not flag_change_num and not flag_change_qrcode:
            print(number_of_order)
            description_of_order = message.text
            qr_code = True
            bot.send_message(message.from_user.id, 'Спасибо! Пришлите QR-код для получения заказа скриншотом')
        elif message.content_type == 'photo' and not flag_change_num and not flag_change_qrcode:
            print(number_of_order)
            raw = message.photo[2].file_id
            name = str(number_of_order) + ".jpg"
            file_info = bot.get_file(raw)
            qr_code_path = file_info
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, 'wb') as new_file:
                new_file.write(downloaded_file)
            user_nick = str(message.from_user.username)
            with open('orders.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                print(user_nick, number_of_order, description_of_order, name, current_time_formatted())
                writer.writerow([user_nick, number_of_order, description_of_order, name, current_time_formatted()])
            bot.send_message(message.from_user.id, 'Большое спасибо за заказ!\nНачать сначала: /start')
        if message.text == '/change':
            flag_change_num = True
            flag_change_qrcode = False
            bot.send_message(message.from_user.id, 'Пришлите номер заказа, QR-код которого вы хотите заменить')
        elif flag_change_num and not flag_change_qrcode:
            with open('orders.csv', encoding='utf-8') as f:
                reader = csv.reader(f)
                b = list(filter(lambda x: x[0] == message.from_user.username and x[1] == message.text, reader))
                change_num = message.text
                flag_change_qrcode = True
                if b:
                    bot.send_message(message.from_user.id, 'Спасибо! Пришлите обновленный QR-код заказа')
                else:
                    bot.send_message(message.from_user.id,
                                     'Вы не отправляли боту заказ с таким номером\n Попробуйте еще раз: /change')
        elif flag_change_num and flag_change_qrcode and message.content_type == 'photo':
            print(change_num, 'change QR code')
            raw = message.photo[2].file_id
            name = str(change_num) + ".jpg"
            file_info = bot.get_file(raw)
            qr_code_path = file_info
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, 'wb') as new_file:
                new_file.write(downloaded_file)
            with open('orders.csv', 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                a = []
                for i in reader:
                    a.append(i)
                for i in a:
                    if i[0] == message.from_user.username and i[1] == change_num:
                        i[4] = current_time_formatted()
                with open('orders.csv', 'w', newline='', encoding='utf-8') as ff:
                    writer = csv.writer(ff)
                    writer.writerows(a)
            # user_nick = str(message.from_user.username)
            # with open('orders.csv', 'a', newline='', encoding='utf-8') as f:
            #    writer = csv.writer(f)
            #    print(user_nick, number_of_order, description_of_order, name)
            #    writer.writerow([user_nick, number_of_order, description_of_order, name])
            bot.send_message(message.from_user.id, 'Спасибо! QR-код обновлен\nНачать сначала: /start')
            flag_change_num = False
            flag_change_qrcode = False


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global num_order, flag_new_dialog
    if not call.message.from_user.username in admins:
        message_id = call.message.message_id
        chat_id = call.message.chat.id
        if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text='*список ссылок на каналы*\nНачать сначала: /start')
        elif call.data == "no":
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text='Спасибо! Пришлите, пожалуйста, номер заказа')
            num_order = True
            flag_new_dialog = True





try:
    bot.polling(none_stop=True, interval=0)
except (telebot.apihelper.ApiException, ConnectionError) as e:
    bot.polling(none_stop=True, interval=0)
# bot.infinity_polling(timeout=10, long_polling_timeout=5)
