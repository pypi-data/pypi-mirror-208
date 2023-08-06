var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
import { showErrorMessage } from '@jupyterlab/apputils';
import { SketcherDialog } from './sketcher/sketcherdialog';
import { FormDialog } from './formdialog';
import { axesIcon, boxIcon, coneIcon, cutIcon, cylinderIcon, explodedViewIcon, extrusionIcon, intersectionIcon, sphereIcon, torusIcon, unionIcon } from './tools';
import formSchema from './_interface/forms.json';
const FORM_SCHEMA = {};
// Injecting "name" in the schema, as it's not part of the official schema but
// we still want to configure it in the dialog
Object.keys(formSchema).forEach(key => {
    if (key === 'Placement of the box') {
        return;
    }
    const value = (FORM_SCHEMA[key] = JSON.parse(JSON.stringify(formSchema[key])));
    value['required'] = ['Name', ...value['required']];
    value['properties'] = Object.assign({ Name: { type: 'string', description: 'The Name of the Object' } }, value['properties']);
});
function newName(type, model) {
    const sharedModel = model.sharedModel;
    let n = 1;
    let name = `${type} 1`;
    while (sharedModel.objectExists(name)) {
        name = `${type} ${++n}`;
    }
    return name;
}
const PARTS = {
    box: {
        title: 'Box parameters',
        shape: 'Part::Box',
        default: (model) => {
            return {
                Name: newName('Box', model),
                Length: 1,
                Width: 1,
                Height: 1,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        }
    },
    cylinder: {
        title: 'Cylinder parameters',
        shape: 'Part::Cylinder',
        default: (model) => {
            return {
                Name: newName('Cylinder', model),
                Radius: 1,
                Height: 1,
                Angle: 360,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        }
    },
    sphere: {
        title: 'Sphere parameters',
        shape: 'Part::Sphere',
        default: (model) => {
            return {
                Name: newName('Sphere', model),
                Radius: 5,
                Angle1: -90,
                Angle2: 90,
                Angle3: 360,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        }
    },
    cone: {
        title: 'Cone parameters',
        shape: 'Part::Cone',
        default: (model) => {
            return {
                Name: newName('Cone', model),
                Radius1: 1,
                Radius2: 0.5,
                Height: 1,
                Angle: 360,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        }
    },
    torus: {
        title: 'Torus parameters',
        shape: 'Part::Torus',
        default: (model) => {
            return {
                Name: newName('Torus', model),
                Radius1: 10,
                Radius2: 2,
                Angle1: -180,
                Angle2: 180,
                Angle3: 360,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        }
    }
};
const OPERATORS = {
    cut: {
        title: 'Cut parameters',
        shape: 'Part::Cut',
        default: (model) => {
            var _a, _b;
            const objects = model.getAllObject();
            return {
                Name: newName('Cut', model),
                Base: (_a = objects[0].name) !== null && _a !== void 0 ? _a : '',
                Tool: (_b = objects[1].name) !== null && _b !== void 0 ? _b : '',
                Refine: false,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        },
        syncData: (model) => {
            return (props) => {
                const { Name } = props, parameters = __rest(props, ["Name"]);
                const objectModel = {
                    shape: 'Part::Cut',
                    parameters,
                    visible: true,
                    name: Name
                };
                const sharedModel = model.sharedModel;
                if (sharedModel) {
                    sharedModel.transact(() => {
                        sharedModel.updateObjectByName(parameters['Base'], 'visible', false);
                        sharedModel.updateObjectByName(parameters['Tool'], 'visible', false);
                        if (!sharedModel.objectExists(objectModel.name)) {
                            sharedModel.addObject(objectModel);
                        }
                        else {
                            showErrorMessage('The object already exists', 'There is an existing object with the same name.');
                        }
                    });
                }
            };
        }
    },
    extrusion: {
        title: 'Extrusion parameters',
        shape: 'Part::Extrusion',
        default: (model) => {
            var _a;
            const objects = model.getAllObject();
            return {
                Name: newName('Extrusion', model),
                Base: [(_a = objects[0].name) !== null && _a !== void 0 ? _a : ''],
                Dir: [0, 0, 1],
                LengthFwd: 10,
                LengthRev: 0,
                Solid: false,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        },
        syncData: (model) => {
            return (props) => {
                const { Name } = props, parameters = __rest(props, ["Name"]);
                const objectModel = {
                    shape: 'Part::Extrusion',
                    parameters,
                    visible: true,
                    name: Name
                };
                const sharedModel = model.sharedModel;
                if (sharedModel) {
                    sharedModel.transact(() => {
                        if (!sharedModel.objectExists(objectModel.name)) {
                            sharedModel.addObject(objectModel);
                        }
                        else {
                            showErrorMessage('The object already exists', 'There is an existing object with the same name.');
                        }
                    });
                }
            };
        }
    },
    union: {
        title: 'Fuse parameters',
        shape: 'Part::MultiFuse',
        default: (model) => {
            var _a, _b;
            const objects = model.getAllObject();
            return {
                Name: newName('Union', model),
                Shapes: [(_a = objects[0].name) !== null && _a !== void 0 ? _a : '', (_b = objects[1].name) !== null && _b !== void 0 ? _b : ''],
                Refine: false,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        },
        syncData: (model) => {
            return (props) => {
                const { Name } = props, parameters = __rest(props, ["Name"]);
                const objectModel = {
                    shape: 'Part::MultiFuse',
                    parameters,
                    visible: true,
                    name: Name
                };
                const sharedModel = model.sharedModel;
                if (sharedModel) {
                    sharedModel.transact(() => {
                        if (!sharedModel.objectExists(objectModel.name)) {
                            sharedModel.addObject(objectModel);
                        }
                        else {
                            showErrorMessage('The object already exists', 'There is an existing object with the same name.');
                        }
                    });
                }
            };
        }
    },
    intersection: {
        title: 'Intersection parameters',
        shape: 'Part::MultiCommon',
        default: (model) => {
            var _a, _b;
            const objects = model.getAllObject();
            return {
                Name: newName('Intersection', model),
                Shapes: [(_a = objects[0].name) !== null && _a !== void 0 ? _a : '', (_b = objects[1].name) !== null && _b !== void 0 ? _b : ''],
                Refine: false,
                Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
            };
        },
        syncData: (model) => {
            return (props) => {
                const { Name } = props, parameters = __rest(props, ["Name"]);
                const objectModel = {
                    shape: 'Part::MultiCommon',
                    parameters,
                    visible: true,
                    name: Name
                };
                const sharedModel = model.sharedModel;
                if (sharedModel) {
                    sharedModel.transact(() => {
                        if (!sharedModel.objectExists(objectModel.name)) {
                            sharedModel.addObject(objectModel);
                        }
                        else {
                            showErrorMessage('The object already exists', 'There is an existing object with the same name.');
                        }
                    });
                }
            };
        }
    }
};
const AXES_FORM = {
    title: 'Axes Helper',
    schema: {
        type: 'object',
        required: ['Size', 'Visible'],
        additionalProperties: false,
        properties: {
            Size: {
                type: 'number',
                description: 'Size of the axes'
            },
            Visible: {
                type: 'boolean',
                description: 'Whether the axes are visible or not'
            }
        }
    },
    default: (panel) => {
        var _a, _b, _c, _d;
        return {
            Size: (_b = (_a = panel.axes) === null || _a === void 0 ? void 0 : _a.size) !== null && _b !== void 0 ? _b : 5,
            Visible: (_d = (_c = panel.axes) === null || _c === void 0 ? void 0 : _c.visible) !== null && _d !== void 0 ? _d : true
        };
    },
    syncData: (panel) => {
        return (props) => {
            const { Size, Visible } = props;
            panel.axes = {
                size: Size,
                visible: Visible
            };
        };
    }
};
const EXPLODED_VIEW_FORM = {
    title: 'Exploded View Settings',
    schema: {
        type: 'object',
        required: ['Enabled', 'Factor'],
        additionalProperties: false,
        properties: {
            Enabled: {
                type: 'boolean',
                description: 'Whether the exploded view is enabled or not'
            },
            Factor: {
                type: 'number',
                description: 'The exploded view factor'
            }
        }
    },
    default: (panel) => {
        var _a, _b, _c, _d;
        return {
            Enabled: (_b = (_a = panel.explodedView) === null || _a === void 0 ? void 0 : _a.enabled) !== null && _b !== void 0 ? _b : false,
            Factor: (_d = (_c = panel.explodedView) === null || _c === void 0 ? void 0 : _c.factor) !== null && _d !== void 0 ? _d : 0.5
        };
    },
    syncData: (panel) => {
        return (props) => {
            const { Enabled, Factor } = props;
            panel.explodedView = {
                enabled: Enabled,
                factor: Factor
            };
        };
    }
};
/**
 * Add the FreeCAD commands to the application's command registry.
 */
export function addCommands(app, tracker, translator) {
    const trans = translator.load('jupyterlab');
    const { commands } = app;
    commands.addCommand(CommandIDs.redo, {
        label: trans.__('Redo'),
        execute: args => {
            const current = tracker.currentWidget;
            if (current) {
                return current.context.model.sharedModel.redo();
            }
        }
    });
    commands.addCommand(CommandIDs.undo, {
        label: trans.__('Undo'),
        execute: args => {
            const current = tracker.currentWidget;
            if (current) {
                return current.context.model.sharedModel.undo();
            }
        }
    });
    commands.addCommand(CommandIDs.newSketch, {
        label: trans.__('New Sketch'),
        iconClass: 'fa fa-pencil',
        execute: async (args) => {
            const current = tracker.currentWidget;
            if (!current) {
                return;
            }
            const props = {
                sharedModel: current.context.model.sharedModel,
                closeCallback: {
                    handler: () => {
                        /* Awful hack to allow the body can close the dialog*/
                    }
                }
            };
            const dialog = new SketcherDialog(props);
            props.closeCallback.handler = () => dialog.close();
            await dialog.launch();
        }
    });
    commands.addCommand(CommandIDs.newBox, {
        label: trans.__('New Box'),
        icon: boxIcon,
        execute: Private.createPart('box', tracker)
    });
    commands.addCommand(CommandIDs.newCylinder, {
        label: trans.__('New Cylinder'),
        icon: cylinderIcon,
        execute: Private.createPart('cylinder', tracker)
    });
    commands.addCommand(CommandIDs.newSphere, {
        label: trans.__('New Sphere'),
        icon: sphereIcon,
        execute: Private.createPart('sphere', tracker)
    });
    commands.addCommand(CommandIDs.newCone, {
        label: trans.__('New Cone'),
        icon: coneIcon,
        execute: Private.createPart('cone', tracker)
    });
    commands.addCommand(CommandIDs.newTorus, {
        label: trans.__('New Torus'),
        icon: torusIcon,
        execute: Private.createPart('torus', tracker)
    });
    commands.addCommand(CommandIDs.extrusion, {
        label: trans.__('Extrusion'),
        icon: extrusionIcon,
        execute: Private.executeOperator('extrusion', tracker)
    });
    commands.addCommand(CommandIDs.cut, {
        label: trans.__('Cut'),
        icon: cutIcon,
        execute: Private.executeOperator('cut', tracker)
    });
    commands.addCommand(CommandIDs.union, {
        label: trans.__('Union'),
        icon: unionIcon,
        execute: Private.executeOperator('union', tracker)
    });
    commands.addCommand(CommandIDs.intersection, {
        label: trans.__('Intersection'),
        icon: intersectionIcon,
        execute: Private.executeOperator('intersection', tracker)
    });
    commands.addCommand(CommandIDs.updateAxes, {
        label: trans.__('Axes Helper'),
        icon: axesIcon,
        execute: async () => {
            const current = tracker.currentWidget;
            if (!current) {
                return;
            }
            const dialog = new FormDialog({
                context: current.context,
                title: AXES_FORM.title,
                schema: AXES_FORM.schema,
                sourceData: AXES_FORM.default(current.content),
                syncData: AXES_FORM.syncData(current.content),
                cancelButton: true
            });
            await dialog.launch();
        }
    });
    commands.addCommand(CommandIDs.updateExplodedView, {
        label: trans.__('Exploded View'),
        icon: explodedViewIcon,
        execute: async () => {
            const current = tracker.currentWidget;
            if (!current) {
                return;
            }
            const dialog = new FormDialog({
                context: current.context,
                title: EXPLODED_VIEW_FORM.title,
                schema: EXPLODED_VIEW_FORM.schema,
                sourceData: EXPLODED_VIEW_FORM.default(current.content),
                syncData: EXPLODED_VIEW_FORM.syncData(current.content),
                cancelButton: true
            });
            await dialog.launch();
        }
    });
}
/**
 * The command IDs used by the FreeCAD plugin.
 */
export var CommandIDs;
(function (CommandIDs) {
    CommandIDs.redo = 'jupytercad:redo';
    CommandIDs.undo = 'jupytercad:undo';
    CommandIDs.newSketch = 'jupytercad:sketch';
    CommandIDs.newBox = 'jupytercad:newBox';
    CommandIDs.newCylinder = 'jupytercad:newCylinder';
    CommandIDs.newSphere = 'jupytercad:newSphere';
    CommandIDs.newCone = 'jupytercad:newCone';
    CommandIDs.newTorus = 'jupytercad:newTorus';
    CommandIDs.cut = 'jupytercad:cut';
    CommandIDs.extrusion = 'jupytercad:extrusion';
    CommandIDs.union = 'jupytercad:union';
    CommandIDs.intersection = 'jupytercad:intersection';
    CommandIDs.updateAxes = 'jupytercad:updateAxes';
    CommandIDs.updateExplodedView = 'jupytercad:updateExplodedView';
})(CommandIDs || (CommandIDs = {}));
var Private;
(function (Private) {
    function createPart(part, tracker) {
        return async (args) => {
            const current = tracker.currentWidget;
            if (!current) {
                return;
            }
            const value = PARTS[part];
            current.context.model.syncFormData(value);
            const syncSelectedField = (id, value, parentType) => {
                let property = null;
                if (id) {
                    const prefix = id.split('_')[0];
                    property = id.substring(prefix.length);
                }
                current.context.model.syncSelectedPropField({
                    id: property,
                    value,
                    parentType
                });
            };
            const dialog = new FormDialog({
                context: current.context,
                title: value.title,
                sourceData: value.default(current.context.model),
                schema: FORM_SCHEMA[value.shape],
                syncData: (props) => {
                    const { Name } = props, parameters = __rest(props, ["Name"]);
                    const objectModel = {
                        shape: value.shape,
                        parameters,
                        visible: true,
                        name: Name
                    };
                    const sharedModel = current.context.model.sharedModel;
                    if (sharedModel) {
                        if (!sharedModel.objectExists(objectModel.name)) {
                            sharedModel.addObject(objectModel);
                        }
                        else {
                            showErrorMessage('The object already exists', 'There is an existing object with the same name.');
                        }
                    }
                },
                cancelButton: () => {
                    current.context.model.syncFormData(undefined);
                },
                syncSelectedPropField: syncSelectedField
            });
            await dialog.launch();
        };
    }
    Private.createPart = createPart;
    function executeOperator(operator, tracker) {
        return async (args) => {
            const current = tracker.currentWidget;
            if (!current) {
                return;
            }
            const op = OPERATORS[operator];
            // Fill form schema with available objects
            const form_schema = JSON.parse(JSON.stringify(FORM_SCHEMA[op.shape]));
            const allObjects = current.context.model.getAllObject().map(o => o.name);
            for (const prop in form_schema['properties']) {
                const fcType = form_schema['properties'][prop]['fcType'];
                if (fcType) {
                    const propDef = form_schema['properties'][prop];
                    switch (fcType) {
                        case 'App::PropertyLink':
                            propDef['enum'] = allObjects;
                            break;
                        case 'App::PropertyLinkList':
                            propDef['items']['enum'] = allObjects;
                            break;
                        default:
                    }
                }
            }
            const dialog = new FormDialog({
                context: current.context,
                title: op.title,
                sourceData: op.default(current.context.model),
                schema: form_schema,
                syncData: op.syncData(current.context.model),
                cancelButton: true
            });
            await dialog.launch();
        };
    }
    Private.executeOperator = executeOperator;
})(Private || (Private = {}));
