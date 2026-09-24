-- database: games.db

Create Table Games (
    GameID INTEGER PRIMARY KEY AUTOINCREMENT,
    Game_Name TEXT UNIQUE COLLATE NOCASE NOT NULL,
    Game_Year int not null,
    Game_Genre varchar(50),
    Game_Studio varchar(50)
);

DROP TABLE Reviews;
DELETE FROM Games;
Insert into Games(Game_Name,Game_Year,Game_Genre,Game_studio)
values
('Horizon: Zero Dawn',2017,'Action/Adventure','Gurrilla Games'),
('Horizon: Forbidden West',2022,'Action/Adventure','Gurrilla Games'),
("Assassin's Creed 3",2012,'Action/Adventure','Ubisoft Montreal'),
('Alan Wake 2',2023,'Survival Horror','Remedy Entertainment'),
('God of War Ragnarök',2022,'Action/Adventure','Santa Monica Studio'),
('EA Sports FC 26',2025,'Sports','Electronic Arts'),
('Resident Evil 9',2026,'Survival horror','Capcom'),
('The Witcher 3: Wild Hunt',2015,'RPG-action','CD Projekt'),
('A Plague Tale: Requiem',2022,'Stealth Game','Asobo Studio'),
('Black Myth: Wukong',2024,'RPG-action','Game Science');

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