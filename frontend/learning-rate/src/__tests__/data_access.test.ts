import { getLessons } from "@/data/lesson-dto";
import { getDatasets, getTrainingData } from "@/data/dataset-dto";
import { getCurrentUserInfo, getCurrentUserLessonProgress, updateCurrentUserLessonProgress } from "@/data/user-dto";
import { getSkillLevels } from "@/data/skill-levels-dto";
import { createUser, login } from "@/data/auth-dto";
import { prismaMock } from '../data/mock_singleton'
import { Session } from "next-auth";
import { hashPassword } from "@/utils/password";
import { RegistrationData } from "@/app/components/signup-signin/registration_form/form_registration";

describe("Lesson data transfer objects.", () => {

    test("getting all lessons.", async () => {

        prismaMock.lesson.findMany.mockResolvedValue([
            {
                lessonID: 1,
                lessonTitle: "The Forward Pass 1",
                lessonTag: "Neurons, Activation, and Layers",
                lessonDescription: "Explore the fundamental components of artificial neural networks! Topics covered include the structure and function of AI neurons, activation mechanisms, and the organization of neurons into layers to form neural networks.",
                lessonImg: "/lmao.jpg",
                lessonLength: 10,
                lessonLink: '/ls1',
                isLocked: 0
            },
            {
                lessonID: 2,
                lessonTitle: "The Forward Pass 2",
                lessonTag: "Input/Hidden/Output Layers and Multi-Layer Perceptrons",
                lessonDescription: "Discover the core elements of Multi-Layer Perceptrons (MLPs). Delve into the architecture and operation of AI neurons, activation functions, and the layering process that constructs robust neural networks.",
                lessonImg: "/lmao.jpg",
                lessonLength: 11,
                lessonLink: '/ls2',
                isLocked: 1
            },
            {
                lessonID: 3,
                lessonTitle: "The Backward Pass 1",
                lessonTag: "Loss Functions and Intro to Backpropagation",
                lessonDescription: "Delve into the concepts of loss functions, from theory to practice. Learn through examples and hands-on calculations. Then, unravel the Chain Rule's role in optimizing MLPs.",
                lessonImg: "/lmao.jpg",
                lessonLength: 12,
                lessonLink: '/ls3',
                isLocked: 1
            }
        ]);

        const lessons = await getLessons();

        // check every lesson has a unique ID
        const lessonIds = lessons.map(lesson => lesson.lessonID);
        const unique = lessonIds.every(id => lessonIds.indexOf(id) === lessonIds.lastIndexOf(id));
        expect(unique).toBe(true);

        // check first lesson is the expected first lesson
        const expected_first_lesson = {
            lessonID: 1,
            lessonTitle: "The Forward Pass 1",
            lessonTag: "Neurons, Activation, and Layers",
            lessonDescription: "Explore the fundamental components of artificial neural networks! Topics covered include the structure and function of AI neurons, activation mechanisms, and the organization of neurons into layers to form neural networks.",
            lessonImg: "/lmao.jpg",
            lessonLength: 10,
            lessonLink: '/ls1',
            isLocked: 0
        };
        expect(lessons[0]).toStrictEqual(expected_first_lesson);


    });



});

describe("dataset data transfer objects.", () => {

    test("getting all datasets.", async () => {

        const expectedSets = [
            {
                trainingSetID: 1,
                setName: "y=2x+1",
                inputWidth: 1,
                outputWidth: 1,
            },
            {
                trainingSetID: 1,
                setName: "XOR Gate",
                inputWidth: 2,
                outputWidth: 1,
            },
            {
                trainingSetID: 1,
                setName: "AND3 Gate",
                inputWidth: 3,
                outputWidth: 1,
            },

        ];

        prismaMock.trainingSets.findMany.mockResolvedValue(expectedSets);

        const sets = await getDatasets();

        sets.forEach((set, i) => expect(set).toStrictEqual(expectedSets[i]));
        
    });

    test("getting data for specfic set.", async () => {

        prismaMock.trainingData.findMany.mockResolvedValue([
            {
                trainingDataID: 1,
                trainingSetID: 1,
                inputData: '[0]',
                outputData: '[1]',
            },
            {
                trainingDataID: 2,
                trainingSetID: 1,
                inputData: '[1]',
                outputData: '[3]',
            },
            {
                trainingDataID: 3,
                trainingSetID: 1,
                inputData: '[2]',
                outputData: '[5]',
            },
            {
                trainingDataID: 4,
                trainingSetID: 1,
                inputData: '[]',
                outputData: '[]',
            },
        ]);

        const data = await getTrainingData(1);

        expect(data.inputs).toEqual([[0], [1], [2], []]);
        expect(data.outputs).toEqual([[1], [3], [5], []]);
    });

    test("getting data for specfic set with wrong params.", async () => {

        prismaMock.trainingData.findMany.mockResolvedValue([
            {
                trainingDataID: 1,
                trainingSetID: 1,
                inputData: '[0]',
                outputData: '[1]',
            },
            {
                trainingDataID: 2,
                trainingSetID: 1,
                inputData: '[1]',
                outputData: '[3]',
            },
            {
                trainingDataID: 3,
                trainingSetID: 1,
                inputData: '[2]',
                outputData: '[5]',
            },
            {
                trainingDataID: 4,
                trainingSetID: 1,
                inputData: '',
                outputData: '',
            },
        ]);

        expect(getTrainingData(1)).rejects.toThrow();
    });



});


describe("user data transfer objects.", () => {

    test("UserInfo DTO", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.userInfo.findUnique.mockResolvedValue({
            userInfoID: 1,
            userID: 'abcd',
            firstname: 'Evertoan',
            lastname: 'Miguel',
            skillLevelID: 3,
        });


        const uinfo = await getCurrentUserInfo(mockSession);
        expect(uinfo).toStrictEqual({
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            firstname: 'Evertoan',
            lastname: 'Miguel',
            skillLevelID: 3,
        });

    });

    test("UserInfo DTO incorrect parameters", async () => {

        const mockSession: Session = {
            user: {
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.userInfo.findUnique.mockResolvedValue(null);


        const uinfo = await getCurrentUserInfo(mockSession);
        expect(uinfo).toStrictEqual(null);

    });

    test("UserInfo DTO incorrect parameters", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue(null);

        prismaMock.userInfo.findUnique.mockResolvedValue(null);


        const uinfo = await getCurrentUserInfo(mockSession);
        expect(uinfo).toStrictEqual(null);

    });

    test("UserInfo DTO incorrect parameters", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue(null);

        prismaMock.userInfo.findUnique.mockResolvedValue(null);


        const uinfo = await getCurrentUserInfo(mockSession);
        expect(uinfo).toStrictEqual(null);

    });


    test("UserProgress DTO", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.lesson.findUnique.mockResolvedValue({
            lessonID: 1,
            lessonTitle: 'ls1',
            lessonTag: 'aaa',
            lessonDescription: 'bbb',
            lessonImg: '/l.jpg',
            lessonLength: 15,
            lessonLink: '/lesson/ls1',
            isLocked: 0
        });

        prismaMock.progress.findFirst.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });


        const uprog = await getCurrentUserLessonProgress(mockSession, 1);

        expect(uprog).toStrictEqual({
            progress: 6,
            length: 15,
        });

    });

    test("UserProgress DTO incorrect parameters", async () => {

        const mockSession: Session = {
            user: {
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue(null);

        prismaMock.lesson.findUnique.mockResolvedValue(null);

        prismaMock.progress.findFirst.mockResolvedValue(null);


        const uprog = await getCurrentUserLessonProgress(mockSession, 1);

        expect(uprog).toStrictEqual(null);

    });

    test("UserProgress DTO incorrect parameters", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue(null);

        prismaMock.lesson.findUnique.mockResolvedValue(null);

        prismaMock.progress.findFirst.mockResolvedValue(null);


        const uprog = await getCurrentUserLessonProgress(mockSession, 1);

        expect(uprog).toStrictEqual(null);

    });

    test("UserProgress DTO incorrect parameters", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.lesson.findUnique.mockResolvedValue(null);

        prismaMock.progress.findFirst.mockResolvedValue(null);


        const uprog = await getCurrentUserLessonProgress(mockSession, 1);

        expect(uprog).toStrictEqual(null);

    });


    test("UserProgress DTO incorrect parameters", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.lesson.findUnique.mockResolvedValue({
            lessonID: 1,
            lessonTitle: 'ls1',
            lessonTag: 'aaa',
            lessonDescription: 'bbb',
            lessonImg: '/l.jpg',
            lessonLength: 15,
            lessonLink: '/lesson/ls1',
            isLocked: 1
        });

        prismaMock.progress.findFirst.mockResolvedValue(null);


        const uprog = await getCurrentUserLessonProgress(mockSession, 1);

        expect(uprog).toStrictEqual(null);

    });

    test("update progress DTO", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.lesson.findUnique.mockResolvedValue({
            lessonID: 1,
            lessonTitle: 'ls1',
            lessonTag: 'aaa',
            lessonDescription: 'bbb',
            lessonImg: '/l.jpg',
            lessonLength: 15,
            lessonLink: '/lesson/ls1',
            isLocked: 0
        });

        prismaMock.progress.findFirst.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 3,
        });

        prismaMock.progress.update.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });

        const uprog = await updateCurrentUserLessonProgress(mockSession, 1, 6);

        expect(uprog).toBe(undefined);

        expect(updateCurrentUserLessonProgress(mockSession, 1, 6)).resolves.not.toThrow();

    });

    test("update progress DTO missing progress", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.lesson.findUnique.mockResolvedValue({
            lessonID: 1,
            lessonTitle: 'ls1',
            lessonTag: 'aaa',
            lessonDescription: 'bbb',
            lessonImg: '/l.jpg',
            lessonLength: 15,
            lessonLink: '/lesson/ls1',
            isLocked: 0
        });

        prismaMock.progress.findFirst.mockResolvedValue(null);

        prismaMock.progress.create.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });


        const uprog = await updateCurrentUserLessonProgress(mockSession, 1, 6);

        expect(uprog).toBe(undefined);

        expect(updateCurrentUserLessonProgress(mockSession, 1, 6)).resolves.not.toThrow();

    });

    test("update progress DTO wrong params", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.lesson.findUnique.mockResolvedValue(null);

        prismaMock.progress.findFirst.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });

        prismaMock.progress.create.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });


        const uprog = await updateCurrentUserLessonProgress(mockSession, 1, 6);

        expect(uprog).toBe(null);

        expect(updateCurrentUserLessonProgress(mockSession, 1, 6)).resolves.not.toThrow();

    });

    test("update progress DTO wrong params", async () => {

        const mockSession: Session = {
            user: {
                id: 'abcd',
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue(null);

        prismaMock.lesson.findUnique.mockResolvedValue({
            lessonID: 1,
            lessonTitle: 'ls1',
            lessonTag: 'aaa',
            lessonDescription: 'bbb',
            lessonImg: '/l.jpg',
            lessonLength: 15,
            lessonLink: '/lesson/ls1',
            isLocked: 0
        });

        prismaMock.progress.findFirst.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });

        prismaMock.progress.create.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });


        const uprog = await updateCurrentUserLessonProgress(mockSession, 1, 6);

        expect(uprog).toBe(null);

        expect(updateCurrentUserLessonProgress(mockSession, 1, 6)).resolves.not.toThrow();

    });

    test("update progress DTO wrong params", async () => {

        const mockSession: Session = {
            user: {
                id: undefined,
                email: 'mrmiguel@emails.co'
            },
            expires: '22/05/2024 23:25'
        }

        prismaMock.user.findUnique.mockResolvedValue(null);

        prismaMock.lesson.findUnique.mockResolvedValue({
            lessonID: 1,
            lessonTitle: 'ls1',
            lessonTag: 'aaa',
            lessonDescription: 'bbb',
            lessonImg: '/l.jpg',
            lessonLength: 15,
            lessonLink: '/lesson/ls1',
            isLocked: 0
        });

        prismaMock.progress.findFirst.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });

        prismaMock.progress.create.mockResolvedValue({
            progressID: 1,
            userID: 'abcd',
            lessonID: 1,
            progress: 6,
        });


        const uprog = await updateCurrentUserLessonProgress(mockSession, 1, 6);

        expect(uprog).toBe(null);

        expect(updateCurrentUserLessonProgress(mockSession, 1, 6)).resolves.not.toThrow();

    });


});

describe("skill level transfer objects.", () => {

    test("get skills DTO", async () => {

        prismaMock.skill.findMany.mockResolvedValue([
            {
                skillLevelID: 1,
                skillname: 'Beginner'
            },
            {
                skillLevelID: 2,
                skillname: 'Intermediate'
            },
            {
                skillLevelID: 3,
                skillname: 'Expert'
            },
        ]);

        const skills = await getSkillLevels();

        // check every lesson has a unique ID
        const skillIds = skills.map(skill => skill.skillLevelID);
        const unique = skillIds.every(id => skillIds.indexOf(id) === skillIds.lastIndexOf(id));
        expect(unique).toBe(true);

    });


});


describe("Authentication transfer objects.", () => {

    test("create user DTO", async () => {

        const data: RegistrationData = {
            name: 'Evertoan', 
            lastName: 'Miguel', 
            skillLevel: 3, 
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co', 
            password: 'cdef'
        };

        prismaMock.user.create.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.user.findFirst.mockResolvedValue({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: 'cdef'
        });

        prismaMock.userInfo.create.mockResolvedValue({
            userInfoID: 1,
            userID: 'abcd',
            firstname: 'Evertoan',
            lastname: 'Miguel',
            skillLevelID: 3,
        });

        prismaMock.$transaction.mockImplementation((callback) => callback(prismaMock));

        const registered = await createUser(data);

        expect(registered).toBe(undefined);

        expect(createUser(data)).resolves.not.toThrow()
    });

    test("login user DTO", async () => {

        // correct user info and password
        prismaMock.user.findUnique.mockResolvedValueOnce({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: await hashPassword('cdef')
        });

        const user = await login('mrmiguel@emails.co', 'cdef');
        expect(user).toStrictEqual({
            id: 'abcd',
            email: 'mrmiguel@emails.co'
        });
            

    });

    test("login user DTO with incorrect parameters", async () => {
        
        // wrong user password
        prismaMock.user.findUnique.mockResolvedValueOnce({
            id: 'abcd',
            name: 'Evertoan Miguel',
            username: 'mrmiguel',
            email: 'mrmiguel@emails.co',
            emailVerified: null,
            image: null,
            createdAt: new Date(Date.parse('22/05/2024')),
            updatedAt: new Date(Date.parse('22/05/2024')),
            password: await hashPassword('cdef')
        });
        expect(login('mrmiguel@emails.co', 'cdefwgsag')).rejects.toThrow('Wrong Password.');

        // invalid email
        prismaMock.user.findUnique.mockResolvedValueOnce(null);
        expect(login('mrmiguel@emails.co', 'cdef')).rejects.toThrow("User not found.");
    

    });


});
