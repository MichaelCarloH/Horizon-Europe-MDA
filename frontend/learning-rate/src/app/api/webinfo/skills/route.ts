import { getSkillLevels } from "@/data/skill-levels-dto";

export async function GET() {
    const res = await getSkillLevels();

    // return success
    return new Response(JSON.stringify(res));
  }