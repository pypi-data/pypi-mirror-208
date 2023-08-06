import { caretRightIcon, closeIcon } from '@jupyterlab/ui-components';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import * as React from 'react';
import { minimizeIcon } from '../tools';
import { Message } from './message';
export const Annotation = (props) => {
    const { itemId, model } = props;
    const annotation = model.getAnnotation(itemId);
    const contents = React.useMemo(() => { var _a; return (_a = annotation === null || annotation === void 0 ? void 0 : annotation.contents) !== null && _a !== void 0 ? _a : []; }, [annotation]);
    const [messageContent, setMessageContent] = React.useState('');
    if (!annotation) {
        return React.createElement("div", null);
    }
    const submitMessage = () => {
        model.addContent(itemId, messageContent);
        setMessageContent('');
    };
    return (React.createElement("div", { className: "jcad-Annotation" },
        props.children,
        React.createElement("div", { style: { paddingBottom: 10, maxHeight: 400, overflow: 'auto' } }, contents.map(content => {
            var _a, _b;
            return (React.createElement(Message, { user: content.user, message: content.value, self: ((_a = model.user) === null || _a === void 0 ? void 0 : _a.username) === ((_b = content.user) === null || _b === void 0 ? void 0 : _b.username) }));
        })),
        React.createElement("div", { className: "jcad-Annotation-Message" },
            React.createElement("textarea", { rows: 3, placeholder: 'Ctrl+Enter to submit', value: messageContent, onChange: e => setMessageContent(e.currentTarget.value), onKeyDown: e => {
                    if (e.ctrlKey && e.key === 'Enter') {
                        submitMessage();
                    }
                } }),
            React.createElement("div", { onClick: submitMessage },
                React.createElement(caretRightIcon.react, { className: "jcad-Annotation-Submit" })))));
};
export const FloatingAnnotation = (props) => {
    const { itemId, model } = props;
    const [open, setOpen] = React.useState(props.open);
    // Function that either
    // - opens the annotation if `open`
    // - removes the annotation if `!open` and the annotation is empty
    // - closes the annotation if `!open` and the annotation is not empty
    const setOpenOrDelete = (open) => {
        var _a;
        if (open) {
            return setOpen(true);
        }
        if (!((_a = model.getAnnotation(itemId)) === null || _a === void 0 ? void 0 : _a.contents.length)) {
            return model.removeAnnotation(itemId);
        }
        setOpen(false);
    };
    return (React.createElement("div", null,
        React.createElement("div", { className: "jcad-Annotation-Handler", onClick: () => setOpenOrDelete(!open) }),
        React.createElement("div", { className: "jcad-FloatingAnnotation", style: { visibility: open ? 'visible' : 'hidden' } },
            React.createElement(Annotation, { model: model, itemId: itemId },
                React.createElement("div", { className: "jcad-Annotation-Topbar" },
                    React.createElement("div", { onClick: async () => {
                            var _a;
                            // If the annotation has no content
                            // we remove it right away without prompting
                            if (!((_a = model.getAnnotation(itemId)) === null || _a === void 0 ? void 0 : _a.contents.length)) {
                                return model.removeAnnotation(itemId);
                            }
                            const result = await showDialog({
                                title: 'Delete Annotation',
                                body: 'Are you sure you want to delete this annotation?',
                                buttons: [
                                    Dialog.cancelButton(),
                                    Dialog.okButton({ label: 'Delete' })
                                ]
                            });
                            if (result.button.accept) {
                                model.removeAnnotation(itemId);
                            }
                        } },
                        React.createElement(closeIcon.react, { className: "jcad-Annotation-TopBarIcon" })),
                    React.createElement("div", { onClick: () => {
                            setOpenOrDelete(false);
                        } },
                        React.createElement(minimizeIcon.react, { className: "jcad-Annotation-TopBarIcon" })))))));
};
