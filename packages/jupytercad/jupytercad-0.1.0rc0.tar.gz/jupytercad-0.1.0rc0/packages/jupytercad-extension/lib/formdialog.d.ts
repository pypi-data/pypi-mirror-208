import { Dialog } from '@jupyterlab/apputils';
import { IDict, IJupyterCadModel } from './types';
import { DocumentRegistry } from '@jupyterlab/docregistry';
export interface IFormDialogOptions {
    schema: IDict;
    sourceData: IDict;
    title: string;
    cancelButton: (() => void) | boolean;
    syncData: (props: IDict) => void;
    syncSelectedPropField?: (id: string | null, value: any, parentType: 'dialog' | 'panel') => void;
    context: DocumentRegistry.IContext<IJupyterCadModel>;
}
export declare class FormDialog extends Dialog<IDict> {
    constructor(options: IFormDialogOptions);
}
