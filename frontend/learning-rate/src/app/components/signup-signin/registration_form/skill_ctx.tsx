import { createContext } from 'react';

export interface skillLevelArray {
    
    levels: {skillLevelID: number, skillname: string}[];

}

export const skillLevelContext = createContext<skillLevelArray>({
    levels: []
});