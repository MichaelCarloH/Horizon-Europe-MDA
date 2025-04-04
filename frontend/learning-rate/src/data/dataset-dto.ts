import 'server-only';
import client from '@/data/prisma'

export async function getDatasets() {

    const datasets = await client.trainingSets.findMany();

    // otherwise return combined user data object
    return datasets;
}


export async function getTrainingData(datasetId: number) {

    const dataRaw = await client.trainingData.findMany({
        where: {
            trainingSetID: datasetId,
        },
        select: {
            inputData: true,
            outputData: true,
        }
    });

    const inputData = dataRaw.map(data => data.inputData);
    const outputData = dataRaw.map(data => data.outputData);

    const inputs: number[][] = inputData.map(input => JSON.parse(input));
    const outputs: number[][] = outputData.map(output => JSON.parse(output));

    const data: { inputs: number[][], outputs: number[][] } = { inputs: inputs, outputs: outputs };

    // otherwise return combined user data object
    return data;
}
