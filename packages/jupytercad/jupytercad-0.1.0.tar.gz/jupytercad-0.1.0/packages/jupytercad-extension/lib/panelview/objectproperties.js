import { ReactWidget } from '@jupyterlab/apputils';
import { PanelWithToolbar } from '@jupyterlab/ui-components';
import { v4 as uuid } from 'uuid';
import * as React from 'react';
import { focusInputField, itemFromName, removeStyleFromProperty } from '../tools';
import { ObjectPropertiesForm } from './formbuilder';
import formSchema from '../_interface/forms.json';
export class ObjectProperties extends PanelWithToolbar {
    constructor(params) {
        super(params);
        this.title.label = 'Objects Properties';
        const body = ReactWidget.create(React.createElement(ObjectPropertiesReact, { cpModel: params.controlPanelModel }));
        this.addWidget(body);
        this.addClass('jpcad-sidebar-propertiespanel');
    }
}
class ObjectPropertiesReact extends React.Component {
    constructor(props) {
        var _a, _b;
        super(props);
        this.syncSelectedField = (id, value, parentType) => {
            var _a;
            let property = null;
            if (id) {
                const prefix = id.split('_')[0];
                property = id.substring(prefix.length);
            }
            (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.syncSelectedPropField({
                parentType,
                id: property,
                value
            });
        };
        this._sharedJcadModelChanged = (_, changed) => {
            this.setState(old => {
                var _a, _b;
                if (old.selectedObject) {
                    const jcadObject = (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.getAllObject();
                    if (jcadObject) {
                        const selectedObj = itemFromName(old.selectedObject, jcadObject);
                        if (!selectedObj) {
                            return old;
                        }
                        const selectedObjectData = selectedObj['parameters'];
                        return Object.assign(Object.assign({}, old), { jcadObject: jcadObject, selectedObjectData });
                    }
                    else {
                        return old;
                    }
                }
                else {
                    return Object.assign(Object.assign({}, old), { jcadObject: (_b = this.props.cpModel.jcadModel) === null || _b === void 0 ? void 0 : _b.getAllObject() });
                }
            });
        };
        this._onClientSharedStateChanged = (sender, clients) => {
            var _a, _b, _c, _d, _e, _f, _g, _h, _j;
            const remoteUser = (_b = (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.localState) === null || _b === void 0 ? void 0 : _b.remoteUser;
            const clientId = this.state.clientId;
            let newState;
            if (remoteUser) {
                newState = clients.get(remoteUser);
                const id = (_c = newState === null || newState === void 0 ? void 0 : newState.selectedPropField) === null || _c === void 0 ? void 0 : _c.id;
                const value = (_d = newState === null || newState === void 0 ? void 0 : newState.selectedPropField) === null || _d === void 0 ? void 0 : _d.value;
                const parentType = (_e = newState === null || newState === void 0 ? void 0 : newState.selectedPropField) === null || _e === void 0 ? void 0 : _e.parentType;
                if (parentType === 'panel') {
                    this._lastSelectedPropFieldId = focusInputField(`${this.state.filePath}::panel`, id, value, (_f = newState === null || newState === void 0 ? void 0 : newState.user) === null || _f === void 0 ? void 0 : _f.color, this._lastSelectedPropFieldId);
                }
            }
            else {
                const localState = clientId ? clients.get(clientId) : null;
                if (this._lastSelectedPropFieldId) {
                    removeStyleFromProperty(`${this.state.filePath}::panel`, this._lastSelectedPropFieldId, ['border-color', 'box-shadow']);
                    this._lastSelectedPropFieldId = undefined;
                }
                if (localState &&
                    ((_g = localState.selected) === null || _g === void 0 ? void 0 : _g.emitter) &&
                    localState.selected.emitter !== this.state.id &&
                    ((_h = localState.selected) === null || _h === void 0 ? void 0 : _h.value)) {
                    newState = localState;
                }
            }
            if (newState) {
                const selected = '' + newState.selected.value;
                if (selected !== this.state.selectedObject) {
                    if (selected.length === 0) {
                        this.setState(old => (Object.assign(Object.assign({}, old), { schema: undefined, selectedObjectData: undefined })));
                        return;
                    }
                    const objectData = (_j = this.props.cpModel.jcadModel) === null || _j === void 0 ? void 0 : _j.getAllObject();
                    if (objectData) {
                        let schema;
                        const selectedObj = itemFromName(selected, objectData);
                        if (!selectedObj) {
                            return;
                        }
                        if (selectedObj.shape) {
                            schema = formSchema[selectedObj.shape];
                        }
                        const selectedObjectData = selectedObj['parameters'];
                        this.setState(old => (Object.assign(Object.assign({}, old), { selectedObjectData, selectedObject: selected, schema })));
                    }
                }
            }
        };
        this.state = {
            filePath: this.props.cpModel.filePath,
            jcadObject: (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.getAllObject(),
            clientId: null,
            id: uuid()
        };
        (_b = this.props.cpModel.jcadModel) === null || _b === void 0 ? void 0 : _b.sharedObjectsChanged.connect(this._sharedJcadModelChanged);
        this.props.cpModel.documentChanged.connect((_, changed) => {
            if (changed) {
                this.props.cpModel.disconnect(this._sharedJcadModelChanged);
                this.props.cpModel.disconnect(this._onClientSharedStateChanged);
                changed.context.model.sharedObjectsChanged.connect(this._sharedJcadModelChanged);
                changed.context.model.clientStateChanged.connect(this._onClientSharedStateChanged);
                this.setState(old => {
                    var _a;
                    return (Object.assign(Object.assign({}, old), { filePath: changed.context.localPath, jcadObject: (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.getAllObject(), clientId: changed.context.model.getClientId() }));
                });
            }
            else {
                this.setState({
                    jcadOption: undefined,
                    filePath: undefined,
                    jcadObject: undefined,
                    selectedObjectData: undefined,
                    selectedObject: undefined,
                    schema: undefined
                });
            }
        });
    }
    syncObjectProperties(objectName, properties) {
        var _a;
        if (!this.state.jcadObject || !objectName) {
            return;
        }
        const model = (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.sharedModel;
        const obj = model === null || model === void 0 ? void 0 : model.getObjectByName(objectName);
        if (model && obj) {
            model.updateObjectByName(objectName, 'parameters', Object.assign(Object.assign({}, obj['parameters']), properties));
        }
    }
    render() {
        return this.state.schema && this.state.selectedObjectData ? (React.createElement(ObjectPropertiesForm, { parentType: "panel", filePath: `${this.state.filePath}::panel`, schema: this.state.schema, sourceData: this.state.selectedObjectData, syncData: (properties) => {
                this.syncObjectProperties(this.state.selectedObject, properties);
            }, syncSelectedField: this.syncSelectedField })) : (React.createElement("div", null));
    }
}
