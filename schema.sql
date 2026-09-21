-- database: games.db

Create Table Games (
    GameID INTEGER PRIMARY KEY AUTOINCREMENT,
    Game_Name TEXT UNIQUE COLLATE NOCASE NOT NULL,
    Game_Year int not null,
    Game_Genre varchar(50),
    Game_Studio varchar(50)
);

DROP TABLE Game_Metrics;
DELETE FROM Games;
Insert into Games(Game_Name,Game_Year,Game_Genre,Game_studio)
values
('Horizon: Zero Dawn',2017,'Action/Adventure','Gurrilla Games'),
('Horizon: Forbidden West',2022,'Action/Adventure','Gurrilla Games'),
("Assassin's Creed III",2012,'Action/Adventure','Ubisoft Montreal'),
('Alan Wake 2',2023,'Survival Horror','Remedy Entertainment'),
('God of War Ragnarök',2022,'Action/Adventure','Santa Monica Studio');

SELECT * FROM Games sort ORDER BY Game_Name;
CREATE TABLE IF NOT EXISTS Game_Metrics (
    MetricID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER NOT NULL,
    Normal_Price REAL,
    Sale_Price REAL,
    Metacritic_Score INTEGER,        -- Global Critic Score (0-100)
    Steam_Rating_Pct INTEGER,        -- Steam Positive %
    PSN_Rating REAL,                 -- PlayStation Store Rating (e.g., 4.5/5.0)
    Xbox_Rating REAL,                -- Xbox Store Rating (e.g., 4.2/5.0)
    Fetched_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (GameID) REFERENCES Games(GameID) ON DELETE CASCADE
);