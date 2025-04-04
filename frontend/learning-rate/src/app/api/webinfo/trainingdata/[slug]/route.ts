import { getTrainingData } from "@/data/dataset-dto";
import { NextRequest } from "next/server";

export async function GET(
    request: NextRequest,
    {params}: {params: {slug:string}}
) {
    const slug = params.slug

    const res = await getTrainingData(Number(slug));

    return new Response(JSON.stringify(res))

}