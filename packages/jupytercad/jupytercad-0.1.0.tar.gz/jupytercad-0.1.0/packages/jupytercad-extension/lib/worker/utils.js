export function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = (hash << 5) - hash + char;
        hash = hash & hash;
    }
    return hash;
}
export function toRad(deg) {
    return (Math.PI * deg) / 180;
}
export function toDeg(rad) {
    return (180 * rad) / Math.PI;
}
