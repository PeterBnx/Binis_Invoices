/* eslint-disable @typescript-eslint/no-unused-vars */
import { BrowserWindow, ipcMain } from "electron";
import { Order } from "../types/objects.js";
import { runPythonScript, startServer } from "../socketConnection.js";

export function register(win: BrowserWindow) {
    ipcMain.handle('get_orders', async (_event, args) => {
        startServer();
        runPythonScript('ipc.py'); 
        
        return { status: "fetching_started" };
    });

    ipcMain.handle('test', async (_event, args) => {
        console.log('[IPC] test handler called');
        startServer();
        runPythonScript('test.py');
        return { status: "test_started" };
    });
}

export default register;