import { IPosition } from './types';
export declare class PanZoom {
    private ctx;
    private gridSize;
    constructor(ctx: CanvasRenderingContext2D, gridSize: number);
    apply(): void;
    scaleAt(x: number, y: number, sc: number): void;
    toWorld(screenCoor: IPosition, snap?: boolean, tol?: number): IPosition;
    toScreen(worldPos: IPosition): IPosition;
    x: number;
    y: number;
    scale: number;
}
