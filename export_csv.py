import sqlite3
import pandas as pd

conn = sqlite3.connect("games.db")

# Export Games table
df_games = pd.read_sql_query("SELECT * FROM Games", conn)
df_games.to_csv("games.csv", index=False)


conn.close()
print("Saved all tables to CSV.")