import * as React from 'react';
import { JupyterCadModel } from '../model';
import { IUserData } from '../types';
interface IProps {
    model: JupyterCadModel;
}
interface IState {
    usersList: IUserData[];
    selectedUser?: IUserData;
}
export declare class UsersItem extends React.Component<IProps, IState> {
    constructor(props: IProps);
    componentDidMount(): void;
    selectUser: (user: IUserData) => void;
    private createUserIcon;
    render(): React.ReactNode;
    private _model;
}
export {};
