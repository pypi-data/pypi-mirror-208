import { ICommandPalette, IThemeManager } from '@jupyterlab/apputils';
import { fileIcon } from '@jupyterlab/ui-components';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { ILauncher } from '@jupyterlab/launcher';
import { ICollaborativeDrive } from '@jupyter/docprovider';
import { IAnnotation, IJupyterCadDocTracker } from '../token';
import { JupyterCadWidgetFactory } from '../factory';
import { JupyterCadJcadModelFactory } from './modelfactory';
import { JupyterCadDoc } from '../model';
const FACTORY = 'Jupytercad Jcad Factory';
const PALETTE_CATEGORY = 'JupyterCAD';
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.createNew = 'jupytercad:create-new-jcad-file';
})(CommandIDs || (CommandIDs = {}));
const activate = (app, tracker, themeManager, annotationModel, browserFactory, drive, launcher, palette) => {
    const widgetFactory = new JupyterCadWidgetFactory({
        name: FACTORY,
        modelName: 'jupytercad-jcadmodel',
        fileTypes: ['jcad'],
        defaultFor: ['jcad'],
        tracker,
        commands: app.commands
    });
    // Registering the widget factory
    app.docRegistry.addWidgetFactory(widgetFactory);
    // Creating and registering the model factory for our custom DocumentModel
    const modelFactory = new JupyterCadJcadModelFactory({ annotationModel });
    app.docRegistry.addModelFactory(modelFactory);
    // register the filetype
    app.docRegistry.addFileType({
        name: 'jcad',
        displayName: 'JCAD',
        mimeTypes: ['text/json'],
        extensions: ['.jcad', '.JCAD'],
        fileFormat: 'text',
        contentType: 'jcad'
    });
    const jcadSharedModelFactory = () => {
        return new JupyterCadDoc();
    };
    drive.sharedModelFactory.registerDocumentFactory('jcad', jcadSharedModelFactory);
    widgetFactory.widgetCreated.connect((sender, widget) => {
        widget.context.pathChanged.connect(() => {
            tracker.save(widget);
        });
        themeManager.themeChanged.connect((_, changes) => widget.context.model.themeChanged.emit(changes));
        tracker.add(widget);
        app.shell.activateById('jupytercad::leftControlPanel');
        app.shell.activateById('jupytercad::rightControlPanel');
    });
    app.commands.addCommand(CommandIDs.createNew, {
        label: args => (args['isPalette'] ? 'New JCAD Editor' : 'JCAD Editor'),
        caption: 'Create a new JCAD Editor',
        icon: args => (args['isPalette'] ? undefined : fileIcon),
        execute: async (args) => {
            var _a;
            // Get the directory in which the JCAD file must be created;
            // otherwise take the current filebrowser directory
            const cwd = (args['cwd'] ||
                ((_a = browserFactory.tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.model.path));
            // Create a new untitled Blockly file
            let model = await app.serviceManager.contents.newUntitled({
                path: cwd,
                type: 'file',
                ext: '.jcad'
            });
            console.debug('Model:', model);
            model = await app.serviceManager.contents.save(model.path, Object.assign(Object.assign({}, model), { format: 'text', size: undefined, content: '{\n\t"objects": [],\n\t"options": {},\n\t"metadata": {}\n}' }));
            // Open the newly created file with the 'Editor'
            return app.commands.execute('docmanager:open', {
                path: model.path,
                factory: FACTORY
            });
        }
    });
    // Add the command to the launcher
    if (launcher) {
        launcher.add({
            command: CommandIDs.createNew,
            category: 'Other',
            rank: 1
        });
    }
    // Add the command to the palette
    if (palette) {
        palette.addItem({
            command: CommandIDs.createNew,
            args: { isPalette: true },
            category: PALETTE_CATEGORY
        });
    }
};
const jcadPlugin = {
    id: 'jupytercad:jcadplugin',
    requires: [
        IJupyterCadDocTracker,
        IThemeManager,
        IAnnotation,
        IFileBrowserFactory,
        ICollaborativeDrive
    ],
    optional: [ILauncher, ICommandPalette],
    autoStart: true,
    activate
};
export default jcadPlugin;
