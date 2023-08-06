import * as React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { LabIcon, PanelWithToolbar, ToolbarButtonComponent, closeIcon } from '@jupyterlab/ui-components';
import { ReactTree } from '@naisutech/react-tree';
import visibilitySvg from '../../style/icon/visibility.svg';
import visibilityOffSvg from '../../style/icon/visibilityOff.svg';
import { v4 as uuid } from 'uuid';
const visibilityIcon = new LabIcon({
    name: 'jupytercad:visibilityIcon',
    svgstr: visibilitySvg
});
const visibilityOffIcon = new LabIcon({
    name: 'jupytercad:visibilityOffIcon',
    svgstr: visibilityOffSvg
});
const TREE_THEMES = {
    labTheme: {
        text: {
            fontSize: '14px',
            fontFamily: 'var(--jp-ui-font-family)',
            color: 'var(--jp-ui-font-color1)',
            selectedColor: 'var(--jp-ui-inverse-font-color1)',
            hoverColor: 'var(--jp-ui-font-color2)'
        },
        nodes: {
            folder: {
                bgColor: 'var(--jp-layout-color1)',
                selectedBgColor: 'var(--jp-layout-color2)',
                hoverBgColor: 'var(--jp-layout-color2)'
            },
            leaf: {
                bgColor: 'var(--jp-layout-color1)',
                selectedBgColor: 'var(--jp-layout-color2)',
                hoverBgColor: 'var(--jp-layout-color2)'
            },
            icons: {
                size: '9px',
                folderColor: 'var(--jp-inverse-layout-color3)',
                leafColor: 'var(--jp-inverse-layout-color3)'
            }
        }
    }
};
export class ObjectTree extends PanelWithToolbar {
    constructor(params) {
        super(params);
        this.title.label = 'Objects tree';
        const body = ReactWidget.create(React.createElement(ObjectTreeReact, { cpModel: params.controlPanelModel }));
        this.addWidget(body);
        this.addClass('jpcad-sidebar-treepanel');
    }
}
class ObjectTreeReact extends React.Component {
    constructor(props) {
        var _a, _b;
        super(props);
        this.stateToTree = () => {
            if (this.state.jcadObject) {
                return this.state.jcadObject.map(obj => {
                    var _a;
                    const name = obj.name;
                    const items = [];
                    if (obj.shape) {
                        items.push({
                            id: `${name}#shape#${obj.shape}#${this.state.filePath}`,
                            label: 'Shape',
                            parentId: name
                        });
                    }
                    if (obj.operators) {
                        items.push({
                            id: `${name}#operator#${this.state.filePath}`,
                            label: 'Operators',
                            parentId: name
                        });
                    }
                    return {
                        id: name,
                        label: (_a = obj.name) !== null && _a !== void 0 ? _a : `Object (#${name})`,
                        parentId: null,
                        items
                    };
                });
            }
            return [];
        };
        this._handleThemeChange = () => {
            const lightTheme = document.body.getAttribute('data-jp-theme-light') === 'true';
            this.setState(old => (Object.assign(Object.assign({}, old), { lightTheme })));
        };
        this._sharedJcadModelChanged = (sender, change) => {
            if (change.objectChange) {
                this.setState(old => {
                    var _a, _b;
                    return (Object.assign(Object.assign({}, old), { jcadObject: (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.getAllObject(), options: (_b = this.props.cpModel.sharedModel) === null || _b === void 0 ? void 0 : _b.options }));
                });
            }
        };
        this._onClientSharedStateChanged = (sender, clients) => {
            var _a, _b, _c;
            const localState = (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.localState;
            if (!localState) {
                return;
            }
            let selectedNode = null;
            if (localState.remoteUser) {
                // We are in following mode.
                // Sync selections from a remote user
                const remoteState = clients.get(localState.remoteUser);
                if ((_b = remoteState === null || remoteState === void 0 ? void 0 : remoteState.selected) === null || _b === void 0 ? void 0 : _b.value) {
                    selectedNode = (_c = remoteState === null || remoteState === void 0 ? void 0 : remoteState.selected) === null || _c === void 0 ? void 0 : _c.value;
                }
            }
            else if (localState.selected.value) {
                selectedNode = localState.selected.value;
            }
            const openNodes = [...this.state.openNodes];
            if (selectedNode && openNodes.indexOf(selectedNode) === -1) {
                openNodes.push(selectedNode);
            }
            this.setState(old => (Object.assign(Object.assign({}, old), { openNodes, selectedNode })));
        };
        this._onClientSharedOptionsChanged = (sender, clients) => {
            this.setState(old => (Object.assign(Object.assign({}, old), { options: sender.options })));
        };
        const lightTheme = document.body.getAttribute('data-jp-theme-light') === 'true';
        this.state = {
            filePath: this.props.cpModel.filePath,
            jcadObject: (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.getAllObject(),
            lightTheme,
            selectedNode: null,
            clientId: null,
            id: uuid(),
            openNodes: []
        };
        (_b = this.props.cpModel.jcadModel) === null || _b === void 0 ? void 0 : _b.sharedObjectsChanged.connect(this._sharedJcadModelChanged);
        this.props.cpModel.documentChanged.connect((_, document) => {
            if (document) {
                this.props.cpModel.disconnect(this._sharedJcadModelChanged);
                this.props.cpModel.disconnect(this._handleThemeChange);
                this.props.cpModel.disconnect(this._onClientSharedStateChanged);
                document.context.model.sharedObjectsChanged.connect(this._sharedJcadModelChanged);
                document.context.model.themeChanged.connect(this._handleThemeChange);
                document.context.model.clientStateChanged.connect(this._onClientSharedStateChanged);
                document.context.model.sharedOptionsChanged.connect(this._onClientSharedOptionsChanged);
                this.setState(old => {
                    var _a, _b;
                    return (Object.assign(Object.assign({}, old), { filePath: document.context.localPath, jcadObject: (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.getAllObject(), options: (_b = this.props.cpModel.sharedModel) === null || _b === void 0 ? void 0 : _b.options, clientId: document.context.model.getClientId() }));
                });
            }
            else {
                this.setState({
                    filePath: undefined,
                    jcadObject: undefined,
                    jcadOption: undefined
                });
            }
        });
    }
    getObjectFromName(name) {
        if (name && this.state.jcadObject) {
            const obj = this.state.jcadObject.filter(o => o.name === name);
            if (obj.length > 0) {
                return obj[0];
            }
        }
    }
    render() {
        const { selectedNode, openNodes, options } = this.state;
        const data = this.stateToTree();
        let selectedNodes = [];
        if (selectedNode) {
            const parentNode = data.filter(node => node.id === selectedNode);
            if (parentNode.length > 0 && parentNode[0].items.length > 0) {
                selectedNodes = [parentNode[0].items[0].id];
            }
        }
        return (React.createElement("div", { className: "jpcad-treeview-wrapper" },
            React.createElement(ReactTree, { nodes: data, openNodes: openNodes, selectedNodes: selectedNodes, messages: { noData: 'No data' }, theme: 'labTheme', themes: TREE_THEMES, onToggleSelectedNodes: id => {
                    var _a, _b;
                    if (id && id.length > 0) {
                        let name = id[0];
                        if (name.includes('#')) {
                            name = name.split('#')[0];
                            (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.syncSelectedObject(name, this.state.id);
                            return;
                        }
                        const openNodes = [...this.state.openNodes];
                        const index = openNodes.indexOf(name);
                        if (index !== -1) {
                            openNodes.splice(index, 1);
                        }
                        else {
                            openNodes.push(name);
                        }
                        this.setState(old => (Object.assign(Object.assign({}, old), { openNodes })));
                    }
                    else {
                        (_b = this.props.cpModel.jcadModel) === null || _b === void 0 ? void 0 : _b.syncSelectedObject(undefined);
                    }
                }, RenderNode: opts => {
                    // const paddingLeft = 25 * (opts.level + 1);
                    const jcadObj = this.getObjectFromName(opts.node.parentId);
                    let visible = true;
                    if (jcadObj &&
                        options &&
                        options['guidata'] &&
                        options['guidata'][jcadObj === null || jcadObj === void 0 ? void 0 : jcadObj.name]) {
                        visible = options['guidata'][jcadObj === null || jcadObj === void 0 ? void 0 : jcadObj.name]['visibility'];
                    }
                    return (React.createElement("div", { className: `jpcad-control-panel-tree ${opts.selected ? 'selected' : ''}` },
                        React.createElement("div", { style: {
                                paddingLeft: '5px',
                                minHeight: '20px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                minWidth: 0
                            } },
                            React.createElement("span", { style: {
                                    whiteSpace: 'nowrap',
                                    textOverflow: 'ellipsis',
                                    overflowX: 'hidden'
                                } }, opts.node.label),
                            opts.type === 'leaf' ? (React.createElement("div", { style: { display: 'flex' } },
                                React.createElement(ToolbarButtonComponent, { className: 'jp-ToolbarButtonComponent', onClick: () => {
                                        var _a, _b;
                                        const objectId = opts.node.parentId;
                                        const guidata = ((_a = this.props.cpModel.sharedModel) === null || _a === void 0 ? void 0 : _a.getOption('guidata')) || { objectId: {} };
                                        if (guidata) {
                                            if (guidata[objectId]) {
                                                guidata[objectId]['visibility'] = !visible;
                                            }
                                            else {
                                                guidata[objectId] = { visibility: !visible };
                                            }
                                        }
                                        (_b = this.props.cpModel.sharedModel) === null || _b === void 0 ? void 0 : _b.setOption('guidata', guidata);
                                    }, icon: visible ? visibilityIcon : visibilityOffIcon }),
                                React.createElement(ToolbarButtonComponent, { className: 'jp-ToolbarButtonComponent', onClick: () => {
                                        var _a, _b;
                                        const objectId = opts.node.parentId;
                                        (_a = this.props.cpModel.jcadModel) === null || _a === void 0 ? void 0 : _a.sharedModel.removeObjectByName(objectId);
                                        (_b = this.props.cpModel.jcadModel) === null || _b === void 0 ? void 0 : _b.syncSelectedObject(undefined);
                                    }, icon: closeIcon }))) : null)));
                } })));
    }
}
