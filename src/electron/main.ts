import { app, BrowserWindow, Menu } from 'electron';
import path from 'path';
import { isDev, setMainWindow } from './util.js';
import { getPreloadPath } from './pathResolver.js';
import { registerAllIpcHandlers } from './ipcHandlers/index.js';

let mainWindow: BrowserWindow | null = null;
let splashWindow: BrowserWindow | null = null;

if (!isDev()) {
  Menu.setApplicationMenu(null);
}

async function createMainWindow() {
  try {
    const splashPath = path.join(app.getAppPath(), 'src/ui/pages/splash/splash.html');

    splashWindow = new BrowserWindow({
      width: 500,
      height: 300,
      frame: false,
      transparent: true,
      alwaysOnTop: true,
      resizable: false,
      show: false
    });

    await splashWindow.loadFile(splashPath);
    splashWindow.show();

    mainWindow = new BrowserWindow({
      width: 1000,
      height: 700,
      minWidth: 600,
      minHeight: 500,
      show: false,
      webPreferences: {
        preload: getPreloadPath(),
        contextIsolation: true,
        sandbox: true,
        nodeIntegration: false
      }
    });

    await registerAllIpcHandlers(mainWindow);
    setMainWindow(mainWindow);

    if (isDev()) {
      await mainWindow.loadURL('http://localhost:4444');
    } else {
      const indexPath = path.join(app.getAppPath(), 'dist-react/index.html');
      await mainWindow.loadFile(indexPath);
    }

    mainWindow.show();
    splashWindow.destroy();
    splashWindow = null;

  } catch (err) {
    console.error('Failed to create main window:', err);
    splashWindow?.destroy();
    splashWindow = null;
  }
}


app.whenReady().then(createMainWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
});
