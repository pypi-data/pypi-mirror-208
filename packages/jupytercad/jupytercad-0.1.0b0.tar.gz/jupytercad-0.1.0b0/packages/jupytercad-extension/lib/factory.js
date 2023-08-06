var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
import { ABCWidgetFactory } from '@jupyterlab/docregistry';
import { JupyterCadPanel, JupyterCadWidget } from './widget';
import { ToolbarWidget } from './toolbar/widget';
export class JupyterCadWidgetFactory extends ABCWidgetFactory {
    constructor(options) {
        const rest = __rest(options, []);
        super(rest);
        this._commands = options.commands;
    }
    /**
     * Create a new widget given a context.
     *
     * @param context Contains the information of the file
     * @returns The widget
     */
    createNewWidget(context) {
        const { model } = context;
        const content = new JupyterCadPanel({ model });
        const toolbar = new ToolbarWidget({
            commands: this._commands,
            model
        });
        return new JupyterCadWidget({ context, content, toolbar });
    }
}
