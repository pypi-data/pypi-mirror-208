import * as React from 'react';
import { IOperator, IPosition, ISketcherModel } from './types';
interface IProps {
    model: ISketcherModel;
    closeCallback: {
        handler: () => void;
    };
}
interface IState {
    mode?: IOperator;
    plane: 'XY' | 'YZ' | 'ZX';
    sketchName?: string;
    currentPointer?: IPosition;
}
export declare class SketcherReactWidget extends React.Component<IProps, IState> {
    constructor(props: IProps);
    componentDidMount(): void;
    get ctx(): CanvasRenderingContext2D | null;
    initiateEditor(): void;
    handleMouseMove: (e: MouseEvent) => void;
    handleRightClick: (e: MouseEvent) => void;
    handleLeftClick: (e: MouseEvent) => void;
    mousePanAnZoom: (e: MouseEvent) => void;
    drawGrid: (gridScreenSize?: number) => void;
    drawCenter: (size: number) => void;
    drawPointer: (x: number, y: number) => void;
    draw: () => void;
    update: () => void;
    globalToLocalPos: (global: IPosition) => IPosition;
    screenToWorldPos: (screen: IPosition) => IPosition;
    toggleMode: (mode: IOperator) => (() => void);
    saveButtonOnClick: () => Promise<void>;
    render(): React.ReactNode;
    private _mouse;
    private _gridLimit;
    private _gridSize;
    private _scaleRate;
    private _topLeft;
    private _divRef;
    private _canvasRef;
    private _panZoom;
}
export {};
