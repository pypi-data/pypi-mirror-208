export class Line {
    constructor(start, end, controlPoints) {
        this.start = start;
        this.end = end;
        this.controlPoints = controlPoints;
    }
    export(scaleFactor = 1) {
        const scaledStart = {
            x: this.start.x / scaleFactor,
            y: this.start.y / scaleFactor
        };
        const scaledEnd = {
            x: this.end.x / scaleFactor,
            y: this.end.y / scaleFactor
        };
        return { start: scaledStart, end: scaledEnd };
    }
}
