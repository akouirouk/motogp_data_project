-- @block create motogp database
CREATE DATABASE motogp;
-- @block show databases
SHOW DATABASES;
-- @block create table containing MotoGP riders
CREATE TABLE IF NOT EXISTS riders(
    id INT NOT NULL AUTO_INCREMENT,
    rider_name VARCHAR(255) UNIQUE NOT NULL,
    race_number INT(2) NOT NULL,
    name_num_abbrev VARCHAR(255) NOT NULL,
    team VARCHAR(255) NOT NULL,
    birth_city VARCHAR(255) NOT NULL,
    birth_country VARCHAR(2) NOT NULL,
    date_of_birth DATE NOT NULL,
    height INT(3),
    weight INT(3),
    PRIMARY KEY (id)
);
-- @block insert MotoGP riders into 'riders' table
INSERT INTO riders(
        rider_name,
        race_number,
        name_num_abbrev,
        team,
        birth_city,
        birth_country,
        date_of_birth,
        height,
        weight
    )
VALUES(
        "FRANCESCO BAGNAIA",
        1,
        "FB1",
        "DUCATI LENOVO TEAM",
        "TORINO",
        "IT",
        "1997-01-14",
        176,
        67
    ),
    (
        "FABIO QUARTARARO",
        20,
        "FB20",
        "MONSTER ENERGY YAMAHA MOTOGP",
        "NICE",
        "FR",
        "1999-04-20",
        177,
        64
    ),
    (
        "MARCO BEZZECCHI",
        72,
        "MB72",
        "MOONEY VR46 RACING TEAM",
        "RIMINI",
        "IT",
        "1998-11-12",
        174,
        61
    );
-- @block return all rows from 'riders' table
SELECT *
FROM riders
ORDER BY motogp_race_wins DESC;
-- @block add motogp_race_wins as column to riders
ALTER TABLE riders
ADD COLUMN motogp_races INT(4) NOT NULL,
    ADD COLUMN motogp_race_wins INT(3) NOT NULL,
    ADD COLUMN motogp_championships INT(2) NOT NULL
AFTER team;
-- @block add race data to newly created columns for each rider_1
UPDATE riders
SET motogp_races = 34,
    motogp_race_wins = 3,
    motogp_championships = 0
WHERE race_number = 72;
-- @block create table containing MotoGP manufacturers
CREATE TABLE IF NOT EXISTS teams(
    id INT NOT NULL AUTO_INCREMENT,
    team VARCHAR(255) UNIQUE,
    bike_manufacturer VARCHAR(255) NOT NULL,
    main_sponsor VARCHAR(255) NOT NULL,
    rider_1 VARCHAR(255) NOT NULL,
    rider_2 VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (team) REFERENCES riders(team)
);
-- @block change new column positioning
ALTER TABLE riders
MODIFY motogp_race_wins INT(3)
AFTER motogp_races;