import sqlite3
import pandas as pd

conn = sqlite3.connect("games.db")

# Export Games table
df_games = pd.read_sql_query("SELECT * FROM Games", conn)
df_games.to_csv("games.csv", index=False)

# Export Prices table
df_prices = pd.read_sql_query("SELECT * FROM Steam_Prices", conn)
df_prices.to_csv("steam_prices.csv", index=False)

# Export Reviews table
df_reviews = pd.read_sql_query("SELECT * FROM Reviews", conn)
df_reviews.to_csv("steam_reviews.csv", index=False)

conn.close()
print("Saved all tables to CSV.")