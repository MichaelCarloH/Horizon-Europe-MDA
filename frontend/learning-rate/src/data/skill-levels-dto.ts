import 'server-only';
import client from '@/data/prisma'

export async function getSkillLevels() {

    const levels = await client.skill.findMany();

    // otherwise return combined user data object
    return levels;
}
