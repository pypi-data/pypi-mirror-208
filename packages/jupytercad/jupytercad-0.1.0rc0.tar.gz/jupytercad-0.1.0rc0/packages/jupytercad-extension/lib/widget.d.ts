/// <reference types="react" />
import { ReactWidget } from '@jupyterlab/apputils';
import { DocumentWidget } from '@jupyterlab/docregistry';
import { IObservableMap, ObservableMap } from '@jupyterlab/observables';
import { JSONValue } from '@lumino/coreutils';
import { ISignal } from '@lumino/signaling';
import { AxeHelper, ExplodedView, IJupyterCadModel, IJupyterCadWidget } from './types';
export declare class JupyterCadWidget extends DocumentWidget<JupyterCadPanel, IJupyterCadModel> implements IJupyterCadWidget {
    constructor(options: DocumentWidget.IOptions<JupyterCadPanel, IJupyterCadModel>);
    /**
     * Dispose of the resources held by the widget.
     */
    dispose(): void;
    onResize: (msg: any) => void;
}
export declare class JupyterCadPanel extends ReactWidget {
    /**
     * Construct a `ExamplePanel`.
     *
     * @param context - The documents context.
     */
    constructor(options: {
        model: IJupyterCadModel;
    });
    get viewChanged(): ISignal<ObservableMap<JSONValue>, IObservableMap.IChangedArgs<JSONValue>>;
    /**
     * Dispose of the resources held by the widget.
     */
    dispose(): void;
    get axes(): AxeHelper | undefined;
    set axes(value: AxeHelper | undefined);
    get explodedView(): ExplodedView | undefined;
    set explodedView(value: ExplodedView | undefined);
    deleteAxes(): void;
    render(): JSX.Element;
    private _view;
    private _jcadModel;
}
