import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { JupyterCadModel } from '../model';
import { WebSocketProvider } from '@jupyter/docprovider';
import { YCommProvider } from './yCommProvider';
const Y_DOCUMENT_PROVIDER_URL = 'api/yjs';
export class JupyterCadWidgetManager {
    constructor(options) {
        this._registry = new Map();
        this._manager = options.manager;
        this._trans = options.translator;
    }
    registerKernel(kernel) {
        const wm = new WidgetModelRegistry({
            kernel,
            manager: this._manager,
            translator: this._trans
        });
        this._registry.set(kernel.id, wm);
    }
    unregisterKernel(kernelId) {
        if (kernelId) {
            this._registry.delete(kernelId);
        }
    }
    getWidgetModel(kernelId, commId) {
        var _a;
        return (_a = this._registry.get(kernelId)) === null || _a === void 0 ? void 0 : _a.getModel(commId);
    }
}
export class WidgetModelRegistry {
    constructor(options) {
        /**
         * Handle when a comm is opened.
         */
        this._handle_comm_open = async (comm, msg) => {
            const { path, format, contentType } = msg.content.data;
            const jcadModel = new JupyterCadModel({});
            const user = this._manager.user;
            if (path && format && contentType) {
                const server = ServerConnection.makeSettings();
                const serverUrl = URLExt.join(server.wsUrl, Y_DOCUMENT_PROVIDER_URL);
                const ywsProvider = new WebSocketProvider({
                    url: serverUrl,
                    path,
                    format,
                    contentType,
                    model: jcadModel.sharedModel,
                    user,
                    translator: this._trans.load('jupyterlab')
                });
                jcadModel.disposed.connect(() => {
                    ywsProvider.dispose();
                });
                await ywsProvider.ready;
            }
            else {
                const awareness = jcadModel.sharedModel.awareness;
                const _onUserChanged = (user) => {
                    awareness.setLocalStateField('user', user.identity);
                };
                user.ready
                    .then(() => {
                    _onUserChanged(user);
                })
                    .catch(e => console.error(e));
                user.userChanged.connect(_onUserChanged, this);
            }
            new YCommProvider({
                comm,
                ydoc: jcadModel.sharedModel.ydoc
            });
            this._jcadModels.set(comm.commId, jcadModel);
        };
        this._jcadModels = new Map();
        const { kernel, manager, translator } = options;
        this._manager = manager;
        this._trans = translator;
        kernel.registerCommTarget('@jupytercad:widget', this._handle_comm_open);
    }
    getModel(id) {
        return this._jcadModels.get(id);
    }
}
