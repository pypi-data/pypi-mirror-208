import { SidePanel } from '@jupyterlab/ui-components';
import { ControlPanelHeader } from './header';
import { ObjectTree } from './objecttree';
import { Annotations } from './annotations';
export class LeftPanelWidget extends SidePanel {
    constructor(options) {
        super();
        this.addClass('jpcad-sidepanel-widget');
        this._model = options.model;
        this._annotationModel = options.annotationModel;
        const header = new ControlPanelHeader();
        this.header.addWidget(header);
        const tree = new ObjectTree({ controlPanelModel: this._model });
        this.addWidget(tree);
        const annotations = new Annotations({ model: this._annotationModel });
        this.addWidget(annotations);
        options.tracker.currentChanged.connect((_, changed) => {
            var _a;
            if (changed) {
                header.title.label = changed.context.localPath;
                this._annotationModel.context =
                    ((_a = options.tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.context) || undefined;
            }
            else {
                header.title.label = '-';
                this._annotationModel.context = undefined;
            }
        });
    }
    dispose() {
        super.dispose();
    }
}
