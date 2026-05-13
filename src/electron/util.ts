import { BrowserWindow } from "electron";

let mainWindow: BrowserWindow | null = null;

export function isDev(): boolean {
    return process.env.NODE_ENV === 'development';
}

export function sendMessageToRenderer<K extends keyof IpcReceiveChannels>(
  win: BrowserWindow | null,
  channel: K,
  ...args: IpcReceiveChannels[K]
) {
    if (win) {
        win.webContents.send(channel as string, ...args);
    }
}

export function setMainWindow(w: BrowserWindow): void {
    mainWindow = w;
}

export function getMainWindow(): BrowserWindow | null {
    return mainWindow;
}

// Returns true if 2 same type objects are different
export function areObjectsDifferent(obj1: Record<string, any>, obj2: Record<string, any>): boolean {
  const keys = new Set([...Object.keys(obj1), ...Object.keys(obj2)]);

  for (const key of keys) {
    const val1 = obj1[key];
    const val2 = obj2[key];

    if (
      val1 !== null &&
      val2 !== null &&
      typeof val1 === "object" &&
      typeof val2 === "object"
    ) {
      if (areObjectsDifferent(val1, val2)) return true;
    } else if (val1 !== val2) {
      return true;
    }
  }

  return false;
}