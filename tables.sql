use musicfan_db;

DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS forum;
DROP TABLE IF EXISTS album;
DROP TABLE IF EXISTS beef;
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS user;

CREATE TABLE `artist` (
  artistID INT AUTO_INCREMENT PRIMARY KEY,
  `name` varchar(20),
  `genre` ENUM ('pop', 'rock', 'hiphop', 'hip hop', 'rnb' ,'rap', 'electronic',
            'dance', 'jazz', 'classical', 'reggae', 'country', 'indie','punk', 'metal'),
  `rating` float DEFAULT NULL,
  `approvalStatus` ENUM ('pending', 'approved', 'rejected') DEFAULT 'pending'
);

CREATE TABLE `ratings` (
  `artistID` INT,
  `rating` float(2),
  `userID` INT
);

CREATE TABLE `beef` (
  `bid` INT AUTO_INCREMENT PRIMARY KEY,
  `artist1` INT,
  `artist2` INT,
  `countArtist1` int DEFAULT 0,
  `countArtist2` int DEFAULT 0,
  `context` text,
  `approved` ENUM ('pending', 'approved', 'rejected') DEFAULT 'pending'
);

CREATE TABLE `album` (
  `albumID` INT AUTO_INCREMENT PRIMARY KEY,
  `title` varchar(50),
  `release` date,
  `artistID` INT,
  `approved` ENUM ('pending', 'approved', 'rejected')
);

CREATE TABLE `user` (
  `userID` INT AUTO_INCREMENT PRIMARY KEY,
  `user_email` varchar(30),
  `fname` varchar(50),
  `lname` varchar(50),
  `password` varchar(100)
);

CREATE TABLE `post` (
  `post_id` INT AUTO_INCREMENT PRIMARY KEY,
  `forum_id` INT,
  `userID` INT,
  `created_at` timestamp,
  `content` text
);

CREATE TABLE `forum` (
  `forum_id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` varchar(20),
  `userID` INT,
  `created_at` timestamp,
  `type` ENUM ('beef', 'music', 'explore')
);

-- ALTER TABLE `ratings` ADD FOREIGN KEY (`rating`) REFERENCES `artist` (`rating`);

ALTER TABLE `ratings` ADD FOREIGN KEY (`artistID`) REFERENCES `artist` (`artistID`);

ALTER TABLE `ratings` ADD FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);

ALTER TABLE `beef` ADD FOREIGN KEY (`artist1`) REFERENCES `artist` (`artistID`);

ALTER TABLE `beef` ADD FOREIGN KEY (`artist2`) REFERENCES `artist` (`artistID`);

ALTER TABLE `album` ADD FOREIGN KEY (`artistID`) REFERENCES `artist` (`artistID`);

ALTER TABLE `post` ADD FOREIGN KEY (`forum_id`) REFERENCES `forum` (`forum_id`);

ALTER TABLE `post` ADD FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);

ALTER TABLE `forum` ADD FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);
