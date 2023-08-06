export class ControlPanelModel {
    constructor(options) {
        this._tracker = options.tracker;
        this._documentChanged = this._tracker.currentChanged;
    }
    get documentChanged() {
        return this._documentChanged;
    }
    get filePath() {
        var _a;
        return (_a = this._tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.context.localPath;
    }
    get jcadModel() {
        var _a;
        return (_a = this._tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.context.model;
    }
    get sharedModel() {
        var _a;
        return (_a = this._tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.context.model.sharedModel;
    }
    disconnect(f) {
        this._tracker.forEach(w => {
            w.context.model.sharedObjectsChanged.disconnect(f);
            w.context.model.sharedOptionsChanged.disconnect(f);
            w.context.model.sharedMetadataChanged.disconnect(f);
        });
        this._tracker.forEach(w => w.context.model.themeChanged.disconnect(f));
        this._tracker.forEach(w => w.context.model.clientStateChanged.disconnect(f));
    }
}
