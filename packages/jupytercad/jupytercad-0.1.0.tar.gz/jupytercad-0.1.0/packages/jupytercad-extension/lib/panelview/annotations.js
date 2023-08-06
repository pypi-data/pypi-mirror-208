import { PanelWithToolbar, ReactWidget } from '@jupyterlab/ui-components';
import * as React from 'react';
import { Annotation } from '../annotation/view';
export class ReactAnnotations extends React.Component {
    constructor(props) {
        super(props);
        const updateCallback = () => {
            this.forceUpdate();
        };
        this._model = props.model;
        this._model.contextChanged.connect(async () => {
            var _a, _b, _c, _d, _e, _f, _g, _h;
            await ((_b = (_a = this._model) === null || _a === void 0 ? void 0 : _a.context) === null || _b === void 0 ? void 0 : _b.ready);
            (_e = (_d = (_c = this._model) === null || _c === void 0 ? void 0 : _c.context) === null || _d === void 0 ? void 0 : _d.model) === null || _e === void 0 ? void 0 : _e.sharedMetadataChanged.disconnect(updateCallback);
            this._model = props.model;
            (_h = (_g = (_f = this._model) === null || _f === void 0 ? void 0 : _f.context) === null || _g === void 0 ? void 0 : _g.model) === null || _h === void 0 ? void 0 : _h.sharedMetadataChanged.connect(updateCallback);
            this.forceUpdate();
        });
    }
    render() {
        var _a;
        const annotationIds = (_a = this._model) === null || _a === void 0 ? void 0 : _a.getAnnotationIds();
        if (!annotationIds || !this._model) {
            return React.createElement("div", null);
        }
        const annotations = annotationIds.map((id) => {
            return (React.createElement("div", null,
                React.createElement(Annotation, { model: this._model, itemId: id }),
                React.createElement("hr", { className: "jpcad-Annotations-Separator" })));
        });
        return React.createElement("div", null, annotations);
    }
}
export class Annotations extends PanelWithToolbar {
    constructor(options) {
        super({});
        this.title.label = 'Annotations';
        this.addClass('jpcad-Annotations');
        this._model = options.model;
        this._widget = ReactWidget.create(React.createElement(ReactAnnotations, { model: this._model }));
        this.addWidget(this._widget);
    }
}
