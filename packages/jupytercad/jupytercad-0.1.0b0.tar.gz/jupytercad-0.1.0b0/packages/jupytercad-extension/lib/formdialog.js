import * as React from 'react';
import { Dialog } from '@jupyterlab/apputils';
import { ObjectPropertiesForm } from './panelview/formbuilder';
import { focusInputField, removeStyleFromProperty } from './tools';
export class FormDialog extends Dialog {
    constructor(options) {
        let cancelCallback = undefined;
        if (options.cancelButton) {
            cancelCallback = () => {
                if (options.cancelButton !== true && options.cancelButton !== false) {
                    options.cancelButton();
                }
                this.resolve(0);
            };
        }
        const filePath = options.context.path;
        const jcadModel = options.context.model;
        const body = (React.createElement("div", { style: { overflow: 'hidden' } },
            React.createElement(ObjectPropertiesForm, { parentType: "dialog", filePath: `${filePath}::dialog`, sourceData: options.sourceData, schema: options.schema, syncData: options.syncData, cancel: cancelCallback, syncSelectedField: options.syncSelectedPropField })));
        let lastSelectedPropFieldId;
        const onClientSharedStateChanged = (sender, clients) => {
            var _a, _b, _c, _d, _e;
            const remoteUser = (_a = jcadModel === null || jcadModel === void 0 ? void 0 : jcadModel.localState) === null || _a === void 0 ? void 0 : _a.remoteUser;
            if (remoteUser) {
                const newState = clients.get(remoteUser);
                const id = (_b = newState === null || newState === void 0 ? void 0 : newState.selectedPropField) === null || _b === void 0 ? void 0 : _b.id;
                const value = (_c = newState === null || newState === void 0 ? void 0 : newState.selectedPropField) === null || _c === void 0 ? void 0 : _c.value;
                const parentType = (_d = newState === null || newState === void 0 ? void 0 : newState.selectedPropField) === null || _d === void 0 ? void 0 : _d.parentType;
                if (parentType === 'dialog') {
                    lastSelectedPropFieldId = focusInputField(`${filePath}::dialog`, id, value, (_e = newState === null || newState === void 0 ? void 0 : newState.user) === null || _e === void 0 ? void 0 : _e.color, lastSelectedPropFieldId);
                }
            }
            else {
                if (lastSelectedPropFieldId) {
                    removeStyleFromProperty(`${filePath}::dialog`, lastSelectedPropFieldId, ['border-color', 'box-shadow']);
                    lastSelectedPropFieldId = undefined;
                }
            }
        };
        jcadModel === null || jcadModel === void 0 ? void 0 : jcadModel.clientStateChanged.connect(onClientSharedStateChanged);
        super({ title: options.title, body, buttons: [Dialog.cancelButton()] });
        this.addClass('jpcad-property-FormDialog');
    }
}
