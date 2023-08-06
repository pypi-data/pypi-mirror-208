import { IDict, IJupyterCadDoc } from '../types';
import { ICircle, ILine, IOperator, IPlane, IPoint, IPosition, ISketcherModel } from './types';
export declare class SketcherModel implements ISketcherModel {
    constructor(options: {
        gridSize: number;
        sharedModel?: IJupyterCadDoc;
    });
    get gridSize(): number;
    get points(): Map<string, IPoint>;
    get lines(): Map<string, ILine>;
    get circles(): Map<string, ICircle>;
    get editing(): {
        type: IOperator | null;
        content: IDict | null;
    };
    startEdit(type: IOperator, content: IDict): void;
    updateEdit(type: IOperator, content: IDict): void;
    stopEdit(removeLast?: boolean): void;
    addPoint(position: IPosition, option?: {
        color: string;
    }): string;
    removePoint(id: string): void;
    getPointByPosition(pos: IPosition): string | undefined;
    getPointById(id: string): IPoint | undefined;
    addLine(start: IPosition, end: IPosition): string;
    removeLine(id: string): void;
    getLineById(id: string): ILine | undefined;
    getLineByControlPoint(pointId: string): string[];
    addCircle(center: IPosition, radius: number): void;
    removeCircle(id: string): void;
    getCircleById(id: string): ICircle | undefined;
    getCircleByControlPoint(id: string): string[];
    save(fileName: string, plane: IPlane): Promise<void>;
    private _writeLine;
    private _writeCircle;
    private _points;
    private _lines;
    private _circles;
    private _gridSize;
    private _editing;
    private _sharedModel?;
}
