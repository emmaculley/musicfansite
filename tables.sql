CREATE TABLE `artist` (
  `artistID` varchar(10) PRIMARY KEY,
  `name` varchar(20),
  `genre` ENUM ('pop', 'rock', 'hiphop', 'rap', 'electronic', 'dance', 'jazz'),
  `rating` float,
  `approvalStatus` ENUM ('pending', 'approved', 'rejected')
);

CREATE TABLE `ratings` (
  `ArtistID` varchar(10),
  `rating` float(2),
  `userID` varchar(10)
);

CREATE TABLE `beef` (
  `bid` varchar(10) PRIMARY KEY,
  `artist1` varchar(10),
  `artist2` varchar(10),
  `countArtist1` int(5),
  `countArtist2` int(5),
  `context` text,
  `approved` ENUM ('pending', 'approved', 'rejected')
);

CREATE TABLE `album` (
  `albumID` varchar(10) PRIMARY KEY,
  `title` varchar(50),
  `release` date,
  `artistID` varchar(10),
  `approved` ENUM ('pending', 'approved', 'rejected')
);

CREATE TABLE `user` (
  `userID` varchar(10) PRIMARY KEY,
  `user_email` varchar(30),
  `fname` varchar(50),
  `lname` varchar(50),
  `password` varchar(30)
);

CREATE TABLE `post` (
  `post_id` varchar(10) PRIMARY KEY,
  `forum_id` integer,
  `userID` varchar(10),
  `created_at` timestamp,
  `content` text
);

CREATE TABLE `forum` (
  `forum_id` varchar(10) PRIMARY KEY,
  `title` varchar[500],
  `userID` varchar(30),
  `created_at` timestamp,
  `type` ENUM ('beef', 'music', 'explore')
);

ALTER TABLE `ratings` ADD FOREIGN KEY (`rating`) REFERENCES `artist` (`rating`);

ALTER TABLE `ratings` ADD FOREIGN KEY (`ArtistID`) REFERENCES `artist` (`artistID`);

ALTER TABLE `beef` ADD FOREIGN KEY (`artist1`) REFERENCES `artist` (`artistID`);

ALTER TABLE `beef` ADD FOREIGN KEY (`artist2`) REFERENCES `artist` (`artistID`);

ALTER TABLE `album` ADD FOREIGN KEY (`artistID`) REFERENCES `artist` (`artistID`);

ALTER TABLE `forum` ADD FOREIGN KEY (`forum_id`) REFERENCES `post` (`forum_id`);

ALTER TABLE `post` ADD FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);

ALTER TABLE `forum` ADD FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);
