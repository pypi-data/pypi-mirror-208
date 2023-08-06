/**
 * Action definitions for worker
 */
export var WorkerAction;
(function (WorkerAction) {
    WorkerAction["LOAD_FILE"] = "LOAD_FILE";
    WorkerAction["SAVE_FILE"] = "SAVE_FILE";
    WorkerAction["REGISTER"] = "REGISTER";
})(WorkerAction || (WorkerAction = {}));
/**
 * Action definitions for main thread
 */
export var MainAction;
(function (MainAction) {
    MainAction["DISPLAY_SHAPE"] = "DISPLAY_SHAPE";
    MainAction["INITIALIZED"] = "INITIALIZED";
})(MainAction || (MainAction = {}));
