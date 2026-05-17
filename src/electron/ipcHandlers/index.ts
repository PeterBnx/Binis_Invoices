import { BrowserWindow } from 'electron';
import registerMessageHandlers from './messageHandler.js';

export async function registerAllIpcHandlers(mainWindow: BrowserWindow) {
  try {
    console.log('[IPC] Initializing manual IPC registration...');

    // Register handlers from messageHandler.ts
    if (typeof registerMessageHandlers === 'function') {
      registerMessageHandlers(mainWindow);
      console.log('[IPC] messageHandler registered successfully.');
    } else {
      console.error('[IPC] Failed to register: messageHandler export is not a function.');
    }

  } catch (err) {
    console.error('[IPC] Fatal error during IPC handler registration:', err);
  }
}

export default registerAllIpcHandlers;