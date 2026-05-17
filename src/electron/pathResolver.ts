import path from 'path';
import { app } from 'electron';

const isPackaged = app.isPackaged;

export function getPreloadPath() {
  if (!isPackaged) {
    return path.join(app.getAppPath(), 'dist-electron', 'preload.cjs');
  }
  return path.join(app.getAppPath(), 'dist-electron', 'preload.cjs');
}

export function getScriptsPath() {
  if (!isPackaged) {
    return path.join(app.getAppPath(), 'src','scripts'); 
  }
  return path.join(process.resourcesPath, 'bin');
}

export function getAssetsPath() {
  if (!isPackaged) {
    return path.join(app.getAppPath(), 'src', 'ui', 'assets');
  }
  return path.join(app.getAppPath(), 'dist', 'assets');
}