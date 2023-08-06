import { Dialog } from '@jupyterlab/apputils';
import * as React from 'react';
import { SketcherModel } from './sketchermodel';
import { SketcherReactWidget } from './sketcherwidget';
export class SketcherDialog extends Dialog {
    constructor(options) {
        const model = new SketcherModel({
            gridSize: 64,
            sharedModel: options.sharedModel
        });
        const body = (React.createElement(SketcherReactWidget, { model: model, closeCallback: options.closeCallback }));
        super({ title: 'Sketcher', body, buttons: [], hasClose: false });
        this.addClass('jpcad-sketcher-SketcherDialog');
    }
}
