import { IDict } from '../types';
import { TopoDS_Shape } from '@jupytercad/jupytercad-opencascade';
import { IJCadObject } from '../_interface/jcad';
import { IEdge, IFace } from '../types';
interface IShapeList {
    occShape: TopoDS_Shape;
    jcObject: IJCadObject;
}
export declare class OccParser {
    private _shapeList;
    private _occ;
    private _showEdge;
    constructor(shapeList: IShapeList[]);
    execute(): {
        [key: string]: {
            jcObject: IJCadObject;
            faceList: Array<IFace>;
            edgeList: Array<IEdge>;
            guiData?: IDict;
        };
    };
    private _build_wire_mesh;
    private _build_face_mesh;
    private _build_edge_mesh;
}
export {};
