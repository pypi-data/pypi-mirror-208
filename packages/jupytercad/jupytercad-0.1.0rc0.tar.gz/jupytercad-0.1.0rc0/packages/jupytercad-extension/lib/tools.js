import { LabIcon } from '@jupyterlab/ui-components';
import jvControlLight from '../style/icon/jvcontrol.svg';
import minimizeIconStr from '../style/icon/minimize.svg';
import boxIconStr from '../style/icon/box.svg';
import coneIconStr from '../style/icon/cone.svg';
import sphereIconStr from '../style/icon/sphere.svg';
import cylinderIconStr from '../style/icon/cylinder.svg';
import torusIconStr from '../style/icon/torus.svg';
import cutIconStr from '../style/icon/cut.svg';
import unionIconStr from '../style/icon/union.svg';
import intersectionIconStr from '../style/icon/intersection.svg';
import extrusionIconStr from '../style/icon/extrusion.svg';
import axesIconStr from '../style/icon/axes.svg';
export const jcLightIcon = new LabIcon({
    name: 'jupytercad:control-light',
    svgstr: jvControlLight
});
export const minimizeIcon = new LabIcon({
    name: 'jupytercad:minimize-icon',
    svgstr: minimizeIconStr
});
export const boxIcon = new LabIcon({
    name: 'jupytercad:box-icon',
    svgstr: boxIconStr
});
export const coneIcon = new LabIcon({
    name: 'jupytercad:cone-icon',
    svgstr: coneIconStr
});
export const sphereIcon = new LabIcon({
    name: 'jupytercad:sphere-icon',
    svgstr: sphereIconStr
});
export const cylinderIcon = new LabIcon({
    name: 'jupytercad:cylinder-icon',
    svgstr: cylinderIconStr
});
export const torusIcon = new LabIcon({
    name: 'jupytercad:torus-icon',
    svgstr: torusIconStr
});
export const cutIcon = new LabIcon({
    name: 'jupytercad:cut-icon',
    svgstr: cutIconStr
});
export const unionIcon = new LabIcon({
    name: 'jupytercad:union-icon',
    svgstr: unionIconStr
});
export const intersectionIcon = new LabIcon({
    name: 'jupytercad:intersection-icon',
    svgstr: intersectionIconStr
});
export const extrusionIcon = new LabIcon({
    name: 'jupytercad:extrusion-icon',
    svgstr: extrusionIconStr
});
export const axesIcon = new LabIcon({
    name: 'jupytercad:axes-icon',
    svgstr: axesIconStr
});
export const explodedViewIcon = new LabIcon({
    name: 'jupytercad:explodedView-icon',
    svgstr: jvControlLight
});
export const debounce = (func, timeout = 100) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func(...args);
        }, timeout);
    };
};
export function throttle(callback, delay = 100) {
    let last;
    let timer;
    return function (...args) {
        const now = +new Date();
        if (last && now < last + delay) {
            clearTimeout(timer);
            timer = setTimeout(() => {
                last = now;
                callback(...args);
            }, delay);
        }
        else {
            last = now;
            callback(...args);
        }
    };
}
export function itemFromName(name, arr) {
    for (const it of arr) {
        if (it.name === name) {
            return it;
        }
    }
    return undefined;
}
export function focusInputField(filePath, fieldId, value, color, lastSelectedPropFieldId) {
    var _a;
    const propsToRemove = ['border-color', 'box-shadow'];
    let newSelected;
    if (!fieldId) {
        if (lastSelectedPropFieldId) {
            removeStyleFromProperty(filePath, lastSelectedPropFieldId, propsToRemove);
            if (value) {
                const el = getElementFromProperty(filePath, lastSelectedPropFieldId);
                if (((_a = el === null || el === void 0 ? void 0 : el.tagName) === null || _a === void 0 ? void 0 : _a.toLowerCase()) === 'input') {
                    el.value = value;
                }
            }
            newSelected = undefined;
        }
    }
    else {
        if (fieldId !== lastSelectedPropFieldId) {
            removeStyleFromProperty(filePath, lastSelectedPropFieldId, propsToRemove);
            const el = getElementFromProperty(filePath, fieldId);
            if (el) {
                el.style.borderColor = color !== null && color !== void 0 ? color : 'red';
                el.style.boxShadow = `inset 0 0 4px ${color !== null && color !== void 0 ? color : 'red'}`;
            }
            newSelected = fieldId;
        }
    }
    return newSelected;
}
export function getElementFromProperty(filePath, prop) {
    if (!filePath || !prop) {
        return;
    }
    const parent = document.querySelector(`[data-path="${filePath}"]`);
    if (parent) {
        const el = parent.querySelector(`[id$=${prop}]`);
        return el;
    }
}
export function removeStyleFromProperty(filePath, prop, properties) {
    if (!filePath || !prop || properties.length === 0) {
        return;
    }
    const el = getElementFromProperty(filePath, prop);
    if (el) {
        properties.forEach(prop => el.style.removeProperty(prop));
    }
}
export function nearest(n, tol) {
    const round = Math.round(n);
    if (Math.abs(round - n) < tol) {
        return round;
    }
    else {
        return n;
    }
}
