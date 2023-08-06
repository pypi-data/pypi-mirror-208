import { ReactWidget } from '@jupyterlab/apputils';
import { DocumentWidget } from '@jupyterlab/docregistry';
import { ObservableMap } from '@jupyterlab/observables';
import { Signal } from '@lumino/signaling';
import * as React from 'react';
import { MainView } from './mainview';
export class JupyterCadWidget extends DocumentWidget {
    constructor(options) {
        super(options);
        this.onResize = (msg) => {
            window.dispatchEvent(new Event('resize'));
        };
    }
    /**
     * Dispose of the resources held by the widget.
     */
    dispose() {
        this.content.dispose();
        super.dispose();
    }
}
export class JupyterCadPanel extends ReactWidget {
    /**
     * Construct a `ExamplePanel`.
     *
     * @param context - The documents context.
     */
    constructor(options) {
        super();
        this.addClass('jp-jupytercad-panel');
        this._jcadModel = options.model;
        this._view = new ObservableMap();
    }
    get viewChanged() {
        return this._view.changed;
    }
    /**
     * Dispose of the resources held by the widget.
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        Signal.clearData(this);
        super.dispose();
    }
    get axes() {
        return this._view.get('axes');
    }
    set axes(value) {
        this._view.set('axes', value || null);
    }
    get explodedView() {
        return this._view.get('explodedView');
    }
    set explodedView(value) {
        this._view.set('explodedView', value || null);
    }
    deleteAxes() {
        this._view.delete('axes');
    }
    render() {
        return React.createElement(MainView, { view: this._view, jcadModel: this._jcadModel });
    }
}
