/// <reference types="react" />
import { IPosition } from './types';
export declare function drawPoint(ctx: CanvasRenderingContext2D, point: IPosition, fillStyle?: string, size?: number): void;
export declare function drawLine(ctx: CanvasRenderingContext2D, start: IPosition, end: IPosition, strokeStyle: string, lineWidth?: number): void;
export declare function drawCircle(ctx: CanvasRenderingContext2D, center: IPosition, radius: number, strokeStyle: string, lineWidth?: number): void;
export declare function ToolbarSwitch(props: {
    label: string;
    toggled: boolean;
    onClick: () => void;
}): JSX.Element;
export declare function distance(p1: IPosition, p2: IPosition): number;
