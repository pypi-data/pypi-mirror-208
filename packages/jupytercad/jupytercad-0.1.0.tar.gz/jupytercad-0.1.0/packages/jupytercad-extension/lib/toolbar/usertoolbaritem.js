import * as React from 'react';
export class UsersItem extends React.Component {
    constructor(props) {
        super(props);
        this.selectUser = (user) => {
            var _a;
            let selected = undefined;
            if (user.userId !== ((_a = this.state.selectedUser) === null || _a === void 0 ? void 0 : _a.userId)) {
                selected = user;
            }
            this.setState(old => (Object.assign(Object.assign({}, old), { selectedUser: selected })), () => {
                this._model.setUserToFollow(selected === null || selected === void 0 ? void 0 : selected.userId);
            });
        };
        this._model = props.model;
        this.state = { usersList: [] };
    }
    componentDidMount() {
        this.setState(old => (Object.assign(Object.assign({}, old), { usersList: this._model.users })));
        this._model.userChanged.connect((_, usersList) => {
            this.setState(old => (Object.assign(Object.assign({}, old), { usersList: usersList })));
        });
    }
    createUserIcon(options) {
        var _a;
        let el;
        const { userId, userData } = options;
        const selected = `${userId === ((_a = this.state.selectedUser) === null || _a === void 0 ? void 0 : _a.userId) ? 'selected' : ''}`;
        if (userData.avatar_url) {
            el = (React.createElement("div", { key: userId, title: userData.display_name, className: `lm-MenuBar-itemIcon jp-MenuBar-imageIcon ${selected}`, onClick: () => this.selectUser(options) },
                React.createElement("img", { src: userData.avatar_url, alt: "" })));
        }
        else {
            el = (React.createElement("div", { key: userId, title: userData.display_name, className: `lm-MenuBar-itemIcon jp-MenuBar-anonymousIcon ${selected}`, style: { backgroundColor: userData.color }, onClick: () => this.selectUser(options) },
                React.createElement("span", null, userData.initials)));
        }
        return el;
    }
    render() {
        return (React.createElement("div", { className: "jpcad-toolbar-usertoolbar" }, this.state.usersList.map(item => {
            if (item.userId !== this._model.currentUserId) {
                return this.createUserIcon(item);
            }
        })));
    }
}
