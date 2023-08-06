import { ISubmitEvent } from '@rjsf/core';
import * as React from 'react';
import { IDict } from '../types';
interface IStates {
    internalData?: IDict;
    schema?: IDict;
}
interface IProps {
    parentType: 'dialog' | 'panel';
    sourceData: IDict | undefined;
    filePath?: string;
    syncData: (properties: IDict) => void;
    syncSelectedField?: (id: string | null, value: any, parentType: 'panel' | 'dialog') => void;
    schema?: IDict;
    cancel?: () => void;
}
export declare const LuminoSchemaForm: (props: React.PropsWithChildren<any>) => JSX.Element;
export declare class ObjectPropertiesForm extends React.Component<IProps, IStates> {
    constructor(props: IProps);
    setStateByKey: (key: string, value: any) => void;
    componentDidUpdate(prevProps: IProps, prevState: IStates): void;
    buildForm(): JSX.Element[];
    removeArrayButton(schema: IDict, uiSchema: IDict): void;
    generateUiSchema(schema: IDict): IDict;
    onFormSubmit: (e: ISubmitEvent<any>) => void;
    render(): React.ReactNode;
}
export {};
