import { showErrorMessage } from '@jupyterlab/apputils';
import { v4 as uuid } from 'uuid';
import { distance } from './helper';
import { Line } from './elements/line';
import { Point } from './elements/point';
import { Circle } from './elements/circle';
// TODO Refactor this model to make use of the elemental classes (Point, Circle...)
export class SketcherModel {
    constructor(options) {
        this._points = new Map();
        this._lines = new Map();
        this._circles = new Map([]);
        this._editing = {
            type: null,
            content: null
        };
        this._gridSize = options.gridSize;
        this._sharedModel = options.sharedModel;
    }
    get gridSize() {
        return this._gridSize;
    }
    get points() {
        return this._points;
    }
    get lines() {
        return this._lines;
    }
    get circles() {
        return this._circles;
    }
    get editing() {
        return this._editing;
    }
    startEdit(type, content) {
        this._editing.type = type;
        this._editing.content = content;
    }
    updateEdit(type, content) {
        if (type === this._editing.type) {
            this.editing.content = content;
        }
    }
    stopEdit(removeLast) {
        var _a;
        if (removeLast) {
            const tempId = (_a = this._editing.content) === null || _a === void 0 ? void 0 : _a['tempId'];
            if (tempId) {
                switch (this._editing.type) {
                    case 'CIRCLE': {
                        this.removeCircle(tempId);
                        break;
                    }
                    case 'LINE': {
                        this.removeLine(tempId);
                        break;
                    }
                    default:
                        break;
                }
            }
        }
        this._editing.type = null;
        this._editing.content = null;
    }
    addPoint(position, option) {
        const near = this.getPointByPosition(position);
        if (near) {
            return near;
        }
        const id = uuid();
        this._points.set(id, new Point(position.x, position.y, option));
        return id;
    }
    removePoint(id) {
        this._points.delete(id);
    }
    getPointByPosition(pos) {
        for (const [key, val] of this._points.entries()) {
            if (distance(val.position, pos) < 0.05 * this._gridSize) {
                return key;
            }
        }
    }
    getPointById(id) {
        return this._points.get(id);
    }
    addLine(start, end) {
        const id = uuid();
        this._lines.set(id, new Line(start, end));
        return id;
    }
    removeLine(id) {
        this._lines.delete(id);
    }
    getLineById(id) {
        return this._lines.get(id);
    }
    getLineByControlPoint(pointId) {
        const lines = [];
        for (const [key, val] of this._lines.entries()) {
            if (val.controlPoints && val.controlPoints.includes(pointId)) {
                lines.push(key);
            }
        }
        return lines;
    }
    addCircle(center, radius) {
        const id = uuid();
        this._circles.set(id, new Circle(center, radius));
        return id;
    }
    removeCircle(id) {
        this._circles.delete(id);
    }
    getCircleById(id) {
        return this._circles.get(id);
    }
    getCircleByControlPoint(id) {
        const circles = [];
        for (const [key, val] of this._circles.entries()) {
            if (val.controlPoints && val.controlPoints.includes(id)) {
                circles.push(key);
            }
        }
        return circles;
    }
    async save(fileName, plane) {
        var _a;
        if (!this._sharedModel) {
            return;
        }
        if (!this._sharedModel.objectExists(fileName)) {
            const geometryList = [];
            this._circles.forEach(c => void geometryList.push(this._writeCircle(c.export(this._gridSize), plane)));
            this._lines.forEach(l => void geometryList.push(this._writeLine(l.export(this._gridSize), plane)));
            const newSketch = {
                shape: 'Sketcher::SketchObject',
                name: fileName,
                visible: true,
                parameters: {
                    Geometry: geometryList,
                    Placement: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 },
                    AttachmentOffset: { Position: [0, 0, 0], Axis: [0, 0, 1], Angle: 0 }
                }
            };
            (_a = this._sharedModel) === null || _a === void 0 ? void 0 : _a.addObject(newSketch);
        }
        else {
            showErrorMessage('The object already exists', 'There is an existing object with the same name.');
        }
    }
    _writeLine(l, plane) {
        let StartX = 0;
        let StartY = 0;
        let StartZ = 0;
        let EndX = 0;
        let EndY = 0;
        let EndZ = 0;
        if (plane === 'XY') {
            StartX = l.start.x;
            StartY = l.start.y;
            EndX = l.end.x;
            EndY = l.end.y;
        }
        else if (plane === 'YZ') {
            StartY = l.start.x;
            StartZ = l.start.y;
            EndY = l.end.x;
            EndZ = l.end.y;
        }
        else {
            StartZ = l.start.x;
            StartX = l.start.y;
            EndZ = l.end.x;
            EndX = l.end.y;
        }
        return {
            TypeId: 'Part::GeomLineSegment',
            StartX,
            StartY,
            StartZ,
            EndX,
            EndY,
            EndZ
        };
    }
    _writeCircle(c, plane) {
        let CenterX, CenterY, CenterZ;
        let NormalX = 0;
        let NormalY = 0;
        let NormalZ = 0;
        if (plane === 'XY') {
            CenterX = c.center.x;
            CenterY = c.center.y;
            CenterZ = 0;
            NormalZ = 1;
        }
        else if (plane === 'YZ') {
            CenterX = 0;
            CenterY = c.center.x;
            CenterZ = c.center.y;
            NormalX = 1;
        }
        else {
            CenterX = c.center.y;
            CenterY = 0;
            CenterZ = c.center.x;
            NormalY = 1;
        }
        return {
            TypeId: 'Part::GeomCircle',
            CenterX,
            CenterY,
            CenterZ,
            NormalX,
            NormalY,
            NormalZ,
            Radius: c.radius,
            AngleXU: 0
        };
    }
}
