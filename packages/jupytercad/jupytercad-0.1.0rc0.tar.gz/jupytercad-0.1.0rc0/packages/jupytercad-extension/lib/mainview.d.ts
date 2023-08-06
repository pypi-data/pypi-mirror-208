import { ObservableMap } from '@jupyterlab/observables';
import { User } from '@jupyterlab/services';
import { JSONValue } from '@lumino/coreutils';
import * as React from 'react';
import * as THREE from 'three';
import { IAnnotation, IDict, IJupyterCadModel, IMainMessage } from './types';
export type BasicMesh = THREE.Mesh<THREE.BufferGeometry, THREE.MeshBasicMaterial>;
interface IProps {
    view: ObservableMap<JSONValue>;
    jcadModel: IJupyterCadModel;
}
interface IStates {
    id: string;
    loading: boolean;
    lightTheme: boolean;
    remoteUser?: User.IIdentity | null;
    annotations: IDict<IAnnotation>;
    firstLoad: boolean;
}
/**
 * The result of mesh picking, contains the picked mesh and the 3D position of the pointer.
 */
interface IPickedResult {
    mesh: BasicMesh;
    position: THREE.Vector3;
}
export declare class MainView extends React.Component<IProps, IStates> {
    constructor(props: IProps);
    componentDidMount(): void;
    componentDidUpdate(oldProps: IProps, oldState: IStates): void;
    componentWillUnmount(): void;
    addContextMenu: () => void;
    sceneSetup: () => void;
    _pick(): IPickedResult | null;
    startAnimationLoop: () => void;
    resizeCanvasToDisplaySize: () => void;
    generateScene: () => void;
    messageHandler: (msg: IMainMessage) => void;
    private _projectVector;
    private _updateAnnotation;
    private _onPointerMove;
    private _onClick;
    private _shapeToMesh;
    private _postMessage;
    private _updatePointers;
    private _createPointer;
    private _selectObject;
    private _deselectObject;
    private _onSharedMetadataChanged;
    private _onClientSharedStateChanged;
    private _onSharedObjectsChanged;
    private _onSharedOptionsChanged;
    private _onViewChanged;
    private _setupExplodedView;
    private _computeExplodedState;
    private _handleThemeChange;
    private _handleWindowResize;
    render(): JSX.Element;
    private divRef;
    private _model;
    private _worker?;
    private _messageChannel?;
    private _pointer;
    private _syncPointer;
    private _selectedMesh;
    private _meshGroup;
    private _boundingGroup;
    private _explodedView;
    private _explodedViewLinesHelperGroup;
    private _scene;
    private _camera;
    private _raycaster;
    private _renderer;
    private _requestID;
    private _geometry;
    private _refLength;
    private _sceneAxe;
    private _controls;
    private _pointer3D;
    private _collaboratorPointers;
    private _pointerGeometry;
    private _contextMenu;
}
export {};
