import { getLessons } from "@/data/lesson-dto";

export async function GET() {
    const res = await getLessons();

    // return success
    return new Response(JSON.stringify(res));
  }