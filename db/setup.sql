-- @block create motogp database
CREATE DATABASE IF NOT EXISTS motogp;
-- @block select database
USE motogp;
-- @block create table containing MotoGP riders
CREATE TABLE IF NOT EXISTS riders (
    id INT NOT NULL AUTO_INCREMENT,
    rider_name VARCHAR(255) NOT NULL,
    hero_hashtag VARCHAR(255) NOT NULL,
    race_number INT NOT NULL,
    team VARCHAR(255),
    bike VARCHAR(255),
    gp_class VARCHAR(6) NOT NULL,
    representing_country VARCHAR(2) NOT NULL,
    place_of_birth VARCHAR(255),
    date_of_birth DATE,
    height INT,
    weight INT,
    PRIMARY KEY (id)
);
-- @block create table with the above select statement
CREATE TABLE IF NOT EXISTS teams (
    id INT NOT NULL AUTO_INCREMENT,
    team VARCHAR(255) UNIQUE NOT NULL,
    manufacturer VARCHAR(255),
    gp_class VARCHAR(6) NOT NULL,
    PRIMARY KEY(id)
);