import { getDatasets } from "@/data/dataset-dto";

export async function GET() {
    const res = await getDatasets();

    // return success
    return new Response(JSON.stringify(res));
  }