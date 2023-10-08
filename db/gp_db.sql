-- @block create motogp database
CREATE DATABASE IF NOT EXISTS motogp;
-- @block create table containing MotoGP riders
CREATE TABLE IF NOT EXISTS motogp_riders(
    id INT NOT NULL AUTO_INCREMENT,
    rider_name VARCHAR(255) UNIQUE NOT NULL,
    hero_hashtag VARCHAR(255) NOT NULL,
    race_number INT(2) NOT NULL,
    team VARCHAR(255),
    bike VARCHAR(255),
    representing_country VARCHAR(2) NOT NULL,
    place_of_birth VARCHAR(255),
    date_of_birth DATE,
    height INT(3),
    weight INT(3),
    PRIMARY KEY (id)
);
-- @block clone motogp_riders table to other GP classes (inherit all table definitions)
CREATE TABLE IF NOT EXISTS moto2_riders LIKE motogp_riders;
CREATE TABLE IF NOT EXISTS moto3_riders LIKE motogp_riders;
CREATE TABLE IF NOT EXISTS motoe_riders LIKE motogp_riders;