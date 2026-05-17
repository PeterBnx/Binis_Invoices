/* eslint-disable @typescript-eslint/no-unused-vars */
import { BrowserWindow, dialog, ipcMain } from "electron";
import { runPythonScript, startServer } from "../socketConnection.js";
import * as dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function register(win: BrowserWindow) {
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

    ipcMain.handle('get_email', async(_event, args) => {
        dotenv.config({ path: path.join(__dirname, '../../.env') });
        console.log(path.join(__dirname, '../../.env'));
        return process.env.VITE_USER_EMAIL;
    });

    ipcMain.handle('save_credentials', async(_event, creds) => {
        const { empUser, empPass, cisUser, cisPass } = creds;
        runPythonScript('ipc.py', ['save_credentials', empUser, empPass, cisUser, cisPass], null);
        return true;
    });

    ipcMain.handle('get_credentials', async(_event, creds) => {
        runPythonScript('ipc.py', ['get_credentials'], null);
        return true;
    });

    ipcMain.handle('show_message_dialog', async (event, config) => {
        return await dialog.showMessageBox({
            type: config.type,
            buttons: ['OK'],
            defaultId: 0,
            title: config.title,
            message: config.message,
            detail: config.detail,
        });
    });
}

export default register;