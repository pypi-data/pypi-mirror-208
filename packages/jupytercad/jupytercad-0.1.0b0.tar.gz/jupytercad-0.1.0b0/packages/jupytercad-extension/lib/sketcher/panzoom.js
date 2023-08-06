import { nearest } from '../tools';
export class PanZoom {
    constructor(ctx, gridSize) {
        this.ctx = ctx;
        this.gridSize = gridSize;
        this.x = 0;
        this.y = 0;
        this.scale = 1;
    }
    apply() {
        this.ctx.setTransform(this.scale, 0, 0, this.scale, this.x, this.y);
    }
    scaleAt(x, y, sc) {
        // x & y are screen coords, not world
        this.scale *= sc;
        this.x = x - (x - this.x) * sc;
        this.y = y - (y - this.y) * sc;
    }
    toWorld(screenCoor, snap = false, tol = 0.1) {
        // converts from screen coords to world coords
        const inv = 1 / this.scale;
        let x = (screenCoor.x - this.x) * inv;
        let y = (screenCoor.y - this.y) * inv;
        if (snap) {
            x = nearest(x / this.gridSize, tol) * this.gridSize;
            y = nearest(y / this.gridSize, tol) * this.gridSize;
        }
        return { x, y };
    }
    toScreen(worldPos) {
        const x = worldPos.x * this.scale + this.x;
        const y = worldPos.y * this.scale + this.y;
        return { x, y };
    }
}
