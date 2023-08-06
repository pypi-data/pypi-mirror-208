import { MessageLoop } from '@lumino/messaging';
import { Panel, Widget } from '@lumino/widgets';
import { JupyterCadPanel } from '../widget';
export const CLASS_NAME = 'mimerenderer-jupytercad';
export class NotebookRenderer extends Panel {
    /**
     * Construct a new output widget.
     */
    constructor(options) {
        super();
        this.onResize = () => {
            if (this._jcadWidget) {
                MessageLoop.sendMessage(this._jcadWidget, Widget.ResizeMessage.UnknownSize);
            }
        };
        this._modelFactory = options.factory;
        this._mimeType = options.mimeType;
        this.addClass(CLASS_NAME);
    }
    dispose() {
        var _a;
        if (this.isDisposed) {
            return;
        }
        (_a = this._jcadModel) === null || _a === void 0 ? void 0 : _a.dispose();
        super.dispose();
    }
    async renderModel(mimeModel) {
        const { commId } = JSON.parse(mimeModel.data[this._mimeType]);
        this._jcadModel = await this._modelFactory.createJcadModel(commId);
        if (!this._jcadModel) {
            return;
        }
        this._jcadWidget = new JupyterCadPanel({ model: this._jcadModel });
        this.addWidget(this._jcadWidget);
    }
}
