-- CreateTable
CREATE TABLE "User" (
    "id" VARCHAR(191) NOT NULL,
    "name" VARCHAR(191),
    "username" VARCHAR(191),
    "email" VARCHAR(191),
    "emailVerified" TIMESTAMP(3),
    "image" VARCHAR(191),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    "password" VARCHAR(72) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "UserInfo" (
    "userInfoID" SERIAL NOT NULL,
    "userID" VARCHAR(45) NOT NULL,
    "firstname" VARCHAR(45) NOT NULL,
    "lastname" VARCHAR(45) NOT NULL,
    "skillLevelID" INTEGER NOT NULL,

    CONSTRAINT "UserInfo_pkey" PRIMARY KEY ("userInfoID")
);

-- CreateTable
CREATE TABLE "lesson" (
    "lessonID" SERIAL NOT NULL,
    "lessonTitle" VARCHAR(150) NOT NULL,
    "lessonTag" VARCHAR(100) NOT NULL,
    "lessonDescription" TEXT NOT NULL,
    "lessonImg" VARCHAR(45) NOT NULL,
    "lessonLength" INTEGER NOT NULL,
    "lessonLink" VARCHAR(45) NOT NULL,
    "isLocked" SMALLINT NOT NULL DEFAULT 1,

    CONSTRAINT "lesson_pkey" PRIMARY KEY ("lessonID")
);

-- CreateTable
CREATE TABLE "progress" (
    "progressID" SERIAL NOT NULL,
    "userID" VARCHAR(191) NOT NULL,
    "lessonID" INTEGER NOT NULL,
    "progress" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "progress_pkey" PRIMARY KEY ("progressID")
);

-- CreateTable
CREATE TABLE "skill" (
    "skillLevelID" INTEGER NOT NULL,
    "skillname" VARCHAR(45) NOT NULL,

    CONSTRAINT "skill_pkey" PRIMARY KEY ("skillLevelID")
);

-- CreateTable
CREATE TABLE "trainingData" (
    "trainingDataID" SERIAL NOT NULL,
    "trainingSetID" INTEGER NOT NULL,
    "inputData" TEXT NOT NULL,
    "outputData" TEXT NOT NULL,

    CONSTRAINT "trainingData_pkey" PRIMARY KEY ("trainingDataID")
);

-- CreateTable
CREATE TABLE "trainingSets" (
    "trainingSetID" SERIAL NOT NULL,
    "setName" VARCHAR(45) NOT NULL,
    "inputWidth" INTEGER NOT NULL,
    "outputWidth" INTEGER NOT NULL,

    CONSTRAINT "trainingSets_pkey" PRIMARY KEY ("trainingSetID")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_username_key" ON "User"("username");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "UserInfo_userID_key" ON "UserInfo"("userID");

-- CreateIndex
CREATE UNIQUE INDEX "skill_skillname_key" ON "skill"("skillname");

-- AddForeignKey
ALTER TABLE "UserInfo" ADD CONSTRAINT "skill" FOREIGN KEY ("skillLevelID") REFERENCES "skill"("skillLevelID") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "progress" ADD CONSTRAINT "User" FOREIGN KEY ("userID") REFERENCES "User"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "progress" ADD CONSTRAINT "lesson" FOREIGN KEY ("lessonID") REFERENCES "lesson"("lessonID") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "trainingData" ADD CONSTRAINT "id" FOREIGN KEY ("trainingSetID") REFERENCES "trainingSets"("trainingSetID") ON DELETE NO ACTION ON UPDATE NO ACTION;

