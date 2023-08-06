import { Panel } from '@lumino/widgets';
import { NotebookRendererModel } from './model';
import { IRenderMime } from '@jupyterlab/rendermime';
export declare const CLASS_NAME = "mimerenderer-jupytercad";
export declare class NotebookRenderer extends Panel implements IRenderMime.IRenderer {
    /**
     * Construct a new output widget.
     */
    constructor(options: {
        factory: NotebookRendererModel;
        mimeType: string;
    });
    dispose(): void;
    renderModel(mimeModel: IRenderMime.IMimeModel): Promise<void>;
    onResize: () => void;
    private _jcadWidget;
    private _modelFactory;
    private _mimeType;
    private _jcadModel?;
}
