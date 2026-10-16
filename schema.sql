-- database: games.db

Create Table Games (
    GameID INTEGER PRIMARY KEY AUTOINCREMENT,
    Game_Name TEXT UNIQUE COLLATE NOCASE NOT NULL,
    Game_Year int not null,
    Game_Genre varchar(50),
    Game_Subgenre varchar(50),
    Game_Studio varchar(50)
);

DROP TABLE Steam_Prices;
DELETE FROM Steam_Prices;
DELETE FROM Reviews;
DELETE FROM Games;

DELETE FROM sqlite_sequence WHERE name = 'Games';

SELECT * FROM Games sort ORDER BY Game_Name;


CREATE TABLE IF NOT EXISTS Reviews (
    MetricID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER,
    Steam_AppID INTEGER,
    Steam_Rating_Pct REAL,       -- Positive review percentage (e.g., 88.5)
    Steam_Total_Reviews INTEGER, -- Total review count for weighting/popularity
    RAWG_Rating REAL,
    Added_Count INTEGER, 
    Ratings_Count INTEGER,
    Metacritics REAL DEFAULT 0.0,
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);
CREATE TABLE IF NOT EXISTS Steam_Prices (
    PriceID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER NOT NULL,
    Steam_AppID INTEGER NOT NULL,
    Initial_Price REAL DEFAULT 0.0,   
    FOREIGN KEY (GameID) REFERENCES Games(GameID) ON DELETE CASCADE
);
DELETE FROM Games
WHERE GameID NOT IN (
    SELECT MIN(GameID)
    FROM Games
    GROUP BY Game_Name
);
ALTER TABLE Reviews ADD COLUMN Metacritics REAL DEFAULT 0.0;
ALTER TABLE Steam_Prices DROP COLUMN Discount_Pct;
