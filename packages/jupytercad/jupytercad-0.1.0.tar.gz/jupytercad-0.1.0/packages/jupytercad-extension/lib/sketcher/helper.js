import { Button } from '@jupyterlab/ui-components';
import * as React from 'react';
export function drawPoint(ctx, point, fillStyle = 'blue', size = 6) {
    ctx.save();
    ctx.fillStyle = fillStyle;
    ctx.fillRect(point.x - size / 2, point.y - size / 2, size, size);
    ctx.restore();
}
export function drawLine(ctx, start, end, strokeStyle, lineWidth = 0.5) {
    ctx.save();
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = strokeStyle;
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.stroke();
    ctx.closePath();
    ctx.restore();
}
export function drawCircle(ctx, center, radius, strokeStyle, lineWidth = 1) {
    ctx.save();
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = strokeStyle;
    ctx.beginPath();
    ctx.arc(center.x, center.y, radius, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.closePath();
    ctx.restore();
}
export function ToolbarSwitch(props) {
    return (React.createElement(Button, { className: `jp-Button jp-mod-minimal jp-ToolbarButtonComponent jp-mod-styled ${props.toggled ? 'highlight' : ''}`, style: { color: 'const(--jp-ui-font-color1)' }, onClick: props.onClick }, props.label.toUpperCase()));
}
export function distance(p1, p2) {
    return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
}
