-- database: games.db

Create Table Games (
    GameID INTEGER PRIMARY KEY AUTOINCREMENT,
    Game_Name TEXT UNIQUE COLLATE NOCASE NOT NULL,
    Game_Year int not null,
    Game_Genre varchar(50),
    Game_Studio varchar(50)
);

DROP TABLE Steam_Prices;
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
Insert into Games(Game_Name,Game_Year,Game_Genre,Game_studio)
values
('It Takes Two', 2021,'Platform','Hazelight Studios'),
("Five Nights at Freddy's: Secret of the Mimic", 2025,'Survival Horror','Steel Wool Studios'),
("Marvel's Spider-Man Remastered", 2022,'Action/Adventure','Insomniac Games'),
('Hollow Knight',2017,'Metroidvania','Team Cherry'),
('Detroit: Become Human',2018,'Interactive Story','Quantic Dream'),
('Where Winds Meet',2024,'RPG','Everstone Studio'),
('Palworld',2024,'Survival','Pocketpair'),
('Final Fantasy VII Remake Intergrade',2020,'RPG','Square Enix'),
('Silent Hill 2',2024,'Survival Horror','Konami'),
('Call of Duty: Black Ops 7',2025,'FPS','Activision');


