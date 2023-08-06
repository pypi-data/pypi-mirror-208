import { Signal } from '@lumino/signaling';
export class AnnotationModel {
    constructor(options) {
        this._contextChanged = new Signal(this);
        this._updateSignal = new Signal(this);
        this.context = options.context;
    }
    get updateSignal() {
        return this._updateSignal;
    }
    get user() {
        return this._user;
    }
    set context(context) {
        var _a;
        this._context = context;
        const state = (_a = this._context) === null || _a === void 0 ? void 0 : _a.model.sharedModel.awareness.getLocalState();
        this._user = state === null || state === void 0 ? void 0 : state.user;
        this._contextChanged.emit(void 0);
    }
    get context() {
        return this._context;
    }
    get contextChanged() {
        return this._contextChanged;
    }
    update() {
        this._updateSignal.emit(null);
    }
    getAnnotation(id) {
        var _a;
        const rawData = (_a = this._context) === null || _a === void 0 ? void 0 : _a.model.sharedModel.getMetadata(id);
        if (rawData) {
            return JSON.parse(rawData);
        }
    }
    getAnnotationIds() {
        var _a;
        const annotationIds = [];
        for (const id in (_a = this._context) === null || _a === void 0 ? void 0 : _a.model.sharedModel.metadata) {
            if (id.startsWith('annotation')) {
                annotationIds.push(id);
            }
        }
        return annotationIds;
    }
    addAnnotation(key, value) {
        var _a;
        (_a = this._context) === null || _a === void 0 ? void 0 : _a.model.sharedModel.setMetadata(`annotation_${key}`, JSON.stringify(value));
    }
    removeAnnotation(key) {
        var _a;
        (_a = this._context) === null || _a === void 0 ? void 0 : _a.model.removeMetadata(key);
    }
    addContent(id, value) {
        var _a;
        const newContent = {
            value,
            user: this._user
        };
        const currentAnnotation = this.getAnnotation(id);
        if (currentAnnotation) {
            const newAnnotation = Object.assign(Object.assign({}, currentAnnotation), { contents: [...currentAnnotation.contents, newContent] });
            (_a = this._context) === null || _a === void 0 ? void 0 : _a.model.sharedModel.setMetadata(id, JSON.stringify(newAnnotation));
        }
    }
}
