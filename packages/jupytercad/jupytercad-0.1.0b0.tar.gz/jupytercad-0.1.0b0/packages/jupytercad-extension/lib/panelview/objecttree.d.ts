import { PanelWithToolbar } from '@jupyterlab/ui-components';
import { Panel } from '@lumino/widgets';
import { IControlPanelModel } from '../types';
export declare class ObjectTree extends PanelWithToolbar {
    constructor(params: ObjectTree.IOptions);
}
export declare namespace ObjectTree {
    /**
     * Instantiation options for `ObjectTree`.
     */
    interface IOptions extends Panel.IOptions {
        controlPanelModel: IControlPanelModel;
    }
}
