-- database: games.db

CREATE TABLE IF NOT EXISTS Games (
    GameID              INTEGER PRIMARY KEY AUTOINCREMENT,
    Steam_AppID         INTEGER UNIQUE NOT NULL,
    Game_Name           TEXT,
    Game_Year           INTEGER,
    Initial_Price       REAL,
    Rating_Tier         TEXT,
    Metacritics         INTEGER,
    Steam_Total_Reviews INTEGER,
    Game_Genres_All     TEXT
);
