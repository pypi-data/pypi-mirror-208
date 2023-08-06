import { INotebookTracker } from '@jupyterlab/notebook';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { ITranslator } from '@jupyterlab/translation';
import { NotebookRendererModel } from './model';
import { IJupyterCadWidgetManager } from './token';
import { NotebookRenderer } from './view';
import { JupyterCadWidgetManager } from './widgetManager';
const MIME_TYPE = 'application/FCStd';
export const notebookRendererPlugin = {
    id: 'jupytercad:notebookRenderer',
    autoStart: true,
    requires: [IRenderMimeRegistry, INotebookTracker, IJupyterCadWidgetManager],
    activate: (app, rendermime, nbTracker, wmManager) => {
        const rendererFactory = {
            safe: true,
            mimeTypes: [MIME_TYPE],
            createRenderer: options => {
                var _a, _b, _c;
                const kernelId = (_c = (_b = (_a = nbTracker.currentWidget) === null || _a === void 0 ? void 0 : _a.sessionContext.session) === null || _b === void 0 ? void 0 : _b.kernel) === null || _c === void 0 ? void 0 : _c.id;
                const mimeType = options.mimeType;
                const modelFactory = new NotebookRendererModel({
                    kernelId,
                    widgetManager: wmManager
                });
                return new NotebookRenderer({ mimeType, factory: modelFactory });
            }
        };
        rendermime.addFactory(rendererFactory, -100);
    }
};
export const ypyWidgetManager = {
    id: 'jupytercad:serverInfoPlugin',
    autoStart: true,
    requires: [INotebookTracker, ITranslator],
    provides: IJupyterCadWidgetManager,
    activate: (app, tracker, translator) => {
        const registry = new JupyterCadWidgetManager({
            manager: app.serviceManager,
            translator
        });
        const onKernelChanged = (_, changedArgs) => {
            const { newValue, oldValue } = changedArgs;
            if (newValue) {
                registry.unregisterKernel(oldValue === null || oldValue === void 0 ? void 0 : oldValue.id);
                registry.registerKernel(newValue);
                newValue.disposed.connect(() => {
                    registry.unregisterKernel(newValue.id);
                });
            }
        };
        tracker.widgetAdded.connect(async (_, notebook) => {
            notebook.sessionContext.kernelChanged.connect(onKernelChanged);
            notebook.disposed.connect(() => {
                notebook.sessionContext.kernelChanged.disconnect(onKernelChanged);
            });
        });
        return registry;
    }
};
