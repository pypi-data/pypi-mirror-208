import { ILabShell } from '@jupyterlab/application';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { ITranslator } from '@jupyterlab/translation';
import { folderIcon } from '@jupyterlab/ui-components';
const browserWidget = {
    id: '@jupyterlab/filebrowser-extension:widget',
    description: 'Adds the file browser to the application shell.',
    requires: [IDefaultFileBrowser, ITranslator, ILabShell],
    autoStart: true,
    activate: (app, browser, translator, labShell) => {
        const trans = translator.load('jupyterlab');
        browser.node.setAttribute('role', 'region');
        browser.node.setAttribute('aria-label', trans.__('File Browser Section'));
        browser.title.icon = folderIcon;
        browser.model.setFilter(e => {
            const name = e.name.toLowerCase();
            if (e.type === 'directory') {
                return {};
            }
            if (name.endsWith('fcstd') || name.endsWith('jcad')) {
                return {};
            }
            return null;
        });
        labShell.add(browser, 'left', { rank: 100, type: 'File Browser' });
    }
};
export default browserWidget;
