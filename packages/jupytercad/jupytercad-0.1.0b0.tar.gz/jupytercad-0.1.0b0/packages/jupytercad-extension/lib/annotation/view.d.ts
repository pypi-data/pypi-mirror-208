/// <reference types="react" />
import { IAnnotationModel } from '../types';
interface IAnnotationProps {
    itemId: string;
    model: IAnnotationModel;
    children?: JSX.Element[] | JSX.Element;
}
interface IFloatingAnnotationProps extends IAnnotationProps {
    open: boolean;
}
export declare const Annotation: (props: IAnnotationProps) => JSX.Element;
export declare const FloatingAnnotation: (props: IFloatingAnnotationProps) => JSX.Element;
export {};
