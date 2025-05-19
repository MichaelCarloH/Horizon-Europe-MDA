export const API_CONFIG = {
    CHAT: {
        BASE_URL: "http://localhost:8000",
        //BASE_URL: "https://mda-horizon-backend-2025.azurewebsites.net",
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
            projectID?: string;
            projectAcronym?: string; 
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
            if (metadata.projectID) formattedResponse += `**Project ID:** ${metadata.projectID}\n`;
            if (metadata.projectAcronym) formattedResponse += `**Acronym:** ${metadata.projectAcronym}\n`;
            formattedResponse += `**Relevance:** ${(source.relevance_score * 100).toFixed(1)}%\n`;
        });
    }

    return formattedResponse;
}; 