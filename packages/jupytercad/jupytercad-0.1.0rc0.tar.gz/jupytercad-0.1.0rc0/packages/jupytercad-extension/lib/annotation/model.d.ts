import { DocumentRegistry } from '@jupyterlab/docregistry';
import { User } from '@jupyterlab/services';
import { ISignal } from '@lumino/signaling';
import { IAnnotationModel, IAnnotation, IJupyterCadModel } from '../types';
export declare class AnnotationModel implements IAnnotationModel {
    constructor(options: AnnotationModel.IOptions);
    get updateSignal(): ISignal<this, null>;
    get user(): User.IIdentity | undefined;
    set context(context: DocumentRegistry.IContext<IJupyterCadModel> | undefined);
    get context(): DocumentRegistry.IContext<IJupyterCadModel> | undefined;
    get contextChanged(): ISignal<this, void>;
    update(): void;
    getAnnotation(id: string): IAnnotation | undefined;
    getAnnotationIds(): string[];
    addAnnotation(key: string, value: IAnnotation): void;
    removeAnnotation(key: string): void;
    addContent(id: string, value: string): void;
    private _context;
    private _contextChanged;
    private _updateSignal;
    private _user?;
}
declare namespace AnnotationModel {
    interface IOptions {
        context: DocumentRegistry.IContext<IJupyterCadModel> | undefined;
    }
}
export {};
