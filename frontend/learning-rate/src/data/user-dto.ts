import 'server-only';
import client from '@/data/prisma'
import { Session } from 'next-auth';


export async function getCurrentUserInfo(session: Session | null) {
    const uid = session?.user.id;

    // quit if invalid
    if(!uid) return null;


    // get user data from the 2 tables
    const userRaw = await client.user.findUnique({
        where: {
            id: uid,
        },
        select: {
            username: true,
            email: true,
        }
    });

    const userInfo = await client.userInfo.findUnique({
        where: {
            userID: uid,
        },
        select: {
            firstname: true,
            lastname: true,
            skillLevelID: true,
            }
    });

    // if either is undefined return null
    if(!userInfo || !userRaw) return null;

    // otherwise return combined user data object
    return {
        username: userRaw.username,
        email: userRaw.email,
        firstname: userInfo.firstname,
        lastname: userInfo.lastname,
        skillLevelID: userInfo.skillLevelID,
    };
}

export async function getCurrentUserLessonProgress(session: Session | null, lessonId: number) {
    const uid = session?.user.id;

    if(!uid) return null;

    const userRaw = await client.user.findUnique({
        where: {
            id: uid,
        },
        select: {
            email: true,
        }
    });

    if(!userRaw || userRaw.email != session.user.email) return null;

    // verify lesson id is valid
    const lesson = await client.lesson.findUnique({
        where: {
            lessonID: lessonId,
        },
        select: {
            lessonID: true,
            lessonLength: true
        }
    });

    if(!lesson) return null;

    // get lesson progress for user
    const lessonProgress = await client.progress.findFirst({
        where: {
            userID: uid,
            lessonID: lesson.lessonID
        },
        select: {
            progress: true
        }
    });

    if(!lessonProgress) return null;

    return {
        progress: lessonProgress.progress,
        length: lesson.lessonLength
    };
}

export async function updateCurrentUserLessonProgress(session: Session | null, lessonId: number, newProgress: number) {
    const uid = session?.user.id;

    if(!uid) return null;

    const userRaw = await client.user.findUnique({
        where: {
            id: uid,
        },
        select: {
            email: true,
        }
    });

    if(!userRaw || userRaw.email != session.user.email) return null;

    // verify lesson id is valid
    const lesson = await client.lesson.findUnique({
        where: {
            lessonID: lessonId,
        },
        select: {
            lessonID: true,
            lessonLength: true
        }
    });

    if(!lesson) return null;

    // get lesson progress for user
    const lessonProgress = await client.progress.findFirst({
        where: {
            userID: uid,
            lessonID: lesson.lessonID
        },
        select: {
            progressID: true,
            progress: true
        }
    });

    // verify progress exists
    if(!lessonProgress) {
        // add if it doesnt exist
        await client.progress.create({
            data: {
                userID: uid,
                lessonID: lessonId,
                progress: newProgress
            }
        });
    }
    else if(newProgress !== lessonProgress.progress) {
        // update progress
        await client.progress.update({
            where: {
                progressID: lessonProgress.progressID
            },
            data: {
                progress: newProgress
            }
        });
    }

}