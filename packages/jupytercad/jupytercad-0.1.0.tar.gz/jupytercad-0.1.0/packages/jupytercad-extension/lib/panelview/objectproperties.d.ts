import { PanelWithToolbar } from '@jupyterlab/ui-components';
import { Panel } from '@lumino/widgets';
import { IControlPanelModel } from '../types';
export declare class ObjectProperties extends PanelWithToolbar {
    constructor(params: ObjectProperties.IOptions);
}
export declare namespace ObjectProperties {
    /**
     * Instantiation options for `ObjectProperties`.
     */
    interface IOptions extends Panel.IOptions {
        controlPanelModel: IControlPanelModel;
    }
}
