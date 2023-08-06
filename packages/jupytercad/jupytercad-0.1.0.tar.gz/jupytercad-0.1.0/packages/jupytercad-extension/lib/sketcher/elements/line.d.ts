import { ILine, IPosition } from '../types';
export declare class Line implements ILine {
    start: IPosition;
    end: IPosition;
    controlPoints?: string[] | undefined;
    constructor(start: IPosition, end: IPosition, controlPoints?: string[] | undefined);
    export(scaleFactor?: number): {
        start: IPosition;
        end: IPosition;
    };
}
