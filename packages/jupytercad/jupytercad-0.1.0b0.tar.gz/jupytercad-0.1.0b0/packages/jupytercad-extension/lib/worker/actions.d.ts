import { IJCadObject } from '../_interface/jcad';
import { OpenCascadeInstance, TopoDS_Shape } from '@jupytercad/jupytercad-opencascade';
import { WorkerAction } from '../types';
export declare function getOcc(): OpenCascadeInstance;
/**
 * Convert OpenCascade shapes into `THREE` compatible data types.
 *
 * @param {Array<TopoDS_Shape>} shapeData
 * @returns {{
 *   faceList: any[];
 *   edgeList: any[];
 * }}
 */
export declare function shapeToThree(shapeData: Array<{
    occShape: TopoDS_Shape;
    jcObject: IJCadObject;
}>): {
    faceList: any[];
    edgeList: any[];
};
declare const WorkerHandler: {
    [key in WorkerAction]: (payload: any) => any;
};
export default WorkerHandler;
