import sqlite3


create_players_table_query = """
CREATE TABLE IF NOT EXISTS players (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  surname TEXT NOT NULL,
  telegram_id INTEGER
);
"""

create_season_table_query = """
CREATE TABLE IF NOT EXISTS season (
  player_id INTEGER NOT NULL PRIMARY KEY,
  summ INTEGER,
  FOREIGN KEY (player_id) REFERENCES players (id)
);
"""

create_trainings_table_query = """
CREATE TABLE IF NOT EXISTS trainings (
  player_id INTEGER NOT NULL PRIMARY KEY,
  jan INTEGER,
  feb INTEGER,
  mar INTEGER,
  apr INTEGER,
  may INTEGER,
  jun INTEGER,
  jul INTEGER,
  aug INTEGER,
  sep INTEGER,
  oct INTEGER,
  nov INTEGER,
  dec INTEGER,
  FOREIGN KEY (player_id) REFERENCES players (id)
);
"""

create_spendings_table_query = """
CREATE TABLE IF NOT EXISTS spendings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  summ INTEGER,
  description TEXT
);
"""


def create_tables(connection):
    connection.execute(create_players_table_query)
    connection.execute(create_season_table_query)
    connection.execute(create_trainings_table_query)
    connection.execute(create_spendings_table_query)


if __name__ == "__main__":
    connection = sqlite3.connect("db/atletico_finance.db")
    cursor = connection.cursor()
    create_tables(connection)
