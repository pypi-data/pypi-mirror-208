import * as decoding from 'lib0/decoding';
import * as encoding from 'lib0/encoding';
import * as syncProtocol from 'y-protocols/sync';
export var YMessageType;
(function (YMessageType) {
    YMessageType[YMessageType["SYNC"] = 0] = "SYNC";
    YMessageType[YMessageType["AWARENESS"] = 1] = "AWARENESS";
})(YMessageType || (YMessageType = {}));
export class YCommProvider {
    constructor(options) {
        this._onMsg = (msg) => {
            if (msg.buffers) {
                const buffer = msg.buffers[0];
                const encoder = Private.readMessage(this, new Uint8Array(buffer), true);
                if (encoding.length(encoder) > 1) {
                    this._sendOverComm(encoding.toUint8Array(encoder));
                }
            }
        };
        this._updateHandler = (update, origin) => {
            const encoder = encoding.createEncoder();
            encoding.writeVarUint(encoder, YMessageType.SYNC);
            syncProtocol.writeUpdate(encoder, update);
            this._sendOverComm(encoding.toUint8Array(encoder));
        };
        this._isDisposed = false;
        this._comm = options.comm;
        this._ydoc = options.ydoc;
        this._ydoc.on('update', this._updateHandler);
        this._connect();
    }
    get doc() {
        return this._ydoc;
    }
    get synced() {
        return this._synced;
    }
    set synced(state) {
        if (this._synced !== state) {
            this._synced = state;
        }
    }
    get isDisposed() {
        return this._isDisposed;
    }
    dispose() {
        if (this._isDisposed) {
            return;
        }
        this._comm.close();
        this._isDisposed = true;
    }
    _connect() {
        this._sync();
        this._comm.onMsg = this._onMsg;
    }
    _sync() {
        const encoder = encoding.createEncoder();
        encoding.writeVarUint(encoder, YMessageType.SYNC);
        syncProtocol.writeSyncStep1(encoder, this._ydoc);
        this._sendOverComm(encoding.toUint8Array(encoder));
    }
    _sendOverComm(bufferArray) {
        this._comm.send({}, undefined, [bufferArray.buffer]);
    }
}
var Private;
(function (Private) {
    function syncMessageHandler(encoder, decoder, provider, emitSynced) {
        encoding.writeVarUint(encoder, YMessageType.SYNC);
        const syncMessageType = syncProtocol.readSyncMessage(decoder, encoder, provider.doc, provider);
        if (emitSynced &&
            syncMessageType === syncProtocol.messageYjsSyncStep2 &&
            !provider.synced) {
            syncProtocol.writeSyncStep2(encoder, provider.doc);
            provider.synced = true;
        }
    }
    Private.syncMessageHandler = syncMessageHandler;
    function readMessage(provider, buf, emitSynced) {
        const decoder = decoding.createDecoder(buf);
        const encoder = encoding.createEncoder();
        const messageType = decoding.readVarUint(decoder);
        if (messageType === YMessageType.SYNC) {
            syncMessageHandler(encoder, decoder, provider, emitSynced);
        }
        else {
            console.error('Unable to compute message');
        }
        return encoder;
    }
    Private.readMessage = readMessage;
})(Private || (Private = {}));
