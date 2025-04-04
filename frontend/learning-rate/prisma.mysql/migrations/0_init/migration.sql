-- CreateTable
CREATE TABLE `User` (
    `id` VARCHAR(191) NOT NULL,
    `name` VARCHAR(191) NULL,
    `username` VARCHAR(191) NULL,
    `email` VARCHAR(191) NULL,
    `emailVerified` DATETIME(3) NULL,
    `image` VARCHAR(191) NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `password` VARCHAR(72) NOT NULL,

    UNIQUE INDEX `User_username_key`(`username`),
    UNIQUE INDEX `User_email_key`(`email`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `lesson` (
    `lessonID` INTEGER NOT NULL AUTO_INCREMENT,
    `lessonTitle` VARCHAR(150) NOT NULL,
    `lessonTag` VARCHAR(100) NOT NULL,
    `lessonDescription` TEXT NOT NULL,
    `lessonImg` VARCHAR(45) NOT NULL,
    `lessonLength` INTEGER NOT NULL,
    `lessonLink` VARCHAR(45) NOT NULL,
    `isLocked` TINYINT NOT NULL DEFAULT 1,

    UNIQUE INDEX `lessonTitle_UNIQUE`(`lessonTitle`),
    PRIMARY KEY (`lessonID`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `progress` (
    `progressID` INTEGER NOT NULL AUTO_INCREMENT,
    `userID` VARCHAR(191) NOT NULL,
    `lessonID` INTEGER NOT NULL,
    `progress` INTEGER NOT NULL DEFAULT 0,

    INDEX `lesson_idx`(`lessonID`),
    INDEX `user_idx`(`userID`),
    PRIMARY KEY (`progressID`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `skill` (
    `skillLevelID` INTEGER NOT NULL,
    `skillname` VARCHAR(45) NOT NULL,

    PRIMARY KEY (`skillLevelID`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `trainingData` (
    `trainingDataID` INTEGER NOT NULL AUTO_INCREMENT,
    `trainingSetID` INTEGER NOT NULL,
    `inputData` MEDIUMTEXT NOT NULL,
    `outputData` MEDIUMTEXT NOT NULL,

    UNIQUE INDEX `trainingDataID_UNIQUE`(`trainingDataID`),
    INDEX `id_idx`(`trainingSetID`),
    PRIMARY KEY (`trainingDataID`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `trainingSets` (
    `trainingSetID` INTEGER NOT NULL AUTO_INCREMENT,
    `setName` VARCHAR(45) NOT NULL,
    `inputWidth` INTEGER NOT NULL,
    `outputWidth` INTEGER NOT NULL,

    UNIQUE INDEX `trainingSetID_UNIQUE`(`trainingSetID`),
    UNIQUE INDEX `setName_UNIQUE`(`setName`),
    PRIMARY KEY (`trainingSetID`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `UserInfo` (
    `userInfoID` INTEGER NOT NULL AUTO_INCREMENT,
    `userID` VARCHAR(45) NOT NULL,
    `firstname` VARCHAR(45) NOT NULL,
    `lastname` VARCHAR(45) NOT NULL,
    `skillLevelID` INTEGER NOT NULL,

    UNIQUE INDEX `userInfoID_UNIQUE`(`userInfoID`),
    UNIQUE INDEX `userID_UNIQUE`(`userID`),
    INDEX `skill_idx`(`skillLevelID`),
    PRIMARY KEY (`userInfoID`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `progress` ADD CONSTRAINT `User` FOREIGN KEY (`userID`) REFERENCES `User`(`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE `progress` ADD CONSTRAINT `lesson` FOREIGN KEY (`lessonID`) REFERENCES `lesson`(`lessonID`) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE `trainingData` ADD CONSTRAINT `setid` FOREIGN KEY (`trainingSetID`) REFERENCES `trainingSets`(`trainingSetID`) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE `UserInfo` ADD CONSTRAINT `skill` FOREIGN KEY (`skillLevelID`) REFERENCES `skill`(`skillLevelID`) ON DELETE NO ACTION ON UPDATE NO ACTION;

