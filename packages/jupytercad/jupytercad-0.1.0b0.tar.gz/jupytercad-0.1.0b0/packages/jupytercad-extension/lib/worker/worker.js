import initOpenCascade from '@jupytercad/jupytercad-opencascade';
import { WorkerAction, MainAction } from '../types';
import WorkerHandler from './actions';
let occ;
const ports = {};
console.log('Initializing OCC...');
initOpenCascade().then(occInstance => {
    console.log('Done!');
    occ = occInstance;
    self.occ = occ;
    for (const id of Object.keys(ports)) {
        sendToMain({ action: MainAction.INITIALIZED, payload: false }, id);
    }
});
const registerWorker = async (id, port) => {
    ports[id] = port;
    if (occ) {
        sendToMain({ action: MainAction.INITIALIZED, payload: false }, id);
    }
};
const sendToMain = (msg, id) => {
    if (id in ports) {
        ports[id].postMessage(msg);
    }
};
self.onmessage = async (event) => {
    const message = event.data;
    const { id } = message;
    switch (message.action) {
        case WorkerAction.REGISTER: {
            const port = event.ports[0];
            await registerWorker(id, port);
            break;
        }
        case WorkerAction.LOAD_FILE: {
            const result = WorkerHandler[message.action](message.payload);
            sendToMain({
                action: MainAction.DISPLAY_SHAPE,
                payload: result
            }, id);
            break;
        }
    }
};
