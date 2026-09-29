-- database: games.db

Create Table Games (
    GameID INTEGER PRIMARY KEY AUTOINCREMENT,
    Game_Name TEXT UNIQUE COLLATE NOCASE NOT NULL,
    Game_Year int not null,
    Game_Genre varchar(50),
    Game_Subgenre varchar(50),
    Game_Studio varchar(50)
);

DROP TABLE Games;
DROP TABLE Steam_Prices;
DROP TABLE Reviews;
DELETE FROM Games;

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
    Fetched_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);
CREATE TABLE IF NOT EXISTS Steam_Prices (
    PriceID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER NOT NULL,
    Steam_AppID INTEGER NOT NULL,
    Initial_Price REAL DEFAULT 0.0,   -- Original price (MSRP)
    Final_Price REAL DEFAULT 0.0,     -- Current selling price
    Discount_Pct INTEGER DEFAULT 0,    -- Active discount percentage
    Is_Free INTEGER DEFAULT 0,        -- 1 = Free to play, 0 = Paid
    Currency TEXT DEFAULT 'EUR',
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (GameID) REFERENCES Games(GameID) ON DELETE CASCADE
);
DELETE FROM Games
WHERE GameID NOT IN (
    SELECT MIN(GameID)
    FROM Games
    GROUP BY Game_Name
);