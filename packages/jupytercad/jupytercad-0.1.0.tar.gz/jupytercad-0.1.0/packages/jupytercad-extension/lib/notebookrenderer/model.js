export class NotebookRendererModel {
    constructor(options) {
        this._isDisposed = false;
        this._widgetManager = options.widgetManager;
        this._kernelId = options.kernelId;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    dispose() {
        if (this._isDisposed) {
            return;
        }
        this._isDisposed = true;
    }
    createJcadModel(commId) {
        if (this._kernelId) {
            return this._widgetManager.getWidgetModel(this._kernelId, commId);
        }
    }
}
