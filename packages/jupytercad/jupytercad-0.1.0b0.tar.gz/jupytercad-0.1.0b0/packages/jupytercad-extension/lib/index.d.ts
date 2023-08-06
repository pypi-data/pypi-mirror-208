import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IJupyterCadTracker } from './token';
import { IAnnotationModel } from './types';
declare const _default: (JupyterFrontEndPlugin<void> | JupyterFrontEndPlugin<import("./notebookrenderer/token").IJupyterCadWidgetManager> | JupyterFrontEndPlugin<IJupyterCadTracker> | JupyterFrontEndPlugin<IAnnotationModel>)[];
export default _default;
