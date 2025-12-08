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
  `name` varchar(50) UNIQUE,
  `genre` ENUM ('pop','rock','hiphop','rap','electronic','R&B',
            'dance','jazz','classical','metal','reggae',
            'country','indie','punk', 'folk'),
  `rating` float DEFAULT NULL,
  `approvalStatus` ENUM ('pending', 'approved', 'rejected') DEFAULT 'pending'
);

CREATE TABLE `ratings` (
  `artistID` INT,
  `rating` float(2),
  `userID` INT
);

CREATE TABLE beef (
  bid INT AUTO_INCREMENT PRIMARY KEY,
  artist1 INT,
  artist2 INT,

  -- Canonical ordering so (artist1, artist2) and (artist2, artist1) mean the same beef
  a1 INT AS (LEAST(artist1, artist2)) STORED,
  a2 INT AS (GREATEST(artist1, artist2)) STORED,

  countArtist1 INT DEFAULT 0,
  countArtist2 INT DEFAULT 0,
  context TEXT,
  approved ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',

  UNIQUE(a1, a2)
);

--want to talk about a certain pair of id's
-- primary key as the combination of artist1 and artist2

CREATE TABLE `album` (
  `albumID` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(50),
  `release` INT,
  `artistID` INT,
  `approved` ENUM('pending', 'approved', 'rejected'),
  UNIQUE KEY `unique_album_per_artist` (`artistID`, `title`)
);

 
CREATE TABLE `user` (
  `userID` INT AUTO_INCREMENT PRIMARY KEY,
  `user_email` VARCHAR(30) UNIQUE,
  `fname` VARCHAR(50),
  `lname` VARCHAR(50),
  `password` VARCHAR(100)
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

CREATE TABLE `beef_votes` (
  `vote_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `bid` INT NOT NULL,
  `voted_for` INT NOT NULL,

  UNIQUE KEY `unique_user_beef` (`user_id`, `bid`),

  FOREIGN KEY (`user_id`) REFERENCES `user`(`userID`) ON DELETE CASCADE,

  FOREIGN KEY (`bid`) REFERENCES `beef`(`bid`) ON DELETE CASCADE,

  FOREIGN KEY (`voted_for`) REFERENCES `artist`(`artistID`) ON DELETE CASCADE
);

ALTER TABLE `ratings` ADD FOREIGN KEY (`artistID`) REFERENCES `artist` (`artistID`);

ALTER TABLE `ratings` ADD FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);

ALTER TABLE `beef` ADD FOREIGN KEY (`artist1`) REFERENCES `artist` (`artistID`);

ALTER TABLE `beef` ADD FOREIGN KEY (`artist2`) REFERENCES `artist` (`artistID`);

ALTER TABLE `album` ADD FOREIGN KEY (`artistID`) REFERENCES `artist` (`artistID`);

ALTER TABLE `post` ADD FOREIGN KEY (`forum_id`) REFERENCES `forum` (`forum_id`);

ALTER TABLE `post` ADD FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);

ALTER TABLE `forum` ADD FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);
