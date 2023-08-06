import { ServiceManager } from '@jupyterlab/services';
import { Kernel } from '@jupyterlab/services';
import { IJupyterCadWidgetModelRegistry, IJupyterCadWidgetManager } from './token';
import { IJupyterCadModel } from '../types';
import { ITranslator } from '@jupyterlab/translation';
export declare class JupyterCadWidgetManager implements IJupyterCadWidgetManager {
    constructor(options: {
        manager: ServiceManager.IManager;
        translator: ITranslator;
    });
    registerKernel(kernel: Kernel.IKernelConnection): void;
    unregisterKernel(kernelId?: string | null): void;
    getWidgetModel(kernelId: string, commId: string): IJupyterCadModel | undefined;
    private _registry;
    private _manager;
    private _trans;
}
export declare class WidgetModelRegistry implements IJupyterCadWidgetModelRegistry {
    constructor(options: {
        kernel: Kernel.IKernelConnection;
        manager: ServiceManager.IManager;
        translator: ITranslator;
    });
    getModel(id: string): IJupyterCadModel | undefined;
    /**
     * Handle when a comm is opened.
     */
    private _handle_comm_open;
    private _jcadModels;
    private _manager;
    private _trans;
}
