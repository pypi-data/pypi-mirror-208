import { ICircle, IPosition } from '../types';
export declare class Circle implements ICircle {
    center: IPosition;
    radius: number;
    controlPoints?: string[] | undefined;
    constructor(center: IPosition, radius: number, controlPoints?: string[] | undefined);
    export(scaleFactor?: number): {
        center: IPosition;
        radius: number;
    };
}
