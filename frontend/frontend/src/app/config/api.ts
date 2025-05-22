export const API_CONFIG = {
    CHAT: {
        BASE_URL: "http://localhost:8000",
        //BASE_URL: "https://mda-backend-egdkfreqeve7evd4.westeurope-01.azurewebsites.net/",
        ENDPOINTS: {
            QUERY: "/query"
        },
        TIMEOUT: 30000,
        HEADERS: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }
};

export interface QueryResponse {
    answer: string;
    sources?: {
        metadata: {
            title?: string;
            project_id?: string;
            acronym?: string; 
        };
        relevance_score: number;
    }[];
}

export const formatResponse = (response: QueryResponse): string => {
    let formattedResponse = response.answer;
    
    if (response.sources?.length) {
        formattedResponse += "\n\n**Sources:**\n";
        response.sources.forEach((source, index) => {
            const metadata = source.metadata;
            formattedResponse += `\n${index + 1}. `;
            if (metadata.title) formattedResponse += `**Title:** ${metadata.title}\n`;
            if (metadata.project_id) formattedResponse += `**Project ID:** ${metadata.project_id}\n`;
            if (metadata.acronym) formattedResponse += `**Acronym:** ${metadata.acronym}\n`;
            //formattedResponse += `**Relevance:** ${(source.relevance_score * 100).toFixed(1)}%\n`;
        });
    }

    return formattedResponse;
}; 
