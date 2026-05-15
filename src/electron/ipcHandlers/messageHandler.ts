/* eslint-disable @typescript-eslint/no-unused-vars */
import { BrowserWindow, ipcMain } from "electron";
import { Order } from "../types/objects.js";
import { runPythonScript, startServer } from "../socketConnection.js";

const CORRECT_PASSWORD = process.env.PASSWORD  

export function register(win: BrowserWindow) {
    ipcMain.handle('auth_login', (_event, password) => {
        return password === CORRECT_PASSWORD;
    })

    ipcMain.handle('get_orders', async (_event, args) => {
        startServer();
        runPythonScript('ipc.py', ['get_orders']); 
        
        return { status: "fetching_started" };
    });

    ipcMain.handle('get_order_data', async (_event, args) => {
        startServer();
        runPythonScript('ipc.py', args); 
        
        return { status: "fetching_started" };
    });

    ipcMain.handle('register_products', async (_event, args) => {
        startServer();
        runPythonScript('ipc.py', ['register_products'], args);
        return { status: "registering_started" };
    });

    ipcMain.handle('extract_invoice', async (_event, args) => {
        startServer();
        runPythonScript('ipc.py', ['extract_invoice'], args);
        return { status: "invoice_extraction_started" };
    });
}

export default register;