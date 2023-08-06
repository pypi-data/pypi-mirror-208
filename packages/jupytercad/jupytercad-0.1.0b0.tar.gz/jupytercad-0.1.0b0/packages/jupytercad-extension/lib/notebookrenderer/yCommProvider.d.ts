import { Kernel } from '@jupyterlab/services';
import * as Y from 'yjs';
import { IDisposable } from '@lumino/disposable';
export declare enum YMessageType {
    SYNC = 0,
    AWARENESS = 1
}
export declare class YCommProvider implements IDisposable {
    constructor(options: {
        comm: Kernel.IComm;
        ydoc: Y.Doc;
    });
    get doc(): Y.Doc;
    get synced(): boolean;
    set synced(state: boolean);
    get isDisposed(): boolean;
    dispose(): void;
    private _onMsg;
    private _updateHandler;
    private _connect;
    private _sync;
    private _sendOverComm;
    private _comm;
    private _ydoc;
    private _synced;
    private _isDisposed;
}
