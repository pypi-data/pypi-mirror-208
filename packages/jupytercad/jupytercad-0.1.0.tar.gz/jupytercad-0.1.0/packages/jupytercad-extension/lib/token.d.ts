import { IWidgetTracker } from '@jupyterlab/apputils';
import { Token } from '@lumino/coreutils';
import { IJupyterCadWidget, IAnnotationModel } from './types';
export type IJupyterCadTracker = IWidgetTracker<IJupyterCadWidget>;
export declare const IJupyterCadDocTracker: Token<IJupyterCadTracker>;
export declare const IAnnotation: Token<IAnnotationModel>;
