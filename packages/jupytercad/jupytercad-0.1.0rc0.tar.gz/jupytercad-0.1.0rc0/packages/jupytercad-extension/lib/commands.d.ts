import { JupyterFrontEnd } from '@jupyterlab/application';
import { WidgetTracker } from '@jupyterlab/apputils';
import { ITranslator } from '@jupyterlab/translation';
import { JupyterCadWidget } from './widget';
/**
 * Add the FreeCAD commands to the application's command registry.
 */
export declare function addCommands(app: JupyterFrontEnd, tracker: WidgetTracker<JupyterCadWidget>, translator: ITranslator): void;
/**
 * The command IDs used by the FreeCAD plugin.
 */
export declare namespace CommandIDs {
    const redo = "jupytercad:redo";
    const undo = "jupytercad:undo";
    const newSketch = "jupytercad:sketch";
    const newBox = "jupytercad:newBox";
    const newCylinder = "jupytercad:newCylinder";
    const newSphere = "jupytercad:newSphere";
    const newCone = "jupytercad:newCone";
    const newTorus = "jupytercad:newTorus";
    const cut = "jupytercad:cut";
    const extrusion = "jupytercad:extrusion";
    const union = "jupytercad:union";
    const intersection = "jupytercad:intersection";
    const updateAxes = "jupytercad:updateAxes";
    const updateExplodedView = "jupytercad:updateExplodedView";
}
