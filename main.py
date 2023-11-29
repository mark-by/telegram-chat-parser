from telethon.sync import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
from datetime import datetime
import time
import asyncio
import csv
import curses
import settings


def astimate(start_time, processed, total):
    gone_time = (datetime.now() - start_time).total_seconds()
    speed = processed / gone_time
    return (total - processed) / speed


def get_fio(first_name, last_name):
    res = ""
    if first_name:
        res += first_name
    if last_name:
        if first_name:
            res += " "
        res += last_name
    return res


def get_first_name(fio):
    return fio.split(" ")[0]


def get_last_name(fio):
    splitted = fio.split(" ")
    if len(splitted) > 1:
        return splitted[1]
    return None


async def main(stdscr):
    s = stdscr
    client = TelegramClient('session_name', settings.API_ID, settings.API_HASH)

    await client.connect()
    await client.start()

    # s = curses.initscr()
    s.clear()
    curses.echo()

    s.addstr(0, 0, 'Введите ID чата:')
    try:
        chat_id = int(s.getstr(0, 17, 30))
    except:
        curses.endwin()
        print("ID чата должeн быть числом")
        exit()

    s.clear()

    if chat_id > 0:
        chat_id = -1 * chat_id

    try:
        my_chat = await client.get_entity(chat_id)
    except:
        curses.endwin()
        print("Нет такого чата:", chat_id)
        exit()

    try:
        participants = await client.get_participants(my_chat)
    except ChatAdminRequiredError:
        curses.endwin()
        print("Нет прав для получения доступа к участникам")
        exit()

    s.addstr(0, 0, "Работаем...")
    s.refresh()

    total = len(participants)
    s.addstr(1, 0, f"Всего: {total}")
    s.refresh()

    counter = 0
    start_time = datetime.now()

    total_len = len(str(total))
    with open('out.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Фамилия', 'Имя', 'Ник', 'Телефон', 'Био'])
        for participant in participants:
            user = await client.get_entity(participant)
            full = await client(GetFullUserRequest(user.id))
            fio = get_fio(user.first_name, user.last_name)
            first_name = get_first_name(fio)
            last_name = get_last_name(fio)

            writer.writerow([last_name, first_name, user.username, user.phone, full.full_user.about])
            counter += 1
            s.addstr(2, 0, f"{counter}")

            percent = f"[{round(counter / total * 100, 2)}%]"
            s.addstr(2, total_len + 1, percent)

            len_percent = 8

            gone = f"Прошло: {time.strftime('%H:%M:%S', time.gmtime((datetime.now() - start_time).total_seconds()))}"
            s.addstr(2, total_len + 1 + len_percent + 1, gone)

            left = f"Осталось примерно: {time.strftime('%H:%M:%S', time.gmtime(astimate(start_time, counter, total)))}"
            s.addstr(2, total_len + 1 + len_percent + 1 + len(gone) + 1, left)

            s.refresh()

    s.addstr(3, 0, "Готово!")
    s.addstr(4, 0, "Введите Enter для завершения...")
    s.getstr(0)
    curses.endwin()


def recover_curses(stdscr):
    try:
        asyncio.run(main(stdscr))
    except Exception as e:
        raise e


curses.wrapper(recover_curses)
