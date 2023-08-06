import { Dialog } from '@jupyterlab/apputils';
import { IDict, IJupyterCadDoc } from '../types';
export interface ISketcherDialogOptions {
    sharedModel: IJupyterCadDoc;
    closeCallback: {
        handler: () => void;
    };
}
export declare class SketcherDialog extends Dialog<IDict> {
    constructor(options: ISketcherDialogOptions);
}
