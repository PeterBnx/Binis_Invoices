import { BrowserWindow, ipcMain } from 'electron';

export function register(win: BrowserWindow) {

  ipcMain.handle('test', async(_event, args) => {
    console.log(JSON.stringify(args, null, 2));
    console.log();
  })
}

export default register;
