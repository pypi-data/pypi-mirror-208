import { ILayoutRestorer } from '@jupyterlab/application';
import { WidgetTracker } from '@jupyterlab/apputils';
import { ITranslator } from '@jupyterlab/translation';
import { IMainMenu } from '@jupyterlab/mainmenu';
import fcplugin from './fcplugin/plugins';
import jcadPlugin from './jcadplugin/plugins';
import { JupyterCadModel } from './model';
import { ControlPanelModel } from './panelview/model';
import { LeftPanelWidget } from './panelview/leftpanel';
import { RightPanelWidget } from './panelview/rightpanel';
import { IJupyterCadDocTracker, IAnnotation } from './token';
import { jcLightIcon } from './tools';
import { AnnotationModel } from './annotation/model';
import { notebookRendererPlugin, ypyWidgetManager } from './notebookrenderer';
import { addCommands, CommandIDs } from './commands';
const NAME_SPACE = 'jupytercad';
const plugin = {
    id: 'jupytercad:plugin',
    autoStart: true,
    requires: [ITranslator],
    optional: [IMainMenu],
    provides: IJupyterCadDocTracker,
    activate: (app, translator, mainMenu) => {
        const tracker = new WidgetTracker({
            namespace: NAME_SPACE
        });
        JupyterCadModel.worker = new Worker(new URL('./worker', import.meta.url));
        console.log('JupyterLab extension jupytercad is activated!');
        /**
         * Whether there is an active notebook.
         */
        const isEnabled = () => {
            return (tracker.currentWidget !== null &&
                tracker.currentWidget === app.shell.currentWidget);
        };
        addCommands(app, tracker, translator);
        if (mainMenu) {
            populateMenus(mainMenu, isEnabled);
        }
        return tracker;
    }
};
const annotationPlugin = {
    id: 'jupytercad:annotation',
    autoStart: true,
    requires: [IJupyterCadDocTracker],
    provides: IAnnotation,
    activate: (app, tracker) => {
        var _a;
        const annotationModel = new AnnotationModel({
            context: (_a = tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.context
        });
        tracker.currentChanged.connect((_, changed) => {
            annotationModel.context = (changed === null || changed === void 0 ? void 0 : changed.context) || undefined;
        });
        return annotationModel;
    }
};
const controlPanel = {
    id: 'jupytercad:controlpanel',
    autoStart: true,
    requires: [ILayoutRestorer, IJupyterCadDocTracker, IAnnotation],
    activate: (app, restorer, tracker, annotationModel) => {
        const controlModel = new ControlPanelModel({ tracker });
        const leftControlPanel = new LeftPanelWidget({
            model: controlModel,
            annotationModel,
            tracker
        });
        leftControlPanel.id = 'jupytercad::leftControlPanel';
        leftControlPanel.title.caption = 'JupyterCad Control Panel';
        leftControlPanel.title.icon = jcLightIcon;
        const rightControlPanel = new RightPanelWidget({ model: controlModel });
        rightControlPanel.id = 'jupytercad::rightControlPanel';
        rightControlPanel.title.caption = 'JupyterCad Control Panel';
        rightControlPanel.title.icon = jcLightIcon;
        if (restorer) {
            restorer.add(leftControlPanel, NAME_SPACE);
            restorer.add(rightControlPanel, NAME_SPACE);
        }
        app.shell.add(leftControlPanel, 'left', { rank: 2000 });
        app.shell.add(rightControlPanel, 'right', { rank: 2000 });
    }
};
/**
 * Populates the application menus for the notebook.
 */
function populateMenus(mainMenu, isEnabled) {
    // Add undo/redo hooks to the edit menu.
    mainMenu.editMenu.undoers.redo.add({
        id: CommandIDs.redo,
        isEnabled
    });
    mainMenu.editMenu.undoers.undo.add({
        id: CommandIDs.undo,
        isEnabled
    });
}
export default [
    plugin,
    controlPanel,
    fcplugin,
    jcadPlugin,
    annotationPlugin,
    notebookRendererPlugin,
    ypyWidgetManager
];
