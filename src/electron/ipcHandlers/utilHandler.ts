import { BrowserWindow, ipcMain } from "electron";
import { areObjectsDifferent } from "../util.js";

function register(win: BrowserWindow) {
    ipcMain.handle('are_objects_different', async(_event, [obj1, obj2])=> {
        return areObjectsDifferent(obj1, obj2);
    });
}

export default register;