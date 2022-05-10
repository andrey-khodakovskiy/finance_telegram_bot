from decouple import config

SEASON_TOTAL = int(config("SEASON_TOTAL"))
SPENDINGS_TOTAL = int(config("SPENDINGS_TOTAL"))

months_rus = {
    "jan": "Январь",
    "feb": "Февраль",
    "mar": "Март",
    "apr": "Апрель",
    "may": "Май",
    "jun": "Июнь",
    "jul": "Июль",
    "aug": "Август",
    "sep": "Сентябрь",
    "oct": "Октябрь",
    "nov": "Ноябрь",
    "dec": "Декабрь",
}

months_count = {
    "jan": 11,
    "feb": 1,
    "mar": 2,
    "apr": 3,
    "may": 4,
    "jun": 5,
    "jul": 5,
    "aug": 6,
    "sep": 7,
    "oct": 8,
    "nov": 9,
    "dec": 10,
}

add_player_query = (
    "INSERT INTO players (name, surname, telegram_id) VALUES ('{}', '{}', {});"
)
add_season_query = "INSERT INTO season ( player_id, summ ) VALUES ( {}, 0 );"
add_trainings_query = """INSERT INTO trainings ( player_id, jan, feb , mar, apr, may, jun, jul, aug, sep, oct, nov, dec) 
    VALUES ( {}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 )"""
add_spending_query = (
    "INSERT INTO spendings (date, summ, description) VALUES ('{}', {}, '{}');"
)
del_player_query = "DELETE FROM players WHERE id = {};"
del_season_query = "DELETE FROM season WHERE player_id = {};"
del_trainings_query = "DELETE FROM trainings WHERE player_id = {};"
incr_summ_query = "UPDATE {} SET {} = {} + {} WHERE player_id = {};"

get_all_stats_query = """SELECT p.name || ' ' || p.surname AS player_name,
            s.summ AS season_summ,
            t.{} AS trainings_this_months
            FROM players p
            JOIN season s ON s.player_id = p.id
            JOIN trainings t ON t.player_id = p.id
            ORDER BY s.summ DESC, p.surname ASC;
        """

get_player_stats_query = """SELECT p.name || ' ' || p.surname AS player_name,
            s.summ AS season_summ,
            t.{} AS trainings_this_months
            FROM players p
            JOIN season s ON s.player_id = p.id
            JOIN trainings t ON t.player_id = p.id
            WHERE p.id = '{}'
        """

get_all_players_query = """SELECT p.name || ' ' || p.surname AS player_name
            FROM players p
            ORDER BY p.surname ASC;
        """

get_last_spendings_query = (
    """SELECT date, summ, description FROM spendings ORDER BY id DESC LIMIT 3;"""
)
get_summ_season_query = """SELECT SUM(summ) FROM season;"""
get_summ_spendings_query = """SELECT SUM(summ) FROM spendings;"""
