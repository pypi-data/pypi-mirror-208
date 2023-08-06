import { SchemaForm } from '@deathbeds/jupyterlab-rjsf';
import { MessageLoop } from '@lumino/messaging';
import { Widget } from '@lumino/widgets';
import * as React from 'react';
// Reusing the datalayer/jupyter-react component:
// https://github.com/datalayer/jupyter-react/blob/main/packages/react/src/jupyter/lumino/Lumino.tsx
export const LuminoSchemaForm = (props) => {
    const ref = React.useRef(null);
    const { children } = props;
    React.useEffect(() => {
        const widget = children;
        try {
            MessageLoop.sendMessage(widget, Widget.Msg.BeforeAttach);
            ref.current.insertBefore(widget.node, null);
            MessageLoop.sendMessage(widget, Widget.Msg.AfterAttach);
        }
        catch (e) {
            console.warn('Exception while attaching Lumino widget.', e);
        }
        return () => {
            try {
                if (widget.isAttached || widget.node.isConnected) {
                    Widget.detach(widget);
                }
            }
            catch (e) {
                console.warn('Exception while detaching Lumino widget.', e);
            }
        };
    }, [children]);
    return React.createElement("div", { ref: ref });
};
export class ObjectPropertiesForm extends React.Component {
    constructor(props) {
        super(props);
        this.setStateByKey = (key, value) => {
            const floatValue = parseFloat(value);
            if (Number.isNaN(floatValue)) {
                return;
            }
            this.setState(old => (Object.assign(Object.assign({}, old), { internalData: Object.assign(Object.assign({}, old.internalData), { [key]: floatValue }) })), () => this.props.syncData({ [key]: floatValue }));
        };
        this.onFormSubmit = (e) => {
            const internalData = Object.assign({}, this.state.internalData);
            Object.entries(e.formData).forEach(([k, v]) => (internalData[k] = v));
            this.setState(old => (Object.assign(Object.assign({}, old), { internalData })), () => {
                this.props.syncData(e.formData);
                this.props.cancel && this.props.cancel();
            });
        };
        this.state = {
            internalData: Object.assign({}, this.props.sourceData),
            schema: props.schema
        };
    }
    componentDidUpdate(prevProps, prevState) {
        if (prevProps.sourceData !== this.props.sourceData) {
            this.setState(old => (Object.assign(Object.assign({}, old), { internalData: this.props.sourceData })));
        }
    }
    buildForm() {
        if (!this.props.sourceData || !this.state.internalData) {
            return [];
        }
        const inputs = [];
        for (const [key, value] of Object.entries(this.props.sourceData)) {
            let input;
            if (typeof value === 'string' || typeof value === 'number') {
                input = (React.createElement("div", { key: key },
                    React.createElement("label", { htmlFor: "" }, key),
                    React.createElement("input", { type: "number", value: this.state.internalData[key], onChange: e => this.setStateByKey(key, e.target.value) })));
                inputs.push(input);
            }
        }
        return inputs;
    }
    removeArrayButton(schema, uiSchema) {
        Object.entries(schema['properties']).forEach(([k, v]) => {
            if (v['type'] === 'array') {
                uiSchema[k] = {
                    'ui:options': {
                        orderable: false,
                        removable: false,
                        addable: false
                    }
                };
            }
            else if (v['type'] === 'object') {
                uiSchema[k] = {};
                this.removeArrayButton(v, uiSchema[k]);
            }
        });
    }
    generateUiSchema(schema) {
        const uiSchema = {
            additionalProperties: {
                'ui:label': false,
                classNames: 'jpcad-hidden-field'
            }
        };
        this.removeArrayButton(schema, uiSchema);
        return uiSchema;
    }
    render() {
        var _a;
        if (this.props.schema) {
            const schema = Object.assign(Object.assign({}, this.props.schema), { additionalProperties: true });
            const submitRef = React.createRef();
            const formSchema = new SchemaForm(schema !== null && schema !== void 0 ? schema : {}, {
                liveValidate: true,
                formData: this.state.internalData,
                onSubmit: this.onFormSubmit,
                onFocus: (id, value) => {
                    this.props.syncSelectedField
                        ? this.props.syncSelectedField(id, value, this.props.parentType)
                        : null;
                },
                onBlur: (id, value) => {
                    this.props.syncSelectedField
                        ? this.props.syncSelectedField(null, value, this.props.parentType)
                        : null;
                },
                uiSchema: this.generateUiSchema(this.props.schema),
                children: (React.createElement("button", { ref: submitRef, type: "submit", style: { display: 'none' } }))
            });
            return (React.createElement("div", { className: "jpcad-property-panel", "data-path": (_a = this.props.filePath) !== null && _a !== void 0 ? _a : '' },
                React.createElement("div", { className: "jpcad-property-outer" },
                    React.createElement(LuminoSchemaForm, null, formSchema)),
                React.createElement("div", { className: "jpcad-property-buttons" },
                    this.props.cancel ? (React.createElement("button", { className: "jp-Dialog-button jp-mod-reject jp-mod-styled", onClick: this.props.cancel },
                        React.createElement("div", { className: "jp-Dialog-buttonLabel" }, "Cancel"))) : null,
                    React.createElement("button", { className: "jp-Dialog-button jp-mod-accept jp-mod-styled", onClick: () => { var _a; return (_a = submitRef.current) === null || _a === void 0 ? void 0 : _a.click(); } },
                        React.createElement("div", { className: "jp-Dialog-buttonLabel" }, "Submit")))));
        }
        else {
            return React.createElement("div", null, this.buildForm());
        }
    }
}
