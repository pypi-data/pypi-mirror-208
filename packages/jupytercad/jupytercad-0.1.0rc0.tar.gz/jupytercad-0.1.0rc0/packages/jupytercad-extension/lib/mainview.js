import { CommandRegistry } from '@lumino/commands';
import { ContextMenu } from '@lumino/widgets';
import * as Color from 'd3-color';
import * as React from 'react';
import * as THREE from 'three';
import { acceleratedRaycast, computeBoundsTree, disposeBoundsTree } from 'three-mesh-bvh';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { v4 as uuid } from 'uuid';
import { MainAction, WorkerAction } from './types';
import { FloatingAnnotation } from './annotation/view';
import { throttle } from './tools';
import { Vector2 } from 'three';
// Apply the BVH extension
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;
const DARK_BG_COLOR = 'linear-gradient(rgb(0, 0, 42), rgb(82, 87, 110))';
const LIGHT_BG_COLOR = 'radial-gradient(#efeded, #8f9091)';
const DEFAULT_MESH_COLOR = new THREE.Color('#434442');
const SELECTED_MESH_COLOR = new THREE.Color('#AB5118');
export class MainView extends React.Component {
    constructor(props) {
        super(props);
        this.addContextMenu = () => {
            const commands = new CommandRegistry();
            commands.addCommand('add-annotation', {
                execute: () => {
                    var _a;
                    if (!this._pointer3D) {
                        return;
                    }
                    const position = new THREE.Vector3().copy(this._pointer3D.mesh.position);
                    // If in exploded view, we scale down to the initial position (to before exploding the view)
                    if (this._explodedView.enabled) {
                        const explodedState = this._computeExplodedState(this._pointer3D.mesh);
                        position.add(explodedState.vector.multiplyScalar(-explodedState.distance));
                    }
                    (_a = this._model.annotationModel) === null || _a === void 0 ? void 0 : _a.addAnnotation(uuid(), {
                        position: [position.x, position.y, position.z],
                        label: 'New annotation',
                        contents: [],
                        parent: this._pointer3D.parent.name
                    });
                },
                label: 'Add annotation',
                isEnabled: () => {
                    return !!this._pointer3D;
                }
            });
            this._contextMenu = new ContextMenu({ commands });
            this._contextMenu.addItem({
                command: 'add-annotation',
                selector: 'canvas',
                rank: 1
            });
        };
        this.sceneSetup = () => {
            if (this.divRef.current !== null) {
                this._camera = new THREE.PerspectiveCamera(90, 2, 0.1, 1000);
                this._camera.position.set(8, 8, 8);
                this._camera.up.set(0, 0, 1);
                this._scene = new THREE.Scene();
                this._scene.add(new THREE.AmbientLight(0xffffff, 0.8)); // soft white light
                const light = new THREE.SpotLight(0xffffff, 0.2);
                light.castShadow = true;
                light.shadow.radius = 32;
                light.shadow.mapSize.width = 128;
                light.shadow.mapSize.height = 128;
                this._camera.add(light);
                this._scene.add(this._camera);
                this._renderer = new THREE.WebGLRenderer({
                    alpha: true,
                    antialias: true
                });
                // this._renderer.setPixelRatio(window.devicePixelRatio);
                this._renderer.setClearColor(0x000000, 0);
                this._renderer.setSize(500, 500, false);
                this.divRef.current.appendChild(this._renderer.domElement); // mount using React ref
                this._syncPointer = throttle((position, parent) => {
                    if (position && parent) {
                        this._model.syncPointer({
                            parent,
                            x: position.x,
                            y: position.y,
                            z: position.z
                        });
                    }
                    else {
                        this._model.syncPointer(undefined);
                    }
                }, 100);
                this._renderer.domElement.addEventListener('pointermove', this._onPointerMove.bind(this));
                this._renderer.domElement.addEventListener('mouseup', e => {
                    this._onClick.bind(this)(e);
                });
                this._renderer.domElement.addEventListener('contextmenu', e => {
                    e.preventDefault();
                    e.stopPropagation();
                    this._contextMenu.open(e);
                });
                const controls = new OrbitControls(this._camera, this._renderer.domElement);
                // controls.rotateSpeed = 1.0;
                // controls.zoomSpeed = 1.2;
                // controls.panSpeed = 0.8;
                controls.target.set(this._scene.position.x, this._scene.position.y, this._scene.position.z);
                this._controls = controls;
                this._controls.addEventListener('change', () => {
                    this._updateAnnotation();
                });
                this._controls.addEventListener('change', throttle(() => {
                    var _a;
                    // Not syncing camera state if following someone else
                    if ((_a = this._model.localState) === null || _a === void 0 ? void 0 : _a.remoteUser) {
                        return;
                    }
                    this._model.syncCamera({
                        position: this._camera.position.toArray([]),
                        rotation: this._camera.rotation.toArray([]),
                        up: this._camera.up.toArray([])
                    }, this.state.id);
                }, 100));
            }
        };
        this.startAnimationLoop = () => {
            this._requestID = window.requestAnimationFrame(this.startAnimationLoop);
            this._controls.update();
            this._renderer.setRenderTarget(null);
            this._renderer.clearDepth();
            this._renderer.render(this._scene, this._camera);
        };
        this.resizeCanvasToDisplaySize = () => {
            if (this.divRef.current !== null) {
                this._renderer.setSize(this.divRef.current.clientWidth, this.divRef.current.clientHeight, false);
                this._camera.aspect =
                    this.divRef.current.clientWidth / this.divRef.current.clientHeight;
                this._camera.updateProjectionMatrix();
            }
        };
        this.generateScene = () => {
            this.sceneSetup();
            this.startAnimationLoop();
            this.resizeCanvasToDisplaySize();
        };
        this.messageHandler = (msg) => {
            switch (msg.action) {
                case MainAction.DISPLAY_SHAPE: {
                    this._shapeToMesh(msg.payload);
                    break;
                }
                case MainAction.INITIALIZED: {
                    if (!this._model) {
                        return;
                    }
                    this._postMessage({
                        action: WorkerAction.LOAD_FILE,
                        payload: {
                            content: this._model.getContent()
                        }
                    });
                }
            }
        };
        this._projectVector = (vector) => {
            const copy = new THREE.Vector3().copy(vector);
            const canvas = this._renderer.domElement;
            copy.project(this._camera);
            return new Vector2((0.5 + copy.x / 2) * canvas.width, (0.5 - copy.y / 2) * canvas.height);
        };
        this._shapeToMesh = (payload) => {
            var _a;
            if (this._meshGroup !== null) {
                this._scene.remove(this._meshGroup);
            }
            if (this._explodedViewLinesHelperGroup !== null) {
                this._scene.remove(this._explodedViewLinesHelperGroup);
            }
            const guidata = this._model.sharedModel.getOption('guidata');
            this._boundingGroup = new THREE.Box3();
            this._meshGroup = new THREE.Group();
            Object.entries(payload).forEach(([objName, data]) => {
                var _a;
                const { faceList, edgeList, jcObject } = data;
                const vertices = [];
                const normals = [];
                const triangles = [];
                let vInd = 0;
                if (faceList.length === 0 && edgeList.length === 0) {
                    return;
                }
                faceList.forEach(face => {
                    // Copy Vertices into three.js Vector3 List
                    vertices.push(...face.vertexCoord);
                    normals.push(...face.normalCoord);
                    // Sort Triangles into a three.js Face List
                    for (let i = 0; i < face.triIndexes.length; i += 3) {
                        triangles.push(face.triIndexes[i + 0] + vInd, face.triIndexes[i + 1] + vInd, face.triIndexes[i + 2] + vInd);
                    }
                    vInd += face.vertexCoord.length / 3;
                });
                const objdata = guidata ? guidata === null || guidata === void 0 ? void 0 : guidata[objName] : null;
                let color = DEFAULT_MESH_COLOR;
                let visible = true;
                if (objdata) {
                    if (Object.prototype.hasOwnProperty.call(objdata, 'color')) {
                        const rgba = objdata['color'];
                        color = new THREE.Color(rgba[0], rgba[1], rgba[2]);
                    }
                    visible = guidata[objName]['visibility'] = jcObject.visible;
                }
                else if (guidata) {
                    guidata[objName] = { visibility: jcObject.visible };
                }
                // Compile the connected vertices and faces into a model
                // And add to the scene
                // We need one material per-mesh because we will set the uniform color independently later
                // it's too bad Three.js does not easily allow setting uniforms independently per-mesh
                const material = new THREE.MeshPhongMaterial({
                    color,
                    side: THREE.DoubleSide,
                    wireframe: false,
                    flatShading: false,
                    shininess: 40
                });
                const geometry = new THREE.BufferGeometry();
                geometry.setIndex(triangles);
                geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
                geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
                geometry.computeBoundingBox();
                if (vertices.length > 0) {
                    geometry.computeBoundsTree();
                }
                const mesh = new THREE.Mesh(geometry, material);
                mesh.castShadow = true;
                mesh.name = objName;
                mesh.visible = visible;
                if (visible) {
                    this._boundingGroup.expandByObject(mesh);
                }
                if (((_a = this._selectedMesh) === null || _a === void 0 ? void 0 : _a.name) === objName) {
                    this._selectedMesh = mesh;
                    mesh.material.color = SELECTED_MESH_COLOR;
                }
                const edgeMaterial = new THREE.LineBasicMaterial({
                    linewidth: 5,
                    color: 'black'
                });
                edgeList.forEach(edge => {
                    const edgeVertices = new THREE.Float32BufferAttribute(edge.vertexCoord, 3);
                    const edgeGeometry = new THREE.BufferGeometry();
                    edgeGeometry.setAttribute('position', edgeVertices);
                    const edgesMesh = new THREE.Line(edgeGeometry, edgeMaterial);
                    edgesMesh.name = 'edge';
                    mesh.add(edgesMesh);
                });
                if (this._meshGroup) {
                    this._meshGroup.add(mesh);
                }
            });
            if (guidata) {
                (_a = this._model.sharedModel) === null || _a === void 0 ? void 0 : _a.setOption('guidata', guidata);
            }
            // Update the reflength
            if (this._refLength === null && this._meshGroup.children.length) {
                const boxSizeVec = new THREE.Vector3();
                this._boundingGroup.getSize(boxSizeVec);
                this._refLength =
                    Math.max(boxSizeVec.x, boxSizeVec.y, boxSizeVec.z) / 5 || 1;
                this._updatePointers(this._refLength);
                this._camera.lookAt(this._scene.position);
                this._camera.position.set(10 * this._refLength, 10 * this._refLength, 10 * this._refLength);
                this._camera.far = 200 * this._refLength;
            }
            // Reset reflength if there are no objects
            if (!this._meshGroup.children.length) {
                this._refLength = null;
            }
            // Set the expoded view if it's enabled
            this._setupExplodedView();
            this._scene.add(this._meshGroup);
            this.setState(old => (Object.assign(Object.assign({}, old), { loading: false })));
        };
        this._postMessage = (msg, port) => {
            if (this._worker) {
                const newMsg = Object.assign(Object.assign({}, msg), { id: this.state.id });
                if (port) {
                    this._worker.postMessage(newMsg, [port]);
                }
                else {
                    this._worker.postMessage(newMsg);
                }
            }
        };
        this._onSharedMetadataChanged = (_, changes) => {
            const newState = Object.assign({}, this.state.annotations);
            changes.forEach((val, key) => {
                if (!key.startsWith('annotation')) {
                    return;
                }
                const data = this._model.sharedModel.getMetadata(key);
                let open = true;
                if (this.state.firstLoad) {
                    open = false;
                }
                if (data && (val.action === 'add' || val.action === 'update')) {
                    const jsonData = JSON.parse(data);
                    jsonData['open'] = open;
                    newState[key] = jsonData;
                }
                else if (val.action === 'delete') {
                    delete newState[key];
                }
            });
            this.setState(old => (Object.assign(Object.assign({}, old), { annotations: newState, firstLoad: false })));
        };
        this._onClientSharedStateChanged = (sender, clients) => {
            var _a, _b, _c, _d, _e, _f, _g, _h, _j;
            const remoteUser = (_a = this._model.localState) === null || _a === void 0 ? void 0 : _a.remoteUser;
            // If we are in following mode, we update our camera and selection
            if (remoteUser) {
                const remoteState = clients.get(remoteUser);
                if (!remoteState) {
                    return;
                }
                if (((_b = remoteState.user) === null || _b === void 0 ? void 0 : _b.username) !== ((_c = this.state.remoteUser) === null || _c === void 0 ? void 0 : _c.username)) {
                    this.setState(old => (Object.assign(Object.assign({}, old), { remoteUser: remoteState.user })));
                }
                // Sync selected
                if (remoteState.selected.value !== ((_d = this._selectedMesh) === null || _d === void 0 ? void 0 : _d.name)) {
                    this._deselectObject();
                    if (remoteState.selected.value) {
                        this._selectObject(remoteState.selected.value);
                    }
                }
                // Sync camera
                const remoteCamera = remoteState.camera;
                if (remoteCamera === null || remoteCamera === void 0 ? void 0 : remoteCamera.value) {
                    const { position, rotation, up } = remoteCamera.value;
                    this._camera.position.set(position[0], position[1], position[2]);
                    this._camera.rotation.set(rotation[0], rotation[1], rotation[2]);
                    this._camera.up.set(up[0], up[1], up[2]);
                }
            }
            else {
                // If we are unfollowing a remote user, we reset our camera to its old position
                if (this.state.remoteUser !== null) {
                    this.setState(old => (Object.assign(Object.assign({}, old), { remoteUser: null })));
                    const camera = (_f = (_e = this._model.localState) === null || _e === void 0 ? void 0 : _e.camera) === null || _f === void 0 ? void 0 : _f.value;
                    if (camera) {
                        const position = camera.position;
                        const rotation = camera.rotation;
                        const up = camera.up;
                        this._camera.position.set(position[0], position[1], position[2]);
                        this._camera.rotation.set(rotation[0], rotation[1], rotation[2]);
                        this._camera.up.set(up[0], up[1], up[2]);
                    }
                }
                // Sync local selection if needed
                const localState = this._model.localState;
                if (((_g = localState === null || localState === void 0 ? void 0 : localState.selected) === null || _g === void 0 ? void 0 : _g.value) !== ((_h = this._selectedMesh) === null || _h === void 0 ? void 0 : _h.name)) {
                    this._deselectObject();
                    if ((_j = localState === null || localState === void 0 ? void 0 : localState.selected) === null || _j === void 0 ? void 0 : _j.value) {
                        this._selectObject(localState.selected.value);
                    }
                }
            }
            // Displaying collaborators pointers
            clients.forEach((clientState, clientId) => {
                var _a, _b;
                const pointer = (_a = clientState.pointer) === null || _a === void 0 ? void 0 : _a.value;
                // We already display our own cursor on mouse move
                if (this._model.getClientId() === clientId) {
                    return;
                }
                let collaboratorPointer = this._collaboratorPointers[clientId];
                if (pointer) {
                    const parent = (_b = this._meshGroup) === null || _b === void 0 ? void 0 : _b.getObjectByName(pointer.parent);
                    if (!collaboratorPointer) {
                        const mesh = this._createPointer(clientState.user);
                        collaboratorPointer = this._collaboratorPointers[clientId] = {
                            mesh,
                            parent
                        };
                        this._scene.add(mesh);
                    }
                    collaboratorPointer.mesh.visible = true;
                    // If we are in exploded view, we display the collaborator cursor at the exploded position
                    if (this._explodedView.enabled) {
                        const explodedState = this._computeExplodedState(parent);
                        const explodeVector = explodedState.vector.multiplyScalar(explodedState.distance);
                        collaboratorPointer.mesh.position.copy(new THREE.Vector3(pointer.x + explodeVector.x, pointer.y + explodeVector.y, pointer.z + explodeVector.z));
                    }
                    else {
                        collaboratorPointer.mesh.position.copy(new THREE.Vector3(pointer.x, pointer.y, pointer.z));
                    }
                    collaboratorPointer.parent = parent;
                }
                else {
                    if (this._collaboratorPointers[clientId]) {
                        this._collaboratorPointers[clientId].mesh.visible = false;
                    }
                }
            });
        };
        this._handleThemeChange = () => {
            const lightTheme = document.body.getAttribute('data-jp-theme-light') === 'true';
            this.setState(old => (Object.assign(Object.assign({}, old), { lightTheme })));
        };
        this._handleWindowResize = () => {
            this.resizeCanvasToDisplaySize();
            this._updateAnnotation();
        };
        this.divRef = React.createRef(); // Reference of render div
        this._worker = undefined;
        this._selectedMesh = null;
        this._meshGroup = null; // The list of ThreeJS meshes
        this._boundingGroup = new THREE.Box3();
        // TODO Make this a shared property
        this._explodedView = { enabled: false, factor: 0 };
        this._explodedViewLinesHelperGroup = null; // The list of line helpers for the exploded view
        this._raycaster = new THREE.Raycaster();
        this._requestID = null; // ID of window.requestAnimationFrame
        this._refLength = null; // Length of bounding box of current object
        this._pointer3D = null;
        this._geometry = new THREE.BufferGeometry();
        this._geometry.setDrawRange(0, 3 * 10000);
        this.props.view.changed.connect(this._onViewChanged, this);
        const lightTheme = document.body.getAttribute('data-jp-theme-light') === 'true';
        this.state = {
            id: uuid(),
            lightTheme,
            loading: true,
            annotations: {},
            firstLoad: true
        };
        this._model = this.props.jcadModel;
        this._worker = this._model.getWorker();
        this._pointer = new THREE.Vector2();
        this._collaboratorPointers = {};
        this._messageChannel = new MessageChannel();
        this._messageChannel.port1.onmessage = msgEvent => {
            this.messageHandler(msgEvent.data);
        };
        this._postMessage({ action: WorkerAction.REGISTER, payload: { id: this.state.id } }, this._messageChannel.port2);
        this._model.themeChanged.connect(this._handleThemeChange, this);
        this._model.sharedObjectsChanged.connect(this._onSharedObjectsChanged, this);
        this._model.sharedOptionsChanged.connect(this._onSharedOptionsChanged, this);
        this._model.clientStateChanged.connect(this._onClientSharedStateChanged, this);
        this._model.sharedMetadataChanged.connect(this._onSharedMetadataChanged, this);
        if (this._raycaster.params.Line) {
            this._raycaster.params.Line.threshold = 0.1;
        }
    }
    componentDidMount() {
        window.addEventListener('resize', this._handleWindowResize);
        this.generateScene();
        this.addContextMenu();
    }
    componentDidUpdate(oldProps, oldState) {
        this.resizeCanvasToDisplaySize();
    }
    componentWillUnmount() {
        window.cancelAnimationFrame(this._requestID);
        window.removeEventListener('resize', this._handleWindowResize);
        this.props.view.changed.disconnect(this._onViewChanged, this);
        this._controls.dispose();
        this._model.themeChanged.disconnect(this._handleThemeChange, this);
        this._model.sharedOptionsChanged.disconnect(this._onSharedOptionsChanged, this);
        this._model.sharedObjectsChanged.disconnect(this._onSharedObjectsChanged, this);
        this._model.clientStateChanged.disconnect(this._onClientSharedStateChanged, this);
        this._model.sharedMetadataChanged.disconnect(this._onSharedMetadataChanged, this);
    }
    _pick() {
        if (this._meshGroup === null || !this._meshGroup.children) {
            return null;
        }
        this._raycaster.setFromCamera(this._pointer, this._camera);
        const intersects = this._raycaster.intersectObjects(this._meshGroup.children);
        if (intersects.length > 0) {
            // Find the first intersection with a visible object
            for (const intersect of intersects) {
                if (!intersect.object.visible) {
                    continue;
                }
                return {
                    mesh: intersect.object,
                    position: intersect.point
                };
            }
        }
        return null;
    }
    _updateAnnotation() {
        Object.keys(this.state.annotations).forEach(key => {
            var _a, _b;
            const el = document.getElementById(key);
            if (el) {
                const annotation = (_a = this._model.annotationModel) === null || _a === void 0 ? void 0 : _a.getAnnotation(key);
                let screenPosition = new THREE.Vector2();
                if (annotation) {
                    const parent = (_b = this._meshGroup) === null || _b === void 0 ? void 0 : _b.getObjectByName(annotation.parent);
                    const position = new THREE.Vector3(annotation.position[0], annotation.position[1], annotation.position[2]);
                    // If in exploded view, we explode the annotation position as well
                    if (this._explodedView.enabled && parent) {
                        const explodedState = this._computeExplodedState(parent);
                        const explodeVector = explodedState.vector.multiplyScalar(explodedState.distance);
                        position.add(explodeVector);
                    }
                    screenPosition = this._projectVector(position);
                }
                el.style.left = `${Math.round(screenPosition.x)}px`;
                el.style.top = `${Math.round(screenPosition.y)}px`;
            }
        });
    }
    _onPointerMove(e) {
        const rect = this._renderer.domElement.getBoundingClientRect();
        this._pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this._pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        const picked = this._pick();
        // Update our 3D pointer locally so there is no visual latency in the local pointer movement
        if (!this._pointer3D && this._model.localState && picked) {
            this._pointer3D = {
                parent: picked.mesh,
                mesh: this._createPointer(this._model.localState.user)
            };
            this._scene.add(this._pointer3D.mesh);
        }
        if (picked) {
            if (!this._pointer3D) {
                this._syncPointer(undefined, undefined);
                return;
            }
            this._pointer3D.mesh.visible = true;
            this._pointer3D.mesh.position.copy(picked.position);
            this._pointer3D.parent = picked.mesh;
            // If in exploded view, we scale down to the initial position (to before exploding the view)
            if (this._explodedView.enabled) {
                const explodedState = this._computeExplodedState(this._pointer3D.parent);
                picked.position.add(explodedState.vector.multiplyScalar(-explodedState.distance));
            }
            this._syncPointer(picked.position, picked.mesh.name);
        }
        else {
            if (this._pointer3D) {
                this._pointer3D.mesh.visible = false;
            }
            this._syncPointer(undefined, undefined);
        }
    }
    _onClick(e) {
        const selection = this._pick();
        const guidata = this._model.sharedModel.getOption('guidata');
        if (selection) {
            // Deselect old selection
            if (this._selectedMesh) {
                let originalColor = DEFAULT_MESH_COLOR;
                if (guidata &&
                    guidata[this._selectedMesh.name] &&
                    guidata[this._selectedMesh.name]['color']) {
                    const rgba = guidata[this._selectedMesh.name]['color'];
                    originalColor = new THREE.Color(rgba[0], rgba[1], rgba[2]);
                }
                this._selectedMesh.material.color = originalColor;
            }
            // Set new selection
            if (selection.mesh === this._selectedMesh) {
                this._selectedMesh = null;
            }
            else {
                // TODO Support selecting edges?
                if (selection.mesh.name.startsWith('edge')) {
                    this._selectedMesh = selection.mesh.parent;
                }
                else {
                    this._selectedMesh = selection.mesh;
                }
            }
            if (this._selectedMesh) {
                this._selectedMesh.material.color = SELECTED_MESH_COLOR;
                this._model.syncSelectedObject(this._selectedMesh.name, this.state.id);
            }
            else {
                this._model.syncSelectedObject(undefined, this.state.id);
            }
        }
    }
    _updatePointers(refLength) {
        this._pointerGeometry = new THREE.SphereGeometry(refLength / 10, 32, 32);
        for (const clientId in this._collaboratorPointers) {
            this._collaboratorPointers[clientId].mesh.geometry =
                this._pointerGeometry;
        }
    }
    _createPointer(user) {
        var _a;
        let clientColor = null;
        if ((_a = user.color) === null || _a === void 0 ? void 0 : _a.startsWith('var')) {
            clientColor = Color.color(getComputedStyle(document.documentElement).getPropertyValue(user.color.slice(4, -1)));
        }
        else {
            clientColor = Color.color(user.color);
        }
        const material = new THREE.MeshBasicMaterial({
            color: clientColor
                ? new THREE.Color(clientColor.r / 255, clientColor.g / 255, clientColor.b / 255)
                : 'black'
        });
        return new THREE.Mesh(this._pointerGeometry, material);
    }
    _selectObject(name) {
        var _a, _b;
        if (name === ((_a = this._selectedMesh) === null || _a === void 0 ? void 0 : _a.name)) {
            return;
        }
        const selected = (_b = this._meshGroup) === null || _b === void 0 ? void 0 : _b.getObjectByName(name);
        if (selected) {
            this._selectedMesh = selected;
            this._selectedMesh.material.color = SELECTED_MESH_COLOR;
        }
    }
    _deselectObject() {
        if (!this._selectedMesh) {
            return;
        }
        let originalColor = DEFAULT_MESH_COLOR;
        const guidata = this._model.sharedModel.getOption('guidata');
        if (guidata &&
            guidata[this._selectedMesh.name] &&
            guidata[this._selectedMesh.name]['color']) {
            const rgba = guidata[this._selectedMesh.name]['color'];
            originalColor = new THREE.Color(rgba[0], rgba[1], rgba[2]);
        }
        this._selectedMesh.material.color = originalColor;
        this._selectedMesh = null;
    }
    _onSharedObjectsChanged(_, change) {
        if (change.objectChange) {
            this._postMessage({
                action: WorkerAction.LOAD_FILE,
                payload: {
                    content: this._model.getContent()
                }
            });
        }
    }
    _onSharedOptionsChanged(sender, change) {
        var _a, _b;
        const guidata = sender.getOption('guidata');
        if (guidata) {
            for (const objName in guidata) {
                if (Object.prototype.hasOwnProperty.call(guidata[objName], 'visibility')) {
                    const obj = (_a = this._meshGroup) === null || _a === void 0 ? void 0 : _a.getObjectByName(objName);
                    const explodedLineHelper = (_b = this._explodedViewLinesHelperGroup) === null || _b === void 0 ? void 0 : _b.getObjectByName(objName);
                    const objGuiData = guidata[objName];
                    if (obj && objGuiData) {
                        obj.visible = objGuiData['visibility'];
                        if (explodedLineHelper) {
                            explodedLineHelper.visible = objGuiData['visibility'];
                        }
                    }
                }
            }
        }
    }
    _onViewChanged(sender, change) {
        var _a;
        if (change.key === 'axes') {
            (_a = this._sceneAxe) === null || _a === void 0 ? void 0 : _a.removeFromParent();
            const axe = change.newValue;
            if (change.type !== 'remove' && axe && axe.visible) {
                this._sceneAxe = new THREE.AxesHelper(axe.size);
                this._scene.add(this._sceneAxe);
            }
        }
        if (change.key === 'explodedView') {
            const explodedView = change.newValue;
            if (change.type !== 'remove' && explodedView) {
                this._explodedView = explodedView;
                this._setupExplodedView();
            }
        }
    }
    _setupExplodedView() {
        var _a, _b, _c, _d;
        if (this._explodedView.enabled) {
            const center = new THREE.Vector3();
            this._boundingGroup.getCenter(center);
            (_a = this._explodedViewLinesHelperGroup) === null || _a === void 0 ? void 0 : _a.removeFromParent();
            this._explodedViewLinesHelperGroup = new THREE.Group();
            for (const mesh of (_b = this._meshGroup) === null || _b === void 0 ? void 0 : _b.children) {
                const explodedState = this._computeExplodedState(mesh);
                mesh.position.set(0, 0, 0);
                mesh.translateOnAxis(explodedState.vector, explodedState.distance);
                // Draw lines
                const material = new THREE.LineBasicMaterial({
                    color: 'black',
                    linewidth: 2
                });
                const geometry = new THREE.BufferGeometry().setFromPoints([
                    explodedState.oldGeometryCenter,
                    explodedState.newGeometryCenter
                ]);
                const line = new THREE.Line(geometry, material);
                line.name = mesh.name;
                line.visible = mesh.visible;
                this._explodedViewLinesHelperGroup.add(line);
            }
            this._scene.add(this._explodedViewLinesHelperGroup);
        }
        else {
            // Exploded view is disabled, we reset the initial positions
            for (const mesh of (_c = this._meshGroup) === null || _c === void 0 ? void 0 : _c.children) {
                mesh.position.set(0, 0, 0);
            }
            (_d = this._explodedViewLinesHelperGroup) === null || _d === void 0 ? void 0 : _d.removeFromParent();
        }
    }
    _computeExplodedState(mesh) {
        var _a;
        const center = new THREE.Vector3();
        this._boundingGroup.getCenter(center);
        const oldGeometryCenter = new THREE.Vector3();
        (_a = mesh.geometry.boundingBox) === null || _a === void 0 ? void 0 : _a.getCenter(oldGeometryCenter);
        const centerToMesh = new THREE.Vector3(oldGeometryCenter.x - center.x, oldGeometryCenter.y - center.y, oldGeometryCenter.z - center.z);
        const distance = centerToMesh.length() * this._explodedView.factor;
        centerToMesh.normalize();
        const newGeometryCenter = new THREE.Vector3(oldGeometryCenter.x + distance * centerToMesh.x, oldGeometryCenter.y + distance * centerToMesh.y, oldGeometryCenter.z + distance * centerToMesh.z);
        return {
            oldGeometryCenter,
            newGeometryCenter,
            vector: centerToMesh,
            distance
        };
    }
    render() {
        var _a;
        return (React.createElement("div", { className: "jcad-Mainview", style: {
                border: this.state.remoteUser
                    ? `solid 3px ${this.state.remoteUser.color}`
                    : 'unset'
            } },
            React.createElement("div", { className: 'jpcad-Spinner', style: { display: this.state.loading ? 'flex' : 'none' } },
                ' ',
                React.createElement("div", { className: 'jpcad-SpinnerContent' }),
                ' '),
            ((_a = this.state.remoteUser) === null || _a === void 0 ? void 0 : _a.display_name) ? (React.createElement("div", { style: {
                    position: 'absolute',
                    top: 1,
                    right: 3,
                    background: this.state.remoteUser.color
                } }, `Following ${this.state.remoteUser.display_name}`)) : null,
            Object.entries(this.state.annotations).map(([key, annotation]) => {
                var _a;
                if (!this._model.annotationModel) {
                    return null;
                }
                const parent = (_a = this._meshGroup) === null || _a === void 0 ? void 0 : _a.getObjectByName(annotation.parent);
                const position = new THREE.Vector3(annotation.position[0], annotation.position[1], annotation.position[2]);
                // If in exploded view, we explode the annotation position as well
                if (this._explodedView.enabled && parent) {
                    const explodedState = this._computeExplodedState(parent);
                    const explodeVector = explodedState.vector.multiplyScalar(explodedState.distance);
                    position.add(explodeVector);
                }
                const screenPosition = this._projectVector(position);
                return (React.createElement("div", { key: key, id: key, style: {
                        left: screenPosition.x,
                        top: screenPosition.y
                    }, className: 'jcad-Annotation-Wrapper' },
                    React.createElement(FloatingAnnotation, { itemId: key, model: this._model.annotationModel, open: false })));
            }),
            React.createElement("div", { ref: this.divRef, style: {
                    width: '100%',
                    height: 'calc(100%)',
                    background: this.state.lightTheme ? LIGHT_BG_COLOR : DARK_BG_COLOR
                } })));
    }
}
