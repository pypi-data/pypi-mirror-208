import { SidePanel } from '@jupyterlab/ui-components';
import { JupyterCadDoc } from '../model';
import { IControlPanelModel, IAnnotationModel } from '../types';
import { IJupyterCadTracker } from '../token';
export declare class LeftPanelWidget extends SidePanel {
    constructor(options: LeftPanelWidget.IOptions);
    dispose(): void;
    private _model;
    private _annotationModel;
}
export declare namespace LeftPanelWidget {
    interface IOptions {
        model: IControlPanelModel;
        annotationModel: IAnnotationModel;
        tracker: IJupyterCadTracker;
    }
    interface IProps {
        filePath?: string;
        sharedModel?: JupyterCadDoc;
    }
}
