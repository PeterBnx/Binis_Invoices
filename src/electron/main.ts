import { app, BrowserWindow, Menu } from 'electron';
import path from 'path';
import { isDev, setMainWindow } from './util.js';
import { getPreloadPath } from './pathResolver.js';
import { registerAllIpcHandlers } from './ipcHandlers/index.js';
import { fileURLToPath } from 'url';
import pkg from 'electron-updater';
const { autoUpdater } = pkg;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow: BrowserWindow | null = null;
let splashWindow: BrowserWindow | null = null;

if (!isDev()) {
  Menu.setApplicationMenu(null);
}

async function createMainWindow() {
  try {
    // if (app.isPackaged) {
    //   mainWindow.loadFile(path.join(app.getAppPath(), 'dist-react', 'index.html'));
    // } else {
    //   mainWindow.loadURL('http://localhost:5173');
    // }

    // splashWindow = new BrowserWindow({
    //   width: 500,
    //   height: 300,
    //   frame: false,
    //   transparent: true,
    //   alwaysOnTop: true,
    //   resizable: false,
    //   show: false
    // });

    // await splashWindow.loadFile(splashPath);
    // splashWindow.show();

    mainWindow = new BrowserWindow({
      width: 1300,
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
      const indexPath = path.join(__dirname, '..', 'dist-react', 'index.html');
      await mainWindow.loadFile(indexPath);
    }

    mainWindow.show();
    mainWindow.webContents.openDevTools();
    // splashWindow.destroy();
    // splashWindow = null;

  } catch (err) {
    console.error('Failed to create main window:', err);
    splashWindow?.destroy();
    splashWindow = null;
  }
}

app.whenReady().then(() => {
  if (app.isPackaged && !process.env.ELECTRON_IS_DEV) {
    autoUpdater.checkForUpdatesAndNotify().catch((err) => {
    console.error('Failed to check for updates:', err);
  });}
  createMainWindow();
});

autoUpdater.on('checking-for-update', () => {
  console.log('Checking for update...');
});

autoUpdater.on('update-available', (info) => {
  console.log('Update available:', info.version);
});

autoUpdater.on('update-downloaded', () => {
  console.log('Update downloaded; will install now');
  autoUpdater.quitAndInstall(); 
});

autoUpdater.on('error', (err) => {
  console.error('Updater error:', err);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
});
