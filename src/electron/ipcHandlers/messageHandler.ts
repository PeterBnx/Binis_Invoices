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

    ipcMain.handle('get_order_data', async (_event, args) => {
        startServer();
        runPythonScript('ipc.py', args); 
        
        return { status: "fetching_started" };
    });
}

export default register;