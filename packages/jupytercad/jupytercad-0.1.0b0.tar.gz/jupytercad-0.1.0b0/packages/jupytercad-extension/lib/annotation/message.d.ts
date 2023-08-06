import { User } from '@jupyterlab/services';
interface IProps {
    message: string;
    self: boolean;
    user?: User.IIdentity;
}
export declare const Message: (props: IProps) => JSX.Element;
export {};
