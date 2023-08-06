import { MainMenu } from './widget';
const PLUGIN_ID = 'jupytercad:topmenu';
/**
 * A service providing an interface to the main menu.
 */
const plugin = {
    id: PLUGIN_ID,
    requires: [],
    autoStart: true,
    activate: (app) => {
        const menu = new MainMenu();
        menu.id = 'jupytercad-topmenu';
        app.shell.add(menu, 'menu', { rank: 100 });
    }
};
export default plugin;
