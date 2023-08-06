import { SidePanel } from '@jupyterlab/ui-components';
import { JupyterCadDoc } from '../model';
import { IControlPanelModel } from '../types';
export declare class RightPanelWidget extends SidePanel {
    constructor(options: RightPanelWidget.IOptions);
    dispose(): void;
    private _model;
}
export declare namespace RightPanelWidget {
    interface IOptions {
        model: IControlPanelModel;
    }
    interface IProps {
        filePath?: string;
        sharedModel?: JupyterCadDoc;
    }
}
