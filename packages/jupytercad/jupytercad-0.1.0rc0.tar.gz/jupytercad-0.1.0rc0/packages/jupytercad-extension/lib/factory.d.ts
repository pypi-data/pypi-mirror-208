import { IJupyterCadTracker } from './token';
import { ABCWidgetFactory, DocumentRegistry } from '@jupyterlab/docregistry';
import { CommandRegistry } from '@lumino/commands';
import { JupyterCadModel } from './model';
import { JupyterCadWidget } from './widget';
interface IOptios extends DocumentRegistry.IWidgetFactoryOptions {
    tracker: IJupyterCadTracker;
    commands: CommandRegistry;
}
export declare class JupyterCadWidgetFactory extends ABCWidgetFactory<JupyterCadWidget, JupyterCadModel> {
    private _commands;
    constructor(options: IOptios);
    /**
     * Create a new widget given a context.
     *
     * @param context Contains the information of the file
     * @returns The widget
     */
    protected createNewWidget(context: DocumentRegistry.IContext<JupyterCadModel>): JupyterCadWidget;
}
export {};
