import { YDocument } from '@jupyter/ydoc';
import { JSONExt } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';
import Ajv from 'ajv';
import * as Y from 'yjs';
import jcadSchema from './schema/jcad.json';
export class JupyterCadModel {
    constructor(options) {
        this.collaborative = true;
        this._onClientStateChanged = changed => {
            const clients = this.sharedModel.awareness.getStates();
            this._clientStateChanged.emit(clients);
            this._sharedModel.awareness.on('change', update => {
                if (update.added.length || update.removed.length) {
                    this._userChanged.emit(this.users);
                }
            });
        };
        this.defaultKernelName = '';
        this.defaultKernelLanguage = '';
        this._dirty = false;
        this._readOnly = false;
        this._isDisposed = false;
        this._userChanged = new Signal(this);
        this._disposed = new Signal(this);
        this._contentChanged = new Signal(this);
        this._stateChanged = new Signal(this);
        this._themeChanged = new Signal(this);
        this._clientStateChanged = new Signal(this);
        const { annotationModel, sharedModel } = options;
        if (sharedModel) {
            this._sharedModel = sharedModel;
        }
        else {
            this._sharedModel = JupyterCadDoc.create();
        }
        this.sharedModel.awareness.on('change', this._onClientStateChanged);
        this.annotationModel = annotationModel;
    }
    get sharedModel() {
        return this._sharedModel;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    get contentChanged() {
        return this._contentChanged;
    }
    get stateChanged() {
        return this._stateChanged;
    }
    get themeChanged() {
        return this._themeChanged;
    }
    get currentUserId() {
        var _a;
        return (_a = this.sharedModel) === null || _a === void 0 ? void 0 : _a.awareness.clientID;
    }
    get users() {
        var _a;
        this._usersMap = (_a = this._sharedModel) === null || _a === void 0 ? void 0 : _a.awareness.getStates();
        const users = [];
        if (this._usersMap) {
            this._usersMap.forEach((val, key) => {
                users.push({ userId: key, userData: val.user });
            });
        }
        return users;
    }
    get userChanged() {
        return this._userChanged;
    }
    get dirty() {
        return this._dirty;
    }
    set dirty(value) {
        this._dirty = value;
    }
    get readOnly() {
        return this._readOnly;
    }
    set readOnly(value) {
        this._readOnly = value;
    }
    get localState() {
        return this.sharedModel.awareness.getLocalState();
    }
    get clientStateChanged() {
        return this._clientStateChanged;
    }
    get sharedMetadataChanged() {
        return this.sharedModel.metadataChanged;
    }
    get sharedOptionsChanged() {
        return this.sharedModel.optionsChanged;
    }
    get sharedObjectsChanged() {
        return this.sharedModel.objectsChanged;
    }
    get disposed() {
        return this._disposed;
    }
    dispose() {
        if (this._isDisposed) {
            return;
        }
        this._isDisposed = true;
        this._sharedModel.dispose();
        this._disposed.emit();
        Signal.clearData(this);
    }
    toString() {
        return JSON.stringify(this.getContent(), null, 2);
    }
    fromString(data) {
        const jsonData = JSON.parse(data);
        const ajv = new Ajv();
        const validate = ajv.compile(jcadSchema);
        const valid = validate(jsonData);
        if (!valid) {
            throw Error('File format error');
        }
        this.sharedModel.transact(() => {
            var _a;
            this.sharedModel.addObjects(jsonData.objects);
            this.sharedModel.setOptions((_a = jsonData.options) !== null && _a !== void 0 ? _a : {});
        });
    }
    toJSON() {
        return JSON.parse(this.toString());
    }
    fromJSON(data) {
        // nothing to do
    }
    initialize() {
        //
    }
    getWorker() {
        if (!JupyterCadModel.worker) {
            JupyterCadModel.worker = new Worker(new URL('./worker', import.meta.url));
        }
        return JupyterCadModel.worker;
    }
    getContent() {
        return {
            objects: this.sharedModel.objects,
            options: this.sharedModel.options
        };
    }
    getAllObject() {
        return this.sharedModel.objects;
    }
    syncPointer(pointer, emitter) {
        this.sharedModel.awareness.setLocalStateField('pointer', {
            value: pointer,
            emitter: emitter
        });
    }
    syncCamera(camera, emitter) {
        this.sharedModel.awareness.setLocalStateField('camera', {
            value: camera,
            emitter: emitter
        });
    }
    syncSelectedObject(name, emitter) {
        this.sharedModel.awareness.setLocalStateField('selected', {
            value: name,
            emitter: emitter
        });
    }
    syncSelectedPropField(data) {
        this.sharedModel.awareness.setLocalStateField('selectedPropField', data);
    }
    setUserToFollow(userId) {
        if (this._sharedModel) {
            this._sharedModel.awareness.setLocalStateField('remoteUser', userId);
        }
    }
    syncFormData(form) {
        if (this._sharedModel) {
            this._sharedModel.awareness.setLocalStateField('toolbarForm', form);
        }
    }
    getClientId() {
        return this.sharedModel.awareness.clientID;
    }
    addMetadata(key, value) {
        this.sharedModel.setMetadata(key, value);
    }
    removeMetadata(key) {
        this.sharedModel.removeMetadata(key);
    }
}
export class JupyterCadDoc extends YDocument {
    constructor() {
        super();
        this._objectsObserver = (events) => {
            const changes = [];
            events.forEach(event => {
                const name = event.target.get('name');
                if (name) {
                    event.keys.forEach((change, key) => {
                        changes.push({
                            name,
                            key,
                            newValue: JSONExt.deepCopy(event.target.toJSON())
                        });
                    });
                }
            });
            this._changed.emit({ objectChange: changes });
            this._objectsChanged.emit({ objectChange: changes });
        };
        this._metaObserver = (event) => {
            this._metadataChanged.emit(event.keys);
        };
        this._optionsObserver = (event) => {
            this._optionsChanged.emit(event.keys);
        };
        this._metadataChanged = new Signal(this);
        this._optionsChanged = new Signal(this);
        this._objectsChanged = new Signal(this);
        this._options = this.ydoc.getMap('options');
        this._objects = this.ydoc.getArray('objects');
        this._metadata = this.ydoc.getMap('metadata');
        this.undoManager.addToScope(this._objects);
        this._objects.observeDeep(this._objectsObserver);
        this._metadata.observe(this._metaObserver);
        this._options.observe(this._optionsObserver);
    }
    dispose() {
        this._objects.unobserveDeep(this._objectsObserver);
        this._metadata.unobserve(this._metaObserver);
        this._options.unobserve(this._optionsObserver);
        super.dispose();
    }
    get version() {
        return '0.1.0';
    }
    get objects() {
        return this._objects.map(obj => JSONExt.deepCopy(obj.toJSON()));
    }
    get options() {
        return JSONExt.deepCopy(this._options.toJSON());
    }
    get metadata() {
        return JSONExt.deepCopy(this._metadata.toJSON());
    }
    get objectsChanged() {
        return this._objectsChanged;
    }
    get optionsChanged() {
        return this._optionsChanged;
    }
    get metadataChanged() {
        return this._metadataChanged;
    }
    objectExists(name) {
        return Boolean(this._getObjectAsYMapByName(name));
    }
    getObjectByName(name) {
        const obj = this._getObjectAsYMapByName(name);
        if (obj) {
            return JSONExt.deepCopy(obj.toJSON());
        }
        return undefined;
    }
    removeObjectByName(name) {
        let index = 0;
        for (const obj of this._objects) {
            if (obj.get('name') === name) {
                break;
            }
            index++;
        }
        if (this._objects.length > index) {
            this.transact(() => {
                this._objects.delete(index);
            });
        }
    }
    addObject(value) {
        this.addObjects([value]);
    }
    addObjects(value) {
        this.transact(() => {
            value.map(obj => {
                if (!this.objectExists(obj.name)) {
                    this._objects.push([new Y.Map(Object.entries(obj))]);
                }
                else {
                    console.error('There is already an object with the name:', obj.name);
                }
            });
        });
    }
    updateObjectByName(name, key, value) {
        const obj = this._getObjectAsYMapByName(name);
        if (!obj) {
            return;
        }
        this.transact(() => obj.set(key, value));
    }
    getOption(key) {
        const content = this._options.get(key);
        if (!content) {
            return;
        }
        return JSONExt.deepCopy(content);
    }
    setOption(key, value) {
        this._options.set(key, value);
    }
    setOptions(options) {
        for (const [key, value] of Object.entries(options)) {
            this._options.set(key, value);
        }
    }
    getMetadata(key) {
        return this._metadata.get(key);
    }
    setMetadata(key, value) {
        this._metadata.set(key, value);
    }
    removeMetadata(key) {
        if (this._metadata.has(key)) {
            this._metadata.delete(key);
        }
    }
    static create() {
        return new JupyterCadDoc();
    }
    _getObjectAsYMapByName(name) {
        for (const obj of this._objects) {
            if (obj.get('name') === name) {
                return obj;
            }
        }
        return undefined;
    }
}
