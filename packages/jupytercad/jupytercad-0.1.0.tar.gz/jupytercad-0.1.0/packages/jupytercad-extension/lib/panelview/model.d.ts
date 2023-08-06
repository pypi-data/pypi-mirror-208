import { ISignal } from '@lumino/signaling';
import { IJupyterCadTracker } from '../token';
import { IControlPanelModel, IJupyterCadDoc, IJupyterCadModel, IJupyterCadWidget } from '../types';
export declare class ControlPanelModel implements IControlPanelModel {
    constructor(options: ControlPanelModel.IOptions);
    get documentChanged(): ISignal<IJupyterCadTracker, IJupyterCadWidget | null>;
    get filePath(): string | undefined;
    get jcadModel(): IJupyterCadModel | undefined;
    get sharedModel(): IJupyterCadDoc | undefined;
    disconnect(f: any): void;
    private readonly _tracker;
    private _documentChanged;
}
declare namespace ControlPanelModel {
    interface IOptions {
        tracker: IJupyterCadTracker;
    }
}
export {};
