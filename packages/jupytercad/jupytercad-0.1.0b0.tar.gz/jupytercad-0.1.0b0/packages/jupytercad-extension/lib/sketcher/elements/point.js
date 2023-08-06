export class Point {
    constructor(x, y, option) {
        this.option = option;
        this._x = x;
        this._y = y;
    }
    get position() {
        return { x: this._x, y: this._y };
    }
    export(scaleFactor = 1) {
        return { x: this._x / scaleFactor, y: this._y / scaleFactor };
    }
}
