import { IPoint, IPosition } from '../types';
export declare class Point implements IPoint {
    option?: {
        color: string;
    } | undefined;
    constructor(x: number, y: number, option?: {
        color: string;
    } | undefined);
    get position(): IPosition;
    export(scaleFactor?: number): IPosition;
    private _x;
    private _y;
}
