import { NextRequest } from "next/server";
import { NextResponse } from 'next/server';
import { updateCurrentUserLessonProgress } from '@/data/user-dto'
import { auth } from "@/auth";

export async function POST(request: NextRequest) {
    const { lessonId, newProgress }: { lessonId: number, newProgress: number } = await request.json()

    const session = await auth();

    // push user to data base
    await updateCurrentUserLessonProgress(session, lessonId, newProgress);

    // return success
    return NextResponse.json({ status: 200 });
}
  
