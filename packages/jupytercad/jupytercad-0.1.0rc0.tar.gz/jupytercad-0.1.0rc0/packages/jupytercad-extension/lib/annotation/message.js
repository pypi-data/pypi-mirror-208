import * as React from 'react';
export const Message = (props) => {
    var _a, _b, _c;
    const { self, message, user } = props;
    const color = (_a = user === null || user === void 0 ? void 0 : user.color) !== null && _a !== void 0 ? _a : 'black';
    const author = (_b = user === null || user === void 0 ? void 0 : user.display_name) !== null && _b !== void 0 ? _b : '';
    const initials = (_c = user === null || user === void 0 ? void 0 : user.initials) !== null && _c !== void 0 ? _c : '';
    return (React.createElement("div", { className: "jcad-Annotation-Message", style: {
            flexFlow: self ? 'row' : 'row-reverse'
        } },
        React.createElement("div", { className: "jcad-Annotation-User-Icon", style: {
                backgroundColor: color
            }, title: author },
            React.createElement("span", { style: { width: 24, textAlign: 'center' } }, initials)),
        React.createElement("div", { className: "jcad-Annotation-Message-Content" },
            React.createElement("p", { style: { padding: 7, margin: 0 } }, message))));
};
