import sqlite3
import datetime
import emoji

from app.functions.queries_data import (
    months_rus,
    months_count,
    SEASON_TOTAL,
    SPENDINGS_TOTAL,
    add_player_query,
    add_season_query,
    add_trainings_query,
    add_spending_query,
    del_player_query,
    del_season_query,
    del_trainings_query,
    incr_summ_query,
    get_all_stats_query,
    get_player_stats_query,
    get_all_players_query,
    get_last_spendings_query,
    get_summ_season_query,
    get_summ_spendings_query,
)

SMILE = emoji.emojize(":slightly_smiling_face:")
THUMBS_UP = emoji.emojize(":thumbs_up:")
SHIT = emoji.emojize(":pile_of_poo:")
STAR = emoji.emojize(":star:")
CHICKEN = emoji.emojize(":chicken:")


def get_month():
    mydate = datetime.datetime.now()
    return mydate.strftime("%b").lower()


def get_user_id_by_name(cur, name, surname):
    user_id = cur.execute(
        f"SELECT id FROM players WHERE name == '{name}' AND surname == '{surname}';"
    ).fetchone()
    return user_id


def get_user_id_by_telegram_id(cur, telegram_id):
    user_id = cur.execute(
        f"SELECT id FROM players WHERE telegram_id == {telegram_id};"
    ).fetchone()
    return user_id


def get_season_stat_smile(summ):
    average_for_this_month = SEASON_TOTAL / 11 * months_count[get_month()]
    min_for_this_month = average_for_this_month - 1000

    if summ >= SEASON_TOTAL:
        return STAR
    elif summ <= 0.2 * min_for_this_month:
        return CHICKEN
    elif summ < min_for_this_month:
        return SHIT
    elif summ > average_for_this_month:
        return THUMBS_UP
    else:
        return SMILE


def add_user(con, name, surname, telegram_id=0):
    cursor = con.cursor()
    if get_user_id_by_name(cursor, name, surname):
        return "Такой игрок уже существует!"

    with con:
        con.execute(add_player_query.format(name, surname, telegram_id))
        user_id = get_user_id_by_name(cursor, name, surname)[0]
        con.execute(add_season_query.format(user_id))
        con.execute(add_trainings_query.format(user_id))
        return f"Игрок {name} {surname} добавлен"


def del_user(con, name, surname):
    cursor = con.cursor()
    user_id = get_user_id_by_name(cursor, name, surname)
    if not user_id:
        return "Такого игрока не существует!"

    user_id = user_id[0]
    with con:
        con.execute(del_player_query.format(user_id))
        con.execute(del_season_query.format(user_id))
        con.execute(del_trainings_query.format(user_id))
        return f"Игрок {name} {surname} удален"


def add_spending(con, summ, description):
    mydate = datetime.datetime.now()
    date = mydate.strftime("%d-%b-%Y %H:%M:%S")
    with con:
        con.execute(add_spending_query.format(date, summ, description))


def get_all_players(con):
    cursor = con.cursor()
    with con:
        result = cursor.execute(get_all_players_query).fetchall()

    return result


def get_all_stats(con, telegram_id):
    cursor = con.cursor()
    month_eng = get_month()
    month_rus = months_rus[month_eng]

    user_id = get_user_id_by_telegram_id(cursor, telegram_id)
    if not user_id:
        return "Извините, Вы отсутствуете в базе"

    output = []
    with con:
        result = cursor.execute(get_all_stats_query.format(month_eng)).fetchall()
        for name_surname, season, trainings in result:
            smile = get_season_stat_smile(season)
            output.append(
                f"{smile} <b>{name_surname}\n</b>Сезон: {season}/{SEASON_TOTAL} руб.\nТренировки {month_rus}: {trainings} руб."
            )

    return f"\n{'*'*25}\n".join(output)


def get_player_stats(con, telegram_id=None, player_id=None):
    cursor = con.cursor()
    month_eng = get_month()
    month_rus = months_rus[month_eng]

    if telegram_id:
        user_id = get_user_id_by_telegram_id(cursor, telegram_id)
        if not user_id:
            return "Извините, Вы отсутствуете в базе"
        user_id = user_id[0]
    else:
        user_id = player_id

    with con:
        result = cursor.execute(
            get_player_stats_query.format(month_eng, user_id)
        ).fetchone()

    name_surname, season, trainings = result
    smile = get_season_stat_smile(season)
    text = f"{smile} <b>{name_surname}</b>\nСезон: {season}/{SEASON_TOTAL} руб.\nТренировки {month_rus}: {trainings} руб."

    return text


def set_summ(con, name, surname, table, summ):
    cursor = con.cursor()
    with con:
        user_id = get_user_id_by_name(cursor, name, surname)
        if not user_id:
            return "Такого игрока не существует!"

        payment_type = "summ" if table == "season" else get_month()
        con.execute(
            incr_summ_query.format(table, payment_type, payment_type, summ, *user_id)
        )


def create_report(con):
    cursor = con.cursor()
    last_spendings_list = []
    with con:
        last_spendings = cursor.execute(get_last_spendings_query).fetchall()
        for date, summ, description in last_spendings:
            last_spendings_list.append(f"{date}\n{summ} руб. {description}")

        summ_season = cursor.execute(get_summ_season_query).fetchone()[0]
        summ_spendings = cursor.execute(get_summ_spendings_query).fetchone()[0]

    last_spendings_text = f"\n{'*'*25}\n".join(last_spendings_list)
    report_text = f"Всего сдано: {summ_season}/{SPENDINGS_TOTAL} руб."
    report_text += f"\nВсего оплачено: {summ_spendings}/{SPENDINGS_TOTAL} руб."
    report_text += f"\nВ запасе осталось: <b>{summ_season - summ_spendings} руб.</b>"

    return last_spendings_text, report_text
