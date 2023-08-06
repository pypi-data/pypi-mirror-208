export class Circle {
    constructor(center, radius, controlPoints) {
        this.center = center;
        this.radius = radius;
        this.controlPoints = controlPoints;
    }
    export(scaleFactor = 1) {
        const scaledCenter = {
            x: this.center.x / scaleFactor,
            y: this.center.y / scaleFactor
        };
        return { center: scaledCenter, radius: this.radius / scaleFactor };
    }
}
