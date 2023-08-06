import { IDisposable } from '@lumino/disposable';
import { IJupyterCadModel } from '../types';
import { IJupyterCadWidgetManager } from './token';
export declare class NotebookRendererModel implements IDisposable {
    constructor(options: NotebookRendererModel.IOptions);
    get isDisposed(): boolean;
    dispose(): void;
    createJcadModel(commId: string): IJupyterCadModel | undefined;
    private _isDisposed;
    private _kernelId?;
    private _widgetManager;
}
export declare namespace NotebookRendererModel {
    interface IOptions {
        kernelId?: string;
        widgetManager: IJupyterCadWidgetManager;
    }
}
