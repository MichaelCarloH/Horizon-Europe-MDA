import 'server-only';
import client from '@/data/prisma'

export async function getLessons() {

    const lessons = await client.lesson.findMany({
        orderBy: {
            lessonID: 'asc'
        }
    });

    // otherwise return combined user data object
    return lessons;
}
